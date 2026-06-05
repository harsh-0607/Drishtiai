from __future__ import annotations

import json
import os
from typing import Optional

import firebase_admin
from firebase_admin import credentials, auth


def _init_firebase() -> None:
    if firebase_admin._apps:
        return

    # Option A: raw JSON string (recommended for docker secrets)
    raw = os.getenv("FIREBASE_SERVICE_ACCOUNT_JSON")
    if raw:
        try:
            info = json.loads(raw)
            cred = credentials.Certificate(info)
            firebase_admin.initialize_app(cred)
            return
        except Exception:
            # If raw isn't json, treat as a path.
            if os.path.exists(raw):
                cred = credentials.Certificate(raw)
                firebase_admin.initialize_app(cred)
                return
            raise

    # Option B: default credentials (rare)
    project_id = os.getenv("FIREBASE_PROJECT_ID")
    if project_id:
        firebase_admin.initialize_app(options={"projectId": project_id})
        return

    # If neither provided, leave uninitialized.


async def verify_bearer_token(authorization: Optional[str]) -> Optional[dict]:
    """Verify Firebase JWT from Authorization header.

    Returns decoded token dict if valid, else None.
    """

    if not authorization:
        return None

    if not authorization.lower().startswith("bearer "):
        return None

    token = authorization.split(" ", 1)[1].strip()
    if not token:
        return None

    _init_firebase()
    if not firebase_admin._apps:
        return None

    # firebase-admin is sync; offload if needed by caller.
    decoded = auth.verify_id_token(token)
    return decoded
