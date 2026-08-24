import json as js
from pathlib import Path
import sys, os
import drive_util as drive
import separate_folders as sf
from concurrent.futures import ThreadPoolExecutor, as_completed

data = {}
files = []
files_to_backup = []
files_to_erase = []
created_folders = []

folders_scanned = 0
folders_to_scan = 0
files_scanned = 0
total_files_scanned = 0

service = None
BASEDIR = "BACKUP-FILES"
base_folder_id = ""

folders_info = {}

progress_callback = None
current_folder = ""


def run_delete_backup(callback=None):
    global progress_callback, current_folder, folders_info

    progress_callback = callback
    current_folder = ""

    try:
        service = drive.get_drive_service()
        log("Buscando backup en la nube...")

        deleted = drive.delete_backup_root(service, BASEDIR)

        if deleted:
            log("Backup eliminado de Google Drive.")
        else:
            log("No se encontró ningún backup en la nube.")

        folders_info.clear()

        backup_data_path = external_path("backup_data.json")
        if os.path.exists(backup_data_path):
            os.remove(backup_data_path)

        d = load_json()
        d["parents_id"] = {}
        with open(external_path("backup_info.json"), "w", encoding="utf-8") as file:
            js.dump(d, file, indent=4)

        log("Estado local reiniciado.")

    finally:
        progress_callback = None


def external_path(relative_path):
    if getattr(sys, "frozen", False):
        base_path = os.path.dirname(sys.executable)
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)


def log(msg="", end="\n", flush=False):
    print(msg, end=end, flush=flush)

    if progress_callback:
        text = str(msg).split("\r")[-1].split("\n")[-1]
        if text:
            progress_callback(current_folder, text)


def load_backup_data():
    path = external_path("backup_data.json")
    
    if not os.path.exists(path):
        default = []
        with open(path, "w", encoding="utf-8") as file:
            js.dump(default, file, indent=4)
        return default

    with open(path, "r", encoding="utf-8") as file:
        return js.load(file)


def search_deleted_files():
    if Path(external_path("backup_data.json")).exists():
        backup = load_backup_data()
        backup_by_path = {file["filepath"]: file for file in files}
        erased_files = 0
        pos = 1

        for file in backup:
            math = (pos / len(backup)) * 100
            log(f"\rBuscando archivos eliminados... ({math:.1f}%)", end="", flush=True)
            pos += 1

            f = backup_by_path.get(file["filepath"])

            if not f:
                files_to_erase.append(file["filepath"])
                erased_files += 1

        log(f"\nArchivos borrados: {erased_files}")


def compare_data():
    if Path(external_path("backup_data.json")).exists():
        backup = load_backup_data()
        backup_by_path = {file["filepath"]: file for file in backup}
        modified_files = 0
        data_compared = 1

        for file in files:
            math = (data_compared / total_files_scanned) * 100
            log(f"\rComparando datos del backup... ({math:.1f}%)", end="", flush=True)
            data_compared += 1

            ogf = backup_by_path.get(file["filepath"])

            if ogf and file["modified"] == ogf["modified"]:
                continue

            files_to_backup.append(file["filepath"])
            modified_files += 1

        log(f"\nModified files: {modified_files}")
    else:
        for file in files:
            files_to_backup.append(file["filepath"])


def save_backup_data():
    with open(external_path("backup_data.json"), "w", encoding="utf-8") as file:
        js.dump(files, file, indent=4)
    log("Backup data updated.")


def error(msg):
    log(f"[ERROR] {msg}")


def load_json():
    path = external_path("backup_info.json")

    if not os.path.exists(path):
        default = {"folders": [], "excluded": [], "parents_id": {}}
        with open(path, "w", encoding="utf-8") as file:
            js.dump(default, file, indent=4)
        return default

    with open(path, "r", encoding="utf-8") as file:
        return js.load(file)


def load_directory_info():
    d = load_json()
    return d["parents_id"]


