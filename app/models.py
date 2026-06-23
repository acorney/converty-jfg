from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class FileStatus(Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    DONE = "done"
    ERROR = "error"


class RunState(Enum):
    IDLE = "idle"
    CONVERTING = "converting"
    DONE = "done"
    ERROR = "error"


class OutputFormat(Enum):
    DOCX = "docx"
    MD = "md"


class LogLevel(Enum):
    INFO = "info"
    SUCCESS = "success"
    ERROR = "error"


@dataclass
class FileItem:
    path: str
    name: str
    size_bytes: int = 0
    pages: int = 0
    is_scanned: Optional[bool] = None
    status: FileStatus = FileStatus.PENDING
    progress: float = 0.0
    output_path: Optional[str] = None
    error_message: Optional[str] = None


@dataclass
class LogEntry:
    ts: str
    line: str
    level: LogLevel = LogLevel.INFO


@dataclass
class AppState:
    files: list = field(default_factory=list)
    output_format: OutputFormat = OutputFormat.DOCX
    output_dir: Optional[str] = None
    run_state: RunState = RunState.IDLE
    overall_progress: float = 0.0
    current_index: int = -1
    log: list = field(default_factory=list)
