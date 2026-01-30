from googleapiclient.discovery import build
from googleapiclient.http import MediaInMemoryUpload
import json


def upload_drive_backup(creds, folder_id, filename, payload):
    drive = build("drive", "v3", credentials=creds)

    media = MediaInMemoryUpload(
        json.dumps(payload, indent=2).encode("utf-8"),
        mimetype="application/json",
    )

    drive.files().create(
        body={"name": filename, "parents": [folder_id]},
        media_body=media,
    ).execute()
