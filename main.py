import sys, os
from main_win import Ui_MainWindow
import json as js
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QPushButton,
    QHBoxLayout, QSizePolicy, QFrame, QVBoxLayout, QFileDialog,
    QDialog, QVBoxLayout, QProgressBar, QMessageBox, QTextBrowser
)
from PySide6.QtCore import Qt, Signal, QThread, QUrl
from PySide6.QtGui import QFontMetrics
import manage_backup as backup
from PySide6.QtGui import QIcon
import webbrowser as web
import help


# DELETE BACKUP
class DeleteWorker(QThread):
    progress = Signal(str, str)
    finished_ok = Signal()
    failed = Signal(str)

    def run(self):
        try:
            backup.run_delete_backup(callback=self.progress.emit)
            self.finished_ok.emit()
        except Exception as e:
            self.failed.emit(str(e))


# BACKUP
class DownloadWorker(QThread):
    progress = Signal(str, str)
    finished_ok = Signal()
    failed = Signal(str)

    def __init__(self, local_path):
        super().__init__()
        self.local_path = local_path

    def run(self):
        try:
            backup.run_restore(self.local_path, callback=self.progress.emit)
            self.finished_ok.emit()
        except Exception as e:
            self.failed.emit(str(e))


class BackupWorker(QThread):
    progress = Signal(str, str)
    finished_ok = Signal()
    failed = Signal(str)

    def run(self):
        try:
            backup.run_backup(callback=self.progress.emit)
            self.finished_ok.emit()
        except Exception as e:
            self.failed.emit(str(e))


class ProgressDialog(QDialog):
    def __init__(self, parent=None, title=""):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setFixedSize(320, 110)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowCloseButtonHint)

        layout = QVBoxLayout(self)

        self.folder_label = QLabel("")
        self.folder_label.setWordWrap(True)
        self.folder_label.setStyleSheet("font-weight: bold;")

        self.status_label = QLabel("Iniciando backup...")
        self.status_label.setWordWrap(True)

        self.bar = QProgressBar()
        self.bar.setRange(0, 0)

        layout.addWidget(self.folder_label)
        layout.addWidget(self.status_label)
        layout.addWidget(self.bar)

    def update_text(self, folder, status):
        self.folder_label.setText(folder)
        self.folder_label.setVisible(bool(folder))
        self.status_label.setText(status)


# GLOBAL INFO
backup_folders = []
excluded_folders = []


# CREATE A FOLDER ITEM
class FolderItem(QWidget):
    delete_requested = Signal(object)

    def __init__(self, path):
        self.full_path = path
        super().__init__()

        self.separator = None
        self.layout_ref = None
        self.data_list = None

        self.setFixedHeight(20)
        self.setMaximumHeight(20)

        layout = QHBoxLayout(self)

        layout.setContentsMargins(5, 0, 5, 0)
        layout.setSpacing(5)

        self.label = QLabel(path)
        self.label.setSizePolicy(
            QSizePolicy.Policy.Ignored,
            QSizePolicy.Policy.Preferred
        )

        button = QPushButton("X")
        button.setStyleSheet("""
            QPushButton {
                padding: 0px;
                margin: 0px;
                font-size: 11px;
            }
        """)
        button.setFixedSize(20, 20)
        button.clicked.connect(lambda: self.delete_requested.emit(self))

        layout.addWidget(self.label, 1)
        layout.addWidget(button, 0)

    def resizeEvent(self, event):
        super().resizeEvent(event)

        if not hasattr(self, "label"):
            return

        metrics = QFontMetrics(self.label.font())
        elided = metrics.elidedText(
            self.full_path,
            Qt.TextElideMode.ElideLeft,
            self.label.width()
        )
        self.label.setText(elided)

        if elided != self.full_path:
            self.label.setToolTip(self.full_path)
        else:
            self.label.setToolTip("")


# HELP MENU
class HelpDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Cómo usar")
        self.resize(520, 600)

        layout = QVBoxLayout(self)

        browser = QTextBrowser()
        browser.setOpenExternalLinks(True)
        browser.setHtml(help.HELP_HTML)

        close_button = QPushButton("Cerrar")
        close_button.clicked.connect(self.accept)

        layout.addWidget(browser)
        layout.addWidget(close_button)


