import sys
import os
import re
import json
import shutil
import tempfile
from pathlib import Path

from PySide6.QtCore import (
    Qt, QRect, QSize, QRegularExpression, QPropertyAnimation,
    QEasingCurve, QProcess, Signal, QTimer
)
from PySide6.QtGui import (
    QColor, QPainter, QTextFormat, QFont, QFontMetricsF, QKeySequence,
    QSyntaxHighlighter, QTextCharFormat, QAction, QActionGroup, QTextCursor,
    QShortcut, QTextDocument
)
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QPlainTextEdit, QWidget, QTextEdit,
    QTabWidget, QVBoxLayout, QHBoxLayout, QDialog, QLabel, QComboBox,
    QSpinBox, QCheckBox, QPushButton, QFontComboBox, QFileDialog,
    QMessageBox, QDockWidget, QStatusBar, QToolBar, QStyleFactory,
    QFormLayout, QLineEdit, QInputDialog
)

APP_NAME = "IVP Editor"
SETTINGS_DIR = Path.home() / ".pyforge_editor"
SETTINGS_FILE = SETTINGS_DIR / "settings.json"

DEFAULT_SETTINGS = {
    "theme": "Dark+",
    "font_family": "JetBrains Mono",
    "font_size": 13,
    "tab_width": 4,
    "word_wrap": False,
    "smooth_typing": True,
}



THEMES = {
    "Dark+": {
        "bg": "#1e1e1e", "editor_bg": "#1e1e1e", "fg": "#d4d4d4",
        "sidebar_bg": "#252526", "line_number_fg": "#6e7681",
        "line_number_bg": "#1e1e1e", "current_line": "#2a2d2e",
        "selection_bg": "#264f78", "selection_fg": "#ffffff",
        "accent": "#0e639c", "accent_hover": "#1177bb", "border": "#3c3c3c",
        "scrollbar_bg": "#1e1e1e", "scrollbar_handle": "#424242",
        "menu_bg": "#2d2d30", "menu_hover": "#094771",
        "tab_bg": "#2d2d2d", "tab_active_bg": "#1e1e1e",
        "keyword": "#569cd6", "string": "#ce9178", "comment": "#6a9955",
        "number": "#b5cea8", "function": "#dcdcaa", "class_name": "#4ec9b0",
        "decorator": "#dcdcaa", "operator": "#d4d4d4", "builtin": "#4ec9b0",
        "self_kw": "#9cdcfe",
    },
    "Dracula": {
        "bg": "#282a36", "editor_bg": "#282a36", "fg": "#f8f8f2",
        "sidebar_bg": "#21222c", "line_number_fg": "#6272a4",
        "line_number_bg": "#282a36", "current_line": "#44475a",
        "selection_bg": "#44475a", "selection_fg": "#f8f8f2",
        "accent": "#bd93f9", "accent_hover": "#caa9fa", "border": "#191a21",
        "scrollbar_bg": "#282a36", "scrollbar_handle": "#44475a",
        "menu_bg": "#21222c", "menu_hover": "#44475a",
        "tab_bg": "#21222c", "tab_active_bg": "#282a36",
        "keyword": "#ff79c6", "string": "#f1fa8c", "comment": "#6272a4",
        "number": "#bd93f9", "function": "#50fa7b", "class_name": "#8be9fd",
        "decorator": "#50fa7b", "operator": "#ff79c6", "builtin": "#8be9fd",
        "self_kw": "#bd93f9",
    },
    "Monokai": {
        "bg": "#272822", "editor_bg": "#272822", "fg": "#f8f8f2",
        "sidebar_bg": "#1e1f1c", "line_number_fg": "#75715e",
        "line_number_bg": "#272822", "current_line": "#3e3d32",
        "selection_bg": "#49483e", "selection_fg": "#f8f8f2",
        "accent": "#a6e22e", "accent_hover": "#b6f23e", "border": "#1e1f1c",
        "scrollbar_bg": "#272822", "scrollbar_handle": "#49483e",
        "menu_bg": "#1e1f1c", "menu_hover": "#3e3d32",
        "tab_bg": "#1e1f1c", "tab_active_bg": "#272822",
        "keyword": "#f92672", "string": "#e6db74", "comment": "#75715e",
        "number": "#ae81ff", "function": "#a6e22e", "class_name": "#66d9ef",
        "decorator": "#a6e22e", "operator": "#f92672", "builtin": "#66d9ef",
        "self_kw": "#fd971f",
    },
    "Nord": {
        "bg": "#2e3440", "editor_bg": "#2e3440", "fg": "#d8dee9",
        "sidebar_bg": "#272c36", "line_number_fg": "#4c566a",
        "line_number_bg": "#2e3440", "current_line": "#3b4252",
        "selection_bg": "#434c5e", "selection_fg": "#eceff4",
        "accent": "#88c0d0", "accent_hover": "#8fbcbb", "border": "#242933",
        "scrollbar_bg": "#2e3440", "scrollbar_handle": "#4c566a",
        "menu_bg": "#272c36", "menu_hover": "#434c5e",
        "tab_bg": "#272c36", "tab_active_bg": "#2e3440",
        "keyword": "#81a1c1", "string": "#a3be8c", "comment": "#616e88",
        "number": "#b48ead", "function": "#88c0d0", "class_name": "#8fbcbb",
        "decorator": "#ebcb8b", "operator": "#81a1c1", "builtin": "#8fbcbb",
        "self_kw": "#d08770",
    },
    "Solarized Light": {
        "bg": "#fdf6e3", "editor_bg": "#fdf6e3", "fg": "#657b83",
        "sidebar_bg": "#eee8d5", "line_number_fg": "#93a1a1",
        "line_number_bg": "#fdf6e3", "current_line": "#eee8d5",
        "selection_bg": "#d3e4e0", "selection_fg": "#586e75",
        "accent": "#268bd2", "accent_hover": "#2aa1f2", "border": "#d6cfb4",
        "scrollbar_bg": "#fdf6e3", "scrollbar_handle": "#d6cfb4",
        "menu_bg": "#eee8d5", "menu_hover": "#d3e4e0",
        "tab_bg": "#eee8d5", "tab_active_bg": "#fdf6e3",
        "keyword": "#859900", "string": "#2aa198", "comment": "#93a1a1",
        "number": "#d33682", "function": "#268bd2", "class_name": "#cb4b16",
        "decorator": "#b58900", "operator": "#657b83", "builtin": "#cb4b16",
        "self_kw": "#6c71c4",
    },
    "Pure Light": {
        "bg": "#ffffff", "editor_bg": "#ffffff", "fg": "#24292e",
        "sidebar_bg": "#f6f8fa", "line_number_fg": "#a0a5aa",
        "line_number_bg": "#ffffff", "current_line": "#f1f3f5",
        "selection_bg": "#cce5ff", "selection_fg": "#24292e",
        "accent": "#0969da", "accent_hover": "#1a7bef", "border": "#d0d7de",
        "scrollbar_bg": "#ffffff", "scrollbar_handle": "#d0d7de",
        "menu_bg": "#f6f8fa", "menu_hover": "#dbe4ee",
        "tab_bg": "#f6f8fa", "tab_active_bg": "#ffffff",
        "keyword": "#cf222e", "string": "#0a3069", "comment": "#6e7781",
        "number": "#0550ae", "function": "#8250df", "class_name": "#953800",
        "decorator": "#8250df", "operator": "#24292e", "builtin": "#953800",
        "self_kw": "#e36209",
    },
}


