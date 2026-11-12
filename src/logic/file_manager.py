import shutil
from pathlib import Path
from typing import Optional


class FileManager:
    @staticmethod
    def move_file(source: Path, destination_folder: Path) -> bool:
        try:
            destination_folder.mkdir(parents=True, exist_ok=True)
            dest_path = destination_folder / source.name

            if dest_path.exists():
                return False

            shutil.move(str(source), str(dest_path))
            return True
        except Exception:
            return False

    @staticmethod
    def trash_file(source: Path) -> Optional[Path]:
        """Move a file to the system trash (freedesktop trash on Linux).

        Returns the file's new location inside the trash, or None on failure.
        """
        try:
            from PyQt6.QtCore import QFile
            ok, trashed = QFile.moveToTrash(str(source))
            if ok:
                return Path(trashed) if trashed else source
        except Exception:
            pass
        return None

    @staticmethod
    def restore_from_trash(trashed: Path, original: Path) -> bool:
        """Move a trashed file back to its original location and drop its
        .trashinfo entry (freedesktop layout: Trash/files + Trash/info)."""
        try:
            if original.exists() or not trashed.exists():
                return False
            original.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(trashed), str(original))
            if trashed.parent.name == "files":
                info = trashed.parent.parent / "info" / f"{trashed.name}.trashinfo"
                if info.exists():
                    info.unlink()
            return True
        except Exception:
            return False

    @staticmethod
    def file_exists(path: Path) -> bool:
        return path.exists()

    @staticmethod
    def get_file_size(path: Path) -> str:
        size = path.stat().st_size
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024:
                return f"{size:.1f} {unit}"
            size /= 1024
        return f"{size:.1f} TB"
