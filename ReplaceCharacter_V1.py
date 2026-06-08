"""
╔══════════════════════════════════════════════════════════════════════════════╗
║  ReplaceCharacter v1.0.0  —  Advanced File Rename Suite                      ║
║  Single-file PyQt6 application                                               ║
║                                                                              ║
║  v1:                                                                         ║
║   • Light / Dark theme toggle in header                                      ║
║   • Regex support for character replacement patterns                         ║
║   • Case-insensitive matching option                                         ║
║   • Live preview before applying changes                                     ║
║   • Undo / Redo for all rename operations                                    ║
║   • Detailed in-app + optional file logging with timestamps                  ║
║   • JSON configuration file (saves user preferences)                         ║
║   • Batch processing with overall progress bar + per-file updates            ║
║   • Activity indicator ("Processing…", "Undoing…")                           ║
║   • Drag-and-drop file / folder support                                      ║
║   • QThread worker — UI never freezes on large directories                   ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

# ─────────────────────────────────────────────────────────────────────────────
#  STANDARD LIBRARY
# ─────────────────────────────────────────────────────────────────────────────
import os
import re
import sys
import json
import logging
import shutil
from copy import deepcopy
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Tuple, Dict

# ─────────────────────────────────────────────────────────────────────────────
#  PyQt6 IMPORTS
# ─────────────────────────────────────────────────────────────────────────────
from PyQt6.QtCore import (
    Qt,
    QThread,
    pyqtSignal,
    QTimer,
    QDateTime,
    QSize,
    QMimeData,
)
from PyQt6.QtGui import (
    QFont,
    QIcon,
    QColor,
    QPalette,
    QCursor,
    QAction,
    QDragEnterEvent,
    QDropEvent,
)
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QPushButton,
    QLineEdit,
    QLabel,
    QFileDialog,
    QProgressBar,
    QMessageBox,
    QFrame,
    QCheckBox,
    QTabWidget,
    QTextEdit,
    QComboBox,
    QGroupBox,
    QScrollArea,
    QSplitter,
    QSizePolicy,
    QSpacerItem,
    QListWidget,
    QListWidgetItem,
    QDialog,
    QDialogButtonBox,
    QMenuBar,
    QMenu,
    QStatusBar,
    QToolBar,
    QToolButton,
    QRadioButton,
    QButtonGroup,
    QTextBrowser,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QAbstractItemView,
)

# ══════════════════════════════════════════════════════════════════════════════
#  CONSTANTS / METADATA
# ══════════════════════════════════════════════════════════════════════════════

APP_NAME = "ReplaceCharacter"
APP_VERSION = "1.0.0"
APP_COMPANY = "SPARKS"
CONFIG_FILE = "replace_character_config.json"
LOG_FILE = "replace_character.log"


# ══════════════════════════════════════════════════════════════════════════════
#  THEME MANAGER
# ══════════════════════════════════════════════════════════════════════════════


class ThemeManager:
    """
    Manages light and dark themes.
    Call ThemeManager.apply(app, 'dark'|'light').
    """

    current: str = "light"  # default light

    DARK = """