def build_stylesheet(c: dict) -> str:
    """Build the app-wide QSS from a theme color dict, using placeholder
    substitution so QSS's own curly braces don't clash with str.format()."""
    template = """
    QWidget {
        background-color: @bg@;
        color: @fg@;
        selection-background-color: @selection_bg@;
        selection-color: @selection_fg@;
    }
    QMainWindow, QDialog { background-color: @bg@; }

    QMenuBar {
        background-color: @menu_bg@;
        border-bottom: 1px solid @border@;
        padding: 2px;
    }
    QMenuBar::item { background: transparent; padding: 4px 10px; border-radius: 4px; }
    QMenuBar::item:selected { background-color: @menu_hover@; }
    QMenu { background-color: @menu_bg@; border: 1px solid @border@; padding: 4px; }
    QMenu::item { padding: 6px 24px 6px 12px; border-radius: 4px; }
    QMenu::item:selected { background-color: @menu_hover@; }
    QMenu::separator { height: 1px; background: @border@; margin: 4px 6px; }

    QToolBar {
        background-color: @menu_bg@;
        border: none;
        spacing: 4px;
        padding: 4px;
    }
    QToolButton {
        background-color: transparent;
        border-radius: 6px;
        padding: 5px 10px;
        color: @fg@;
    }
    QToolButton:hover { background-color: @menu_hover@; }
    QToolButton:pressed { background-color: @accent@; }

    QStatusBar { background-color: @menu_bg@; border-top: 1px solid @border@; color: @fg@; }
    QStatusBar QLabel { padding: 0 8px; }

    QTabWidget::pane { border: none; border-top: 1px solid @border@; top: -1px; }
    QTabBar { background-color: @tab_bg@; }
    QTabBar::tab {
        background-color: @tab_bg@;
        color: @fg@;
        padding: 7px 16px;
        border: none;
        border-right: 1px solid @border@;
        min-width: 90px;
    }
    QTabBar::tab:selected {
        background-color: @tab_active_bg@;
        border-bottom: 2px solid @accent@;
    }
    QTabBar::tab:hover:!selected { background-color: @current_line@; }
    QTabBar::close-button { subcontrol-position: right; }

    QPlainTextEdit, QTextEdit {
        background-color: @editor_bg@;
        color: @fg@;
        border: none;
        selection-background-color: @selection_bg@;
        selection-color: @selection_fg@;
    }

    QDockWidget {
        color: @fg@;
        titlebar-close-icon: none;
    }
    QDockWidget::title {
        background-color: @menu_bg@;
        padding: 6px;
        border-bottom: 1px solid @border@;
    }

    QScrollBar:vertical {
        background: @scrollbar_bg@;
        width: 12px;
        margin: 0;
    }
    QScrollBar::handle:vertical {
        background: @scrollbar_handle@;
        min-height: 24px;
        border-radius: 5px;
        margin: 2px;
    }
    QScrollBar::handle:vertical:hover { background: @accent@; }
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }

    QScrollBar:horizontal {
        background: @scrollbar_bg@;
        height: 12px;
        margin: 0;
    }
    QScrollBar::handle:horizontal {
        background: @scrollbar_handle@;
        min-width: 24px;
        border-radius: 5px;
        margin: 2px;
    }
    QScrollBar::handle:horizontal:hover { background: @accent@; }
    QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal { width: 0; }

    QPushButton {
        background-color: @accent@;
        color: white;
        border: none;
        border-radius: 6px;
        padding: 7px 16px;
        font-weight: 600;
    }
    QPushButton:hover { background-color: @accent_hover@; }
    QPushButton:pressed { background-color: @accent@; }
    QPushButton:disabled { background-color: @border@; color: @line_number_fg@; }
    QPushButton#secondary {
        background-color: transparent;
        color: @fg@;
        border: 1px solid @border@;
    }
    QPushButton#secondary:hover { background-color: @menu_hover@; }

    QComboBox, QSpinBox, QFontComboBox, QLineEdit {
        background-color: @sidebar_bg@;
        border: 1px solid @border@;
        border-radius: 5px;
        padding: 5px 8px;
        min-height: 20px;
    }
    QComboBox:hover, QSpinBox:hover, QFontComboBox:hover, QLineEdit:focus { border: 1px solid @accent@; }
    QComboBox::drop-down { border: none; width: 22px; }
    QComboBox QAbstractItemView {
        background-color: @sidebar_bg@;
        border: 1px solid @border@;
        selection-background-color: @accent@;
        outline: none;
    }

    QCheckBox { spacing: 8px; }
    QCheckBox::indicator {
        width: 17px; height: 17px;
        border-radius: 4px;
        border: 1px solid @border@;
        background: @sidebar_bg@;
    }
    QCheckBox::indicator:checked { background: @accent@; border: 1px solid @accent@; }

    QLabel#dialogTitle { font-size: 16px; font-weight: 700; }
    QLabel#hint { color: @line_number_fg@; font-size: 11px; }

    QSplitter::handle { background-color: @border@; }
    """
    for k, v in c.items():
        template = template.replace(f"@{k}@", v)
    return template




PY_KEYWORDS = [
    "False", "None", "True", "and", "as", "assert", "async", "await",
    "break", "class", "continue", "def", "del", "elif", "else", "except",
    "finally", "for", "from", "global", "if", "import", "in", "is",
    "lambda", "nonlocal", "not", "or", "pass", "raise", "return", "try",
    "while", "with", "yield", "match", "case",
]
PY_BUILTINS = [
    "print", "len", "range", "int", "float", "str", "list", "dict", "set",
    "tuple", "bool", "object", "type", "super", "isinstance", "enumerate",
    "zip", "map", "filter", "open", "input", "sorted", "reversed", "sum",
    "min", "max", "abs", "round", "any", "all", "iter", "next",
]

C_KEYWORDS = [
    "auto", "break", "case", "char", "const", "continue", "default", "do",
    "double", "else", "enum", "extern", "float", "for", "goto", "if", "int",
    "long", "register", "return", "short", "signed", "sizeof", "static",
    "struct", "switch", "typedef", "union", "unsigned", "void", "volatile",
    "while", "inline", "restrict",
]
C_BUILTINS = [
    "printf", "scanf", "malloc", "calloc", "realloc", "free", "NULL",
    "fopen", "fclose", "fprintf", "fscanf", "strlen", "strcpy", "strcat",
    "strcmp", "memcpy", "memset", "exit", "size_t",
]

CPP_KEYWORDS = C_KEYWORDS + [
    "class", "public", "private", "protected", "virtual", "override", "new",
    "delete", "namespace", "using", "template", "typename", "try", "catch",
    "throw", "friend", "this", "true", "false", "nullptr", "bool",
    "explicit", "mutable", "operator", "constexpr", "noexcept", "decltype",
    "export", "final", "concept", "requires",
]
CPP_BUILTINS = C_BUILTINS + ["std", "cout", "cin", "endl", "string", "vector", "map", "make_unique", "make_shared"]

CSHARP_KEYWORDS = [
    "abstract", "as", "base", "bool", "break", "byte", "case", "catch",
    "char", "checked", "class", "const", "continue", "decimal", "default",
    "delegate", "do", "double", "else", "enum", "event", "explicit",
    "extern", "false", "finally", "fixed", "float", "for", "foreach",
    "goto", "if", "implicit", "in", "int", "interface", "internal", "is",
    "lock", "long", "namespace", "new", "null", "object", "operator", "out",
    "override", "params", "private", "protected", "public", "readonly",
    "ref", "return", "sbyte", "sealed", "short", "sizeof", "stackalloc",
    "static", "string", "struct", "switch", "this", "throw", "true", "try",
    "typeof", "uint", "ulong", "unchecked", "unsafe", "ushort", "using",
    "var", "virtual", "void", "volatile", "while", "async", "await",
    "yield", "get", "set", "partial", "dynamic", "nameof",
]

