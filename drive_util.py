from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.exceptions import RefreshError
from googleapiclient.http import MediaFileUpload
from googleapiclient.http import MediaIoBaseDownload
from googleapiclient.discovery import build
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
import os, sys, time


SCOPES = ["https://www.googleapis.com/auth/drive"]


_thread_local = threading.local()


def delete_backup_root(service, f_path:str):
    folder = find_folder(service, f_path)
    if not folder:
        return False
    service.files().delete(fileId=folder["id"]).execute()
    return True


def external_path(relative_path):
    if getattr(sys, "frozen", False):
        base_path = os.path.dirname(sys.executable)
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)


def get_thread_service():
    if not hasattr(_thread_local, "service"):
        _thread_local.service = get_drive_service()
    return _thread_local.service


def _list_children(folder_id, local_path, file_list, lock, counter, callback):
    os.makedirs(local_path, exist_ok=True)

    this_service = get_thread_service()
    subfolders = []
    page_token = None 

    while True:
        response = this_service.files().list(
            q=f"'{folder_id}' in parents and trashed = false",
            spaces="drive",
            fields="nextPageToken, files(id, name, mimeType)",
            pageSize=1000,
            pageToken=page_token
        ).execute()

        for item in response.get("files", []):
            local_item = os.path.join(local_path, item["name"])

            if item["mimeType"] == "application/vnd.google-apps.folder":
                subfolders.append((item["id"], local_item))
            else:
                with lock:
                    file_list.append((item["id"], local_item))
                    counter["n"] += 1
                    n = counter["n"]
                if callback:
                    callback(n)

        page_token = response.get("nextPageToken")
        if not page_token:
            break

    return subfolders


def list_folder_tree(service, root_folder_id, root_local_path, callback=None, max_workers=30):
    file_list = []
    lock = threading.Lock()
    counter = {"n": 0}

    current_level = [(root_folder_id, root_local_path)]

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        while current_level:
            futures = [
                executor.submit(_list_children, fid, path, file_list, lock, counter, callback)
                for fid, path in current_level
            ]

            next_level = []
            for future in as_completed(futures):
                next_level.extend(future.result())

            current_level = next_level

    return file_list


def download_file(service, file_id, local_path):
    request = service.files().get_media(fileId=file_id)

    with open(local_path, "wb") as output:
        downloader = MediaIoBaseDownload(output, request)
        done = False
        while not done:
            _, done = downloader.next_chunk()


def get_drive_service():
    creds = None

    if os.path.exists(external_path("token.json")):
        creds = Credentials.from_authorized_user_file(external_path("token.json"), SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except RefreshError:
                creds = None

        if not creds or not creds.valid:
            cred_path = external_path("credentials.json")

            if not os.path.exists(cred_path):
                raise FileNotFoundError(
                    "No se encontró 'credentials.json' junto al ejecutable. "
                    "Descárgalo desde Google Cloud Console y colócalo en la "
                    "misma carpeta que la aplicación."
                )

            flow = InstalledAppFlow.from_client_secrets_file(cred_path, SCOPES)
            creds = flow.run_local_server(port=0)

    return build("drive", "v3", credentials=creds)


def is_folder_empty(service, folder_id, retries=3, delay=1.5):
    for attempt in range(retries):
        results = service.files().list(
            q=f"'{folder_id}' in parents and trashed = false",
            spaces="drive",
            fields="files(id)",
            pageSize=1
        ).execute()

        if not results.get("files"):
            return True

        if attempt < retries - 1:
            time.sleep(delay)

    return False


def delete_folder(service, folder_id):
    service.files().delete(fileId=folder_id).execute()


def upload_file(service, file_path: str, parent_id: str):
    file_name = os.path.basename(file_path)

    metadata = {
        "name": file_name,
        "parents": [parent_id]
    }

    media = MediaFileUpload(
        file_path,
        resumable=True
    )

    file = service.files().create(
        body=metadata,
        media_body=media,
        fields="id, name, size"
    ).execute()

    return file["id"]


def find_file(service, name, parent_id):
    name = name.replace("'","\\'")

    query = (
        f"name = '{name}' "
        f"and '{parent_id}' in parents "
        f"and trashed = false"
    )

    results = service.files().list(
        q=query,
        spaces="drive",
        fields="files(id, name, mimeType, size)",
        pageSize=10
    ).execute()

    files = results.get("files", [])

    if files:
        return files[0]["id"]

    return None


def update_file(service, file_path: str, file_id: str):
    file_name = os.path.basename(file_path)

    metadata = {
        "name": file_name
    }

    media = MediaFileUpload(
        file_path,
        resumable=True
    )

    file = service.files().update(
        fileId=file_id,
        body=metadata,
        media_body=media,
        fields="id, name, size"
    ).execute()

    return file["id"]


def delete_file(service, file_id: str):
    service.files().delete(
        fileId=file_id
    ).execute()


def find_folder(service, name, parent_id=None):
    name = name.replace("'","\\'")

    query = (
        "name = '{}' "
        "and mimeType = 'application/vnd.google-apps.folder' "
        "and trashed = false"
    ).format(name.replace("'", "\\'"))

    if parent_id:
        query += f" and '{parent_id}' in parents"

    results = service.files().list(
        q=query,
        spaces="drive",
        fields="files(id, name)",
        pageSize=10
    ).execute()

    folders = results.get("files", [])

    if folders:
        return folders[0]

    return None


def create_folder(service, name, parent_id=None):
    name = name.replace("'","\\'")
    
    metadata = {
        "name": name,
        "mimeType": "application/vnd.google-apps.folder"
    }

    if parent_id:
        metadata["parents"] = [parent_id]

    folder = service.files().create(
        body=metadata,
        fields="id, name"
    ).execute()

    return folder


def get_or_create_folder(service, name, parent_id=None):
    name = name.replace("'","\\'")
    
    folder = find_folder(service, name, parent_id)

    if folder:
        return folder["id"]

    folder = create_folder(
        service,
        name,
        parent_id
    )

    return folder["id"]

def get_folder(service,f_path:str):
    path = f_path.split('/')
    parent_id = None

    for p in path:
        parent_id = get_or_create_folder(
            service,
            p,
            parent_id
        )

    return parent_id