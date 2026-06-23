"""Left control column — mascot, drop zone, format toggle, save-to, convert button."""
import os
from pathlib import Path

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QProgressBar, QFileDialog, QSizePolicy, QFrame
)

from app.models import RunState, OutputFormat
from app.ui.mascot import MascotWidget
from app.ui.drop_zone import DropZone
from app.ui import styles as S


class LeftPanel(QWidget):
    files_added = pyqtSignal(list)
    format_changed = pyqtSignal(str)
    output_dir_changed = pyqtSignal(str)
    convert_clicked = pyqtSignal()
    cancel_clicked = pyqtSignal()
    open_folder_clicked = pyqtSignal()
    reset_clicked = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("leftPanel")
        self.setFixedWidth(330)
        self._output_dir = None
        self._file_count = 0
        self._run_state = RunState.IDLE
        self._fmt = OutputFormat.DOCX
        self._build()

    def _build(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(22, 22, 22, 22)
        root.setSpacing(18)
        root.setAlignment(Qt.AlignmentFlag.AlignTop)

        # --- Mascot + heading ---
        self._mascot = MascotWidget(self)
        root.addWidget(self._mascot, alignment=Qt.AlignmentFlag.AlignLeft)

        self._heading = QLabel("Convert PDFs", self)
        self._heading.setObjectName("arrowHeading")
        root.addWidget(self._heading)

        self._subheading = QLabel("Drop files to begin", self)
        self._subheading.setObjectName("arrowSubheading")
        root.addWidget(self._subheading)

        # --- Drop zone ---
        self._drop_zone = DropZone(compact=False, parent=self)
        self._drop_zone.files_dropped.connect(self.files_added)
        root.addWidget(self._drop_zone)

        # --- Progress / result card (hidden initially) ---
        self._progress_card = self._build_progress_card()
        self._progress_card.hide()
        root.addWidget(self._progress_card)

        self._done_card = self._build_done_card()
        self._done_card.hide()
        root.addWidget(self._done_card)

        self._error_card = self._build_error_card()
        self._error_card.hide()
        root.addWidget(self._error_card)

        # --- Format toggle ---
        self._fmt_widget = self._build_format_toggle()
        root.addWidget(self._fmt_widget)

        # --- Save-to row ---
        self._save_row = self._build_save_row()
        root.addWidget(self._save_row)

        root.addStretch()

        # --- Convert button (pinned to bottom) ---
        self._btn_convert = QPushButton("Convert", self)
        self._btn_convert.setObjectName("btnPrimary")
        self._btn_convert.setEnabled(False)
        self._btn_convert.setMinimumHeight(42)
        self._btn_convert.clicked.connect(self.convert_clicked)
        root.addWidget(self._btn_convert)

        self._btn_cancel = QPushButton("Cancel Conversion", self)
        self._btn_cancel.setObjectName("btnCancel")
        self._btn_cancel.setMinimumHeight(42)
        self._btn_cancel.hide()
        self._btn_cancel.clicked.connect(self.cancel_clicked)
        root.addWidget(self._btn_cancel)

        self._btn_open_folder = QPushButton("Open Output Folder", self)
        self._btn_open_folder.setObjectName("btnPrimary")
        self._btn_open_folder.setMinimumHeight(42)
        self._btn_open_folder.hide()
        self._btn_open_folder.clicked.connect(self.open_folder_clicked)
        root.addWidget(self._btn_open_folder)

        self._btn_reset = QPushButton("Convert More Files", self)
        self._btn_reset.setObjectName("btnOutline")
        self._btn_reset.setMinimumHeight(42)
        self._btn_reset.hide()
        self._btn_reset.clicked.connect(self.reset_clicked)
        root.addWidget(self._btn_reset)

    def _build_progress_card(self) -> QWidget:
        card = QWidget(self)
        card.setObjectName("progressCard")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(6)

        lbl = QLabel("OVERALL PROGRESS", card)
        lbl.setObjectName("progressLabel")
        layout.addWidget(lbl)

        self._pct_label = QLabel("0%", card)
        self._pct_label.setObjectName("progressPercent")
        layout.addWidget(self._pct_label)

        self._progress_bar = QProgressBar(card)
        self._progress_bar.setRange(0, 100)
        self._progress_bar.setValue(0)
        self._progress_bar.setTextVisible(False)
        self._progress_bar.setFixedHeight(7)
        layout.addWidget(self._progress_bar)

        self._now_label = QLabel("", card)
        self._now_label.setObjectName("progressNow")
        self._now_label.setWordWrap(True)
        layout.addWidget(self._now_label)

        return card

    def _build_done_card(self) -> QWidget:
        card = QWidget(self)
        card.setObjectName("doneCard")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(14, 14, 14, 14)
        self._done_text = QLabel("", card)
        self._done_text.setObjectName("doneCardText")
        self._done_text.setWordWrap(True)
        layout.addWidget(self._done_text)
        return card

    def _build_error_card(self) -> QWidget:
        card = QWidget(self)
        card.setObjectName("errorCard")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(14, 14, 14, 14)
        self._error_text = QLabel("", card)
        self._error_text.setObjectName("errorCardText")
        self._error_text.setWordWrap(True)
        layout.addWidget(self._error_text)
        return card

    def _build_format_toggle(self) -> QWidget:
        wrapper = QWidget(self)
        wrapper.setObjectName("formatToggle")
        layout = QHBoxLayout(wrapper)
        layout.setContentsMargins(2, 2, 2, 2)
        layout.setSpacing(0)

        self._btn_docx = QPushButton("DOCX", wrapper)
        self._btn_docx.setObjectName("fmtBtnActive")
        self._btn_docx.clicked.connect(lambda: self._set_format(OutputFormat.DOCX))
        layout.addWidget(self._btn_docx)

        self._btn_md = QPushButton("MD", wrapper)
        self._btn_md.setObjectName("fmtBtn")
        self._btn_md.clicked.connect(lambda: self._set_format(OutputFormat.MD))
        layout.addWidget(self._btn_md)

        return wrapper

    def _build_save_row(self) -> QWidget:
        row = QWidget(self)
        layout = QHBoxLayout(row)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)

        icon = QLabel("📁", row)
        icon.setStyleSheet("background: transparent; font-size: 13px;")
        layout.addWidget(icon)

        self._save_path_label = QLabel("Same folder as source", row)
        self._save_path_label.setObjectName("saveToPath")
        self._save_path_label.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred
        )
        layout.addWidget(self._save_path_label)

        btn = QPushButton("Change", row)
        btn.setObjectName("btnChange")
        btn.clicked.connect(self._pick_output_dir)
        layout.addWidget(btn)

        return row

    def _set_format(self, fmt: OutputFormat):
        self._fmt = fmt
        if fmt == OutputFormat.DOCX:
            self._btn_docx.setObjectName("fmtBtnActive")
            self._btn_md.setObjectName("fmtBtn")
        else:
            self._btn_docx.setObjectName("fmtBtn")
            self._btn_md.setObjectName("fmtBtnActive")
        self._btn_docx.style().unpolish(self._btn_docx)
        self._btn_docx.style().polish(self._btn_docx)
        self._btn_md.style().unpolish(self._btn_md)
        self._btn_md.style().polish(self._btn_md)
        self.format_changed.emit(fmt.value)

    def _pick_output_dir(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Output Folder")
        if folder:
            self._output_dir = folder
            self._save_path_label.setText(folder)
            self.output_dir_changed.emit(folder)

    # --- Public update API ---

    def update_file_count(self, count: int):
        self._file_count = count
        if count == 0:
            self._btn_convert.setText("Convert")
            self._btn_convert.setEnabled(False)
            self._heading.setText("Convert PDFs")
            self._subheading.setText("Drop files to begin")
            self._mascot.set_state("idle")
        else:
            self._btn_convert.setText(f"Convert {count} {'File' if count == 1 else 'Files'} →")
            self._btn_convert.setEnabled(True)
            self._heading.setText(f"{count} {'file' if count == 1 else 'files'} ready")
            self._subheading.setText("")
            self._mascot.set_state("queued")

    def set_converting(self, current_name: str, done: int, total: int):
        self._mascot.set_state("converting")
        self._heading.setText("Converting…")
        self._subheading.setText(f"{done} of {total} files")

        self._drop_zone.hide()
        self._progress_card.show()
        self._done_card.hide()
        self._error_card.hide()

        self._now_label.setText(f"Now: {current_name} · reading text layer")

        self._btn_convert.hide()
        self._btn_cancel.show()
        self._btn_open_folder.hide()
        self._btn_reset.hide()

        self._fmt_widget.setEnabled(False)

    def update_progress(self, pct: float, current_name: str = ""):
        val = int(pct * 100)
        self._progress_bar.setValue(val)
        self._pct_label.setText(f"{val}%")
        if current_name:
            self._now_label.setText(f"Now: {current_name}")

    def set_done(self, converted: int, total: int, output_dir: str):
        self._mascot.set_state("done")
        self._heading.setText("All done!")
        self._subheading.setText(f"{converted} {'file' if converted == 1 else 'files'} converted")

        self._drop_zone.hide()
        self._progress_card.hide()
        self._error_card.hide()
        self._done_card.show()
        self._done_text.setText(
            f"{converted} of {total} converted · Saved to {output_dir} · all temp files cleaned up."
        )

        self._btn_convert.hide()
        self._btn_cancel.hide()
        self._btn_open_folder.show()
        self._btn_reset.show()
        self._fmt_widget.setEnabled(True)

    def set_error(self, converted: int, skipped: int, total: int):
        self._mascot.set_state("error")
        self._heading.setText(f"{skipped} {'needs' if skipped == 1 else 'need'} attention")
        self._subheading.setText(f"{converted} done · {skipped} skipped")

        self._drop_zone.hide()
        self._progress_card.hide()
        self._done_card.hide()
        self._error_card.show()
        self._error_text.setText(
            f"Batch finished. {converted} {'file' if converted == 1 else 'files'} converted. "
            f"{skipped} {'was' if skipped == 1 else 'were'} skipped and left unchanged — "
            f"nothing was overwritten."
        )

        self._btn_convert.hide()
        self._btn_cancel.hide()
        self._btn_open_folder.show()
        self._btn_reset.show()
        self._fmt_widget.setEnabled(True)

    def reset(self):
        self._drop_zone.show()
        self._progress_card.hide()
        self._done_card.hide()
        self._error_card.hide()
        self._btn_convert.show()
        self._btn_cancel.hide()
        self._btn_open_folder.hide()
        self._btn_reset.hide()
        self._fmt_widget.setEnabled(True)
        self.update_file_count(0)