BATCH_KEYWORDS = [
    "echo", "set", "setlocal", "endlocal", "if", "else", "for", "goto",
    "call", "exit", "pause", "cls", "title", "cd", "dir", "copy", "del",
    "move", "ren", "rename", "mkdir", "rmdir", "start", "shift", "exist",
    "not", "defined", "errorlevel", "do", "in", "choice", "findstr",
    "timeout", "taskkill", "ping", "xcopy", "robocopy", "net", "reg",
    "attrib", "cscript", "wscript",
]

LANGUAGES = {
    "Python": {
        "keywords": PY_KEYWORDS, "builtins": PY_BUILTINS,
        "comment": "#", "block_comment": (r"('''|\"\"\")", r"('''|\"\"\")"),
        "block_is_string": True, "class_pattern": True, "def_pattern": True,
        "decorator": True, "self_kw": "self",
        "extensions": [".py", ".pyw"],
    },
    "C": {
        "keywords": C_KEYWORDS, "builtins": C_BUILTINS,
        "comment": "//", "block_comment": (r"/\*", r"\*/"),
        "extensions": [".c", ".h"],
    },
    "C++": {
        "keywords": CPP_KEYWORDS, "builtins": CPP_BUILTINS,
        "comment": "//", "block_comment": (r"/\*", r"\*/"),
        "class_pattern": True, "self_kw": "this",
        "extensions": [".cpp", ".cc", ".cxx", ".hpp", ".hh"],
    },
    "C#": {
        "keywords": CSHARP_KEYWORDS, "builtins": [],
        "comment": "//", "block_comment": (r"/\*", r"\*/"),
        "class_pattern": True, "self_kw": "this", "attribute": True,
        "extensions": [".cs"],
    },
    "Batch": {
        "keywords": BATCH_KEYWORDS, "builtins": [],
        "comment": "REM", "comment_alt": "::", "case_insensitive": True,
        "block_comment": None, "var_pattern": r"%[^%\s]+%|![^!\s]+!",
        "extensions": [".bat", ".cmd"],
    },
    "Plain Text": {
        "keywords": [], "builtins": [], "comment": "#",
        "block_comment": None, "extensions": [".txt"],
    },
}

EXT_TO_LANGUAGE = {}
for _name, _spec in LANGUAGES.items():
    for _ext in _spec.get("extensions", []):
        EXT_TO_LANGUAGE[_ext] = _name

DEFAULT_EXTENSION = {name: spec["extensions"][0] for name, spec in LANGUAGES.items()}




class CodeHighlighter(QSyntaxHighlighter):
    def __init__(self, document, colors, lang_spec):
        super().__init__(document)
        self.set_colors_and_language(colors, lang_spec)

    def _fmt(self, color, bold=False, italic=False):
        f = QTextCharFormat()
        f.setForeground(QColor(color))
        if bold:
            f.setFontWeight(QFont.Bold)
        f.setFontItalic(italic)
        return f

    def set_colors(self, colors):
        self.set_colors_and_language(colors, self.lang)

    def set_language(self, lang_spec):
        self.set_colors_and_language(self.colors, lang_spec)

    def set_colors_and_language(self, colors, lang_spec):
        self.colors = colors
        self.lang = lang_spec
        self.rules = []

        flags = QRegularExpression.CaseInsensitiveOption if lang_spec.get("case_insensitive") \
            else QRegularExpression.NoPatternOption


        self.rules.append((QRegularExpression(r"\b([A-Za-z_]\w*)\s*(?=\()"), self._fmt(colors["function"])))

        for b in lang_spec.get("builtins", []):
            self.rules.append((QRegularExpression(rf"\b{re.escape(b)}\b", flags), self._fmt(colors["builtin"])))

        kw_fmt = self._fmt(colors["keyword"], bold=True)
        for kw in lang_spec.get("keywords", []):
            self.rules.append((QRegularExpression(rf"\b{re.escape(kw)}\b", flags), kw_fmt))

        if lang_spec.get("self_kw"):
            self.rules.append((QRegularExpression(rf"\b{lang_spec['self_kw']}\b"), self._fmt(colors["self_kw"], italic=True)))

        if lang_spec.get("class_pattern"):
            self.rules.append((QRegularExpression(r"\bclass\s+(\w+)\b"), self._fmt(colors["class_name"], bold=True)))

        if lang_spec.get("def_pattern"):
            self.rules.append((QRegularExpression(r"\bdef\s+(\w+)"), self._fmt(colors["function"], bold=True)))

        if lang_spec.get("decorator"):
            self.rules.append((QRegularExpression(r"@\w+"), self._fmt(colors["decorator"], italic=True)))

        if lang_spec.get("attribute"):
            self.rules.append((QRegularExpression(r"\[\s*\w+(\([^\]]*\))?\s*\]"), self._fmt(colors["decorator"], italic=True)))

        if lang_spec.get("var_pattern"):
            self.rules.append((QRegularExpression(lang_spec["var_pattern"]), self._fmt(colors["function"])))

        self.rules.append((QRegularExpression(r"\b0[xX][0-9a-fA-F]+\b|\b\d+\.?\d*\b"), self._fmt(colors["number"])))
        self.rules.append((QRegularExpression(r"'[^'\\]*(\\.[^'\\]*)*'"), self._fmt(colors["string"])))
        self.rules.append((QRegularExpression(r'"[^"\\]*(\\.[^"\\]*)*"'), self._fmt(colors["string"])))

        if lang_spec.get("case_insensitive") and lang_spec.get("comment_alt"):
            self.rules.append((QRegularExpression(r"^\s*(REM\b|::).*", QRegularExpression.CaseInsensitiveOption),
                                self._fmt(colors["comment"], italic=True)))
        else:
            tok = re.escape(lang_spec.get("comment", "#"))
            self.rules.append((QRegularExpression(tok + r".*"), self._fmt(colors["comment"], italic=True)))

    def highlightBlock(self, text):
        for pattern, fmt in self.rules:
            it = pattern.globalMatch(text)
            while it.hasNext():
                m = it.next()
                self.setFormat(m.capturedStart(), m.capturedLength(), fmt)
        self._highlight_block_comment(text)

    def _highlight_block_comment(self, text):
        self.setCurrentBlockState(0)
        block_comment = self.lang.get("block_comment")
        if not block_comment:
            return
        start_re = QRegularExpression(block_comment[0])
        end_re = QRegularExpression(block_comment[1])
        is_string = self.lang.get("block_is_string", False)
        fmt = self._fmt(self.colors["string" if is_string else "comment"], italic=not is_string)

        pos = 0
        if self.previousBlockState() == 1:
            end_match = end_re.match(text, 0)
            if end_match.hasMatch():
                end_pos = end_match.capturedEnd()
                self.setFormat(0, end_pos, fmt)
                pos = end_pos
            else:
                self.setFormat(0, len(text), fmt)
                self.setCurrentBlockState(1)
                return

        while True:
            start_match = start_re.match(text, pos)
            if not start_match.hasMatch():
                break
            s = start_match.capturedStart()
            search_from = start_match.capturedEnd()
            end_match = end_re.match(text, search_from)
            if end_match.hasMatch():
                e = end_match.capturedEnd()
                self.setFormat(s, e - s, fmt)
                pos = e
            else:
                self.setFormat(s, len(text) - s, fmt)
                self.setCurrentBlockState(1)
                return




class LineNumberArea(QWidget):
    def __init__(self, editor):
        super().__init__(editor)
        self.editor = editor

    def sizeHint(self):
        return QSize(self.editor.line_number_area_width(), 0)

    def paintEvent(self, event):
        self.editor.line_number_area_paint_event(event)


