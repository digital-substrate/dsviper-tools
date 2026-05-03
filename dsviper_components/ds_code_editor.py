"""DSCodeEditor — Python code editor widget with syntax highlighting, line numbers,
find/replace, auto-completion, and output panel.

Transposed from ge-qml CodeEditor.qml to Qt Widgets.
"""
from __future__ import annotations

import re

from PySide6.QtCore import Qt, QSize, QRect, QKeyCombination
from PySide6.QtGui import (
    QColor, QPainter, QTextCursor, QAction, QIcon,
    QTextCharFormat, QPalette, QFont, QFontDatabase, QFontInfo, QGuiApplication
)
from PySide6.QtWidgets import (
    QWidget, QPlainTextEdit, QTextEdit, QVBoxLayout, QHBoxLayout,
    QSplitter, QToolBar, QToolButton, QLineEdit, QLabel, QPushButton,
    QMenu, QInputDialog, QFileDialog
)

from dsviper_components.python_editor_model import PythonEditorModel
from dsviper_components.syntax_highlighter import PythonHighlighter, _COLORS

import resources_rc  # noqa: F401  — register Qt resource icons


# ---------------------------------------------------------------------------
# Line number area (painted alongside _CodeArea)
# ---------------------------------------------------------------------------

class _LineNumberArea(QWidget):
    def __init__(self, editor: _CodeArea):
        super().__init__(editor)
        self._editor = editor

    def sizeHint(self):
        return QSize(self._editor.line_number_area_width(), 0)

    def paintEvent(self, event):
        self._editor.line_number_area_paint_event(event)


# ---------------------------------------------------------------------------
# Font — prefer modern monospace fonts, fallback to system default
# ---------------------------------------------------------------------------

def _mono_font(pixel_size: int = 13) -> QFont:
    for family in ("Cascadia Mono", "Consolas", "SF Mono", "Menlo"):
        font = QFont(family)
        if QFontInfo(font).exactMatch():
            font.setPixelSize(pixel_size)
            return font
    font = QFontDatabase.systemFont(QFontDatabase.SystemFont.FixedFont)
    font.setPixelSize(pixel_size)
    return font

# ---------------------------------------------------------------------------
# Code area — QPlainTextEdit with line numbers, current-line highlight, tab
# ---------------------------------------------------------------------------