# INTERNAL FUNCTIONS
def resource_path(relative_path):
    base_path = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)


def external_path(relative_path):
    if getattr(sys, "frozen", False):
        base_path = os.path.dirname(sys.executable)
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)

def load_json():
    path = external_path("backup_info.json")

    if not os.path.exists(path):
        default = {"folders": [], "excluded": [], "parents_id": {}}
        with open(path, "w", encoding="utf-8") as file:
            js.dump(default, file, indent=4)
        return default

    with open(path, "r", encoding="utf-8") as file:
        return js.load(file)

def load_folders():
    global backup_folders, excluded_folders

    info = load_json()

    backup_folders = info.get("folders",[])
    excluded_folders = info.get("excluded",[])

    # setup items
    for folder in backup_folders:
        item = FolderItem(folder)
        window.add_item_backup(item)

    for folder in excluded_folders:
        item = FolderItem(folder)
        window.add_item_excluded(item)


def save_folders():
    info = load_json()

    info["folders"] = backup_folders
    info["excluded"] = excluded_folders

    with open(external_path("backup_info.json"),"w",encoding="utf-8") as file:
        js.dump(info,file,indent=4)


# WINDOW FUNCTIONS
def uploadBackup():
    dialog = ProgressDialog(window, "Subiendo backup")
    worker = BackupWorker()
    error_holder = {"msg": None}

    def on_failed(msg):
        error_holder["msg"] = msg
        dialog.reject()

    worker.progress.connect(dialog.update_text)
    worker.finished_ok.connect(dialog.accept)
    worker.failed.connect(on_failed)

    worker.start()
    dialog.exec()
    worker.wait()

    if error_holder["msg"] is None:
        QMessageBox.information(
            window, "Backup completado",
            "Backup almacenado correctamente en Google Drive"
        )
    else:
        QMessageBox.critical(window, "Error haciendo el backup", error_holder["msg"])

def downloadBackup():
    folder = QFileDialog.getExistingDirectory(window,"Selecciona una carpeta donde descargar el contenido del drive")
    
    if not folder:
        return

    dialog = ProgressDialog(window,"Descargando backup")
    worker = DownloadWorker(folder)
    error_holder = {"msg": None}

    def on_failed(msg):
        error_holder["msg"] = msg
        dialog.reject()

    worker.progress.connect(dialog.update_text)
    worker.finished_ok.connect(dialog.accept)
    worker.failed.connect(on_failed)

    worker.start()
    dialog.exec()
    worker.wait()

    if error_holder["msg"] is None:
        QMessageBox.information(
            window, "Descarga completada",
            "Datos del backup descargados correctamente en:\n"+folder
        )
    else:
        QMessageBox.critical(window, "Error de descarga", error_holder["msg"])

def deleteBackup():
    confirm = QMessageBox.warning(
        window,
        "Eliminar backup",
        "¿Estás seguro? Esta acción eliminará los archivos subidos en la nube de forma permanente.\n"
        "Esta acción NO se puede revertir.",
        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        QMessageBox.StandardButton.No
    )

    if confirm != QMessageBox.StandardButton.Yes:
        return

    dialog = ProgressDialog(window, "Borrando backup")
    worker = DeleteWorker()
    error_holder = {"msg": None}

    def on_failed(msg):
        error_holder["msg"] = msg
        dialog.reject()

    worker.progress.connect(dialog.update_text)
    worker.finished_ok.connect(dialog.accept)
    worker.failed.connect(on_failed)

    worker.start()
    dialog.exec()
    worker.wait()

    if error_holder["msg"] is None:
        QMessageBox.information(
            window, "Backup eliminado",
            "El backup se eliminó correctamente de la nube."
        )
    else:
        QMessageBox.critical(window, "Error al eliminar", error_holder["msg"])

def addFolder():
    folder = QFileDialog.getExistingDirectory(window,"Elegir carpeta para añadir al backup")

    if folder:
        item = FolderItem(folder)
        window.add_item_backup(item)
        backup_folders.append(folder.replace("/","\\"))

        save_folders()

