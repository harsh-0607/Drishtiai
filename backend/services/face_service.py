from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import numpy as np
import face_recognition

from motor.motor_asyncio import AsyncIOMotorDatabase

logger = logging.getLogger(__name__)


@dataclass
class FaceMatch:
    name: str
    distance: float


class FaceService:
    """Face registration and identification using MongoDB + face_recognition.

    MongoDB collection schema (faces):
      { user_id: str, person_name: str, embedding: [float, ...] }
    """

    def __init__(self, db: AsyncIOMotorDatabase) -> None:
        self._db = db
        self._collection = db.get_collection("faces")

    async def register_face(self, user_id: str, person_name: str, image_bytes: bytes) -> bool:
        """Register a person's face for a given user."""

        loop = asyncio.get_running_loop()

        def _encode() -> Optional[List[float]]:
            img = face_recognition.load_image_file(
                # face_recognition accepts file-like; bytes need wrapping
                # We use numpy frombuffer via PIL fallback is not allowed here.
                # load_image_file can take a file object; use BytesIO.
                __import__("io").BytesIO(image_bytes)
            )
            encodings = face_recognition.face_encodings(img)
            if not encodings:
                return None
            emb = encodings[0]
            return emb.astype(float).tolist()

        embedding = await loop.run_in_executor(None, _encode)
        if embedding is None:
            return False

        doc = {
            "user_id": user_id,
            "person_name": person_name,
            "embedding": embedding,
        }

        # Upsert by (user_id, person_name)
        await self._collection.update_one(
            {"user_id": user_id, "person_name": person_name},
            {"$set": doc},
            upsert=True,
        )
        return True

    async def identify_face(self, user_id: str, current_frame_bytes: bytes) -> Dict[str, Any]:
        """Identify a face in the current frame for the given user."""

        # Fetch registered faces for user
        registered = await self._collection.find({"user_id": user_id}).to_list(length=None)
        if not registered:
            return {"found": False}

        loop = asyncio.get_running_loop()

        def _identify() -> Dict[str, Any]:
            frame = face_recognition.load_image_file(__import__("io").BytesIO(current_frame_bytes))
            encs = face_recognition.face_encodings(frame)
            if not encs:
                return {"found": False}

            current_enc = encs[0]

            known_names: List[str] = []
            known_encs: List[np.ndarray] = []

            for doc in registered:
                emb = doc.get("embedding")
                name = doc.get("person_name")
                if not emb or not name:
                    continue
                known_names.append(str(name))
                known_encs.append(np.array(emb, dtype=np.float64))

            if not known_encs:
                return {"found": False}

            known_matrix = np.vstack(known_encs)

            # Compare and compute distances
            matches = face_recognition.compare_faces(known_matrix, current_enc, tolerance=0.6)
            distances = face_recognition.face_distance(known_matrix, current_enc)

            if distances.size == 0:
                return {"found": False}

            best_idx = int(np.argmin(distances))
            best_distance = float(distances[best_idx])

            if matches[best_idx] and best_distance < 0.6:
                return {"found": True, "name": known_names[best_idx], "distance": best_distance}

            return {"found": False}

        return await loop.run_in_executor(None, _identify)
