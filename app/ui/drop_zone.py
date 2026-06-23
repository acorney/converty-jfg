"""Drag-and-drop zone widget that accepts PDF files and folders."""
from pathlib import Path

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QDragEnterEvent, QDropEvent
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QHBoxLayout, QPushButton, QFileDialog
)

from app.ui.styles import GREEN


class DropZone(QWidget):
    files_dropped = pyqtSignal(list)  # list of PDF file paths

    def __init__(self, compact=False, parent=None):
        super().__init__(parent)
        self.compact = compact
        self.setAcceptDrops(True)
        self.setObjectName("dropZone")
        self._build(compact)

    def _build(self, compact: bool):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setSpacing(8)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        icon = QLabel("⬆", self)
        icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon.setStyleSheet(f"font-size: 22px; color: {GREEN}; background: transparent;")
        layout.addWidget(icon)

        main_label = QLabel("Drop a PDF or folder here", self)
        main_label.setObjectName("dropZoneLabel")
        main_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(main_label)

        if not compact:
            sub_label = QLabel("Scanned files are read with on-device OCR", self)
            sub_label.setObjectName("dropZoneSubLabel")
            sub_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(sub_label)

            btn_row = QHBoxLayout()
            btn_row.setSpacing(8)

            btn_files = QPushButton("Choose Files", self)
            btn_files.setObjectName("btnPrimary")
            btn_files.clicked.connect(self._pick_files)
            btn_row.addWidget(btn_files)

            btn_folder = QPushButton("Choose Folder", self)
            btn_folder.setObjectName("btnOutline")
            btn_folder.clicked.connect(self._pick_folder)
            btn_row.addWidget(btn_folder)

            layout.addLayout(btn_row)

    def _pick_files(self):
        paths, _ = QFileDialog.getOpenFileNames(
            self, "Select PDF files", "", "PDF Files (*.pdf)"
        )
        if paths:
            self.files_dropped.emit(paths)

    def _pick_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Folder")
        if folder:
            pdfs = [str(p) for p in Path(folder).glob("*.pdf")]
            if pdfs:
                self.files_dropped.emit(pdfs)

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            self.setStyleSheet(
                f"#dropZone {{ border: 2px dashed {GREEN}; border-radius: 9px; "
                f"background: #EEF6E3; }}"
            )
        else:
            event.ignore()

    def dragLeaveEvent(self, event):
        self.setStyleSheet("")

    def dropEvent(self, event: QDropEvent):
        self.setStyleSheet("")
        paths = []
        for url in event.mimeData().urls():
            local = url.toLocalFile()
            p = Path(local)
            if p.is_dir():
                paths.extend(str(f) for f in p.glob("*.pdf"))
            elif p.suffix.lower() == ".pdf":
                paths.append(str(p))
        if paths:
            self.files_dropped.emit(paths)
        event.acceptProposedAction()