def excludeFolder():
    folder = QFileDialog.getExistingDirectory(window,"Elegir carpeta para excluir del backup")
    
    if folder:
        item = FolderItem(folder)
        window.add_item_excluded(item)
        excluded_folders.append(folder.replace("/","\\"))

        save_folders()

def openGithub():
    web.open("https://github.com/CerosDeveloper/Google-drive-cloud-util")

def openHelp():
    dialog = HelpDialog(window)
    dialog.exec()


# MAIN WINDOW CLASS
class MainWindow(QMainWindow):
    def add_separator(self, layout):
        separator = QFrame()
        separator.setFixedHeight(1)

        separator.setStyleSheet("""
            QFrame {
                background-color: #353535;
            }
        """)

        layout.addWidget(separator)
        return separator
    
    def add_item_backup(self, item: FolderItem):
        self.ui.verticalLayout.addWidget(item)
        separator = self.add_separator(self.ui.verticalLayout)

        item.layout_ref = self.ui.verticalLayout
        item.separator = separator
        item.data_list = backup_folders
        item.delete_requested.connect(self.remove_item)

    def add_item_excluded(self, item: FolderItem):
        self.ui.verticalLayout_2.addWidget(item)
        separator = self.add_separator(self.ui.verticalLayout_2)

        item.layout_ref = self.ui.verticalLayout_2
        item.separator = separator
        item.data_list = excluded_folders
        item.delete_requested.connect(self.remove_item)

    def remove_item(self, item: FolderItem):
        item.layout_ref.removeWidget(item)
        item.setParent(None)
        item.deleteLater()

        if item.separator is not None:
            item.layout_ref.removeWidget(item.separator)
            item.separator.setParent(None)
            item.separator.deleteLater()

        if item.full_path in item.data_list:
            item.data_list.remove(item.full_path)

        save_folders()
    
    def __init__(self):
        super().__init__()

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        fix_layout = QVBoxLayout(self.ui.scrollAreaWidgetContents)
        fix_layout.setContentsMargins(0, 1, 0, 0)
        fix_layout.addWidget(self.ui.verticalLayoutWidget, 0, Qt.AlignmentFlag.AlignTop)

        fix_layout_2 = QVBoxLayout(self.ui.scrollAreaWidgetContents_2)
        fix_layout_2.setContentsMargins(0, 1, 0, 0)
        fix_layout_2.addWidget(self.ui.verticalLayoutWidget_2, 0, Qt.AlignmentFlag.AlignTop)

        self.ui.verticalLayoutWidget.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Minimum
        )

        self.ui.verticalLayoutWidget_2.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Minimum
        )

        self.ui.verticalLayout.setSpacing(2)

        self.ui.verticalLayout_2.setSpacing(2)

        self.ui.statusbar.hide()
        self.setFixedSize(380, 528)

        self.ui.menubar.setStyleSheet("""
            QMenuBar {
                background-color: #161616;
                color: #ffffff;
            }
            QMenuBar::item {
                background-color: #1E1E1E;
                padding: 5px 16px;
                margin-left: 2px;
                margin-top: 2px;
                margin-bottom: 1px;
                border-radius: 8px;
                border-width: 2px;
                border-color: #161616;
                border-style: solid;
            }
            QMenuBar::item:selected {
                background-color: #3d3d3d;
            }
        """)

        # setup actions
        self.ui.actionCreate_Backup.triggered.connect(uploadBackup)
        self.ui.actionDownload_Backup.triggered.connect(downloadBackup)
        self.ui.actionDelete.triggered.connect(deleteBackup)
        self.ui.actionHowtouse.triggered.connect(openHelp)
        self.ui.actionGithub.triggered.connect(openGithub)

        # setup buttons
        self.ui.addFolder.clicked.connect(addFolder)
        self.ui.addExcluded.clicked.connect(excludeFolder)


# START WINDOW
app = QApplication(sys.argv)
app.setWindowIcon(QIcon(resource_path("icon.ico")))

window = MainWindow()
window.setWindowIcon(QIcon(resource_path("icon.ico")))
window.show()

load_folders()

sys.exit(app.exec())