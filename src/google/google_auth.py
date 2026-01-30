import os
import json
from google.oauth2.service_account import Credentials

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.file",
]

def get_google_creds():
    # Preferred: Render-style env var
    if "GOOGLE_SERVICE_ACCOUNT_JSON" in os.environ:
        return Credentials.from_service_account_info(
            json.loads(os.environ["GOOGLE_SERVICE_ACCOUNT_JSON"]),
            scopes=SCOPES,
        )

    # Fallback: local file (dev only)
    if os.path.exists("service-account.json"):
        return Credentials.from_service_account_file(
            "service-account.json",
            scopes=SCOPES,
        )

    raise RuntimeError(
        "No Google credentials found. "
        "Set GOOGLE_SERVICE_ACCOUNT_JSON or provide service-account.json"
    )