class SmoothCaret(QWidget):
    """A custom caret painted over the viewport. Its position glides between
    character cells via an animated QPropertyAnimation on 'geometry',
    instead of the native caret's instant per-character jump."""

    def __init__(self, parent):
        super().__init__(parent)
        self.setAttribute(Qt.WA_TransparentForMouseEvents)
        self._color = QColor("#ffffff")

    def set_color(self, color):
        self._color = QColor(color)
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.fillRect(self.rect(), self._color)


class CodeEditor(QPlainTextEdit):
    def __init__(self, colors, settings, language="Python", parent=None):
        super().__init__(parent)
        self.colors = colors
        self.settings = settings
        self.language = language
        self.file_path = None
        self.modified = False
        self.line_number_area = LineNumberArea(self)

        self.blockCountChanged.connect(self.update_line_number_area_width)
        self.updateRequest.connect(self.update_line_number_area)
        self.cursorPositionChanged.connect(self.highlight_current_line)

        self.update_line_number_area_width(0)
        self.highlight_current_line()

        self.highlighter = CodeHighlighter(self.document(), colors, LANGUAGES[language])

        self._scroll_anim = QPropertyAnimation(self.verticalScrollBar(), b"value")
        self._scroll_anim.setEasingCurve(QEasingCurve.OutCubic)
        self._scroll_anim.setDuration(180)


        self.caret = SmoothCaret(self.viewport())
        self.caret.set_color(colors["fg"])
        self.caret.hide()
        self._caret_anim = QPropertyAnimation(self.caret, b"geometry")
        self._caret_anim.setDuration(90)
        self._caret_anim.setEasingCurve(QEasingCurve.OutCubic)
        self._blink_timer = QTimer(self)
        self._blink_timer.setInterval(530)
        self._blink_timer.timeout.connect(self._toggle_blink)
        self._blink_visible = True

        self.cursorPositionChanged.connect(self._on_cursor_moved)
        self.updateRequest.connect(lambda rect, dy: self._update_caret(animate=False))

        self.apply_settings(settings)


    def apply_theme(self, colors):
        self.colors = colors
        self.highlighter.set_colors(colors)
        self.highlighter.rehighlight()
        self.highlight_current_line()
        self.line_number_area.update()
        self.caret.set_color(colors["fg"])

    def apply_settings(self, settings):
        self.settings = settings
        font = QFont(settings["font_family"], settings["font_size"])
        font.setFixedPitch(True)
        self.setFont(font)
        tab_stop = settings["tab_width"] * QFontMetricsF(font).horizontalAdvance(" ")
        self.setTabStopDistance(tab_stop)
        self.setLineWrapMode(QPlainTextEdit.WidgetWidth if settings["word_wrap"] else QPlainTextEdit.NoWrap)
        self.update_line_number_area_width(0)

        if settings.get("smooth_typing", True):
            self.setCursorWidth(0)
            self._update_caret(animate=False)
            if self.hasFocus():
                self._blink_timer.start()
        else:
            self.setCursorWidth(2)
            self.caret.hide()
            self._blink_timer.stop()


    def _on_cursor_moved(self):
        self._blink_visible = True
        self._update_caret(animate=True)
        if self.settings.get("smooth_typing", True) and self.hasFocus():
            self._blink_timer.start()

    def _update_caret(self, animate=True):
        if not self.settings.get("smooth_typing", True) or self.isReadOnly():
            self.caret.hide()
            return
        rect = self.cursorRect()
        target = QRect(rect.x(), rect.y(), 2, rect.height())
        if animate and self.caret.isVisible():
            self._caret_anim.stop()
            self._caret_anim.setStartValue(self.caret.geometry())
            self._caret_anim.setEndValue(target)
            self._caret_anim.start()
        else:
            self.caret.setGeometry(target)
        self.caret.setVisible(self.hasFocus())

    def _toggle_blink(self):
        if not self.settings.get("smooth_typing", True) or not self.hasFocus():
            return
        self._blink_visible = not self._blink_visible
        self.caret.setVisible(self._blink_visible)

    def focusInEvent(self, event):
        super().focusInEvent(event)
        if self.settings.get("smooth_typing", True):
            self._blink_visible = True
            self._update_caret(animate=False)
            self._blink_timer.start()

    def focusOutEvent(self, event):
        super().focusOutEvent(event)
        self.caret.hide()
        self._blink_timer.stop()

    def set_language(self, name):
        self.language = name
        self.highlighter.set_language(LANGUAGES[name])
        self.highlighter.rehighlight()


    def line_number_area_width(self):
        digits = len(str(max(1, self.blockCount())))
        return 14 + self.fontMetrics().horizontalAdvance("9") * digits

    def update_line_number_area_width(self, _):
        self.setViewportMargins(self.line_number_area_width(), 0, 0, 0)

    def update_line_number_area(self, rect, dy):
        if dy:
            self.line_number_area.scroll(0, dy)
        else:
            self.line_number_area.update(0, rect.y(), self.line_number_area.width(), rect.height())
        if rect.contains(self.viewport().rect()):
            self.update_line_number_area_width(0)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        cr = self.contentsRect()
        self.line_number_area.setGeometry(QRect(cr.left(), cr.top(), self.line_number_area_width(), cr.height()))
        if hasattr(self, "caret"):
            self._update_caret(animate=False)

    def line_number_area_paint_event(self, event):
        painter = QPainter(self.line_number_area)
        painter.fillRect(event.rect(), QColor(self.colors["line_number_bg"]))

        block = self.firstVisibleBlock()
        block_number = block.blockNumber()
        top = self.blockBoundingGeometry(block).translated(self.contentOffset()).top()
        bottom = top + self.blockBoundingRect(block).height()

        painter.setPen(QColor(self.colors["line_number_fg"]))
        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                number = str(block_number + 1)
                painter.drawText(0, int(top), self.line_number_area.width() - 6, self.fontMetrics().height(),
                                  Qt.AlignRight, number)
            block = block.next()
            top = bottom
            bottom = top + self.blockBoundingRect(block).height()
            block_number += 1

    def highlight_current_line(self):
        extra = []
        if not self.isReadOnly():
            sel = QTextEdit.ExtraSelection()
            sel.format.setBackground(QColor(self.colors["current_line"]))
            sel.format.setProperty(QTextFormat.FullWidthSelection, True)
            sel.cursor = self.textCursor()
            sel.cursor.clearSelection()
            extra.append(sel)
        self.setExtraSelections(extra)


    def wheelEvent(self, event):
        if not self.settings.get("smooth_typing", True):
            super().wheelEvent(event)
            return
        bar = self.verticalScrollBar()
        delta = event.angleDelta().y()
        step = bar.singleStep() * 3
        target = bar.value() - (step if delta > 0 else -step)
        target = max(bar.minimum(), min(bar.maximum(), target))
        self._animate_scroll(target)
        event.accept()

    def _animate_scroll(self, target):
        bar = self.verticalScrollBar()
        self._scroll_anim.stop()
        self._scroll_anim.setStartValue(bar.value())
        self._scroll_anim.setEndValue(target)
        self._scroll_anim.start()


    def keyPressEvent(self, event):
        key = event.key()
        mods = event.modifiers()

        if key in (Qt.Key_PageDown, Qt.Key_PageUp) and self.settings.get("smooth_typing", True):
            bar = self.verticalScrollBar()
            page = self.viewport().height() - self.fontMetrics().height()
            target = bar.value() + (page if key == Qt.Key_PageDown else -page)
            target = max(bar.minimum(), min(bar.maximum(), target))
            super().keyPressEvent(event)
            self._animate_scroll(target)
            return

        if key == Qt.Key_Tab and self.textCursor().hasSelection():
            self.indent_selection()
            return
        if key == Qt.Key_Backtab:
            self.dedent_selection()
            return

        super().keyPressEvent(event)

    def duplicate_line(self):
        cursor = self.textCursor()
        cursor.beginEditBlock()
        cursor.movePosition(QTextCursor.StartOfBlock)
        cursor.movePosition(QTextCursor.EndOfBlock, QTextCursor.KeepAnchor)
        text = cursor.selectedText()
        cursor.movePosition(QTextCursor.EndOfBlock)
        cursor.insertText("\n" + text)
        cursor.endEditBlock()

    def delete_line(self):
        cursor = self.textCursor()
        cursor.beginEditBlock()
        cursor.movePosition(QTextCursor.StartOfBlock)
        cursor.movePosition(QTextCursor.EndOfBlock, QTextCursor.KeepAnchor)
        cursor.removeSelectedText()
        cursor.deleteChar()
        cursor.endEditBlock()

    def select_line(self):
        cursor = self.textCursor()
        cursor.movePosition(QTextCursor.StartOfBlock)
        cursor.movePosition(QTextCursor.EndOfBlock, QTextCursor.KeepAnchor)
        self.setTextCursor(cursor)

    def move_line_up(self):
        cursor = self.textCursor()
        block = cursor.block()
        prev_block = block.previous()
        if not prev_block.isValid():
            return
        col = cursor.positionInBlock()
        doc = self.document()
        cursor.beginEditBlock()
        span = QTextCursor(doc)
        span.setPosition(prev_block.position())
        end_pos = block.position() + block.length() - 1
        span.setPosition(end_pos, QTextCursor.KeepAnchor)
        text = span.selectedText()
        parts = text.split("\u2029")
        if len(parts) == 2:
            span.insertText(parts[1] + "\u2029" + parts[0])
            new_cursor = QTextCursor(doc)
            new_cursor.setPosition(prev_block.position() + col)
            self.setTextCursor(new_cursor)
        cursor.endEditBlock()

    def move_line_down(self):
        cursor = self.textCursor()
        block = cursor.block()
        next_block = block.next()
        if not next_block.isValid():
            return
        col = cursor.positionInBlock()
        doc = self.document()
        cursor.beginEditBlock()
        span = QTextCursor(doc)
        span.setPosition(block.position())
        end_pos = next_block.position() + next_block.length() - 1
        span.setPosition(end_pos, QTextCursor.KeepAnchor)
        text = span.selectedText()
        parts = text.split("\u2029")
        if len(parts) == 2:
            span.insertText(parts[1] + "\u2029" + parts[0])
            new_block = doc.findBlock(block.position()).next()
            new_cursor = QTextCursor(doc)
            new_cursor.setPosition(new_block.position() + col)
            self.setTextCursor(new_cursor)
        cursor.endEditBlock()

    def toggle_comment(self):
        cursor = self.textCursor()
        doc = self.document()
        if cursor.hasSelection():
            start_block = doc.findBlock(cursor.selectionStart()).blockNumber()
            end_block = doc.findBlock(cursor.selectionEnd()).blockNumber()
        else:
            start_block = end_block = cursor.blockNumber()

        prefix = LANGUAGES[self.language].get("comment", "#")

        all_commented = True
        for bn in range(start_block, end_block + 1):
            text = doc.findBlockByNumber(bn).text()
            stripped = text.lstrip()
            if stripped and not stripped.startswith(prefix):
                all_commented = False
                break

        cursor.beginEditBlock()
        for bn in range(start_block, end_block + 1):
            block = doc.findBlockByNumber(bn)
            text = block.text()
            indent_len = len(text) - len(text.lstrip(" \t"))
            indent = text[:indent_len]
            rest = text[indent_len:]
            if all_commented:
                if rest.startswith(prefix + " "):
                    rest = rest[len(prefix) + 1:]
                elif rest.startswith(prefix):
                    rest = rest[len(prefix):]
                new_text = indent + rest
            else:
                new_text = text if rest == "" else indent + prefix + " " + rest
            block_cursor = QTextCursor(block)
            block_cursor.select(QTextCursor.LineUnderCursor)
            block_cursor.insertText(new_text)
        cursor.endEditBlock()

    def indent_selection(self):
        cursor = self.textCursor()
        doc = self.document()
        pad = " " * self.settings.get("tab_width", 4)
        start_block = doc.findBlock(cursor.selectionStart()).blockNumber()
        end_block = doc.findBlock(cursor.selectionEnd()).blockNumber()
        cursor.beginEditBlock()
        for bn in range(start_block, end_block + 1):
            block = doc.findBlockByNumber(bn)
            block_cursor = QTextCursor(block)
            block_cursor.movePosition(QTextCursor.StartOfBlock)
            block_cursor.insertText(pad)
        cursor.endEditBlock()

    def dedent_selection(self):
        cursor = self.textCursor()
        doc = self.document()
        width = self.settings.get("tab_width", 4)
        start_block = doc.findBlock(cursor.selectionStart()).blockNumber()
        end_block = doc.findBlock(cursor.selectionEnd()).blockNumber()
        cursor.beginEditBlock()
        for bn in range(start_block, end_block + 1):
            block = doc.findBlockByNumber(bn)
            text = block.text()
            strip_n = 0
            for ch in text[:width]:
                if ch == " ":
                    strip_n += 1
                elif ch == "\t":
                    strip_n += 1
                    break
                else:
                    break
            if strip_n:
                block_cursor = QTextCursor(block)
                block_cursor.movePosition(QTextCursor.StartOfBlock)
                block_cursor.movePosition(QTextCursor.Right, QTextCursor.KeepAnchor, strip_n)
                block_cursor.removeSelectedText()
        cursor.endEditBlock()

    def goto_line(self, parent=None):
        max_lines = self.blockCount()
        line, ok = QInputDialog.getInt(parent or self, "Go to Line",
                                        f"Line number (1-{max_lines}):", 1, 1, max_lines)
        if ok:
            block = self.document().findBlockByNumber(line - 1)
            self.setTextCursor(QTextCursor(block))
            self.ensureCursorVisible()




