"""Right panel — queue list + run log."""
import os
from datetime import datetime
from pathlib import Path

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QScrollArea, QFrame, QProgressBar, QSizePolicy, QFileDialog,
    QTextEdit
)

from app.models import FileItem, FileStatus
from app.ui import styles as S


class FileRow(QWidget):
    retry_clicked = pyqtSignal(str)

    def __init__(self, item: FileItem, parent=None):
        super().__init__(parent)
        self._path = item.path
        self._build(item)

    def _build(self, item: FileItem):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 10, 16, 10)
        layout.setSpacing(4)

        top = QHBoxLayout()
        top.setSpacing(8)

        icon = QLabel(self._status_icon(item.status), self)
        icon.setStyleSheet(f"font-size: 14px; background: transparent; color: {self._icon_color(item.status)};")
        top.addWidget(icon)

        name_col = QVBoxLayout()
        name_col.setSpacing(1)

        name = QLabel(item.name, self)
        name.setObjectName("fileName")
        name_col.addWidget(name)

        size_kb = item.size_bytes // 1024 if item.size_bytes else 0
        meta_text = f"{size_kb} KB" if size_kb else ""
        if item.output_path:
            meta_text = Path(item.output_path).name
        meta = QLabel(meta_text, self)
        meta.setObjectName("fileMeta")
        name_col.addWidget(meta)

        top.addLayout(name_col)
        top.addStretch()

        self._pill = QLabel(self._pill_text(item.status), self)
        self._pill.setObjectName(self._pill_obj(item.status))
        self._pill.setAlignment(Qt.AlignmentFlag.AlignCenter)
        top.addWidget(self._pill)

        layout.addLayout(top)

        if item.status == FileStatus.PROCESSING:
            self._prog = QProgressBar(self)
            self._prog.setRange(0, 100)
            self._prog.setValue(int(item.progress * 100))
            self._prog.setTextVisible(False)
            self._prog.setFixedHeight(5)
            layout.addWidget(self._prog)

        if item.status == FileStatus.ERROR and item.error_message:
            err = QLabel(item.error_message, self)
            err.setObjectName("fileErrorMsg")
            err.setWordWrap(True)
            layout.addWidget(err)

            retry_row = QHBoxLayout()
            retry_row.setContentsMargins(0, 0, 0, 0)
            btn = QPushButton("Retry", self)
            btn.setObjectName("btnChange")
            btn.clicked.connect(lambda: self.retry_clicked.emit(self._path))
            retry_row.addWidget(btn)
            retry_row.addStretch()
            layout.addLayout(retry_row)

        obj = "fileRowError" if item.status == FileStatus.ERROR else (
            "fileRowProcessing" if item.status == FileStatus.PROCESSING else "fileRow"
        )
        self.setObjectName(obj)

    def update_progress(self, progress: float):
        if hasattr(self, "_prog"):
            self._prog.setValue(int(progress * 100))

    @staticmethod
    def _status_icon(status: FileStatus) -> str:
        return {
            FileStatus.PENDING: "○",
            FileStatus.PROCESSING: "◑",
            FileStatus.DONE: "✓",
            FileStatus.ERROR: "✕",
        }.get(status, "○")

    @staticmethod
    def _icon_color(status: FileStatus) -> str:
        return {
            FileStatus.PENDING: S.INK_400,
            FileStatus.PROCESSING: S.GREEN,
            FileStatus.DONE: S.GREEN_SECONDARY,
            FileStatus.ERROR: S.ERROR_TEXT,
        }.get(status, S.INK_400)

    @staticmethod
    def _pill_text(status: FileStatus) -> str:
        return {
            FileStatus.PENDING: "Pending",
            FileStatus.PROCESSING: "Processing",
            FileStatus.DONE: "Done",
            FileStatus.ERROR: "Couldn't read",
        }.get(status, "Pending")

    @staticmethod
    def _pill_obj(status: FileStatus) -> str:
        return {
            FileStatus.PENDING: "pillPending",
            FileStatus.PROCESSING: "pillProcessing",
            FileStatus.DONE: "pillDone",
            FileStatus.ERROR: "pillError",
        }.get(status, "pillPending")