def save_directory_info():
    d = load_json()
    d["parents_id"] = folders_info
    with open(external_path("backup_info.json"), "w", encoding="utf-8") as file:
        js.dump(d, file, indent=4)


def scan_file(f_path):
    global files_scanned
    file = Path(f_path)

    files.append({
        "filepath": str(f_path),
        "modified": file.stat().st_mtime
    })
    files_scanned += 1
    log(f"\rEscaneando carpetas y archivos ({folders_scanned}/{folders_to_scan})... {files_scanned}", end="", flush=True)


def norm_path():
    pass


def scan_folder(f_path:str):
    folder = Path(f_path)

    if not folder.exists():
        error(f"folder '{folder}' doesn't exists")
        return

    if not folder.is_dir():
        error(f"{folder} is not a directory")
        return

    if f_path not in data["excluded"]:
        for file in folder.glob("*"):
            if file.is_file():
                scan_file(file)
            else:
                scan_folder(str(file))


def get_clean_dir(f_path:str):
    path = os.path.dirname(f_path)
    path = path.replace(":\\", "/")
    path = path.replace("\\", "/")
    return "/" + path


def backup_file(file:str):
    this_service = drive.get_thread_service()
    fname = os.path.basename(file)
    fdir = get_clean_dir(file)[1:]
    folder_id = folders_info.get(fdir)

    if folder_id:
        file_id = drive.find_file(this_service, fname, folder_id)
        if file_id:
            drive.update_file(this_service, file, file_id)
        else:
            drive.upload_file(this_service, file, folder_id)


def delete_file(file: str):
    this_service = drive.get_thread_service()
    fname = os.path.basename(file)
    fdir = get_clean_dir(file)[1:]
    folder_id = folders_info.get(fdir)

    if folder_id:
        file_id = drive.find_file(this_service, fname, folder_id)
        drive.delete_file(this_service, file_id)


def create_folder(folder_index: int, paths: list, parents: dict):
    folder = paths[folder_index]
    folder_name = os.path.basename(folder)
    parent = parents[folder]

    if folder not in folders_info:
        this_service = drive.get_drive_service()
        parent_id = base_folder_id if parent == -1 else folders_info.get(paths[parent])
        folders_info[folder] = drive.get_or_create_folder(this_service, folder_name, parent_id)


def run_restore(local_path, callback=None):
    global progress_callback, current_folder

    progress_callback = callback
    current_folder = ""

    try:
        service = drive.get_drive_service()
        base_folder_id = drive.get_folder(service, BASEDIR)

        file_list = drive.list_folder_tree(
            service,
            base_folder_id,
            local_path,
            callback=lambda n: log(f"\rIndexando archivos del backup... {n}\n(this might take a while)", end="", flush=True)
        )

        log("")
        log(f"Total archivos a descargar: {len(file_list)}")

        def _download_one(file_id, dest):
            this_service = drive.get_thread_service()
            drive.download_file(this_service, file_id, dest)

        pos = 0
        errors = []

        with ThreadPoolExecutor(max_workers=30) as executor:
            futures = {
                executor.submit(_download_one, fid, dest): dest
                for fid, dest in file_list
            }

            for future in as_completed(futures):
                dest = futures[future]
                try:
                    future.result()
                except Exception as e:
                    errors.append((dest, str(e)))

                pos += 1
                log(f"\rDescargando archivos... ({pos}/{len(file_list)})", end="", flush=True)

        if pos > 0:
            log("")

        if errors:
            log(f"Terminado con {len(errors)} errores.")
            for dest, err in errors[:10]:
                log(f"  - {dest}: {err}")
        else:
            log("Descarga completada.")

    finally:
        progress_callback = None