class FindReplaceDialog(QDialog):
    def __init__(self, get_editor, parent=None):
        super().__init__(parent)
        self.get_editor = get_editor
        self.setWindowTitle("Find & Replace")
        self.setMinimumWidth(380)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 18, 20, 18)
        layout.setSpacing(10)

        form = QFormLayout()
        self.find_edit = QLineEdit()
        self.replace_edit = QLineEdit()
        form.addRow("Find:", self.find_edit)
        form.addRow("Replace:", self.replace_edit)
        self.case_box = QCheckBox("Case sensitive")
        form.addRow("", self.case_box)
        layout.addLayout(form)

        btn_row = QHBoxLayout()
        find_btn = QPushButton("Find Next")
        find_btn.clicked.connect(self.find_next)
        replace_btn = QPushButton("Replace")
        replace_btn.setObjectName("secondary")
        replace_btn.clicked.connect(self.replace_one)
        replace_all_btn = QPushButton("Replace All")
        replace_all_btn.setObjectName("secondary")
        replace_all_btn.clicked.connect(self.replace_all)
        btn_row.addWidget(find_btn)
        btn_row.addWidget(replace_btn)
        btn_row.addWidget(replace_all_btn)
        layout.addLayout(btn_row)

        self.find_edit.returnPressed.connect(self.find_next)

    def _flags(self):
        flags = QTextDocument.FindFlags()
        if self.case_box.isChecked():
            flags |= QTextDocument.FindCaseSensitively
        return flags

    def find_next(self):
        editor = self.get_editor()
        text = self.find_edit.text()
        if not editor or not text:
            return
        if not editor.find(text, self._flags()):
            cursor = editor.textCursor()
            cursor.movePosition(QTextCursor.Start)
            editor.setTextCursor(cursor)
            editor.find(text, self._flags())

    def replace_one(self):
        editor = self.get_editor()
        if not editor:
            return
        cursor = editor.textCursor()
        if cursor.hasSelection():
            cursor.insertText(self.replace_edit.text())
        self.find_next()

    def replace_all(self):
        editor = self.get_editor()
        find_text = self.find_edit.text()
        if not editor or not find_text:
            return
        cursor = editor.textCursor()
        cursor.movePosition(QTextCursor.Start)
        editor.setTextCursor(cursor)
        count = 0
        while editor.find(find_text, self._flags()):
            c = editor.textCursor()
            c.insertText(self.replace_edit.text())
            count += 1
        QMessageBox.information(self, "Replace All", f"Replaced {count} occurrence(s).")