QMainWindow, QWidget {
    background-color: #0D0F14; color: #E8EAFF;
    font-family: 'Segoe UI', 'SF Pro Display', sans-serif;
}
QScrollBar:vertical { background: #131720; width: 8px; border-radius: 4px; }
QScrollBar::handle:vertical { background: #2A3050; border-radius: 4px; min-height: 30px; }
QScrollBar::handle:vertical:hover { background: #00D4AA; }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
QScrollBar:horizontal { background: #131720; height: 8px; border-radius: 4px; }
QScrollBar::handle:horizontal { background: #2A3050; border-radius: 4px; min-width: 30px; }
QScrollBar::handle:horizontal:hover { background: #00D4AA; }
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal { width: 0; }

QPushButton {
    background-color: #1E2436; color: #E8EAFF;
    border: 1px solid #2A3050; padding: 7px 16px;
    border-radius: 6px; font-weight: 600; font-size: 12px;
}
QPushButton:hover { background-color: #2A3050; border-color: #00D4AA; color: #00D4AA; }
QPushButton:pressed { background-color: #00D4AA; color: #0D0F14; }
QPushButton:disabled { background-color: #131720; color: #2A3050; border-color: #1A1F2E; }
QPushButton#accent {
    background: qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 #00D4AA, stop:1 #4A9EFF);
    color: #0D0F14; border: none; font-size: 13px; font-weight: 700; padding: 10px 24px;
}
QPushButton#accent:hover {
    background: qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 #00EEBB, stop:1 #6AB4FF);
    color: #0D0F14;
}
QPushButton#accent:disabled { background: #1E2436; color: #3A4060; border: none; }
QPushButton#danger { background-color: transparent; color: #FF3860; border: 1px solid #FF3860; }
QPushButton#danger:hover { background-color: #FF3860; color: #fff; }
QPushButton#undo { background-color: #1A1F2E; color: #FFB300; border: 1px solid #3A3010; }
QPushButton#undo:hover { border-color: #FFB300; background-color: #2A2810; }
QPushButton#undo:disabled { color: #3A3020; border-color: #2A2010; }

QLineEdit, QTextEdit {
    background-color: #131720; color: #E8EAFF;
    border: 1px solid #2A3050; border-radius: 6px;
    padding: 6px 10px; font-size: 12px;
    selection-background-color: #00D4AA; selection-color: #0D0F14;
}
QLineEdit:focus, QTextEdit:focus { border-color: #00D4AA; background-color: #161B2A; }
QLineEdit:disabled { background-color: #0F1018; color: #3A4060; border-color: #1A1F2E; }

QComboBox {
    background-color: #131720; color: #E8EAFF;
    border: 1px solid #2A3050; border-radius: 6px; padding: 5px 10px; font-size: 12px;
}
QComboBox:hover { border-color: #00D4AA; }
QComboBox::drop-down { subcontrol-origin: padding; subcontrol-position: right center; width: 24px; border: none; }
QComboBox::down-arrow { border-left: 4px solid transparent; border-right: 4px solid transparent; border-top: 5px solid #00D4AA; margin-right: 6px; }
QComboBox QAbstractItemView {
    background-color: #1A1F2E; color: #E8EAFF;
    border: 1px solid #2A3050;
    selection-background-color: #2A3050; selection-color: #00D4AA; outline: none;
}

QProgressBar {
    background-color: #131720; border: 1px solid #2A3050; border-radius: 6px;
    text-align: center; color: #E8EAFF; font-size: 11px; height: 18px;
}
QProgressBar::chunk {
    background: qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 #00D4AA, stop:1 #4A9EFF);
    border-radius: 5px;
}

QGroupBox {
    border: 1px solid #2A3050; border-radius: 6px; margin-top: 10px; padding-top: 6px;
    font-size: 11px; font-weight: 700; color: #6B7299; letter-spacing: 1px;
}
QGroupBox::title { subcontrol-origin: margin; left: 10px; background-color: #0D0F14; padding: 0 4px; color: #00D4AA; }

QCheckBox, QRadioButton { color: #E8EAFF; spacing: 8px; font-size: 12px; }
QCheckBox::indicator, QRadioButton::indicator { width: 15px; height: 15px; border: 1px solid #2A3050; border-radius: 3px; background: #131720; }
QCheckBox::indicator:checked { background: #00D4AA; border-color: #00D4AA; }
QRadioButton::indicator { border-radius: 8px; }
QRadioButton::indicator:checked { background: #4A9EFF; border-color: #4A9EFF; }

QListWidget {
    background-color: #131720; color: #E8EAFF;
    border: 1px solid #2A3050; border-radius: 6px; outline: none; font-size: 12px;
}
QListWidget::item { padding: 5px 10px; }
QListWidget::item:selected { background-color: #1E2436; color: #00D4AA; }
QListWidget::item:hover { background-color: #1A1F2E; }

QTableWidget {
    background-color: #131720; color: #E8EAFF;
    border: 1px solid #2A3050; border-radius: 6px; gridline-color: #1A1F2E;
    font-size: 11px;
}
QHeaderView::section {
    background-color: #1E2436; color: #6B7299; padding: 5px 8px;
    border: none; border-right: 1px solid #2A3050; border-bottom: 1px solid #2A3050;
    font-weight: 700; font-size: 11px; letter-spacing: 1px;
}
QTableWidget::item:selected { background-color: #1E2436; color: #00D4AA; }

QTabWidget::pane { border: 1px solid #2A3050; border-radius: 6px; top: -1px; background-color: #131720; }
QTabBar::tab {
    background-color: #0D0F14; color: #6B7299; padding: 8px 18px;
    border: 1px solid #1A1F2E; border-bottom: none;
    border-top-left-radius: 6px; border-top-right-radius: 6px;
    font-size: 12px; font-weight: 600; margin-right: 2px;
}
QTabBar::tab:selected { background-color: #131720; color: #00D4AA; border-color: #2A3050; border-bottom: 2px solid #00D4AA; }
QTabBar::tab:hover:!selected { background-color: #1A1F2E; color: #E8EAFF; }

QMenuBar { background-color: #0D0F14; color: #E8EAFF; border-bottom: 1px solid #1A1F2E; }
QMenuBar::item:selected { background-color: #1E2436; color: #00D4AA; }
QMenu { background-color: #131720; color: #E8EAFF; border: 1px solid #2A3050; }
QMenu::item:selected { background-color: #1E2436; color: #00D4AA; }
QStatusBar { background-color: #0A0C10; color: #3D4466; font-size: 11px; border-top: 1px solid #1A1F2E; }
"""

    LIGHT = """
QMainWindow, QWidget {
    background-color: #F0F4F8; color: #1A2030;
    font-family: 'Segoe UI', 'SF Pro Display', sans-serif;
}
QScrollBar:vertical { background: #E0E6EE; width: 8px; border-radius: 4px; }
QScrollBar::handle:vertical { background: #B0BED8; border-radius: 4px; min-height: 30px; }
QScrollBar::handle:vertical:hover { background: #0088AA; }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
QScrollBar:horizontal { background: #E0E6EE; height: 8px; border-radius: 4px; }
QScrollBar::handle:horizontal { background: #B0BED8; border-radius: 4px; min-width: 30px; }
QScrollBar::handle:horizontal:hover { background: #0088AA; }
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal { width: 0; }

QPushButton {
    background-color: #FFFFFF; color: #1A2030;
    border: 1px solid #C8D5E0; padding: 7px 16px;
    border-radius: 6px; font-weight: 600; font-size: 12px;
}
QPushButton:hover { background-color: #E8F0F8; border-color: #0088AA; color: #0088AA; }
QPushButton:pressed { background-color: #0088AA; color: #FFFFFF; }
QPushButton:disabled { background-color: #EEF0F4; color: #A0AABB; border-color: #D0D8E0; }
QPushButton#accent {
    background: qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 #0099BB, stop:1 #3A7FDD);
    color: #FFFFFF; border: none; font-size: 13px; font-weight: 700; padding: 10px 24px;
}
QPushButton#accent:hover {
    background: qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 #00AACC, stop:1 #4A8FEE);
}
QPushButton#accent:disabled { background: #E0E8F0; color: #A0B0C0; border: none; }
QPushButton#danger { background-color: transparent; color: #CC2244; border: 1px solid #CC2244; }
QPushButton#danger:hover { background-color: #CC2244; color: #fff; }
QPushButton#undo { background-color: #FFF8E8; color: #AA7700; border: 1px solid #E8D090; }
QPushButton#undo:hover { border-color: #AA7700; background-color: #FFF0CC; }
QPushButton#undo:disabled { color: #C8B888; border-color: #E8E0C0; }

QLineEdit, QTextEdit {
    background-color: #FFFFFF; color: #1A2030;
    border: 1px solid #C8D5E0; border-radius: 6px;
    padding: 6px 10px; font-size: 12px;
    selection-background-color: #0099BB; selection-color: #FFFFFF;
}
QLineEdit:focus, QTextEdit:focus { border-color: #0099BB; background-color: #F8FBFF; }
QLineEdit:disabled { background-color: #F4F6F8; color: #A0AABB; border-color: #D8DEE8; }

QComboBox {
    background-color: #FFFFFF; color: #1A2030;
    border: 1px solid #C8D5E0; border-radius: 6px; padding: 5px 10px; font-size: 12px;
}
QComboBox:hover { border-color: #0099BB; }
QComboBox::drop-down { subcontrol-origin: padding; subcontrol-position: right center; width: 24px; border: none; }
QComboBox::down-arrow { border-left: 4px solid transparent; border-right: 4px solid transparent; border-top: 5px solid #0099BB; margin-right: 6px; }
QComboBox QAbstractItemView {
    background-color: #FFFFFF; color: #1A2030;
    border: 1px solid #C8D5E0;
    selection-background-color: #E0EEF8; selection-color: #0099BB; outline: none;
}

QProgressBar {
    background-color: #E0E6EE; border: 1px solid #C8D5E0; border-radius: 6px;
    text-align: center; color: #1A2030; font-size: 11px; height: 18px;
}
QProgressBar::chunk {
    background: qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 #0099BB, stop:1 #3A7FDD);
    border-radius: 5px;
}

QGroupBox {
    border: 1px solid #C8D5E0; border-radius: 6px; margin-top: 10px; padding-top: 6px;
    font-size: 11px; font-weight: 700; color: #6B7A99; letter-spacing: 1px;
}
QGroupBox::title { subcontrol-origin: margin; left: 10px; background-color: #F0F4F8; padding: 0 4px; color: #0099BB; }

QCheckBox, QRadioButton { color: #1A2030; spacing: 8px; font-size: 12px; }
QCheckBox::indicator, QRadioButton::indicator { width: 15px; height: 15px; border: 1px solid #C8D5E0; border-radius: 3px; background: #FFFFFF; }
QCheckBox::indicator:checked { background: #0099BB; border-color: #0099BB; }
QRadioButton::indicator { border-radius: 8px; }
QRadioButton::indicator:checked { background: #3A7FDD; border-color: #3A7FDD; }

QListWidget {
    background-color: #FFFFFF; color: #1A2030;
    border: 1px solid #C8D5E0; border-radius: 6px; outline: none; font-size: 12px;
}
QListWidget::item { padding: 5px 10px; }
QListWidget::item:selected { background-color: #E0EEF8; color: #0099BB; }
QListWidget::item:hover { background-color: #F0F6FA; }

QTableWidget {
    background-color: #FFFFFF; color: #1A2030;
    border: 1px solid #C8D5E0; border-radius: 6px; gridline-color: #E8EEF4;
    font-size: 11px;
}
QHeaderView::section {
    background-color: #F0F4F8; color: #6B7A99; padding: 5px 8px;
    border: none; border-right: 1px solid #C8D5E0; border-bottom: 1px solid #C8D5E0;
    font-weight: 700; font-size: 11px; letter-spacing: 1px;
}
QTableWidget::item:selected { background-color: #E0EEF8; color: #0099BB; }

QTabWidget::pane { border: 1px solid #C8D5E0; border-radius: 6px; top: -1px; background-color: #FFFFFF; }
QTabBar::tab {
    background-color: #E8EDF4; color: #6B7A99; padding: 8px 18px;
    border: 1px solid #C8D5E0; border-bottom: none;
    border-top-left-radius: 6px; border-top-right-radius: 6px;
    font-size: 12px; font-weight: 600; margin-right: 2px;
}
QTabBar::tab:selected { background-color: #FFFFFF; color: #0099BB; border-color: #C8D5E0; border-bottom: 2px solid #0099BB; }
QTabBar::tab:hover:!selected { background-color: #F0F4F8; color: #1A2030; }

QMenuBar { background-color: #F0F4F8; color: #1A2030; border-bottom: 1px solid #D0D8E4; }
QMenuBar::item:selected { background-color: #E0EEF8; color: #0099BB; }
QMenu { background-color: #FFFFFF; color: #1A2030; border: 1px solid #C8D5E0; }
QMenu::item:selected { background-color: #E0EEF8; color: #0099BB; }
QStatusBar { background-color: #E8EDF4; color: #6B7A99; font-size: 11px; border-top: 1px solid #C8D5E0; }
"""

    @classmethod
    def apply(cls, app: QApplication, theme: str):
        cls.current = theme
        app.setStyleSheet(cls.DARK if theme == "dark" else cls.LIGHT)

    @classmethod
    def is_dark(cls) -> bool:
        return cls.current == "dark"

    @classmethod
    def accent_color(cls) -> str:
        return "#00D4AA" if cls.is_dark() else "#0099BB"

    @classmethod
    def success_color(cls) -> str:
        return "#00EE99" if cls.is_dark() else "#007755"

    @classmethod
    def danger_color(cls) -> str:
        return "#FF3860" if cls.is_dark() else "#CC2244"

    @classmethod
    def warning_color(cls) -> str:
        return "#FFB300" if cls.is_dark() else "#AA7700"

    @classmethod
    def dim_color(cls) -> str:
        return "#6B7299" if cls.is_dark() else "#6B7A99"


# ══════════════════════════════════════════════════════════════════════════════
#  CONFIG MANAGER  — Saves/loads user preferences to JSON
# ══════════════════════════════════════════════════════════════════════════════


class ConfigManager:
    """
    Persists user settings between sessions.
    Stored next to the script as `replace_character_config.json`.
    """

    DEFAULTS: Dict = {
        "theme": "light",
        "use_regex": False,
        "case_sensitive": True,
        "enable_logging": False,
        "last_directory": "",
        "old_char": "",
        "new_char": "",
        "remove_word": "",
    }

    def __init__(self):
        script_dir = Path(sys.argv[0]).parent
        self._path = script_dir / CONFIG_FILE
        self._data: Dict = deepcopy(self.DEFAULTS)
        self._load()

    def _load(self):
        if self._path.exists():
            try:
                with open(self._path, "r", encoding="utf-8") as f:
                    saved = json.load(f)
                # Merge saved over defaults so new keys still have values
                self._data.update(
                    {k: v for k, v in saved.items() if k in self.DEFAULTS}
                )
            except Exception:
                pass

    def save(self):
        try:
            with open(self._path, "w", encoding="utf-8") as f:
                json.dump(self._data, f, indent=2)
        except Exception:
            pass

    def get(self, key: str):
        return self._data.get(key, self.DEFAULTS.get(key))

    def set(self, key: str, value):
        self._data[key] = value


# ══════════════════════════════════════════════════════════════════════════════
#  UNDO / REDO STACK
# ══════════════════════════════════════════════════════════════════════════════


class RenameOperation:
    """Records a single batch of file renames so they can be reversed."""

    def __init__(self, renames: List[Tuple[Path, Path]]):
        """
        renames: list of (old_path, new_path) tuples that were performed.
        """
        self.renames = renames
        self.timestamp = datetime.now().strftime("%H:%M:%S")
        self.count = len(renames)

    def undo(self) -> List[Tuple[Path, Path, bool, str]]:
        """
        Reverse every rename. Returns list of (old, new, success, error_msg).
        """
        results = []
        for old_path, new_path in self.renames:
            try:
                if new_path.exists():
                    new_path.rename(old_path)
                    results.append((old_path, new_path, True, ""))
                else:
                    results.append(
                        (old_path, new_path, False, "File not found at new location")
                    )
            except Exception as e:
                results.append((old_path, new_path, False, str(e)))
        return results


class UndoStack:
    MAX = 20  # keep at most 20 undo levels

    def __init__(self):
        self._undo: List[RenameOperation] = []
        self._redo: List[RenameOperation] = []

    def push(self, op: RenameOperation):
        self._undo.append(op)
        self._redo.clear()
        if len(self._undo) > self.MAX:
            self._undo.pop(0)

    def undo(self) -> Optional[RenameOperation]:
        if not self._undo:
            return None
        op = self._undo.pop()
        self._redo.append(op)
        return op

    def redo(self) -> Optional[RenameOperation]:
        if not self._redo:
            return None
        op = self._redo.pop()
        self._undo.append(op)
        return op

    def can_undo(self) -> bool:
        return bool(self._undo)

    def can_redo(self) -> bool:
        return bool(self._redo)

    def undo_label(self) -> str:
        return (
            f"Undo ({self._undo[-1].count} rename(s) @ {self._undo[-1].timestamp})"
            if self._undo
            else "Undo"
        )

    def redo_label(self) -> str:
        return (
            f"Redo ({self._redo[-1].count} rename(s) @ {self._redo[-1].timestamp})"
            if self._redo
            else "Redo"
        )


# ══════════════════════════════════════════════════════════════════════════════
#  RENAME ENGINE  — Pure logic, no Qt widgets
# ══════════════════════════════════════════════════════════════════════════════


class RenameEngine:
    """
    Applies replace / remove rules to a filename stem.

    Args
    ----
    old_char:       pattern to replace (literal char or regex)
    new_char:       replacement string
    remove_word:    literal substring to remove
    use_regex:      if True, old_char is treated as a regex
    case_sensitive: if False, matching is case-insensitive
    do_replace:     whether the replace-char step is active
    do_remove:      whether the remove-word step is active
    """

    def __init__(
        self,
        old_char: str = "",
        new_char: str = "",
        remove_word: str = "",
        use_regex: bool = False,
        case_sensitive: bool = True,
        do_replace: bool = False,
        do_remove: bool = False,
    ):
        self.old_char = old_char
        self.new_char = new_char
        self.remove_word = remove_word
        self.use_regex = use_regex
        self.case_sensitive = case_sensitive
        self.do_replace = do_replace
        self.do_remove = do_remove

        # Pre-compile regex if needed (raises re.error on bad pattern)
        flags = 0 if case_sensitive else re.IGNORECASE
        if use_regex and old_char:
            self._pattern = re.compile(old_char, flags)
        else:
            self._pattern = None
        self._flags = flags

    def transform(self, stem: str) -> str:
        """Return the new filename stem (without extension) after applying rules."""
        result = stem

        if self.do_replace and self.old_char:
            if self.use_regex and self._pattern:
                result = self._pattern.sub(self.new_char, result)
            else:
                if self.case_sensitive:
                    result = result.replace(self.old_char, self.new_char)
                else:
                    # Case-insensitive literal replace
                    result = re.sub(
                        re.escape(self.old_char),
                        self.new_char,
                        result,
                        flags=re.IGNORECASE,
                    )

        if self.do_remove and self.remove_word:
            if self.case_sensitive:
                result = result.replace(self.remove_word, "")
            else:
                result = re.sub(
                    re.escape(self.remove_word),
                    "",
                    result,
                    flags=re.IGNORECASE,
                )

        # Strip trailing spaces
        result = result.rstrip()
        return result

    def preview_batch(self, paths: List[Path]) -> List[Tuple[str, str, bool]]:
        """
        Return list of (original_name, new_name, will_change) for a list of Paths.
        Used by the Preview tab.
        """
        results = []
        for p in paths:
            stem = p.stem if p.is_file() else p.name
            ext = p.suffix if p.is_file() else ""
            new_stem = self.transform(stem)
            new_name = new_stem + ext
            orig_name = p.name
            results.append((orig_name, new_name, orig_name != new_name))
        return results


# ══════════════════════════════════════════════════════════════════════════════
#  WORKER THREAD  — runs batch processing off the main thread
# ══════════════════════════════════════════════════════════════════════════════


class RenameWorker(QThread):
    """
    Processes files in a background thread so the UI stays responsive.

    Signals
    -------
    progress(current, total, filename)
    log_msg(message, level)
    finished(success, renames_performed)
    """

    progress = pyqtSignal(int, int, str)  # current, total, name
    log_msg = pyqtSignal(str, str)  # message, level
    finished = pyqtSignal(bool, list)  # success, list[tuple]

    def __init__(
        self,
        paths: List[Path],
        engine: RenameEngine,
        parent=None,
    ):
        super().__init__(parent)
        self.paths = paths
        self.engine = engine

    def run(self):
        renames: List[Tuple[Path, Path]] = []  # (old_path, new_path)
        total = len(self.paths)

        try:
            for idx, path in enumerate(self.paths, 1):
                self.progress.emit(idx, total, path.name)

                if path.is_file():
                    stem = path.stem
                    ext = path.suffix
                    new_stem = self.engine.transform(stem)
                    new_name = new_stem + ext
                    if new_name != path.name:
                        new_path = path.parent / new_name
                        try:
                            path.rename(new_path)
                            renames.append((path, new_path))
                            self.log_msg.emit(
                                f"✔  {path.name}  →  {new_name}", "SUCCESS"
                            )
                        except Exception as e:
                            self.log_msg.emit(f"✘  {path.name}:  {e}", "ERROR")
                    else:
                        self.log_msg.emit(f"—  {path.name}  (no change)", "INFO")

                elif path.is_dir():
                    # Process every file inside the directory (non-recursive)
                    try:
                        file_list = [f for f in path.iterdir() if f.is_file()]
                        sub_total = len(file_list)
                        for sub_idx, fp in enumerate(file_list, 1):
                            self.progress.emit(sub_idx, sub_total, fp.name)
                            stem = fp.stem
                            ext = fp.suffix
                            new_stem = self.engine.transform(stem)
                            new_name = new_stem + ext
                            if new_name != fp.name:
                                new_path = fp.parent / new_name
                                try:
                                    fp.rename(new_path)
                                    renames.append((fp, new_path))
                                    self.log_msg.emit(
                                        f"✔  {fp.name}  →  {new_name}", "SUCCESS"
                                    )
                                except Exception as e:
                                    self.log_msg.emit(f"✘  {fp.name}:  {e}", "ERROR")
                            else:
                                self.log_msg.emit(f"—  {fp.name}  (no change)", "INFO")
                    except Exception as e:
                        self.log_msg.emit(f"✘  Directory error: {e}", "ERROR")

            self.finished.emit(True, renames)

        except Exception as fatal:
            self.log_msg.emit(f"Fatal error: {fatal}", "ERROR")
            self.finished.emit(False, renames)


# ══════════════════════════════════════════════════════════════════════════════
#  ACTIVITY INDICATOR
# ══════════════════════════════════════════════════════════════════════════════


class ActivityIndicator(QLabel):
    """Animated status label: shows 'Processing…' / 'Undoing…' with dot cycles."""

    _DOTS = ["", ".", "..", "..."]

    def __init__(self, parent=None):
        super().__init__(parent)
        self._base = "Ready"
        self._dot_i = 0
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._tick)
        self.setText("Ready")
        self._set_style("dim")

    def start(self, operation: str):
        self._base = operation
        self._dot_i = 0
        self._timer.start(350)
        self._tick()

    def stop(self):
        self._timer.stop()
        self.setText("✔  Ready")
        self._set_style("ok")

    def _tick(self):
        dots = self._DOTS[self._dot_i % len(self._DOTS)]
        self.setText(f"⚙  {self._base}{dots}")
        self._set_style("active")
        self._dot_i += 1

    def _set_style(self, mode: str):
        colors = {
            "dim": ThemeManager.dim_color(),
            "ok": ThemeManager.success_color(),
            "active": ThemeManager.accent_color(),
        }
        self.setStyleSheet(
            f"color: {colors.get(mode, '#6B7299')}; font-size: 12px; font-weight: 600;"
        )


# ══════════════════════════════════════════════════════════════════════════════
#  LOG PANEL
# ══════════════════════════════════════════════════════════════════════════════


class LogPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)

        hdr = QHBoxLayout()
        lbl = QLabel("  OPERATION LOG")
        lbl.setStyleSheet(
            "color: #6B7299; font-size: 11px; font-weight: 700; letter-spacing: 1px;"
        )
        save_btn = QPushButton("💾 Save Log")
        save_btn.setFixedHeight(28)
        save_btn.clicked.connect(self._save_log)
        clr = QPushButton("Clear")
        clr.setFixedHeight(28)
        clr.clicked.connect(self.clear)
        hdr.addWidget(lbl)
        hdr.addStretch()
        hdr.addWidget(save_btn)
        hdr.addWidget(clr)
        layout.addLayout(hdr)

        self.log = QTextEdit()
        self.log.setReadOnly(True)
        self.log.setStyleSheet(
            "QTextEdit { border: 1px solid #2A3050; "
            "border-radius: 6px; font-family: Consolas, 'Courier New', monospace; "
            "font-size: 11px; padding: 8px; }"
        )
        layout.addWidget(self.log)

    def add(self, message: str, level: str = "INFO"):
        ts = QDateTime.currentDateTime().toString("HH:mm:ss")
        dark = ThemeManager.is_dark()
        colors = {
            "INFO": "#6B7299" if dark else "#6B7A99",
            "SUCCESS": "#00EE99" if dark else "#007755",
            "ERROR": "#FF3860" if dark else "#CC2244",
            "WARNING": "#FFB300" if dark else "#AA7700",
        }
        ts_color = "#2A3050" if dark else "#A0AACC"
        color = colors.get(level, colors["INFO"])
        self.log.append(
            f'<span style="color:{ts_color}">[{ts}]</span> '
            f'<span style="color:{color}">{message}</span>'
        )
        self.log.verticalScrollBar().setValue(self.log.verticalScrollBar().maximum())

    def clear(self):
        self.log.clear()

    def _save_log(self):
        path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Log File",
            str(Path.home() / "replace_character.log"),
            "Log Files (*.log);;Text Files (*.txt);;All Files (*)",
        )
        if path:
            try:
                # Strip HTML tags for plain text export
                plain = re.sub(r"<[^>]+>", "", self.log.toHtml())
                plain = re.sub(r"&amp;", "&", plain)
                plain = re.sub(r"&lt;", "<", plain)
                plain = re.sub(r"&gt;", ">", plain)
                with open(path, "w", encoding="utf-8") as f:
                    f.write(plain)
                QMessageBox.information(self, "Saved", f"Log saved to:\n{path}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Could not save log:\n{e}")

    def plain_text(self) -> str:
        return re.sub(r"<[^>]+>", "", self.log.toHtml())


# ══════════════════════════════════════════════════════════════════════════════
#  PREVIEW TABLE WIDGET
# ══════════════════════════════════════════════════════════════════════════════


class PreviewTable(QWidget):
    """
    Shows a two-column table: Original Name | New Name.
    Rows with changes are highlighted.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)

        hdr = QHBoxLayout()
        self._info_lbl = QLabel("No preview generated yet. Click  Refresh Preview.")
        self._info_lbl.setStyleSheet(
            f"color: {ThemeManager.dim_color()}; font-size: 11px;"
        )
        hdr.addWidget(self._info_lbl)
        hdr.addStretch()
        layout.addLayout(hdr)

        self._table = QTableWidget(0, 2)
        self._table.setHorizontalHeaderLabels(["ORIGINAL NAME", "NEW NAME"])
        self._table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )
        self._table.verticalHeader().setVisible(False)
        self._table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self._table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        layout.addWidget(self._table)

    def populate(self, previews: List[Tuple[str, str, bool]]):
        """previews: list of (orig, new, changed)"""
        self._table.setRowCount(0)
        changed_count = sum(1 for _, _, c in previews if c)

        for orig, new, changed in previews:
            row = self._table.rowCount()
            self._table.insertRow(row)
            orig_item = QTableWidgetItem(orig)
            new_item = QTableWidgetItem(new)

            if changed:
                accent = ThemeManager.accent_color()
                new_item.setForeground(QColor(accent))
                new_item.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
            else:
                dim = ThemeManager.dim_color()
                orig_item.setForeground(QColor(dim))
                new_item.setForeground(QColor(dim))

            self._table.setItem(row, 0, orig_item)
            self._table.setItem(row, 1, new_item)

        total = len(previews)
        self._info_lbl.setText(
            f"{total} file(s)  —  "
            f"{changed_count} will be renamed  |  "
            f"{total - changed_count} unchanged"
        )
        self._info_lbl.setStyleSheet(
            f"color: {ThemeManager.accent_color() if changed_count else ThemeManager.dim_color()}; font-size: 11px;"
        )

    def clear(self):
        self._table.setRowCount(0)
        self._info_lbl.setText("No preview generated yet. Click  Refresh Preview.")
        self._info_lbl.setStyleSheet(
            f"color: {ThemeManager.dim_color()}; font-size: 11px;"
        )


# ══════════════════════════════════════════════════════════════════════════════
#  ABOUT DIALOG
# ══════════════════════════════════════════════════════════════════════════════


class AboutDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"About {APP_NAME} v{APP_VERSION}")
        self.setMinimumSize(520, 480)

        root = QVBoxLayout(self)
        root.setSpacing(0)
        root.setContentsMargins(0, 0, 0, 0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(14)
        scroll.setWidget(content)
        root.addWidget(scroll, 1)

        hero = QLabel("REPLACE CHARACTER")
        hero.setAlignment(Qt.AlignmentFlag.AlignCenter)
        hero.setStyleSheet(
            f"color: {ThemeManager.accent_color()}; font-size: 22px; font-weight: 900; "
            "letter-spacing: 8px; font-family: 'Consolas', monospace; padding: 12px 0 4px 0;"
        )
        layout.addWidget(hero)

        ver_lbl = QLabel(f"v{APP_VERSION}  ·  Advanced File Rename Suite")
        ver_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        ver_lbl.setStyleSheet("color: #6B7299; font-size: 12px; letter-spacing: 2px;")
        layout.addWidget(ver_lbl)

        sep = QFrame()
        sep.setFixedHeight(2)
        sep.setStyleSheet(
            f"background: qlineargradient(x1:0,y1:0,x2:1,y2:0,"
            f"stop:0 transparent, stop:0.3 {ThemeManager.accent_color()}, "
            f"stop:0.7 #4A9EFF, stop:1 transparent);"
        )
        layout.addWidget(sep)

        sections = [
            (
                "⚡  V1",
                "Light/Dark theme toggle • Regex pattern support • "
                "Case-insensitive matching • Live preview before renaming • "
                "Undo/Redo (up to 20 levels) • Background thread processing • "
                "File logging with timestamps • JSON config file • "
                "Drag-and-drop file/folder support.",
            ),
            (
                "🔤  REPLACE ENGINE",
                "<b>Literal mode</b>: Replace an exact character or substring. "
                "<b>Regex mode</b>: Use regular expressions for advanced patterns (e.g. <code>\\d+</code> to match all digits). "
                "<b>Case-insensitive</b>: Matching ignores letter case.",
            ),
            (
                "↩  UNDO / REDO",
                "Every rename batch is recorded. Press Undo to reverse the last operation "
                "or Redo to reapply it. Up to 20 levels are stored per session.",
            ),
            (
                "👁  PREVIEW",
                "Switch to the Preview tab and click Refresh Preview to see exactly "
                "which filenames will change — before applying any renames.",
            ),
            (
                "👤  CREATOR",
                "Built with <b>Python</b> and <b>PyQt6</b>.  "
                "Created by @Sparky2273 — DM on Telegram for support.",
            ),
        ]

        for title, body in sections:
            lbl = QLabel(title)
            lbl.setStyleSheet(
                f"color: {ThemeManager.accent_color()}; font-size: 13px; "
                "font-weight: 800; letter-spacing: 1px; padding-top: 4px;"
            )
            layout.addWidget(lbl)
            txt = QLabel(body)
            txt.setWordWrap(True)
            txt.setTextFormat(Qt.TextFormat.RichText)
            txt.setStyleSheet(
                "color: #A0A8CC; font-size: 12px; line-height: 160%; padding-left: 4px;"
            )
            layout.addWidget(txt)

        layout.addStretch()

        close_btn = QPushButton("Close")
        close_btn.setObjectName("accent")
        close_btn.setFixedHeight(36)
        close_btn.clicked.connect(self.accept)
        root.addWidget(close_btn)
        root.setContentsMargins(12, 0, 12, 12)


# ══════════════════════════════════════════════════════════════════════════════
#  MANUAL DIALOG
# ══════════════════════════════════════════════════════════════════════════════

MANUAL_TEXT = f"""
# {APP_NAME} v{APP_VERSION} — User Manual

## Overview
ReplaceCharacter v1 renames files by replacing characters or removing words
from their names. It supports literal text, regular expressions, and
case-insensitive matching — with a live preview before any changes are made.

---

## File / Directory Selection

- **Select File**: Opens a file picker. The selected file path appears below.
- **Select Directory**: Opens a folder picker. All files in that folder will
  be processed.
- **Drag & Drop**: Drag a file or folder from Explorer/Finder directly onto
  the application window.

---

## Replace Character Section

| Control | Purpose |
|---|---|
| Enable checkbox | Activates the replace step |
| Pattern to replace | The character, word, or regex to find |
| Replace with | What to substitute in its place (blank = delete) |
| Use Regex | Treat the Pattern as a regular expression |
| Case-insensitive | Match regardless of upper/lower case |

**Regex examples:**
- `\\d+` — remove all digit sequences
- `[aeiou]` — replace all vowels
- `_+` — collapse multiple underscores into one (replace with `_`)
- `\\s+` — replace whitespace runs

---

## Remove Word Section

Enter a word or substring to delete entirely from every filename.
Case-insensitive option applies here too.

---

## Preview Tab

Before applying changes, switch to the **Preview** tab and click
**Refresh Preview**. A table shows the Original Name alongside the New Name.
Rows that will change are highlighted. No files are modified at this step.

---

## Apply Changes

Click **Apply Changes** to run the rename operation. A progress bar tracks
each file. The Log panel on the right records every rename with a timestamp.

---

## Undo / Redo

- **Undo**: Reverses the last batch of renames (restores original names).
- **Redo**: Reapplies a previously undone batch.
- Up to 20 levels of history are kept per session.

---

## Logging

Enable **Save log to file** to write every operation (with timestamps) to
`replace_character.log` in the same directory as the application. You can
also click **Save Log** in the Log panel to export any time.

---

## Configuration

Settings (theme, regex flag, case sensitivity, last directory) are saved
automatically to `replace_character_config.json` so they persist across
sessions.

---

## Contact
Developer: Sparky
Telegram: @Sparky2273
"""


class ManualDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"{APP_NAME} — Manual")
        self.resize(780, 600)

        layout = QVBoxLayout(self)
        browser = QTextBrowser()
        # Use markdown if available; fall back to plain text
        try:
            browser.setMarkdown(MANUAL_TEXT)
        except AttributeError:
            browser.setPlainText(MANUAL_TEXT)
        layout.addWidget(browser)

        btn = QPushButton("Close")
        btn.setObjectName("accent")
        btn.setFixedHeight(34)
        btn.clicked.connect(self.accept)
        layout.addWidget(btn)


# ══════════════════════════════════════════════════════════════════════════════
#  MAIN WINDOW
# ══════════════════════════════════════════════════════════════════════════════


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self._path: Optional[Path] = None  # currently selected file or dir
        self._worker: Optional[RenameWorker] = None
        self._undo_stack = UndoStack()
        self._config = ConfigManager()
        self._file_log_handler: Optional[logging.FileHandler] = None

        self._build_ui()
        self._build_menu()
        self._setup_logging()
        self._load_config()

        self.setAcceptDrops(True)

    # ──────────────────────────────────────────────────────────────────────────
    #  UI BUILD
    # ──────────────────────────────────────────────────────────────────────────

    def _build_ui(self):
        self.setWindowTitle(f"{APP_NAME}  v{APP_VERSION}")
        self.setMinimumSize(900, 600)
        self.resize(1100, 720)

        # Status bar
        self._status_bar = QStatusBar()
        self.setStatusBar(self._status_bar)
        self._status_bar.showMessage("Ready")

        # Central widget
        root = QWidget()
        root_layout = QVBoxLayout(root)
        root_layout.setContentsMargins(16, 12, 16, 12)
        root_layout.setSpacing(10)
        self.setCentralWidget(root)

        # ── Header ────────────────────────────────────────────────────────────
        hdr = QHBoxLayout()

        self._title_lbl = QLabel("REPLACE CHARACTER")
        self._title_lbl.setStyleSheet(
            f"color: {ThemeManager.accent_color()}; font-size: 20px; font-weight: 900; "
            "letter-spacing: 6px; font-family: 'Consolas', monospace;"
        )

        sub_lbl = QLabel(f"Advanced File Rename Suite  v{APP_VERSION}")
        sub_lbl.setStyleSheet(
            f"color: {ThemeManager.dim_color()}; font-size: 11px; letter-spacing: 2px;"
        )
        sub_lbl.setAlignment(Qt.AlignmentFlag.AlignVCenter)

        self._theme_btn = QPushButton("🌙  Dark Mode")
        self._theme_btn.setFixedHeight(30)
        self._theme_btn.setToolTip("Toggle between Light and Dark themes")
        self._theme_btn.clicked.connect(self._toggle_theme)

        about_btn = QPushButton("ℹ  About")
        about_btn.setFixedHeight(30)
        about_btn.clicked.connect(self._open_about)

        manual_btn = QPushButton("📖  Manual")
        manual_btn.setFixedHeight(30)
        manual_btn.clicked.connect(self._open_manual)

        hdr.addWidget(self._title_lbl)
        hdr.addWidget(sub_lbl)
        hdr.addStretch()
        hdr.addWidget(self._theme_btn)
        hdr.addWidget(about_btn)
        hdr.addWidget(manual_btn)
        root_layout.addLayout(hdr)

        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet("background: #1A1F2E; max-height: 1px;")
        root_layout.addWidget(sep)

        # ── Main splitter: left controls | right log ───────────────────────────
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setStyleSheet("QSplitter::handle { background: #1A1F2E; width: 2px; }")
        root_layout.addWidget(splitter, 1)

        # ── Left panel (scrollable) ────────────────────────────────────────────
        left_scroll = QScrollArea()
        left_scroll.setWidgetResizable(True)
        left_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        left_scroll.setStyleSheet(
            "QScrollArea { border: none; background: transparent; }"
        )
        left = QWidget()
        left_layout = QVBoxLayout(left)
        left_layout.setContentsMargins(0, 0, 8, 0)
        left_layout.setSpacing(10)
        left_scroll.setWidget(left)

        # ── File Selection ─────────────────────────────────────────────────────
        file_grp = QGroupBox("FILE SELECTION")
        file_layout = QVBoxLayout(file_grp)
        file_layout.setSpacing(6)

        btn_row = QHBoxLayout()
        self._sel_file_btn = QPushButton("📄  Select File")
        self._sel_dir_btn = QPushButton("📁  Select Directory")
        self._sel_file_btn.clicked.connect(self._select_file)
        self._sel_dir_btn.clicked.connect(self._select_directory)
        btn_row.addWidget(self._sel_file_btn)
        btn_row.addWidget(self._sel_dir_btn)
        file_layout.addLayout(btn_row)

        path_lbl = QLabel("Selected path:")
        path_lbl.setStyleSheet(f"color: {ThemeManager.dim_color()}; font-size: 11px;")
        self._path_display = QLabel(
            "Nothing selected — drag & drop or use buttons above"
        )
        self._path_display.setWordWrap(True)
        self._path_display.setStyleSheet(
            f"color: {ThemeManager.dim_color()}; font-size: 11px; "
            "border: 1px dashed #2A3050; border-radius: 4px; padding: 6px;"
        )
        file_layout.addWidget(path_lbl)
        file_layout.addWidget(self._path_display)
        left_layout.addWidget(file_grp)

        # ── Options ────────────────────────────────────────────────────────────
        opts_grp = QGroupBox("OPTIONS")
        opts_layout = QHBoxLayout(opts_grp)
        self._regex_check = QCheckBox("Use Regex")
        self._regex_check.setToolTip(
            "Treat the 'Pattern to replace' field as a regular expression"
        )
        self._case_check = QCheckBox("Case-sensitive")
        self._case_check.setChecked(True)
        self._case_check.setToolTip("When unchecked, matching ignores letter case")
        opts_layout.addWidget(self._regex_check)
        opts_layout.addSpacing(20)
        opts_layout.addWidget(self._case_check)
        opts_layout.addStretch()
        left_layout.addWidget(opts_grp)

        # ── Tabs: Replace | Remove | Preview ──────────────────────────────────
        self._tabs = QTabWidget()
        left_layout.addWidget(self._tabs)

        # — Tab 1: Replace Character —
        replace_tab = QWidget()
        rt_layout = QVBoxLayout(replace_tab)
        rt_layout.setContentsMargins(10, 10, 10, 10)
        rt_layout.setSpacing(8)

        self._replace_enable = QCheckBox("Enable replace step")
        self._replace_enable.setChecked(False)
        self._replace_enable.stateChanged.connect(self._toggle_replace)
        rt_layout.addWidget(self._replace_enable)

        old_lbl = QLabel("Pattern to replace:")
        old_lbl.setStyleSheet(
            f"color: {ThemeManager.dim_color()}; font-size: 11px; font-weight: 700;"
        )
        self._old_char = QLineEdit()
        self._old_char.setPlaceholderText("e.g.  _   or regex: \\d+")
        self._old_char.setDisabled(True)

        new_lbl = QLabel("Replace with:")
        new_lbl.setStyleSheet(
            f"color: {ThemeManager.dim_color()}; font-size: 11px; font-weight: 700;"
        )
        self._new_char = QLineEdit()
        self._new_char.setPlaceholderText("Replacement text (blank = delete)")
        self._new_char.setDisabled(True)

        rt_layout.addWidget(old_lbl)
        rt_layout.addWidget(self._old_char)
        rt_layout.addWidget(new_lbl)
        rt_layout.addWidget(self._new_char)
        rt_layout.addStretch()
        self._tabs.addTab(replace_tab, "🔡  Replace")

        # — Tab 2: Remove Word —
        remove_tab = QWidget()
        rm_layout = QVBoxLayout(remove_tab)
        rm_layout.setContentsMargins(10, 10, 10, 10)
        rm_layout.setSpacing(8)

        self._remove_enable = QCheckBox("Enable remove step")
        self._remove_enable.setChecked(False)
        self._remove_enable.stateChanged.connect(self._toggle_remove)
        rm_layout.addWidget(self._remove_enable)

        word_lbl = QLabel("Word / substring to remove:")
        word_lbl.setStyleSheet(
            f"color: {ThemeManager.dim_color()}; font-size: 11px; font-weight: 700;"
        )
        self._remove_word = QLineEdit()
        self._remove_word.setPlaceholderText("e.g.  Copy of")
        self._remove_word.setDisabled(True)

        rm_layout.addWidget(word_lbl)
        rm_layout.addWidget(self._remove_word)
        rm_layout.addStretch()
        self._tabs.addTab(remove_tab, "✂  Remove")

        # — Tab 3: Preview —
        preview_tab = QWidget()
        pv_layout = QVBoxLayout(preview_tab)
        pv_layout.setContentsMargins(10, 10, 10, 10)
        pv_layout.setSpacing(6)

        refresh_btn = QPushButton("🔄  Refresh Preview")
        refresh_btn.setObjectName("accent")
        refresh_btn.setFixedHeight(34)
        refresh_btn.clicked.connect(self._refresh_preview)
        pv_layout.addWidget(refresh_btn)

        self._preview_table = PreviewTable()
        pv_layout.addWidget(self._preview_table)
        self._tabs.addTab(preview_tab, "👁  Preview")

        # ── Control Row ────────────────────────────────────────────────────────
        ctrl_grp = QGroupBox("CONTROL")
        ctrl_layout = QVBoxLayout(ctrl_grp)
        ctrl_layout.setSpacing(6)

        action_row = QHBoxLayout()
        self._apply_btn = QPushButton("⚡  Apply Changes")
        self._apply_btn.setObjectName("accent")
        self._apply_btn.setFixedHeight(40)
        self._apply_btn.clicked.connect(self._apply_changes)

        self._undo_btn = QPushButton("↩  Undo")
        self._undo_btn.setObjectName("undo")
        self._undo_btn.setFixedHeight(40)
        self._undo_btn.setEnabled(False)
        self._undo_btn.clicked.connect(self._do_undo)

        self._redo_btn = QPushButton("↪  Redo")
        self._redo_btn.setObjectName("undo")
        self._redo_btn.setFixedHeight(40)
        self._redo_btn.setEnabled(False)
        self._redo_btn.clicked.connect(self._do_redo)

        self._clear_btn = QPushButton("🗑  Clear Fields")
        self._clear_btn.setObjectName("danger")
        self._clear_btn.setFixedHeight(40)
        self._clear_btn.clicked.connect(self._clear_fields)

        action_row.addWidget(self._apply_btn, 3)
        action_row.addWidget(self._undo_btn, 1)
        action_row.addWidget(self._redo_btn, 1)
        action_row.addWidget(self._clear_btn, 1)
        ctrl_layout.addLayout(action_row)

        # Activity indicator + progress bar
        self._activity = ActivityIndicator()
        ctrl_layout.addWidget(self._activity)

        self._progress = QProgressBar()
        self._progress.setValue(0)
        self._progress.setFixedHeight(16)
        ctrl_layout.addWidget(self._progress)

        self._progress_lbl = QLabel("")
        self._progress_lbl.setStyleSheet(
            f"color: {ThemeManager.dim_color()}; font-size: 11px;"
        )
        ctrl_layout.addWidget(self._progress_lbl)
        left_layout.addWidget(ctrl_grp)

        # ── Logging checkbox ───────────────────────────────────────────────────
        log_grp = QGroupBox("LOGGING")
        log_layout = QVBoxLayout(log_grp)
        self._log_file_check = QCheckBox("Save log to file  (replace_character.log)")
        self._log_file_check.toggled.connect(self._toggle_file_logging)
        log_layout.addWidget(self._log_file_check)
        left_layout.addWidget(log_grp)

        left_layout.addStretch()
        splitter.addWidget(left_scroll)

        # ── Right panel: Log ───────────────────────────────────────────────────
        self._log_panel = LogPanel()
        splitter.addWidget(self._log_panel)
        splitter.setSizes([600, 360])

    # ──────────────────────────────────────────────────────────────────────────
    #  MENU BAR
    # ──────────────────────────────────────────────────────────────────────────

    def _build_menu(self):
        menubar = QMenuBar(self)

        # File menu
        file_menu = QMenu("&File", self)
        act_open_file = QAction("📄  Select File…", self)
        act_open_file.setShortcut("Ctrl+O")
        act_open_file.triggered.connect(self._select_file)
        act_open_dir = QAction("📁  Select Directory…", self)
        act_open_dir.triggered.connect(self._select_directory)
        act_quit = QAction("Quit", self)
        act_quit.setShortcut("Ctrl+Q")
        act_quit.triggered.connect(QApplication.quit)
        file_menu.addAction(act_open_file)
        file_menu.addAction(act_open_dir)
        file_menu.addSeparator()
        file_menu.addAction(act_quit)
        menubar.addMenu(file_menu)

        # Edit menu
        edit_menu = QMenu("&Edit", self)
        self._act_undo = QAction("Undo", self)
        self._act_undo.setShortcut("Ctrl+Z")
        self._act_undo.setEnabled(False)
        self._act_undo.triggered.connect(self._do_undo)
        self._act_redo = QAction("Redo", self)
        self._act_redo.setShortcut("Ctrl+Y")
        self._act_redo.setEnabled(False)
        self._act_redo.triggered.connect(self._do_redo)
        act_clear = QAction("Clear Fields", self)
        act_clear.triggered.connect(self._clear_fields)
        edit_menu.addAction(self._act_undo)
        edit_menu.addAction(self._act_redo)
        edit_menu.addSeparator()
        edit_menu.addAction(act_clear)
        menubar.addMenu(edit_menu)

        # Help menu
        help_menu = QMenu("&Help", self)
        act_manual = QAction("📖  Manual", self)
        act_manual.triggered.connect(self._open_manual)
        act_about = QAction("ℹ  About", self)
        act_about.triggered.connect(self._open_about)
        help_menu.addAction(act_manual)
        help_menu.addSeparator()
        help_menu.addAction(act_about)
        menubar.addMenu(help_menu)

        self.setMenuBar(menubar)

    # ──────────────────────────────────────────────────────────────────────────
    #  LOGGING SETUP
    # ──────────────────────────────────────────────────────────────────────────

    def _setup_logging(self):
        panel = self._log_panel

        class _UIPanelHandler(logging.Handler):
            def emit(self_, record):
                lvl_map = {
                    logging.ERROR: "ERROR",
                    logging.WARNING: "WARNING",
                    logging.INFO: "INFO",
                }
                lvl = lvl_map.get(record.levelno, "INFO")
                panel.add(self_.format(record), lvl)

        root_logger = logging.getLogger()
        root_logger.setLevel(logging.INFO)
        h = _UIPanelHandler()
        h.setFormatter(logging.Formatter("%(message)s"))
        root_logger.addHandler(h)

    def _log(self, message: str, level: str = "INFO"):
        self._log_panel.add(message, level)
        self._status_bar.showMessage(re.sub(r"<[^>]+>", "", message), 4000)

        if self._file_log_handler:
            plain = re.sub(r"<[^>]+>", "", message)
            lvl_map = {
                "SUCCESS": logging.INFO,
                "ERROR": logging.ERROR,
                "WARNING": logging.WARNING,
                "INFO": logging.INFO,
            }
            record = logging.LogRecord(
                name="ReplaceCharacter",
                level=lvl_map.get(level, logging.INFO),
                pathname="",
                lineno=0,
                msg=plain,
                args=(),
                exc_info=None,
            )
            self._file_log_handler.emit(record)

    def _toggle_file_logging(self, enabled: bool):
        root_logger = logging.getLogger()
        if enabled:
            log_path = Path(sys.argv[0]).parent / LOG_FILE
            try:
                fh = logging.FileHandler(str(log_path), encoding="utf-8")
                fh.setFormatter(
                    logging.Formatter(
                        "%(asctime)s  [%(levelname)s]  %(message)s",
                        datefmt="%Y-%m-%d %H:%M:%S",
                    )
                )
                root_logger.addHandler(fh)
                self._file_log_handler = fh
                self._log(f"File logging enabled → {log_path}", "INFO")
            except Exception as e:
                self._log(f"Could not open log file: {e}", "ERROR")
                self._log_file_check.setChecked(False)
        else:
            if self._file_log_handler:
                self._log("File logging disabled.", "INFO")
                root_logger.removeHandler(self._file_log_handler)
                self._file_log_handler.close()
                self._file_log_handler = None

        self._config.set("enable_logging", enabled)
        self._config.save()

    # ──────────────────────────────────────────────────────────────────────────
    #  CONFIG  LOAD / SAVE
    # ──────────────────────────────────────────────────────────────────────────

    def _load_config(self):
        theme = self._config.get("theme")
        ThemeManager.apply(QApplication.instance(), theme)
        self._update_theme_btn_label()

        self._regex_check.setChecked(self._config.get("use_regex"))
        self._case_check.setChecked(self._config.get("case_sensitive"))
        self._old_char.setText(self._config.get("old_char"))
        self._new_char.setText(self._config.get("new_char"))
        self._remove_word.setText(self._config.get("remove_word"))

        if self._config.get("enable_logging"):
            self._log_file_check.setChecked(True)  # this will trigger the handler

        last = self._config.get("last_directory")
        if last and Path(last).exists():
            self._set_path(Path(last))

    def _save_config(self):
        self._config.set("theme", ThemeManager.current)
        self._config.set("use_regex", self._regex_check.isChecked())
        self._config.set("case_sensitive", self._case_check.isChecked())
        self._config.set("old_char", self._old_char.text())
        self._config.set("new_char", self._new_char.text())
        self._config.set("remove_word", self._remove_word.text())
        self._config.set("enable_logging", self._log_file_check.isChecked())
        if self._path:
            self._config.set("last_directory", str(self._path))
        self._config.save()

    # ──────────────────────────────────────────────────────────────────────────
    #  THEME TOGGLE
    # ──────────────────────────────────────────────────────────────────────────

    def _toggle_theme(self):
        new_theme = "dark" if ThemeManager.current == "light" else "light"
        ThemeManager.apply(QApplication.instance(), new_theme)
        self._update_theme_btn_label()
        self._save_config()

    def _update_theme_btn_label(self):
        if ThemeManager.is_dark():
            self._theme_btn.setText("☀️  Light Mode")
            self._title_lbl.setStyleSheet(
                "color: #00D4AA; font-size: 20px; font-weight: 900; "
                "letter-spacing: 6px; font-family: 'Consolas', monospace;"
            )
        else:
            self._theme_btn.setText("🌙  Dark Mode")
            self._title_lbl.setStyleSheet(
                "color: #0099BB; font-size: 20px; font-weight: 900; "
                "letter-spacing: 6px; font-family: 'Consolas', monospace;"
            )

    # ──────────────────────────────────────────────────────────────────────────
    #  PATH SELECTION
    # ──────────────────────────────────────────────────────────────────────────

    def _set_path(self, path: Path):
        self._path = path
        icon = "📁" if path.is_dir() else "📄"
        label = "Directory" if path.is_dir() else "File"
        self._path_display.setText(f"{icon}  [{label}]  {path}")
        self._path_display.setStyleSheet(
            f"color: {ThemeManager.accent_color()}; font-size: 11px; "
            "border: 1px solid #2A3050; border-radius: 4px; padding: 6px;"
        )
        self._log(f"Selected: {path}", "INFO")

    def _select_file(self):
        start = str(self._path or Path.home())
        fp, _ = QFileDialog.getOpenFileName(self, "Select File", start)
        if fp:
            self._set_path(Path(fp))

    def _select_directory(self):
        start = str(self._path or Path.home())
        dp = QFileDialog.getExistingDirectory(self, "Select Directory", start)
        if dp:
            self._set_path(Path(dp))

    # ──────────────────────────────────────────────────────────────────────────
    #  TOGGLE CHECKBOXES
    # ──────────────────────────────────────────────────────────────────────────

    def _toggle_replace(self, state):
        enabled = state == Qt.CheckState.Checked.value
        self._old_char.setEnabled(enabled)
        self._new_char.setEnabled(enabled)

    def _toggle_remove(self, state):
        enabled = state == Qt.CheckState.Checked.value
        self._remove_word.setEnabled(enabled)

    # ──────────────────────────────────────────────────────────────────────────
    #  BUILD ENGINE FROM CURRENT FORM STATE
    # ──────────────────────────────────────────────────────────────────────────

    def _build_engine(self) -> Optional[RenameEngine]:
        """
        Validates inputs and constructs a RenameEngine.
        Returns None and shows error messages on validation failure.
        """
        do_replace = self._replace_enable.isChecked()
        do_remove = self._remove_enable.isChecked()

        if not do_replace and not do_remove:
            QMessageBox.warning(
                self,
                "Nothing to do",
                "Enable at least one step: Replace or Remove.",
            )
            return None

        old_char = self._old_char.text()
        new_char = self._new_char.text()
        remove_word = self._remove_word.text()
        use_regex = self._regex_check.isChecked()
        case_sens = self._case_check.isChecked()

        if do_replace and not old_char:
            QMessageBox.warning(self, "Input required", "Enter a pattern to replace.")
            self._tabs.setCurrentIndex(0)
            return None

        if do_remove and not remove_word:
            QMessageBox.warning(self, "Input required", "Enter a word to remove.")
            self._tabs.setCurrentIndex(1)
            return None

        # Validate regex
        if use_regex and do_replace and old_char:
            try:
                re.compile(old_char)
            except re.error as e:
                QMessageBox.critical(
                    self, "Invalid Regex", f"Pattern is not valid regex:\n{e}"
                )
                self._tabs.setCurrentIndex(0)
                return None

        return RenameEngine(
            old_char=old_char,
            new_char=new_char,
            remove_word=remove_word,
            use_regex=use_regex,
            case_sensitive=case_sens,
            do_replace=do_replace,
            do_remove=do_remove,
        )

    def _collect_paths(self) -> Optional[List[Path]]:
        """
        Returns a flat list of Paths to process.
        For a file: [that file].
        For a directory: [the directory] (worker expands it).
        Shows error if nothing is selected or path is gone.
        """
        if not self._path:
            QMessageBox.warning(
                self, "No selection", "Please select a file or directory first."
            )
            return None
        if not self._path.exists():
            QMessageBox.critical(
                self, "Path not found", f"Path no longer exists:\n{self._path}"
            )
            return None
        return [self._path]

    # ──────────────────────────────────────────────────────────────────────────
    #  PREVIEW
    # ──────────────────────────────────────────────────────────────────────────

    def _refresh_preview(self):
        engine = self._build_engine()
        if not engine:
            return

        paths = self._collect_paths()
        if not paths:
            return

        # Expand directories to file lists
        file_paths: List[Path] = []
        for p in paths:
            if p.is_file():
                file_paths.append(p)
            elif p.is_dir():
                try:
                    file_paths.extend(f for f in p.iterdir() if f.is_file())
                except Exception as e:
                    self._log(f"Cannot read directory: {e}", "ERROR")
                    return

        if not file_paths:
            QMessageBox.information(self, "Empty", "No files found to preview.")
            return

        previews = engine.preview_batch(file_paths)
        self._preview_table.populate(previews)
        self._tabs.setCurrentIndex(2)  # switch to preview tab
        self._log(f"Preview generated for {len(file_paths)} file(s).", "INFO")

    # ──────────────────────────────────────────────────────────────────────────
    #  APPLY CHANGES
    # ──────────────────────────────────────────────────────────────────────────

    def _apply_changes(self):
        engine = self._build_engine()
        if not engine:
            return

        paths = self._collect_paths()
        if not paths:
            return

        reply = QMessageBox.question(
            self,
            "Confirm Operation",
            f"Apply rename rules to:\n{self._path}\n\nContinue?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if reply != QMessageBox.StandardButton.Yes:
            return

        self._log("Starting rename operation…", "INFO")
        self._set_busy(True)

        self._worker = RenameWorker(paths=paths, engine=engine, parent=self)
        self._worker.progress.connect(self._on_progress)
        self._worker.log_msg.connect(self._log)
        self._worker.finished.connect(self._on_finished)
        self._worker.start()

    # ──────────────────────────────────────────────────────────────────────────
    #  UNDO / REDO
    # ──────────────────────────────────────────────────────────────────────────

    def _do_undo(self):
        op = self._undo_stack.undo()
        if not op:
            return

        self._log(f"Undoing {op.count} rename(s) from {op.timestamp}…", "WARNING")
        self._activity.start("Undoing")
        self._set_busy(True)

        results = op.undo()
        ok = sum(1 for *_, s, _ in results if s)
        err = len(results) - ok

        for old_path, new_path, success, error in results:
            if success:
                self._log(f"↩  {new_path.name}  →  {old_path.name}", "SUCCESS")
            else:
                self._log(f"✘  {new_path.name}: {error}", "ERROR")

        self._set_busy(False)
        self._update_undo_buttons()
        self._log(
            f"Undo complete — {ok} reversed" + (f", {err} failed" if err else ""),
            "SUCCESS" if err == 0 else "WARNING",
        )

    def _do_redo(self):
        op = self._undo_stack.redo()
        if not op:
            return
        # Redo means re-performing the original renames.
        # Re-run them in forward direction.
        self._log(f"Redoing {op.count} rename(s) from {op.timestamp}…", "INFO")
        self._activity.start("Redoing")
        self._set_busy(True)

        ok = 0
        err = 0
        for old_path, new_path in op.renames:
            try:
                if old_path.exists():
                    old_path.rename(new_path)
                    self._log(f"↪  {old_path.name}  →  {new_path.name}", "SUCCESS")
                    ok += 1
                else:
                    self._log(f"✘  {old_path.name}: file not found", "ERROR")
                    err += 1
            except Exception as e:
                self._log(f"✘  {old_path.name}: {e}", "ERROR")
                err += 1

        self._set_busy(False)
        self._update_undo_buttons()
        self._log(
            f"Redo complete — {ok} applied" + (f", {err} failed" if err else ""),
            "SUCCESS" if err == 0 else "WARNING",
        )

    def _update_undo_buttons(self):
        can_undo = self._undo_stack.can_undo()
        can_redo = self._undo_stack.can_redo()

        self._undo_btn.setEnabled(can_undo)
        self._redo_btn.setEnabled(can_redo)
        self._act_undo.setEnabled(can_undo)
        self._act_redo.setEnabled(can_redo)

        self._undo_btn.setText(
            f"↩  {self._undo_stack.undo_label()}" if can_undo else "↩  Undo"
        )
        self._redo_btn.setText(
            f"↪  {self._undo_stack.redo_label()}" if can_redo else "↪  Redo"
        )
        self._act_undo.setText(self._undo_stack.undo_label() if can_undo else "Undo")
        self._act_redo.setText(self._undo_stack.redo_label() if can_redo else "Redo")

    # ──────────────────────────────────────────────────────────────────────────
    #  CLEAR
    # ──────────────────────────────────────────────────────────────────────────

    def _clear_fields(self):
        self._old_char.clear()
        self._new_char.clear()
        self._remove_word.clear()
        self._replace_enable.setChecked(False)
        self._remove_enable.setChecked(False)
        self._preview_table.clear()
        self._progress.setValue(0)
        self._progress_lbl.setText("")
        self._log("Fields cleared.", "INFO")

    # ──────────────────────────────────────────────────────────────────────────
    #  WORKER SLOTS
    # ──────────────────────────────────────────────────────────────────────────

    def _on_progress(self, current: int, total: int, name: str):
        pct = int((current / max(total, 1)) * 100)
        self._progress.setValue(pct)
        self._progress_lbl.setText(f"Processing: {name}  ({current}/{total})")

    def _on_finished(self, success: bool, renames: list):
        self._set_busy(False)
        self._progress.setValue(0)
        self._progress_lbl.setText("")

        ok = len(renames)
        if success and ok >= 0:
            if renames:
                # Convert the raw (old, new) list into Path tuples and push undo
                op_renames = [(Path(o), Path(n)) for o, n in renames]
                op = RenameOperation(op_renames)
                self._undo_stack.push(op)
                self._update_undo_buttons()

            self._log(
                f"✔  Done — {ok} file(s) renamed successfully.",
                "SUCCESS",
            )
            self._status_bar.showMessage(f"Done — {ok} file(s) renamed.", 6000)
        else:
            self._log("⚠  Operation completed with errors.", "WARNING")

        self._save_config()

    # ──────────────────────────────────────────────────────────────────────────
    #  BUSY STATE
    # ──────────────────────────────────────────────────────────────────────────

    def _set_busy(self, busy: bool):
        self._apply_btn.setEnabled(not busy)
        self._sel_file_btn.setEnabled(not busy)
        self._sel_dir_btn.setEnabled(not busy)
        if busy:
            self._apply_btn.setText("⏳  Running…")
            self._activity.start("Processing")
        else:
            self._apply_btn.setText("⚡  Apply Changes")
            self._activity.stop()

    # ──────────────────────────────────────────────────────────────────────────
    #  DIALOGS
    # ──────────────────────────────────────────────────────────────────────────

    def _open_about(self):
        AboutDialog(self).exec()

    def _open_manual(self):
        ManualDialog(self).exec()

    # ──────────────────────────────────────────────────────────────────────────
    #  DRAG AND DROP
    # ──────────────────────────────────────────────────────────────────────────

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            event.ignore()

    def dropEvent(self, event: QDropEvent):
        urls = event.mimeData().urls()
        if urls:
            local = Path(urls[0].toLocalFile())
            if local.exists():
                self._set_path(local)
                event.acceptProposedAction()

    # ──────────────────────────────────────────────────────────────────────────
    #  CLOSE
    # ──────────────────────────────────────────────────────────────────────────

    def closeEvent(self, event):
        self._save_config()
        event.accept()


# ══════════════════════════════════════════════════════════════════════════════
#  ENTRY POINT
# ══════════════════════════════════════════════════════════════════════════════


def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setApplicationName(APP_NAME)
    app.setApplicationVersion(APP_VERSION)
    app.setOrganizationName(APP_COMPANY)

    try:
        app.setWindowIcon(QIcon("icon.ico"))
    except Exception:
        pass

    # Apply light theme by default; config may override immediately
    ThemeManager.apply(app, "light")

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