def cleanup_empty_folders(erased_files):
    if not erased_files:
        return

    this_service = drive.get_drive_service()

    unique_dirs = []
    for f in erased_files:
        d = get_clean_dir(f)[1:]
        if d not in unique_dirs:
            unique_dirs.append(d)

    checked_non_empty = set()
    already_deleted = set()

    log("Limpiando carpetas vacías...")
    pos = 0

    for start_dir in unique_dirs:
        this_dir = start_dir

        while this_dir and this_dir not in already_deleted:
            folder_id = folders_info.get(this_dir)

            if not folder_id or folder_id in checked_non_empty:
                break

            if not drive.is_folder_empty(this_service, folder_id):
                checked_non_empty.add(folder_id)
                break

            drive.delete_folder(this_service, folder_id)
            folders_info.pop(this_dir, None)
            already_deleted.add(this_dir)

            pos += 1
            log(f"\rCarpeta borrada ({pos}): {this_dir}", end="", flush=True)

            this_dir = os.path.dirname(this_dir)

    if pos > 0:
        log("")


def run_backup(callback=None):
    global data, files, files_to_backup, files_to_erase, created_folders
    global files_scanned, total_files_scanned, service, base_folder_id
    global folders_info, progress_callback, current_folder, folders_to_scan, folders_scanned

    progress_callback = callback
    current_folder = ""
    folders_scanned = 0

    files.clear()
    files_to_backup.clear()
    files_to_erase.clear()
    created_folders.clear()
    folders_info.clear()
    files_scanned = 0
    total_files_scanned = 0

    try:
        service = drive.get_drive_service()
        data = load_json()

        folders_to_scan = len(data["folders"])

        for folder in data["folders"]:
            current_folder = folder
            log(f"Current Folder: {folder}")
            folders_scanned += 1
            scan_folder(folder)
            total_files_scanned += files_scanned
            if files_scanned > 0:
                log("")
            files_scanned = 0

        current_folder = ""

        compare_data()
        search_deleted_files()

        folders_unrepeated_clean = []
        pos = 0
        len_ = len(files_to_backup + files_to_erase)

        for fold in files_to_backup + files_to_erase:
            pos += 1
            log(f"\rAnalizando estructuras de carpetas... ({pos}/{len_})", end="", flush=True)
            fdir = get_clean_dir(fold)
            if fdir not in folders_unrepeated_clean:
                folders_unrepeated_clean.append(fdir)

        if pos > 0:
            log("")

        levels, paths, parents = sf.separate_folders_by_level(folders_unrepeated_clean)
        base_folder_id = drive.get_folder(service, BASEDIR)
        folders_info = load_directory_info()

        pos = 0
        for level in levels:
            with ThreadPoolExecutor(max_workers=30) as executor:
                futures = [executor.submit(create_folder, index, paths, parents) for index in level]
                for future in as_completed(futures):
                    future.result()
                    pos += 1
                    math = (pos / len(paths)) * 100
                    log(f"\rObteniendo carpetas... ({math:.2f}%)", end="", flush=True)

        if pos != 0:
            log("")

        with ThreadPoolExecutor(max_workers=30) as executor:
            futures = [executor.submit(delete_file, file) for file in files_to_erase]
            pos = 0
            for future in as_completed(futures):
                future.result()
                pos += 1
                log(f"\rBorrando archivos del drive... ({pos}/{len(files_to_erase)})", end="", flush=True)
            if pos != 0:
                log("")

        with ThreadPoolExecutor(max_workers=30) as executor:
            futures = [executor.submit(backup_file, file) for file in files_to_backup]
            pos = 0
            for future in as_completed(futures):
                future.result()
                pos += 1
                log(f"\rSubiendo archivos al google drive... ({pos}/{len(files_to_backup)})", end="", flush=True)
            if pos != 0:
                log("")

        if len(files_to_erase) > 0:
            cleanup_empty_folders(files_to_erase)

        save_directory_info()
        save_backup_data()

    finally:
        progress_callback = None


if __name__ == "__main__":
    run_backup()