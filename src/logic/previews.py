"""File-type detection and preview helpers for non-media files.

- Text / Markdown / source files are shown as text.
- Office documents (ODF, OOXML, legacy MS formats, RTF) show their embedded
  thumbnail right away, then are rendered via LibreOffice (headless) to a
  cached PDF so the real pages can be displayed.
"""
import hashlib
import os
import shutil
import zipfile
from collections import deque
from pathlib import Path
from typing import Optional

from PyQt6.QtCore import QObject, QProcess, pyqtSignal


IMAGE_EXTS = {'.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp', '.tif', '.tiff',
              '.ico', '.svg', '.xpm', '.pbm', '.pgm', '.ppm'}
VIDEO_EXTS = {'.mp4', '.avi', '.mov', '.mkv', '.webm', '.flv'}
PDF_EXTS = {'.pdf'}
OFFICE_EXTS = {
    # OpenDocument
    '.odt', '.ods', '.odp', '.odg', '.ott', '.ots', '.otp', '.fodt', '.fods', '.fodp',
    # Microsoft
    '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx', '.rtf',
}
MARKDOWN_EXTS = {'.md', '.markdown', '.mdown', '.mkd'}
TEXT_EXTS = MARKDOWN_EXTS | {
    '.txt', '.text', '.log', '.csv', '.tsv', '.json', '.yaml', '.yml', '.toml',
    '.ini', '.cfg', '.conf', '.xml', '.html', '.htm', '.css', '.js', '.ts',
    '.py', '.sh', '.bash', '.c', '.h', '.cpp', '.hpp', '.java', '.go', '.rs',
    '.php', '.rb', '.pl', '.lua', '.sql', '.tex', '.rst', '.org', '.adoc',
    '.srt', '.vtt', '.env', '.properties', '.diff', '.patch',
}

TEXT_PREVIEW_LIMIT = 256 * 1024


def classify(path: Path) -> str:
    ext = path.suffix.lower()
    if ext in IMAGE_EXTS:
        return 'image'
    if ext in VIDEO_EXTS:
        return 'video'
    if ext in PDF_EXTS:
        return 'pdf'
    if ext in OFFICE_EXTS:
        return 'office'
    if ext in MARKDOWN_EXTS:
        return 'markdown'
    if ext in TEXT_EXTS or looks_like_text(path):
        return 'text'
    return 'other'


def looks_like_text(path: Path, probe: int = 8192) -> bool:
    try:
        with open(path, 'rb') as f:
            chunk = f.read(probe)
    except OSError:
        return False
    if not chunk:
        return True
    if b'\x00' in chunk:
        return False
    try:
        chunk.decode('utf-8')
        return True
    except UnicodeDecodeError as e:
        # A multi-byte char cut off at the probe boundary is fine
        return e.start >= len(chunk) - 3


def read_text(path: Path, limit: int = TEXT_PREVIEW_LIMIT) -> tuple[str, bool]:
    """Return (text, truncated)."""
    with open(path, 'rb') as f:
        data = f.read(limit + 1)
    truncated = len(data) > limit
    return data[:limit].decode('utf-8', errors='replace'), truncated


def embedded_thumbnail(path: Path) -> Optional[bytes]:
    """Thumbnail stored inside ODF (Thumbnails/thumbnail.png) or OOXML
    (docProps/thumbnail.*) packages."""
    try:
        with zipfile.ZipFile(path) as z:
            names = set(z.namelist())
            for candidate in ('Thumbnails/thumbnail.png', 'docProps/thumbnail.jpeg',
                              'docProps/thumbnail.jpg', 'docProps/thumbnail.png'):
                if candidate in names:
                    return z.read(candidate)
    except (zipfile.BadZipFile, OSError, KeyError):
        pass
    return None


def find_soffice() -> Optional[str]:
    for name in ('soffice', 'libreoffice'):
        found = shutil.which(name)
        if found:
            return found
    return None


def cache_dir() -> Path:
    base = Path(os.environ.get('XDG_CACHE_HOME', Path.home() / '.cache'))
    d = base / 'mediafoldersorter'
    d.mkdir(parents=True, exist_ok=True)
    return d


def cached_pdf_path(path: Path) -> Path:
    st = path.stat()
    key = hashlib.sha1(f"{path.resolve()}|{st.st_size}|{st.st_mtime_ns}".encode()).hexdigest()
    return cache_dir() / 'pdf' / key / (path.stem + '.pdf')


class DocConverter(QObject):
    """Converts office documents to PDF with LibreOffice, one at a time.

    Uses a private LibreOffice profile so it works while the user has
    LibreOffice open.
    """
    converted = pyqtSignal(str, str)   # source path, pdf path
    failed = pyqtSignal(str, str)      # source path, message

    def __init__(self, parent=None):
        super().__init__(parent)
        self.soffice = find_soffice()
        self._queue: deque[Path] = deque()
        self._proc: Optional[QProcess] = None
        self._current: Optional[Path] = None

    @property
    def available(self) -> bool:
        return self.soffice is not None

    def request(self, path: Path, priority: bool = False) -> Optional[Path]:
        """Return the cached PDF if present, else queue a conversion."""
        try:
            pdf = cached_pdf_path(path)
        except OSError:
            return None
        if pdf.exists():
            return pdf
        if not self.available:
            return None
        if path == self._current or path in self._queue:
            if priority and path in self._queue:
                self._queue.remove(path)
                self._queue.appendleft(path)
            return None
        if priority:
            self._queue.appendleft(path)
        else:
            self._queue.append(path)
        self._start_next()
        return None

    def _start_next(self) -> None:
        if self._proc is not None or not self._queue:
            return
        path = self._queue.popleft()
        try:
            pdf = cached_pdf_path(path)
        except OSError:
            self._start_next()
            return
        if pdf.exists():
            self.converted.emit(str(path), str(pdf))
            self._start_next()
            return
        pdf.parent.mkdir(parents=True, exist_ok=True)
        profile = (cache_dir() / 'lo-profile').as_uri()
        self._current = path
        self._proc = QProcess(self)
        self._proc.finished.connect(self._on_finished)
        self._proc.errorOccurred.connect(self._on_error)
        self._proc.start(self.soffice, [
            f'-env:UserInstallation={profile}',
            '--headless', '--norestore', '--convert-to', 'pdf',
            '--outdir', str(pdf.parent), str(path),
        ])

    def _on_finished(self, *_args) -> None:
        path = self._current
        proc = self._proc
        self._proc = None
        self._current = None
        if path is not None:
            pdf = cached_pdf_path(path) if path.exists() else None
            if pdf is not None and pdf.exists():
                self.converted.emit(str(path), str(pdf))
            else:
                err = bytes(proc.readAllStandardError()).decode(errors='replace').strip() if proc else ''
                self.failed.emit(str(path), err or 'LibreOffice conversion failed')
        if proc is not None:
            proc.deleteLater()
        self._start_next()

    def _on_error(self, error) -> None:
        if error == QProcess.ProcessError.FailedToStart:
            self._on_finished()

    def shutdown(self) -> None:
        self._queue.clear()
        if self._proc is not None:
            self._proc.kill()
            self._proc.waitForFinished(2000)
