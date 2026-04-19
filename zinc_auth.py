import requests
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials


def refresh_access_token(client_id: str, client_secret: str, refresh_token: str) -> str:
    r = requests.post("https://oauth2.googleapis.com/token", data={
        "client_id": client_id,
        "client_secret": client_secret,
        "refresh_token": refresh_token,
        "grant_type": "refresh_token",
    })
    r.raise_for_status()
    return r.json()["access_token"]


def _creds(access_token: str) -> Credentials:
    return Credentials(token=access_token)


def build_slides_service(access_token: str):
    return build("slides", "v1", credentials=_creds(access_token), cache_discovery=False)


def build_drive_service(access_token: str):
    return build("drive", "v3", credentials=_creds(access_token), cache_discovery=False)