class SettingsDialog(QDialog):
    settings_applied = Signal(dict)

    def __init__(self, current_settings, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Preferences")
        self.setMinimumWidth(420)
        self.settings = dict(current_settings)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(14)

        title = QLabel("Preferences")
        title.setObjectName("dialogTitle")
        layout.addWidget(title)
        hint = QLabel("Press Ctrl+, anytime to reopen this dialog.")
        hint.setObjectName("hint")
        layout.addWidget(hint)

        form = QFormLayout()
        form.setSpacing(12)

        self.theme_box = QComboBox()
        self.theme_box.addItems(list(THEMES.keys()))
        self.theme_box.setCurrentText(self.settings["theme"])
        form.addRow("Theme", self.theme_box)

        self.font_box = QFontComboBox()
        self.font_box.setCurrentFont(QFont(self.settings["font_family"]))
        form.addRow("Font family", self.font_box)

        self.size_box = QSpinBox()
        self.size_box.setRange(8, 32)
        self.size_box.setValue(self.settings["font_size"])
        form.addRow("Font size", self.size_box)

        self.tab_box = QSpinBox()
        self.tab_box.setRange(1, 8)
        self.tab_box.setValue(self.settings["tab_width"])
        form.addRow("Tab width", self.tab_box)

        self.wrap_box = QCheckBox("Wrap long lines")
        self.wrap_box.setChecked(self.settings["word_wrap"])
        form.addRow("", self.wrap_box)

        self.smooth_box = QCheckBox("Smooth typing (animated scrolling)")
        self.smooth_box.setChecked(self.settings["smooth_typing"])
        self.smooth_box.setToolTip(
            "Animates scrolling caused by the mouse wheel and Page Up/Down\n"
            "so the view glides instead of jumping, for a smoother feel while typing."
        )
        form.addRow("", self.smooth_box)

        layout.addLayout(form)

        btn_row = QHBoxLayout()
        btn_row.addStretch()
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setObjectName("secondary")
        cancel_btn.clicked.connect(self.reject)
        apply_btn = QPushButton("Apply")
        apply_btn.clicked.connect(self.on_apply)
        btn_row.addWidget(cancel_btn)
        btn_row.addWidget(apply_btn)
        layout.addLayout(btn_row)

        self.theme_box.currentTextChanged.connect(self._live_preview)

    def _live_preview(self, theme_name):
        preview = dict(self.settings)
        preview["theme"] = theme_name
        self.settings_applied.emit(preview)

    def on_apply(self):
        self.settings = {
            "theme": self.theme_box.currentText(),
            "font_family": self.font_box.currentFont().family(),
            "font_size": self.size_box.value(),
            "tab_width": self.tab_box.value(),
            "word_wrap": self.wrap_box.isChecked(),
            "smooth_typing": self.smooth_box.isChecked(),
        }
        self.settings_applied.emit(self.settings)
        self.accept()




class ConsoleOutput(QPlainTextEdit):
    """A terminal-like output widget. Program output is appended normally;
    while a process is running, the widget becomes editable and you type
    directly after the last printed prompt (like `set /p x=` or `scanf`) --
    pressing Enter submits that line as stdin. Already-printed history stays
    protected from edits even while interactive."""

    line_entered = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setReadOnly(True)
        self.setMaximumBlockCount(4000)
        self.setUndoRedoEnabled(False)
        self.input_start = 0

    def append_output(self, text):
        cursor = self.textCursor()
        cursor.movePosition(QTextCursor.End)
        cursor.insertText(text)
        self.input_start = cursor.position()
        self.setTextCursor(cursor)
        self.ensureCursorVisible()

    def begin_interactive(self):
        self.setReadOnly(False)
        cursor = self.textCursor()
        cursor.movePosition(QTextCursor.End)
        self.input_start = cursor.position()
        self.setTextCursor(cursor)
        self.setFocus()

    def end_interactive(self):
        self.setReadOnly(True)

    def keyPressEvent(self, event):
        if self.isReadOnly():
            super().keyPressEvent(event)
            return

        key = event.key()
        cursor = self.textCursor()

        if key in (Qt.Key_Return, Qt.Key_Enter):
            self._submit_line()
            return

        is_edit_key = (
            key in (Qt.Key_Backspace, Qt.Key_Delete)
            or event.matches(QKeySequence.Paste)
            or event.matches(QKeySequence.Cut)
            or bool(event.text())
        )
        if is_edit_key:
            if cursor.hasSelection():
                if cursor.selectionStart() < self.input_start:
                    cursor.setPosition(self.input_start)
                    cursor.movePosition(QTextCursor.End, QTextCursor.KeepAnchor)
                    self.setTextCursor(cursor)
            elif cursor.position() < self.input_start:
                cursor.movePosition(QTextCursor.End)
                self.setTextCursor(cursor)
            if key == Qt.Key_Backspace and self.textCursor().position() <= self.input_start:
                return

        super().keyPressEvent(event)

    def _submit_line(self):
        cursor = self.textCursor()
        cursor.movePosition(QTextCursor.End)
        cursor.setPosition(self.input_start, QTextCursor.KeepAnchor)
        line = cursor.selectedText().replace("\u2029", "\n")

        end_cursor = self.textCursor()
        end_cursor.movePosition(QTextCursor.End)
        end_cursor.insertText("\n")
        self.setTextCursor(end_cursor)
        self.input_start = end_cursor.position()
        self.ensureCursorVisible()
        self.line_entered.emit(line)




class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(APP_NAME)
        self.resize(1250, 800)

        self.settings = self.load_settings()
        self.process = None
        self.find_dialog = None

        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(True)
        self.tabs.setMovable(True)
        self.tabs.tabCloseRequested.connect(self.close_tab)
        self.tabs.currentChanged.connect(self.update_status)
        self.setCentralWidget(self.tabs)

        self.build_console_dock()

        self.status = QStatusBar()
        self.setStatusBar(self.status)
        self.pos_label = QLabel("Ln 1, Col 1")
        self.lang_label = QLabel("Python")
        self.status.addPermanentWidget(self.lang_label)
        self.status.addPermanentWidget(self.pos_label)

        self.build_menu()
        self.build_toolbar()

        QShortcut(QKeySequence("Ctrl+,"), self, activated=self.open_settings)

        self.new_tab()
        self.apply_theme()


    def build_console_dock(self):
        container = QWidget()
        v = QVBoxLayout(container)
        v.setContentsMargins(0, 0, 0, 0)
        v.setSpacing(0)

        hint = QLabel("Type directly below while a program is running — just like a real terminal.")
        hint.setObjectName("hint")
        hint.setContentsMargins(10, 6, 10, 6)
        v.addWidget(hint)

        self.output = ConsoleOutput()
        self.output.line_entered.connect(self.send_stdin_line)
        v.addWidget(self.output)

        self.console_dock = QDockWidget("Console")
        self.console_dock.setWidget(container)
        self.addDockWidget(Qt.BottomDockWidgetArea, self.console_dock)
        self.console_dock.hide()


    def load_settings(self):
        s = dict(DEFAULT_SETTINGS)
        try:
            if SETTINGS_FILE.exists():
                s.update(json.loads(SETTINGS_FILE.read_text()))
        except Exception:
            pass
        if s["theme"] not in THEMES:
            s["theme"] = "Dark+"
        return s

    def save_settings(self):
        try:
            SETTINGS_DIR.mkdir(parents=True, exist_ok=True)
            SETTINGS_FILE.write_text(json.dumps(self.settings, indent=2))
        except Exception:
            pass


    def build_menu(self):
        m = self.menuBar()

        file_menu = m.addMenu("&File")
        self._act(file_menu, "New", "Ctrl+N", self.new_tab)
        self._act(file_menu, "Open...", "Ctrl+O", self.open_file)
        self._act(file_menu, "Save", "Ctrl+S", self.save_file)
        self._act(file_menu, "Save As...", "Ctrl+Shift+S", self.save_file_as)
        file_menu.addSeparator()
        self._act(file_menu, "Exit", "Ctrl+Q", self.close)

        edit_menu = m.addMenu("&Edit")
        self._act(edit_menu, "Undo", "Ctrl+Z", lambda: self._on_editor(lambda e: e.undo()))
        self._act(edit_menu, "Redo", "Ctrl+Y", lambda: self._on_editor(lambda e: e.redo()))
        edit_menu.addSeparator()
        self._act(edit_menu, "Cut", "Ctrl+X", lambda: self._on_editor(lambda e: e.cut()))
        self._act(edit_menu, "Copy", "Ctrl+C", lambda: self._on_editor(lambda e: e.copy()))
        self._act(edit_menu, "Paste", "Ctrl+V", lambda: self._on_editor(lambda e: e.paste()))
        edit_menu.addSeparator()
        self._act(edit_menu, "Duplicate Line", "Ctrl+D", lambda: self._on_editor(lambda e: e.duplicate_line()))
        self._act(edit_menu, "Delete Line", "Ctrl+Shift+K", lambda: self._on_editor(lambda e: e.delete_line()))
        self._act(edit_menu, "Move Line Up", "Alt+Up", lambda: self._on_editor(lambda e: e.move_line_up()))
        self._act(edit_menu, "Move Line Down", "Alt+Down", lambda: self._on_editor(lambda e: e.move_line_down()))
        self._act(edit_menu, "Select Line", "Ctrl+L", lambda: self._on_editor(lambda e: e.select_line()))
        self._act(edit_menu, "Toggle Comment", "Ctrl+/", lambda: self._on_editor(lambda e: e.toggle_comment()))
        self._act(edit_menu, "Indent", "Ctrl+]", lambda: self._on_editor(lambda e: e.indent_selection()))
        self._act(edit_menu, "Dedent", "Ctrl+[", lambda: self._on_editor(lambda e: e.dedent_selection()))
        edit_menu.addSeparator()
        self._act(edit_menu, "Find && Replace...", "Ctrl+F", self.open_find)
        self._act(edit_menu, "Find && Replace (Replace focus)...", "Ctrl+H", self.open_find)
        self._act(edit_menu, "Go to Line...", "Ctrl+G", self.open_goto_line)
        edit_menu.addSeparator()
        self._act(edit_menu, "Preferences...", "Ctrl+,", self.open_settings)

        view_menu = m.addMenu("&View")
        theme_menu = view_menu.addMenu("Theme")
        for name in THEMES:
            self._act(theme_menu, name, None, lambda checked=False, n=name: self.quick_set_theme(n))
        view_menu.addSeparator()
        self._act(view_menu, "Toggle Console", "Ctrl+`", self.toggle_console)

        lang_menu = m.addMenu("&Language")
        self.lang_group = QActionGroup(self)
        self.lang_group.setExclusive(True)
        self.lang_actions = {}
        for name in LANGUAGES:
            action = QAction(name, self, checkable=True)
            action.triggered.connect(lambda checked=False, n=name: self.set_current_language(n))
            self.lang_group.addAction(action)
            lang_menu.addAction(action)
            self.lang_actions[name] = action
        self.lang_actions["Python"].setChecked(True)

        run_menu = m.addMenu("&Run")
        self._act(run_menu, "Run Current File", "F5", self.run_current_file)
        self._act(run_menu, "Stop", "Shift+F5", self.stop_run)

    def _act(self, menu, text, shortcut, slot):
        action = QAction(text, self)
        if shortcut:
            action.setShortcut(QKeySequence(shortcut))
        action.triggered.connect(slot)
        menu.addAction(action)
        return action

    def _on_editor(self, fn):
        editor = self.current_editor()
        if editor is not None:
            fn(editor)

    def build_toolbar(self):
        tb = QToolBar("Main")
        tb.setMovable(False)
        self.addToolBar(tb)
        tb.addAction("New", self.new_tab)
        tb.addAction("Open", self.open_file)
        tb.addAction("Save", self.save_file)
        tb.addSeparator()
        tb.addAction("Run ▶", self.run_current_file)
        tb.addSeparator()
        tb.addAction("Preferences ⚙", self.open_settings)


    def current_editor(self) -> CodeEditor:
        return self.tabs.currentWidget()

    def new_tab(self, file_path=None, content="", language="Python"):
        colors = THEMES[self.settings["theme"]]
        editor = CodeEditor(colors, self.settings, language=language)
        editor.setPlainText(content)
        editor.file_path = file_path
        editor.textChanged.connect(lambda e=editor: self.mark_modified(e))
        editor.cursorPositionChanged.connect(self.update_status)
        title = os.path.basename(file_path) if file_path else "untitled"
        idx = self.tabs.addTab(editor, title)
        self.tabs.setCurrentIndex(idx)
        editor.modified = False
        self.update_status()
        return editor

    def mark_modified(self, editor):
        editor.modified = True
        idx = self.tabs.indexOf(editor)
        title = self.tabs.tabText(idx)
        if not title.endswith("*"):
            self.tabs.setTabText(idx, title + "*")

    def close_tab(self, index):
        editor = self.tabs.widget(index)
        if getattr(editor, "modified", False):
            resp = QMessageBox.question(
                self, "Unsaved changes",
                f"Save changes to {self.tabs.tabText(index).rstrip('*')}?",
                QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel,
            )
            if resp == QMessageBox.Cancel:
                return
            if resp == QMessageBox.Yes:
                self.tabs.setCurrentIndex(index)
                self.save_file()
        self.tabs.removeTab(index)
        if self.tabs.count() == 0:
            self.new_tab()


    def open_file(self):
        path, _ = QFileDialog.getOpenFileName(self, "Open File", "", "All Files (*)")
        if not path:
            return
        try:
            content = Path(path).read_text(encoding="utf-8")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not open file:\n{e}")
            return
        ext = Path(path).suffix.lower()
        language = EXT_TO_LANGUAGE.get(ext, "Plain Text")
        editor = self.new_tab(file_path=path, content=content, language=language)
        editor.modified = False

    def save_file(self):
        editor = self.current_editor()
        if editor is None:
            return
        if not getattr(editor, "file_path", None):
            return self.save_file_as()
        try:
            Path(editor.file_path).write_text(editor.toPlainText(), encoding="utf-8")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not save file:\n{e}")
            return
        editor.modified = False
        idx = self.tabs.indexOf(editor)
        self.tabs.setTabText(idx, os.path.basename(editor.file_path))

    def save_file_as(self):
        editor = self.current_editor()
        if editor is None:
            return
        default_ext = DEFAULT_EXTENSION.get(editor.language, ".txt")
        path, _ = QFileDialog.getSaveFileName(
            self, "Save As", f"untitled{default_ext}",
            f"{editor.language} Files (*{default_ext});;All Files (*)"
        )
        if not path:
            return
        editor.file_path = path
        self.save_file()


    def open_settings(self):
        dlg = SettingsDialog(self.settings, self)
        dlg.settings_applied.connect(self.on_settings_applied)
        if dlg.exec() == QDialog.Rejected:
            self.apply_theme()

    def on_settings_applied(self, new_settings):
        self.settings.update(new_settings)
        self.apply_theme()
        self.apply_editor_settings()
        self.save_settings()

    def quick_set_theme(self, name):
        self.settings["theme"] = name
        self.apply_theme()
        self.save_settings()

    def apply_theme(self):
        colors = THEMES[self.settings["theme"]]
        app = QApplication.instance()
        app.setStyleSheet(build_stylesheet(colors))
        for i in range(self.tabs.count()):
            self.tabs.widget(i).apply_theme(colors)
        self.output.setStyleSheet(f"background-color:{colors['editor_bg']}; color:{colors['fg']};")

    def apply_editor_settings(self):
        for i in range(self.tabs.count()):
            self.tabs.widget(i).apply_settings(self.settings)


    def set_current_language(self, name):
        editor = self.current_editor()
        if editor is None:
            return
        editor.set_language(name)
        self.lang_label.setText(name)


    def open_find(self):
        if self.find_dialog is None:
            self.find_dialog = FindReplaceDialog(self.current_editor, self)
        self.find_dialog.show()
        self.find_dialog.raise_()
        self.find_dialog.find_edit.setFocus()
        self.find_dialog.find_edit.selectAll()

    def open_goto_line(self):
        editor = self.current_editor()
        if editor is not None:
            editor.goto_line(self)


    def run_current_file(self):
        editor = self.current_editor()
        if editor is None:
            return
        if not getattr(editor, "file_path", None):
            self.save_file_as()
            if not getattr(editor, "file_path", None):
                return
        else:
            self.save_file()

        path = editor.file_path
        language = editor.language
        workdir = os.path.dirname(path) or "."

        self.console_dock.show()
        self.output.clear()
        self.output.end_interactive()

        if language == "Python":
            self.output.append_output(f"$ python \"{path}\"\n\n")
            self._start_process(sys.executable, [path], cwd=workdir, interactive=True)

        elif language in ("C", "C++"):
            compiler = "gcc" if language == "C" else "g++"
            if shutil.which(compiler) is None:
                self.output.append_output(
                    f"[error] '{compiler}' was not found on PATH.\n"
                    f"Install a C/C++ compiler (e.g. 'sudo apt install build-essential', "
                    f"or MinGW on Windows) to run {language} files.\n"
                )
                return
            exe_path = os.path.join(
                tempfile.gettempdir(),
                Path(path).stem + "_pyforge" + (".exe" if os.name == "nt" else "")
            )
            self.output.append_output(f"$ {compiler} \"{path}\" -o \"{exe_path}\"\n\n")
            self._start_process(
                compiler, [path, "-o", exe_path], cwd=workdir, interactive=False,
                on_finished=lambda code, exe=exe_path: self._after_compile(code, exe)
            )

        elif language == "C#":
            if shutil.which("mcs"):
                exe_path = os.path.join(tempfile.gettempdir(), Path(path).stem + "_pyforge.exe")
                self.output.append_output(f"$ mcs \"{path}\" -out:\"{exe_path}\"\n\n")
                self._start_process(
                    "mcs", [path, f"-out:{exe_path}"], cwd=workdir, interactive=False,
                    on_finished=lambda code, exe=exe_path: self._after_compile(code, exe, runner="mono")
                )
            elif shutil.which("csc"):
                exe_path = os.path.join(tempfile.gettempdir(), Path(path).stem + "_pyforge.exe")
                self.output.append_output(f"$ csc \"{path}\" /out:\"{exe_path}\"\n\n")
                self._start_process(
                    "csc", [path, f"/out:{exe_path}"], cwd=workdir, interactive=False,
                    on_finished=lambda code, exe=exe_path: self._after_compile(code, exe)
                )
            else:
                self.output.append_output(
                    "[error] No C# compiler found (looked for 'mcs' or 'csc').\n"
                    "Install Mono (provides 'mcs') or the .NET SDK to run C# files.\n"
                )

        elif language == "Batch":
            if os.name == "nt":
                self.output.append_output(f"$ cmd /c \"{path}\"\n\n")
                self._start_process("cmd.exe", ["/c", path], cwd=workdir, interactive=True)
            else:
                self.output.append_output(
                    "[info] Batch (.bat/.cmd) scripts only run on Windows via cmd.exe.\n"
                    "This machine isn't Windows, so execution was skipped.\n"
                )
        else:
            self.output.append_output(f"[info] Running isn't supported for {language} yet.\n")

    def _after_compile(self, exit_code, exe_path, runner=None):
        if exit_code != 0:
            self.output.append_output(f"\n[compile failed, exit code {exit_code}]\n")
            self.output.end_interactive()
            return
        if runner == "mono":
            self.output.append_output(f"\n$ mono \"{exe_path}\"\n\n")
            self._start_process("mono", [exe_path], interactive=True)
        else:
            self.output.append_output(f"\n$ \"{exe_path}\"\n\n")
            self._start_process(exe_path, [], interactive=True)

    def _start_process(self, program, args, cwd=None, on_finished=None, interactive=False):
        if self.process:
            try:
                self.process.kill()
            except Exception:
                pass
        proc = QProcess(self)
        proc.setProcessChannelMode(QProcess.MergedChannels)
        if cwd:
            proc.setWorkingDirectory(cwd)
        proc.readyReadStandardOutput.connect(lambda p=proc: self._on_proc_output(p))
        if on_finished:
            proc.finished.connect(lambda code, status, cb=on_finished: cb(code))
        else:
            proc.finished.connect(self._on_default_finished)
        proc.start(program, args)
        self.process = proc
        if interactive:
            self.output.begin_interactive()
        else:
            self.output.end_interactive()

    def _on_proc_output(self, proc):
        data = bytes(proc.readAllStandardOutput()).decode(errors="replace")
        if data:
            self.output.append_output(data)

    def _on_default_finished(self, code, status=None):
        self.output.append_output(f"\n[process finished with exit code {code}]\n")
        self.output.end_interactive()

    def send_stdin_line(self, line):
        if self.process and self.process.state() == QProcess.Running:
            self.process.write((line + "\n").encode())

    def stop_run(self):
        if self.process:
            self.process.kill()
        self.output.end_interactive()

    def toggle_console(self):
        self.console_dock.setVisible(not self.console_dock.isVisible())


    def update_status(self):
        editor = self.current_editor()
        if editor is None:
            return
        cursor = editor.textCursor()
        self.pos_label.setText(f"Ln {cursor.blockNumber() + 1}, Col {cursor.columnNumber() + 1}")
        self.lang_label.setText(editor.language)
        action = self.lang_actions.get(editor.language)
        if action is not None:
            action.blockSignals(True)
            action.setChecked(True)
            action.blockSignals(False)

    def closeEvent(self, event):
        for i in range(self.tabs.count()):
            editor = self.tabs.widget(i)
            if getattr(editor, "modified", False):
                self.tabs.setCurrentIndex(i)
                resp = QMessageBox.question(
                    self, "Unsaved changes",
                    f"Save changes to {self.tabs.tabText(i).rstrip('*')}?",
                    QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel,
                )
                if resp == QMessageBox.Cancel:
                    event.ignore()
                    return
                if resp == QMessageBox.Yes:
                    self.save_file()
        self.save_settings()
        event.accept()


def main():
    app = QApplication(sys.argv)
    app.setStyle(QStyleFactory.create("Fusion"))
    app.setApplicationName(APP_NAME)
    win = MainWindow()
    win.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()