class _CodeArea(QPlainTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._model: PythonEditorModel | None = None

        # Mono font
        self.setFont(_mono_font())

        # Dark theme
        palette = self.palette()
        palette.setColor(QPalette.ColorRole.Base, QColor(_COLORS["TextBackground"]))
        palette.setColor(QPalette.ColorRole.Text, QColor(_COLORS["TextPlain"]))
        palette.setColor(QPalette.ColorRole.Highlight, QColor(_COLORS["TextSelection"]))
        palette.setColor(QPalette.ColorRole.HighlightedText, QColor(_COLORS["TextPlain"]))
        self.setPalette(palette)

        self.setLineWrapMode(QPlainTextEdit.LineWrapMode.NoWrap)
        self.setTabStopDistance(self.fontMetrics().horizontalAdvance(' ') * 4)

        # Line number area
        self._line_number_area = _LineNumberArea(self)
        self.blockCountChanged.connect(self._update_line_number_area_width)
        self.updateRequest.connect(self._update_line_number_area)
        self.cursorPositionChanged.connect(self._highlight_current_line)
        self._update_line_number_area_width(0)
        self._highlight_current_line()

        # Syntax highlighter
        self._highlighter = PythonHighlighter(self.document())

    def set_model(self, model: PythonEditorModel):
        self._model = model

    # --- Line numbers ---

    def line_number_area_width(self) -> int:
        digits = max(1, len(str(self.blockCount())))
        return 10 + self.fontMetrics().horizontalAdvance('9') * digits

    def _update_line_number_area_width(self, _):
        self.setViewportMargins(self.line_number_area_width(), 0, 0, 0)

    def _update_line_number_area(self, rect, dy):
        if dy:
            self._line_number_area.scroll(0, dy)
        else:
            self._line_number_area.update(0, rect.y(), self._line_number_area.width(), rect.height())
        if rect.contains(self.viewport().rect()):
            self._update_line_number_area_width(0)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        cr = self.contentsRect()
        self._line_number_area.setGeometry(QRect(cr.left(), cr.top(), self.line_number_area_width(), cr.height()))

    def line_number_area_paint_event(self, event):
        painter = QPainter(self._line_number_area)
        painter.fillRect(event.rect(), QColor("#25262b"))

        block = self.firstVisibleBlock()
        block_number = block.blockNumber()
        top = round(self.blockBoundingGeometry(block).translated(self.contentOffset()).top())
        bottom = top + round(self.blockBoundingRect(block).height())

        current_line = self.textCursor().blockNumber()

        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                number = str(block_number + 1)
                if block_number == current_line:
                    painter.setPen(QColor(_COLORS["TextPlain"]))
                else:
                    painter.setPen(QColor(_COLORS["TextComment"]))
                painter.drawText(0, top, self._line_number_area.width() - 6,
                                 self.fontMetrics().height(), Qt.AlignmentFlag.AlignRight, number)

            block = block.next()
            top = bottom
            bottom = top + round(self.blockBoundingRect(block).height())
            block_number += 1

    # --- Current line highlight ---

    def _highlight_current_line(self):
        selections = []
        if not self.isReadOnly():
            selection = QTextEdit.ExtraSelection()
            line_color = QColor("#2a2d35")
            selection.format.setBackground(line_color)
            selection.format.setProperty(QTextCharFormat.Property.FullWidthSelection, True)
            selection.cursor = self.textCursor()
            selection.cursor.clearSelection()
            selections.append(selection)
        self.setExtraSelections(selections)

    # --- Tab / completion ---

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Tab and not event.modifiers():
            self._handle_tab()
            return
        if event.key() == Qt.Key.Key_Backtab:
            self._shift_left()
            return
        super().keyPressEvent(event)

    def _handle_tab(self):
        if not self._model:
            self._insert_spaces()
            return

        cursor = self.textCursor()
        pos = cursor.position()
        text = self.toPlainText()
        line_start = text.rfind('\n', 0, pos) + 1
        before = text[line_start:pos].lstrip()

        if not before:
            self._insert_spaces()
            return

        result = self._model.complete(text, pos)
        if not result["completions"]:
            self._insert_spaces()
        elif result["completion"] and result["completion"] != result["context"]:
            to_insert = result["completion"][len(result["context"]):]
            cursor.insertText(to_insert)
            if len(result["completions"]) > 1:
                char_width = self.fontMetrics().horizontalAdvance('m')
                chars_per_line = max(40, self.viewport().width() // char_width)
                self._model.set_completion_output(result["completions"], chars_per_line)
        elif len(result["completions"]) > 1:
            char_width = self.fontMetrics().horizontalAdvance('m')
            chars_per_line = max(40, self.viewport().width() // char_width)
            self._model.set_completion_output(result["completions"], chars_per_line)

    def _insert_spaces(self):
        self.textCursor().insertText("    ")

    # --- Edit actions (transposed from CodeEditorLogic.js) ---

    def expression_under_cursor(self) -> str:
        cursor = self.textCursor()
        if cursor.hasSelection():
            return cursor.selectedText().strip()
        pos = cursor.position()
        text = self.toPlainText()
        start = end = pos
        while start > 0 and (text[start - 1].isalnum() or text[start - 1] in '_.'):
            start -= 1
        while end < len(text) and (text[end].isalnum() or text[end] in '_.'):
            end += 1
        return text[start:end]

    def comment_selection(self):
        cursor = self.textCursor()
        text = self.toPlainText()
        r = self._line_range(text, cursor.selectionStart(), cursor.selectionEnd())
        block = text[r[0]:r[1]]
        lines = block.split('\n')
        all_commented = all(line.startswith('#') for line in lines if line.strip())
        if all_commented:
            result = '\n'.join(line[1:] if line.startswith('#') else line for line in lines)
        else:
            result = '\n'.join('#' + line for line in lines)
        cursor.setPosition(r[0])
        cursor.setPosition(r[1], QTextCursor.MoveMode.KeepAnchor)
        cursor.insertText(result)
        cursor.setPosition(r[0])
        cursor.setPosition(r[0] + len(result), QTextCursor.MoveMode.KeepAnchor)
        self.setTextCursor(cursor)

    def shift_right(self):
        cursor = self.textCursor()
        text = self.toPlainText()
        r = self._line_range(text, cursor.selectionStart(), cursor.selectionEnd())
        block = text[r[0]:r[1]]
        result = '\n'.join('    ' + line for line in block.split('\n'))
        cursor.setPosition(r[0])
        cursor.setPosition(r[1], QTextCursor.MoveMode.KeepAnchor)
        cursor.insertText(result)
        cursor.setPosition(r[0])
        cursor.setPosition(r[0] + len(result), QTextCursor.MoveMode.KeepAnchor)
        self.setTextCursor(cursor)

    def _shift_left(self):
        cursor = self.textCursor()
        text = self.toPlainText()
        r = self._line_range(text, cursor.selectionStart(), cursor.selectionEnd())
        block = text[r[0]:r[1]]
        result = '\n'.join(line[4:] if line.startswith('    ') else line for line in block.split('\n'))
        cursor.setPosition(r[0])
        cursor.setPosition(r[1], QTextCursor.MoveMode.KeepAnchor)
        cursor.insertText(result)
        cursor.setPosition(r[0])
        cursor.setPosition(r[0] + len(result), QTextCursor.MoveMode.KeepAnchor)
        self.setTextCursor(cursor)

    def move_line_up(self):
        cursor = self.textCursor()
        text = self.toPlainText()
        r = self._line_range(text, cursor.selectionStart(), cursor.selectionEnd())
        if r[0] == 0:
            return
        prev_line_start = text.rfind('\n', 0, r[0] - 1) + 1
        prev_line = text[prev_line_start:r[0] - 1]
        cur_block = text[r[0]:r[1]]
        cursor.setPosition(prev_line_start)
        cursor.setPosition(r[1], QTextCursor.MoveMode.KeepAnchor)
        cursor.insertText(cur_block + '\n' + prev_line)
        cursor.setPosition(prev_line_start)
        cursor.setPosition(prev_line_start + len(cur_block), QTextCursor.MoveMode.KeepAnchor)
        self.setTextCursor(cursor)

    def move_line_down(self):
        cursor = self.textCursor()
        text = self.toPlainText()
        r = self._line_range(text, cursor.selectionStart(), cursor.selectionEnd())
        if r[1] >= len(text):
            return
        next_line_end = text.find('\n', r[1] + 1)
        if next_line_end == -1:
            next_line_end = len(text)
        next_line = text[r[1] + 1:next_line_end]
        cur_block = text[r[0]:r[1]]
        cursor.setPosition(r[0])
        cursor.setPosition(next_line_end, QTextCursor.MoveMode.KeepAnchor)
        cursor.insertText(next_line + '\n' + cur_block)
        new_start = r[0] + len(next_line) + 1
        cursor.setPosition(new_start)
        cursor.setPosition(new_start + len(cur_block), QTextCursor.MoveMode.KeepAnchor)
        self.setTextCursor(cursor)

    def goto_line(self, line_number: int):
        if line_number < 1:
            return
        block = self.document().findBlockByLineNumber(line_number - 1)
        if block.isValid():
            cursor = QTextCursor(block)
            self.setTextCursor(cursor)
            self.centerCursor()
            self.setFocus()

    def parse_document_items(self) -> list[dict]:
        """Find all def/class declarations."""
        items = []
        pattern = re.compile(r'^[ \t]*(def|class)\s+(\w+)', re.MULTILINE)
        for match in pattern.finditer(self.toPlainText()):
            items.append({
                "name": match.group(2),
                "is_class": match.group(1) == "class",
                "position": match.start()
            })
        return items

    @staticmethod
    def _line_range(text: str, sel_start: int, sel_end: int) -> tuple[int, int]:
        start = text.rfind('\n', 0, sel_start) + 1
        end = text.find('\n', sel_end)
        if end == -1:
            end = len(text)
        return (start, end)

    # --- Context menu ---

    def contextMenuEvent(self, event):
        menu = self.createStandardContextMenu()
        menu.addSeparator()

        expr = self.expression_under_cursor()
        model = self._model

        if model:
            run_action = menu.addAction("Run Script")
            run_action.triggered.connect(lambda: model.eval_buffer(self.toPlainText()))

            eval_action = menu.addAction("Eval Selection")
            cursor = self.textCursor()
            eval_action.triggered.connect(
                lambda: model.eval_selection(self.toPlainText(), cursor.selectionStart(), cursor.selectionEnd()))

            menu.addSeparator()

            help_action = menu.addAction("Help")
            help_action.setEnabled(bool(expr))
            help_action.triggered.connect(lambda: model.show_help(expr))

            type_action = menu.addAction("Type")
            type_action.setEnabled(bool(expr))
            type_action.triggered.connect(lambda: model.show_type(expr))

            print_action = menu.addAction("Print")
            print_action.setEnabled(bool(expr))
            print_action.triggered.connect(lambda: model.show_repr(expr))

            desc_action = menu.addAction("Description")
            desc_action.setEnabled(bool(expr))
            desc_action.triggered.connect(lambda: model.show_description(expr))

            menu.addSeparator()

            jump_action = menu.addAction("Jump to Module")
            jump_action.setEnabled(self.textCursor().hasSelection())
            jump_action.triggered.connect(lambda: model.jump_to_module(self.textCursor().selectedText()))

            items_action = menu.addAction("Document Items")
            items_action.triggered.connect(self._show_document_items_menu)

        menu.exec(event.globalPos())

    def _show_document_items_menu(self):
        items = self.parse_document_items()
        if not items:
            return
        menu = QMenu(self)
        for item in items:
            prefix = "C" if item["is_class"] else "f"
            action = menu.addAction(f"[{prefix}] {item['name']}")
            pos = item["position"]
            text = self.toPlainText()
            line_number = text[:pos].count('\n') + 1
            action.triggered.connect(lambda checked=False, ln=line_number: self.goto_line(ln))
        menu.exec(self.mapToGlobal(self.cursorRect().bottomRight()))


# ---------------------------------------------------------------------------
# Find/Replace bar
# ---------------------------------------------------------------------------

class _FindReplaceBar(QWidget):
    def __init__(self, code_area: _CodeArea, parent=None):
        super().__init__(parent)
        self._code_area = code_area
        self._matches: list[int] = []
        self._current_index = -1

        self.setVisible(False)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 4, 8, 4)
        layout.setSpacing(2)

        # Find row
        find_row = QHBoxLayout()
        self._find_field = QLineEdit()
        self._find_field.setPlaceholderText("Find...")
        self._find_field.textChanged.connect(self._do_find)
        self._find_field.returnPressed.connect(self.find_next)
        find_row.addWidget(self._find_field)

        self._match_label = QLabel("0/0")
        self._match_label.setFixedWidth(50)
        self._match_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        find_row.addWidget(self._match_label)

        prev_btn = QToolButton()
        prev_btn.setText("\u25B2")
        prev_btn.setFixedSize(24, 24)
        prev_btn.clicked.connect(self.find_previous)
        find_row.addWidget(prev_btn)

        next_btn = QToolButton()
        next_btn.setText("\u25BC")
        next_btn.setFixedSize(24, 24)
        next_btn.clicked.connect(self.find_next)
        find_row.addWidget(next_btn)

        close_btn = QToolButton()
        close_btn.setText("\u2715")
        close_btn.setFixedSize(24, 24)
        close_btn.clicked.connect(self.hide_bar)
        find_row.addWidget(close_btn)

        layout.addLayout(find_row)

        # Replace row
        self._replace_row = QWidget()
        replace_layout = QHBoxLayout(self._replace_row)
        replace_layout.setContentsMargins(0, 0, 0, 0)
        replace_layout.setSpacing(4)

        self._replace_field = QLineEdit()
        self._replace_field.setPlaceholderText("Replace...")
        replace_layout.addWidget(self._replace_field)

        replace_btn = QPushButton("Replace")
        replace_btn.setFixedHeight(24)
        replace_btn.clicked.connect(self._replace_current)
        replace_layout.addWidget(replace_btn)

        replace_all_btn = QPushButton("All")
        replace_all_btn.setFixedHeight(24)
        replace_all_btn.clicked.connect(self._replace_all)
        replace_layout.addWidget(replace_all_btn)

        self._replace_row.setVisible(False)
        layout.addWidget(self._replace_row)

    def show_find(self):
        self.setVisible(True)
        self._replace_row.setVisible(False)
        self._find_field.setFocus()
        self._find_field.selectAll()

    def show_replace(self):
        self.setVisible(True)
        self._replace_row.setVisible(True)
        self._find_field.setFocus()
        self._find_field.selectAll()

    def hide_bar(self):
        self.setVisible(False)
        self._matches.clear()
        self._current_index = -1
        self._code_area.setFocus()

    def use_selection_for_find(self):
        expr = self._code_area.expression_under_cursor()
        if expr:
            self._find_field.setText(expr)
            self.show_find()

    def _do_find(self):
        query = self._find_field.text()
        text = self._code_area.toPlainText()
        self._matches.clear()
        if query:
            idx = 0
            while True:
                pos = text.find(query, idx)
                if pos == -1:
                    break
                self._matches.append(pos)
                idx = pos + 1
        self._current_index = 0 if self._matches else -1
        self._update_label()
        if self._current_index >= 0:
            self._select_match()

    def find_next(self):
        if not self._matches:
            return
        self._current_index = (self._current_index + 1) % len(self._matches)
        self._update_label()
        self._select_match()

    def find_previous(self):
        if not self._matches:
            return
        self._current_index = (len(self._matches) + self._current_index - 1) % len(self._matches)
        self._update_label()
        self._select_match()

    def _select_match(self):
        if self._current_index < 0 or self._current_index >= len(self._matches):
            return
        pos = self._matches[self._current_index]
        query_len = len(self._find_field.text())
        cursor = self._code_area.textCursor()
        cursor.setPosition(pos)
        cursor.setPosition(pos + query_len, QTextCursor.MoveMode.KeepAnchor)
        self._code_area.setTextCursor(cursor)
        self._code_area.centerCursor()

    def _update_label(self):
        if self._matches:
            self._match_label.setText(f"{self._current_index + 1}/{len(self._matches)}")
        else:
            self._match_label.setText("0/0")

    def _replace_current(self):
        if self._current_index < 0 or self._current_index >= len(self._matches):
            return
        pos = self._matches[self._current_index]
        query = self._find_field.text()
        replacement = self._replace_field.text()
        cursor = self._code_area.textCursor()
        cursor.setPosition(pos)
        cursor.setPosition(pos + len(query), QTextCursor.MoveMode.KeepAnchor)
        cursor.insertText(replacement)
        self._do_find()

    def _replace_all(self):
        query = self._find_field.text()
        replacement = self._replace_field.text()
        if not query or not self._matches:
            return
        for pos in reversed(self._matches):
            cursor = self._code_area.textCursor()
            cursor.setPosition(pos)
            cursor.setPosition(pos + len(query), QTextCursor.MoveMode.KeepAnchor)
            cursor.insertText(replacement)
        self._do_find()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            self.hide_bar()
            return
        super().keyPressEvent(event)


# ---------------------------------------------------------------------------
# Output panel
# ---------------------------------------------------------------------------

class _OutputPanel(QPlainTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setReadOnly(True)

        self.setFont(_mono_font())

        palette = self.palette()
        palette.setColor(QPalette.ColorRole.Base, QColor(_COLORS["TextBackground"]))
        palette.setColor(QPalette.ColorRole.Text, QColor("#9ea7b8"))
        palette.setColor(QPalette.ColorRole.Highlight, QColor(_COLORS["TextSelection"]))
        palette.setColor(QPalette.ColorRole.HighlightedText, QColor(_COLORS["TextPlain"]))
        self.setPalette(palette)

        self._highlighter = PythonHighlighter(self.document())

    def set_output(self, text: str, mode: str):
        self._highlighter.mode = mode
        self.setPlainText(text)
        cursor = self.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.Start)
        self.setTextCursor(cursor)


# ---------------------------------------------------------------------------
# DSCodeEditor — Main assembled widget
# ---------------------------------------------------------------------------

class DSCodeEditor(QWidget):
    """Python code editor widget with toolbar, code area, find/replace, and output."""

    def __init__(self, model: PythonEditorModel, parent=None):
        super().__init__(parent)
        self._model = model

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Toolbar
        self._toolbar = self._create_toolbar()
        layout.addWidget(self._toolbar)

        # Find/Replace bar
        self._code_area = _CodeArea()
        self._code_area.set_model(model)
        self._find_bar = _FindReplaceBar(self._code_area)
        layout.addWidget(self._find_bar)

        # Splitter: code + output
        splitter = QSplitter(Qt.Orientation.Vertical)

        splitter.addWidget(self._code_area)

        self._output_panel = _OutputPanel()
        splitter.addWidget(self._output_panel)

        splitter.setStretchFactor(0, 3)
        splitter.setStretchFactor(1, 1)

        layout.addWidget(splitter)

        # Connect model signals
        model.output_changed.connect(self._on_output_changed)
        model.source_changed.connect(self._on_source_changed)
        model.error_line_changed.connect(self._on_error_line_changed)
        model.font_size_changed.connect(self._on_font_size_changed)

        # Load initial source
        if model.source:
            self._code_area.setPlainText(model.source)
        font = self._code_area.font()
        font.setPixelSize(model.font_size)
        self._code_area.setFont(font)
        self._output_panel.setFont(font)

        # Setup actions (used by local shortcuts and exposed for Editor menu)
        self._setup_actions()

    def _create_toolbar(self) -> QToolBar:
        tb = QToolBar()
        tb.setMovable(False)
        tb.setIconSize(QSize(22, 22))
        tb.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)

        dark = "-dark" if QGuiApplication.styleHints().colorScheme() == Qt.ColorScheme.Dark else ""

        def _icon(name: str) -> QIcon:
            return QIcon(f":/dsviper_components/images/{name}{dark}.png")

        # Title
        self._title_label = QLabel("  <b>Python Editor</b>  ")
        tb.addWidget(self._title_label)

        self._file_button = QToolButton()
        self._file_button.setText(self._model.file_name or "")
        self._file_button.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextOnly)
        self._file_button.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
        self._scripts_menu = QMenu(self._file_button)
        self._scripts_menu.aboutToShow.connect(self._populate_scripts_menu)
        self._file_button.setMenu(self._scripts_menu)
        tb.addWidget(self._file_button)

        self._model.file_name_changed.connect(lambda name: self._file_button.setText(name))

        tb.addSeparator()

        # Evaluation group
        run_action = tb.addAction(_icon("applescript"), "Run")
        run_action.setToolTip("Run Script (Ctrl+R)")
        run_action.triggered.connect(lambda: self._model.eval_buffer(self._code_area.toPlainText()))

        eval_action = tb.addAction(_icon("bolt"), "Eval")
        eval_action.setToolTip("Eval Selection (Ctrl+Return)")
        eval_action.triggered.connect(self._eval_selection)

        tb.addSeparator()

        # Information group
        help_action = tb.addAction(_icon("questionmark.circle"), "Help")
        help_action.setToolTip("Help (Ctrl+Shift+H)")
        help_action.triggered.connect(lambda: self._model.show_help(self._code_area.expression_under_cursor()))

        print_action = tb.addAction(_icon("p.circle"), "Print")
        print_action.setToolTip("Print")
        print_action.triggered.connect(lambda: self._model.show_repr(self._code_area.expression_under_cursor()))

        type_action = tb.addAction(_icon("eye.circle"), "Type")
        type_action.setToolTip("Type (Ctrl+T)")
        type_action.triggered.connect(lambda: self._model.show_type(self._code_area.expression_under_cursor()))

        desc_action = tb.addAction(_icon("eyeglasses"), "Desc")
        desc_action.setToolTip("Description")
        desc_action.triggered.connect(lambda: self._model.show_description(self._code_area.expression_under_cursor()))

        tb.addSeparator()

        # Error group
        prev_err = tb.addAction(_icon("arrow.left"), "Prev Err")
        prev_err.setToolTip("Previous Error (Ctrl+')")
        prev_err.triggered.connect(self._model.previous_error)

        next_err = tb.addAction(_icon("arrow.right"), "Next Err")
        next_err.setToolTip("Next Error (Ctrl+Shift+')")
        next_err.triggered.connect(self._model.next_error)

        return tb

    def _setup_actions(self):
        """Create all editor actions with names, shortcuts, and connections.

        These actions are used both as local shortcuts and exposed to MainWindow
        for the Editor menu via editor_actions().
        """
        ctrl = Qt.KeyboardModifier.ControlModifier
        alt = Qt.KeyboardModifier.AltModifier
        shift = Qt.KeyboardModifier.ShiftModifier

        def _action(text, shortcut, slot):
            a = QAction(text, self)
            a.setShortcut(shortcut)
            a.setShortcutContext(Qt.ShortcutContext.WidgetWithChildrenShortcut)
            a.triggered.connect(slot)
            self.addAction(a)
            return a

        # --- File operations ---
        self.open_script_action = _action(
            "Open Script", QKeyCombination(ctrl | shift, Qt.Key.Key_O), self._open_script)
        self.save_script_action = _action(
            "Save Script", QKeyCombination(ctrl, Qt.Key.Key_S),
            lambda: self._model.save_source(self._code_area.toPlainText()))

        # --- Find ---
        self.find_action = _action(
            "Find...", QKeyCombination(ctrl, Qt.Key.Key_F), self._find_bar.show_find)
        self.find_next_action = _action(
            "Find Next", QKeyCombination(ctrl, Qt.Key.Key_G), self._find_bar.find_next)
        self.find_previous_action = _action(
            "Find Previous", QKeyCombination(ctrl | shift, Qt.Key.Key_G), self._find_bar.find_previous)
        self.use_selection_for_find_action = _action(
            "Use Selection for Find", QKeyCombination(ctrl, Qt.Key.Key_E),
            self._find_bar.use_selection_for_find)
        self.find_and_replace_action = _action(
            "Find and Replace...", QKeyCombination(ctrl | alt, Qt.Key.Key_F), self._find_bar.show_replace)

        # --- Error navigation ---
        self.next_error_action = _action(
            "Jump to Next Error", QKeyCombination(ctrl, Qt.Key.Key_Apostrophe),
            self._model.next_error)
        self.previous_error_action = _action(
            "Jump to Previous Error", QKeyCombination(ctrl | shift, Qt.Key.Key_Apostrophe),
            self._model.previous_error)

        # --- Jump / Navigation ---
        self.jump_to_line_action = _action(
            "Jump to Line", QKeyCombination(ctrl, Qt.Key.Key_L), self._jump_to_line)
        self.jump_to_definition_action = _action(
            "Jump to Definition", QKeyCombination(ctrl | alt, Qt.Key.Key_J),
            self._jump_to_definition)

        # --- Execution ---
        self.run_script_action = _action(
            "Run Script", QKeyCombination(ctrl, Qt.Key.Key_R),
            lambda: self._model.eval_buffer(self._code_area.toPlainText()))
        self.eval_selection_action = _action(
            "Eval", QKeyCombination(ctrl, Qt.Key.Key_Return), self._eval_selection)

        # --- Information ---
        self.show_help_action = _action(
            "Show Help", QKeyCombination(ctrl | shift, Qt.Key.Key_H),
            lambda: self._model.show_help(self._code_area.expression_under_cursor()))
        self.show_type_action = _action(
            "Show Type", QKeyCombination(ctrl, Qt.Key.Key_T),
            lambda: self._model.show_type(self._code_area.expression_under_cursor()))
        self.show_description_action = _action(
            "Show Description", QKeyCombination(),
            lambda: self._model.show_description(self._code_area.expression_under_cursor()))

        # --- Font ---
        self.bigger_font_action = _action(
            "Bigger Font", QKeyCombination(ctrl, Qt.Key.Key_Equal), self._bigger_font)
        self.smaller_font_action = _action(
            "Smaller Font", QKeyCombination(ctrl, Qt.Key.Key_Minus), self._smaller_font)

        # --- Code formatting ---
        self.comment_selection_action = _action(
            "Comment Selection", QKeyCombination(ctrl, Qt.Key.Key_Slash),
            self._code_area.comment_selection)
        self.shift_right_action = _action(
            "Shift Right", QKeyCombination(ctrl, Qt.Key.Key_BracketRight),
            self._code_area.shift_right)
        self.shift_left_action = _action(
            "Shift Left", QKeyCombination(ctrl, Qt.Key.Key_BracketLeft),
            self._code_area._shift_left)
        self.move_line_up_action = _action(
            "Move Line Up", QKeyCombination(ctrl | alt, Qt.Key.Key_BracketLeft),
            self._code_area.move_line_up)
        self.move_line_down_action = _action(
            "Move Line Down", QKeyCombination(ctrl | alt, Qt.Key.Key_BracketRight),
            self._code_area.move_line_down)

        # --- Refresh ---
        self.refresh_syntax_action = _action(
            "Refresh Syntax Coloring", QKeyCombination(ctrl | alt, Qt.Key.Key_Return),
            self._refresh_syntax)

    # --- Slots ---

    def _eval_selection(self):
        cursor = self._code_area.textCursor()
        self._model.eval_selection(self._code_area.toPlainText(), cursor.selectionStart(), cursor.selectionEnd())

    def _on_output_changed(self, text: str, mode: str):
        self._output_panel.set_output(text, mode)

    def _on_source_changed(self, source: str):
        self._code_area.setPlainText(source)

    def _on_error_line_changed(self, line: int):
        self._code_area.goto_line(line)

    def _on_font_size_changed(self, size: int):
        font = self._code_area.font()
        font.setPixelSize(size)
        self._code_area.setFont(font)
        self._output_panel.setFont(font)

    def _bigger_font(self):
        font = self._code_area.font()
        if font.pixelSize() < 28:
            font.setPixelSize(font.pixelSize() + 1)
            self._code_area.setFont(font)
            self._output_panel.setFont(font)
            self._model.set_font_size(font.pixelSize())

    def _smaller_font(self):
        font = self._code_area.font()
        if font.pixelSize() > 8:
            font.setPixelSize(font.pixelSize() - 1)
            self._code_area.setFont(font)
            self._output_panel.setFont(font)
            self._model.set_font_size(font.pixelSize())

    def _jump_to_line(self):
        line, ok = QInputDialog.getInt(self, "Jump to Line", "Line:", 1, 1, self._code_area.blockCount())
        if ok:
            self._code_area.goto_line(line)

    def _open_script(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Open Script", self._model.scripts_folder(), "Python files (*.py)")
        if path:
            self._model.save_source(self._code_area.toPlainText())
            self._model.open_script(path)

    def _jump_to_definition(self):
        expr = self._code_area.expression_under_cursor()
        if not expr:
            return
        import re as _re
        pattern = _re.compile(r'(?:def|class)\s+' + _re.escape(expr) + r'\b')
        match = pattern.search(self._code_area.toPlainText())
        if match:
            line = self._code_area.toPlainText()[:match.start()].count('\n') + 1
            self._code_area.goto_line(line)

    def _refresh_syntax(self):
        self._code_area._highlighter.rehighlight()
        self._output_panel._highlighter.rehighlight()

    def _populate_scripts_menu(self):
        menu = self._scripts_menu
        menu.clear()
        scripts = self._model.script_list()
        folder = self._model.scripts_folder()
        for script_name in scripts:
            action = menu.addAction(script_name)
            path = f"{folder}/{script_name}"
            action.triggered.connect(
                lambda checked=False, p=path: self._switch_script(p))

    def _switch_script(self, path: str):
        self._model.save_source(self._code_area.toPlainText())
        self._model.open_script(path)
