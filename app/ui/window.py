"""Main application window."""
import os
import subprocess
from pathlib import Path
from datetime import datetime

from PyQt6.QtCore import Qt, QThreadPool
from PyQt6.QtGui import QIcon
from PyQt6.QtSvgWidgets import QSvgWidget
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QLabel, QMessageBox, QInputDialog, QFileDialog
)

from app.models import AppState, FileItem, FileStatus, RunState, OutputFormat, LogEntry
from app.engine.converter import ConvertWorker, build_output_path
from app.engine.checks import find_tesseract, find_poppler
from app.ui.left_panel import LeftPanel
from app.ui.right_panel import RightPanel
from app.ui import styles as S

ASSETS = Path(__file__).parent.parent.parent / "assets"
VENDOR_POPPLER = Path(__file__).parent.parent.parent / "vendor" / "poppler" / "Library" / "bin"


def _vendor_poppler_path() -> str | None:
    p = VENDOR_POPPLER
    if (p / "pdftoppm.exe").exists():
        return str(p)
    return None


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self._state = AppState()
        self._worker: ConvertWorker | None = None
        self._poppler_path: str | None = None
        self._output_dir_override: str | None = None

        self.setWindowTitle("Jade PDF Converter")
        self.setMinimumSize(860, 600)

        self._build_ui()
        self._check_dependencies()

    def _build_ui(self):
        central = QWidget(self)
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        root.addWidget(self._build_title_bar())

        body = QHBoxLayout()
        body.setContentsMargins(0, 0, 0, 0)
        body.setSpacing(0)

        self._left = LeftPanel(self)
        self._left.files_added.connect(self._on_files_added)
        self._left.format_changed.connect(self._on_format_changed)
        self._left.output_dir_changed.connect(self._on_output_dir_changed)
        self._left.convert_clicked.connect(self._start_conversion)
        self._left.cancel_clicked.connect(self._cancel_conversion)
        self._left.open_folder_clicked.connect(self._open_output_folder)
        self._left.reset_clicked.connect(self._reset)
        body.addWidget(self._left)

        self._right = RightPanel(self)
        self._right.retry_clicked.connect(self._retry_file)
        body.addWidget(self._right, stretch=1)

        root.addLayout(body)

    def _build_title_bar(self) -> QWidget:
        bar = QWidget(self)
        bar.setObjectName("titleBar")
        bar.setFixedHeight(46)
        layout = QHBoxLayout(bar)
        layout.setContentsMargins(16, 0, 16, 0)
        layout.setSpacing(8)

        flower = QSvgWidget(str(ASSETS / "mark-flower.svg"), bar)
        flower.setFixedSize(19, 19)
        layout.addWidget(flower)

        title = QLabel("Jade PDF Converter", bar)
        title.setObjectName("titleLabel")
        layout.addWidget(title)

        badge = QLabel("CONVERTY", bar)
        badge.setObjectName("convertyBadge")
        layout.addWidget(badge)

        layout.addStretch()
        return bar

    def _check_dependencies(self):
        tess_ok, tess_info = find_tesseract()
        poppler_ok, poppler_info = find_poppler(str(VENDOR_POPPLER))

        if poppler_ok:
            self._poppler_path = poppler_info

        if not tess_ok:
            QMessageBox.critical(
                self,
                "Tesseract Not Found",
                "Tesseract OCR was not found on this machine.\n\n"
                "Please install it from:\n"
                "https://github.com/UB-Mannheim/tesseract/wiki\n\n"
                "The app will continue but scanned PDFs cannot be processed.",
            )
            self._right.log("error", "Tesseract not found — scanned PDFs will fail.")
        else:
            self._right.log("info", f"Session started · {tess_info} detected")

        if not poppler_ok:
            self._right.log("error", "Poppler not found in vendor/ — scanned PDFs will fail.")
        else:
            self._right.log("info", "Poppler utilities ready.")

        self._right.log("info", "Waiting for files…")

    def _on_files_added(self, paths: list[str]):
        existing = {f.path for f in self._state.files}
        added = 0
        for p in paths:
            if p not in existing:
                stat = Path(p).stat() if Path(p).exists() else None
                item = FileItem(
                    path=p,
                    name=Path(p).name,
                    size_bytes=stat.st_size if stat else 0,
                )
                self._state.files.append(item)
                added += 1

        if added:
            self._right.set_files(self._state.files)
            self._left.update_file_count(len(self._state.files))
            self._right.log("info", f"{len(self._state.files)} files queued · format {self._state.output_format.value.upper()}")
            self._right.log("info", "Ready to convert…")

    def _on_format_changed(self, fmt: str):
        self._state.output_format = OutputFormat(fmt)

    def _on_output_dir_changed(self, path: str):
        self._output_dir_override = path

    def _start_conversion(self):
        if not self._state.files:
            return

        paths = [f.path for f in self._state.files]
        fmt = self._state.output_format.value

        # Check for collisions
        collisions = []
        for src in paths:
            out = build_output_path(src, self._output_dir_override, fmt)
            if Path(out).exists():
                collisions.append((src, out))

        # Handle collisions one by one
        skip_set = set()
        for src, out in collisions:
            reply = QMessageBox.question(
                self,
                "File Already Exists",
                f"A file named '{Path(out).name}' already exists.\n\nOverwrite it or skip this file?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No,
            )
            if reply == QMessageBox.StandardButton.No:
                skip_set.add(src)

        active_paths = [p for p in paths if p not in skip_set]
        if not active_paths:
            return

        # Mark skipped files
        for item in self._state.files:
            if item.path in skip_set:
                item.status = FileStatus.ERROR
                item.error_message = "Skipped — file already exists."

        self._state.run_state = RunState.CONVERTING
        self._left.set_converting(Path(active_paths[0]).name, 0, len(active_paths))
        self._right.set_files(self._state.files)

        self._worker = ConvertWorker(
            active_paths,
            fmt,
            self._output_dir_override,
            poppler_path=self._poppler_path,
        )
        self._worker.signals.file_progress.connect(self._on_file_progress)
        self._worker.signals.file_done.connect(self._on_file_done)
        self._worker.signals.file_error.connect(self._on_file_error)
        self._worker.signals.overall_progress.connect(self._on_overall_progress)
        self._worker.signals.batch_complete.connect(self._on_batch_complete)
        self._worker.signals.log_line.connect(self._right.log)

        self._right.log("info", f"Starting batch · {len(active_paths)} files · {fmt.upper()}")
        QThreadPool.globalInstance().start(self._worker)

    def _cancel_conversion(self):
        if self._worker:
            self._worker.cancel()

    def _on_file_progress(self, index: int, progress: float):
        active_items = [f for f in self._state.files if f.status == FileStatus.PENDING or f.status == FileStatus.PROCESSING]
        # Find the item by tracking which active file index we're on
        active_paths = [f.path for f in self._state.files if f.status != FileStatus.ERROR or f.error_message == "Skipped — file already exists."]
        # Map worker index to state index
        processing_paths = [f.path for f in self._state.files if f.status in (FileStatus.PENDING, FileStatus.PROCESSING)]

        # Simpler: track by order — mark items as they go
        pending = [f for f in self._state.files if f.status == FileStatus.PENDING]
        if pending and index < len([f for f in self._state.files if f.status == FileStatus.PROCESSING or f.status == FileStatus.PENDING]):
            # Find the currently processing item
            for item in self._state.files:
                if item.status == FileStatus.PROCESSING:
                    item.progress = progress
                    state_idx = self._state.files.index(item)
                    self._right.update_file_row(state_idx, item)
                    self._left.update_progress(self._state.overall_progress, item.name)
                    break
            else:
                # Start processing the next pending item
                for item in self._state.files:
                    if item.status == FileStatus.PENDING:
                        item.status = FileStatus.PROCESSING
                        item.progress = progress
                        state_idx = self._state.files.index(item)
                        self._right.update_file_row(state_idx, item)
                        done_count = sum(1 for f in self._state.files if f.status == FileStatus.DONE)
                        self._left.set_converting(item.name, done_count, len([f for f in self._state.files if f.status != FileStatus.ERROR]))
                        break

    def _on_file_done(self, index: int, output_path: str):
        for item in self._state.files:
            if item.status == FileStatus.PROCESSING:
                item.status = FileStatus.DONE
                item.progress = 1.0
                item.output_path = output_path
                state_idx = self._state.files.index(item)
                self._right.update_file_row(state_idx, item)
                break

    def _on_file_error(self, index: int, message: str):
        for item in self._state.files:
            if item.status == FileStatus.PROCESSING:
                item.status = FileStatus.ERROR
                item.error_message = message
                state_idx = self._state.files.index(item)
                self._right.update_file_row(state_idx, item)
                break
        # Advance next pending item to processing
        for item in self._state.files:
            if item.status == FileStatus.PENDING:
                item.status = FileStatus.PROCESSING
                state_idx = self._state.files.index(item)
                self._right.update_file_row(state_idx, item)
                done_count = sum(1 for f in self._state.files if f.status == FileStatus.DONE)
                self._left.set_converting(item.name, done_count, len(self._state.files))
                break

    def _on_overall_progress(self, pct: float):
        self._state.overall_progress = pct
        current_name = ""
        for item in self._state.files:
            if item.status == FileStatus.PROCESSING:
                current_name = item.name
                break
        self._left.update_progress(pct, current_name)

    def _on_batch_complete(self):
        self._worker = None
        self._state.run_state = RunState.DONE

        converted = sum(1 for f in self._state.files if f.status == FileStatus.DONE)
        errors = sum(1 for f in self._state.files if f.status == FileStatus.ERROR)
        total = len(self._state.files)

        output_dir = self._get_effective_output_dir()
        self._right.show_log_download()

        if errors == 0:
            self._left.set_done(converted, total, output_dir)
        else:
            self._left.set_error(converted, errors, total)

        self._right.set_files(self._state.files)

    def _get_effective_output_dir(self) -> str:
        if self._output_dir_override:
            return self._output_dir_override
        done_items = [f for f in self._state.files if f.output_path]
        if done_items:
            return str(Path(done_items[0].output_path).parent)
        if self._state.files:
            return str(Path(self._state.files[0].path).parent)
        return ""

    def _open_output_folder(self):
        folder = self._get_effective_output_dir()
        if folder and Path(folder).exists():
            os.startfile(folder)

    def _retry_file(self, path: str):
        for item in self._state.files:
            if item.path == path:
                item.status = FileStatus.PENDING
                item.error_message = None
                item.progress = 0.0
                break
        self._right.set_files(self._state.files)
        self._left.update_file_count(sum(1 for f in self._state.files if f.status == FileStatus.PENDING))

    def _reset(self):
        self._state = AppState()
        self._output_dir_override = None
        self._right.set_files([])
        self._right.clear_log()
        self._left.reset()
        self._right.log("info", "Session started · Waiting for files…")