class QueuePanel(QWidget):
    retry_clicked = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._rows: list[FileRow] = []
        self._build()

    def _build(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        header = QHBoxLayout()
        header.setContentsMargins(16, 12, 16, 8)
        lbl = QLabel("QUEUE", self)
        lbl.setObjectName("queueHeader")
        header.addWidget(lbl)
        header.addStretch()
        self._count_label = QLabel("", self)
        self._count_label.setObjectName("queueCount")
        header.addWidget(self._count_label)
        layout.addLayout(header)

        sep = QFrame(self)
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet(f"color: {S.HAIRLINE};")
        layout.addWidget(sep)

        self._scroll = QScrollArea(self)
        self._scroll.setWidgetResizable(True)
        self._scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self._scroll.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        self._list_widget = QWidget()
        self._list_layout = QVBoxLayout(self._list_widget)
        self._list_layout.setContentsMargins(0, 0, 0, 0)
        self._list_layout.setSpacing(0)
        self._list_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self._empty_state = self._build_empty_state()
        self._list_layout.addWidget(self._empty_state)

        self._scroll.setWidget(self._list_widget)
        layout.addWidget(self._scroll)

    def _build_empty_state(self) -> QWidget:
        w = QWidget(self)
        layout = QVBoxLayout(w)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(6)
        layout.setContentsMargins(20, 40, 20, 40)

        icon = QLabel("📄", w)
        icon.setStyleSheet(f"font-size: 28px; color: {S.INK_400}; background: transparent;")
        icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(icon)

        lbl = QLabel("No files yet", w)
        lbl.setObjectName("emptyQueueLabel")
        lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(lbl)

        sub = QLabel("Drop PDFs on the left to build your queue", w)
        sub.setObjectName("emptyQueueSub")
        sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(sub)

        return w

    def set_files(self, files: list[FileItem]):
        for row in self._rows:
            self._list_layout.removeWidget(row)
            row.deleteLater()
        self._rows = []

        if not files:
            self._empty_state.show()
            self._count_label.setText("")
            return

        self._empty_state.hide()
        self._count_label.setText(f"{len(files)} files")

        for item in files:
            row = FileRow(item, self._list_widget)
            row.retry_clicked.connect(self.retry_clicked)
            self._list_layout.addWidget(row)
            self._rows.append(row)

    def update_file_row(self, index: int, item: FileItem):
        if 0 <= index < len(self._rows):
            old = self._rows[index]
            self._list_layout.removeWidget(old)
            old.deleteLater()
            new_row = FileRow(item, self._list_widget)
            new_row.retry_clicked.connect(self.retry_clicked)
            self._list_layout.insertWidget(index, new_row)
            self._rows[index] = new_row


class LogPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("logPanel")
        self._entries: list[tuple[str, str]] = []
        self._build()

    def _build(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 10, 16, 10)
        layout.setSpacing(6)

        header = QHBoxLayout()
        lbl = QLabel("RUN LOG", self)
        lbl.setObjectName("logHeader")
        header.addWidget(lbl)
        header.addStretch()

        self._btn_download = QPushButton("Download log", self)
        self._btn_download.setObjectName("btnDownloadLog")
        self._btn_download.hide()
        self._btn_download.clicked.connect(self._download_log)
        header.addWidget(self._btn_download)

        layout.addLayout(header)

        self._log_text = QTextEdit(self)
        self._log_text.setObjectName("logArea")
        self._log_text.setReadOnly(True)
        self._log_text.setFixedHeight(90)
        self._log_text.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap)
        layout.addWidget(self._log_text)

    def add_line(self, level: str, message: str):
        now = datetime.now().strftime("%H:%M:%S")
        self._entries.append((level, f"[{now}] {message}"))
        color = S.GREEN_SECONDARY if level == "success" else (
            S.ERROR_TEXT if level == "error" else S.INK_500
        )
        self._log_text.append(
            f'<span style="color:{color}; font-family: Consolas, monospace; font-size:11px;">'
            f'[{now}] {message}</span>'
        )
        sb = self._log_text.verticalScrollBar()
        sb.setValue(sb.maximum())

    def show_download(self):
        self._btn_download.show()

    def _download_log(self):
        path, _ = QFileDialog.getSaveFileName(
            self, "Save Run Log", "converty-log.txt", "Text Files (*.txt)"
        )
        if path:
            with open(path, "w", encoding="utf-8") as f:
                for _, line in self._entries:
                    f.write(line + "\n")

    def clear(self):
        self._entries = []
        self._log_text.clear()
        self._btn_download.hide()


class RightPanel(QWidget):
    retry_clicked = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("rightPanel")
        self._build()

    def _build(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self._queue = QueuePanel(self)
        self._queue.retry_clicked.connect(self.retry_clicked)
        layout.addWidget(self._queue, stretch=1)

        self._log = LogPanel(self)
        layout.addWidget(self._log)

    # --- Delegate API ---

    def set_files(self, files: list[FileItem]):
        self._queue.set_files(files)

    def update_file_row(self, index: int, item: FileItem):
        self._queue.update_file_row(index, item)

    def log(self, level: str, message: str):
        self._log.add_line(level, message)

    def show_log_download(self):
        self._log.show_download()

    def clear_log(self):
        self._log.clear()
