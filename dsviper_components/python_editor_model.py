"""Python Editor Model — evaluation engine + script management.

Uses Python exec()/eval() directly — no C++ bridge needed (PySide6 advantage).
Adapted from ge-qml version for Qt Widgets.
"""
from __future__ import annotations

import io
import os
import re
import time
import traceback
import contextlib

from PySide6.QtCore import QObject, Signal, QSettings


_ASSIGNMENT_RE = re.compile(r'^\s*.+\s+(?:=|[+\-*/^|&%]=)\s+(.+)$')
_ASSERT_RE = re.compile(r'^assert\s+(.+)$')

_SETTINGS_SCRIPT_KEY = "PythonEditor/scriptName"
_SETTINGS_FONT_SIZE_KEY = "PythonEditor/fontSize"
_DEFAULT_SCRIPT = "playground"
_DEFAULT_FONT_SIZE = 13


class PythonEditorModel(QObject):
    """Evaluation engine + script management for the Python code editor.

    All execution happens in a shared __main__-like namespace so that
    definitions persist across evaluations.
    """

    output_changed = Signal(str, str)  # (output_text, output_mode)
    source_changed = Signal(str)       # new source text
    file_name_changed = Signal(str)    # new file name
    error_line_changed = Signal(int)   # line number (1-based, -1 if none)
    font_size_changed = Signal(int)    # new font size

    def __init__(self, scripts_folder: str, namespace_vars: dict | None = None, parent=None):
        super().__init__(parent)
        self._output = ""
        self._output_mode = "source"
        self._scripts_folder = scripts_folder
        self._current_path = ""
        self._source = ""
        # Shared namespace for exec/eval — persists across evaluations
        self._init_vars = dict(namespace_vars) if namespace_vars else {}
        self._namespace: dict = {"__name__": "__main__", "__builtins__": __builtins__}
        self._namespace.update(self._init_vars)
        # Error management
        self._errors: list[dict] = []  # [{line: int, file: str}]
        self._current_error = -1
        self._error_re = re.compile(r'File "([^"]+)", line (\d+)')
        # Add scripts folder to sys.path
        import sys
        if scripts_folder not in sys.path:
            sys.path.insert(0, scripts_folder)
        # Load last script
        self._load_initial_script()

    # --- Properties ---

    @property
    def output(self) -> str:
        return self._output

    @property
    def output_mode(self) -> str:
        return self._output_mode

    @property
    def source(self) -> str:
        return self._source

    @property
    def file_name(self) -> str:
        return os.path.basename(self._current_path) if self._current_path else ""

    @property
    def is_editable(self) -> bool:
        return "scripts" in self._current_path.lower() if self._current_path else False

    @property
    def error_line(self) -> int:
        """Current error line (1-based), or -1 if no error."""
        if 0 <= self._current_error < len(self._errors):
            return self._errors[self._current_error]["line"]
        return -1

    @property
    def has_error(self) -> bool:
        return len(self._errors) > 0

    # --- Font size persistence ---

    @property
    def font_size(self) -> int:
        try:
            return int(QSettings().value(_SETTINGS_FONT_SIZE_KEY, _DEFAULT_FONT_SIZE))
        except (ValueError, TypeError):
            return _DEFAULT_FONT_SIZE

    def set_font_size(self, size: int):
        QSettings().setValue(_SETTINGS_FONT_SIZE_KEY, size)
        self.font_size_changed.emit(size)

    # --- Output ---

    def _set_output(self, text: str, mode: str = "source"):
        self._output = text
        self._output_mode = mode
        self._extract_errors(text)
        self.output_changed.emit(text, mode)

    # --- Error management ---

    def _extract_errors(self, output: str):
        """Parse errors from output.

        Only collect errors from <string> (eval'd code) or the current script.
        Internal framework files are ignored.
        """
        self._errors.clear()
        self._current_error = -1
        for m in self._error_re.finditer(output):
            filepath, line_str = m.group(1), m.group(2)
            if filepath == "<string>":
                filepath = self._current_path
            elif filepath != self._current_path:
                continue
            self._errors.append({"file": filepath, "line": int(line_str)})
        if self._errors:
            self._current_error = 0
            self.error_line_changed.emit(self.error_line)

    def next_error(self):
        if self._errors:
            self._current_error = (self._current_error + 1) % len(self._errors)
            self.error_line_changed.emit(self.error_line)

    def previous_error(self):
        if self._errors:
            self._current_error = (len(self._errors) + self._current_error - 1) % len(self._errors)
            self.error_line_changed.emit(self.error_line)

    # --- Source / file management ---

    def _load_initial_script(self):
        settings = QSettings()
        name = settings.value(_SETTINGS_SCRIPT_KEY, _DEFAULT_SCRIPT)
        path = os.path.join(self._scripts_folder, f"{name}.py")
        if os.path.exists(path):
            self._load_file(path)
        else:
            playground = os.path.join(self._scripts_folder, f"{_DEFAULT_SCRIPT}.py")
            if not os.path.exists(playground):
                os.makedirs(os.path.dirname(playground), exist_ok=True)
                with open(playground, 'w') as f:
                    f.write("# playground\n")
            self._load_file(playground)

    def _load_file(self, path: str):
        self._current_path = path
        try:
            with open(path, 'r') as f:
                self._source = f.read()
        except OSError:
            self._source = ""
        self.source_changed.emit(self._source)
        self.file_name_changed.emit(self.file_name)

    def open_script(self, path: str):
        """Open a script file."""
        if not os.path.exists(path):
            return
        self._load_file(path)
        name = os.path.splitext(os.path.basename(path))[0]
        QSettings().setValue(_SETTINGS_SCRIPT_KEY, name)

    def save_source(self, source: str):
        """Save current source to file."""
        if not self._current_path or not self.is_editable:
            return
        try:
            with open(self._current_path, 'w') as f:
                f.write(source)
        except OSError as e:
            print(f"save_source error: {e}")

    def scripts_folder(self) -> str:
        return self._scripts_folder

    def script_list(self) -> list[str]:
        """Return list of .py files in the scripts folder."""
        if not os.path.isdir(self._scripts_folder):
            return []
        return sorted(f for f in os.listdir(self._scripts_folder) if f.endswith('.py'))

    # --- Core evaluation ---

    def _run(self, source: str, mode: str, output_mode: str = "source") -> bool:
        """Execute source code and capture output.

        mode: 'exec' (statements) or 'eval' (expression → show result)
        output_mode: 'source' (default), 'help', 'dsm', 'completion'
        Returns True if no error occurred.
        """
        if 'help()' in source:
            self._set_output("Interactive help is unavailable.")
            return False

        stdout_capture = io.StringIO()
        stderr_capture = io.StringIO()
        result_str = ""
        success = True

        start = time.perf_counter()
        try:
            with contextlib.redirect_stdout(stdout_capture), \
                 contextlib.redirect_stderr(stderr_capture):
                if mode == 'eval':
                    result = eval(source, self._namespace)
                    result_str = str(result)
                else:
                    exec(source, self._namespace)
        except Exception:
            import sys
            exc_type, exc_value, exc_tb = sys.exc_info()
            user_tb = exc_tb.tb_next if exc_tb else exc_tb
            lines = traceback.format_exception(exc_type, exc_value, user_tb)
            stderr_capture.write(''.join(lines))
            success = False

        elapsed = time.perf_counter() - start

        captured = stdout_capture.getvalue() + stderr_capture.getvalue()
        if mode == 'eval' and success and result_str:
            captured += result_str

        timing = f"{elapsed:.3f}s" if elapsed >= 0.001 else f"{elapsed * 1000:.1f}ms"
        if output_mode == "source" and "to_dsm(" in source:
            output_mode = "dsm"
        self._set_output(f"Run in {timing}.\n{captured}", output_mode)

        return success

    # --- Public methods ---

    def eval_buffer(self, source: str):
        """Execute entire script."""
        if not source.strip():
            return
        self._run(source, 'exec')

    def eval_selection(self, source: str, sel_start: int, sel_end: int):
        """Evaluate selection or current line."""
        if sel_start == sel_end:
            line_start = source.rfind('\n', 0, sel_start) + 1
            line_end = source.find('\n', sel_start)
            if line_end == -1:
                line_end = len(source)
            text = source[line_start:line_end]
        else:
            text = source[sel_start:sel_end]

        text = text.strip()
        if not text or text == '\n':
            return

        if text.startswith('help()'):
            self._set_output("Interactive help is unavailable.")
            return

        text = self._maybe_uncomment(text)

        lines = text.strip().split('\n')
        num_lines = len(lines)

        eval_expression = None
        if num_lines == 1:
            m = _ASSIGNMENT_RE.match(text)
            if m:
                eval_expression = m.group(1).strip()
            else:
                m = _ASSERT_RE.match(text)
                if m:
                    eval_expression = m.group(1).strip()

        if num_lines > 1:
            mode = 'exec'
        elif text.startswith(('from ', 'import ')) or eval_expression:
            mode = 'exec'
        else:
            mode = 'eval'

        if self._run(text, mode):
            if eval_expression:
                self._run(eval_expression, 'eval')

    def clear_output(self):
        self._set_output("")

    def reset_namespace(self):
        """Reinitialize the shared namespace and re-execute main_init.py."""
        self._namespace.clear()
        self._namespace.update({"__name__": "__main__", "__builtins__": __builtins__})
        self._namespace.update(self._init_vars)
        self.run_init_script()

    def set_completion_output(self, completions: list, chars_per_line: int = 80):
        """Display completions in columns."""
        if not completions:
            return
        col_width = max(len(c) for c in completions) + 2
        num_cols = max(1, chars_per_line // col_width)
        num_rows = (len(completions) + num_cols - 1) // num_cols
        lines = []
        for row in range(num_rows):
            parts = []
            for col in range(num_cols):
                idx = col * num_rows + row
                if idx < len(completions):
                    parts.append(completions[idx].ljust(col_width))
            lines.append(''.join(parts).rstrip())
        self._set_output('\n'.join(lines), 'completion')

    def run_init_script(self):
        """Execute main_init.py at startup."""
        init_path = os.path.join(self._scripts_folder, "main_init.py")
        if not os.path.exists(init_path):
            return
        try:
            with open(init_path, 'r') as f:
                source = f.read()
            self._run(source, 'exec')
        except OSError as e:
            print(f"run_init_script error: {e}")

    # --- Jump to Module ---

    def jump_to_module(self, module_name: str):
        """Search sys.path for module_name.py and open it."""
        if not module_name:
            return
        import sys
        name = module_name.strip()
        candidates = [
            name + '.py',
            name.replace('.', os.sep) + '.py',
            os.path.join(name.replace('.', os.sep), '__init__.py'),
        ]
        for folder in sys.path:
            for candidate in candidates:
                path = os.path.join(folder, candidate)
                if os.path.isfile(path):
                    self.save_source(self._source)
                    self._load_file(path)
                    return

    # --- Introspection ---

    def show_help(self, expression: str):
        if not expression:
            return
        import keyword
        if keyword.iskeyword(expression):
            expression = f"'{expression}'"
        self._run(f"help({expression})", 'exec', output_mode='help')

    def show_type(self, expression: str):
        if expression:
            self._run(f"type({expression})", 'eval')

    def show_repr(self, expression: str):
        if expression:
            self._run(f"print({expression})", 'exec', output_mode='help')

    def show_description(self, expression: str):
        if expression:
            self._run(f"{expression}.vpr_description", 'eval')

    # --- Auto-completion ---

    def complete(self, source: str, cursor_pos: int) -> dict:
        """Attempt auto-completion at cursor position.

        Returns dict: {completion: str, completions: list[str], context: str}
        """
        line_start = source.rfind('\n', 0, cursor_pos) + 1
        before_cursor = source[line_start:cursor_pos]

        context = self._extract_context(before_cursor)
        if not context:
            return {"completion": "", "completions": [], "context": ""}

        context = context.lstrip('#[{ ')

        if context.endswith('('):
            self.show_help(context[:-1])
            return {"completion": "", "completions": [], "context": context}

        if '.' in context:
            return self._complete_dotted(context)
        else:
            return self._complete_module(context)

    def _extract_context(self, before_cursor: str) -> str:
        if not before_cursor:
            return ""
        idx = len(before_cursor) - 1
        if before_cursor[idx] == '(':
            idx -= 1
        paren_depth = 0
        while idx >= 0:
            ch = before_cursor[idx]
            if ch == ' ':
                break
            if ch == ')':
                paren_depth += 1
            if ch == '(':
                paren_depth -= 1
                if paren_depth % 2 != 0:
                    break
            idx -= 1
        return before_cursor[idx + 1:]

    def _complete_module(self, context: str) -> dict:
        use_dunder = context.startswith('_')
        candidates = self._get_attributes(self._namespace, context, use_dunder, include_builtins=True)
        completion = self._extend_partial(context, candidates)

        if len(candidates) == 1 and self._is_callable_in_ns(completion):
            if self._is_no_args(completion):
                completion += '()'
            else:
                completion += '('

        display = [c + ('()' if self._is_callable_in_ns(c) and self._is_no_args(c)
                         else '(' if self._is_callable_in_ns(c)
                         else '') for c in candidates]

        return {"completion": completion, "completions": display, "context": context}

    def _complete_dotted(self, context: str) -> dict:
        dot_pos = context.rfind('.')
        expression = context[:dot_pos]
        partial = context[dot_pos + 1:]

        try:
            obj = eval(expression, self._namespace)
        except Exception:
            return {"completion": "", "completions": [], "context": context}

        use_dunder = partial.startswith('_')
        candidates = self._get_attributes_of(obj, partial, use_dunder)
        completion = self._extend_partial(partial, candidates)

        if candidates:
            result = f"{expression}.{completion}"
        else:
            result = context

        if len(candidates) == 1:
            try:
                attr = getattr(obj, completion)
                if callable(attr):
                    if self._is_no_args_callable(attr):
                        result += '()'
                    else:
                        result += '('
            except Exception:
                pass

        display = []
        for c in candidates:
            try:
                attr = getattr(obj, c)
                if callable(attr):
                    if self._is_no_args_callable(attr):
                        display.append(c + '()')
                    else:
                        display.append(c + '(')
                else:
                    display.append(c)
            except Exception:
                display.append(c)

        return {"completion": result, "completions": display, "context": context}

    def _get_attributes(self, ns: dict, prefix: str, dunders: bool, include_builtins: bool) -> list[str]:
        candidates = []
        for name in sorted(ns.keys()):
            if not dunders and name.startswith('__'):
                continue
            if name.startswith(prefix) and name not in candidates:
                candidates.append(name)
        if include_builtins:
            import builtins
            for name in sorted(dir(builtins)):
                if not dunders and name.startswith('__'):
                    continue
                if name.startswith(prefix) and name not in candidates:
                    candidates.append(name)
        candidates.sort()
        return candidates

    def _get_attributes_of(self, obj: object, prefix: str, dunders: bool) -> list[str]:
        candidates = []
        for name in sorted(dir(obj)):
            if not dunders and name.startswith('__'):
                continue
            if name.startswith(prefix):
                candidates.append(name)
        return candidates

    @staticmethod
    def _extend_partial(partial: str, candidates: list[str]) -> str:
        if not candidates:
            return partial
        if len(candidates) == 1:
            return candidates[0]
        result = partial
        first = candidates[0]
        for length in range(len(partial), len(first) + 1):
            prefix = first[:length]
            if all(c.startswith(prefix) for c in candidates):
                result = prefix
            else:
                break
        return result

    def _is_callable_in_ns(self, name: str) -> bool:
        if name in self._namespace:
            return callable(self._namespace[name])
        import builtins
        return hasattr(builtins, name) and callable(getattr(builtins, name))

    @staticmethod
    def _is_no_args_callable(obj) -> bool:
        try:
            import inspect
            sig = inspect.signature(obj)
            params = [p for p in sig.parameters.values()
                      if p.default is inspect.Parameter.empty
                      and p.kind not in (p.VAR_POSITIONAL, p.VAR_KEYWORD)
                      and p.name != 'self']
            return len(params) == 0
        except (ValueError, TypeError):
            return False

    def _is_no_args(self, name: str) -> bool:
        obj = self._namespace.get(name)
        if obj is None:
            import builtins
            obj = getattr(builtins, name, None)
        if obj and callable(obj):
            return self._is_no_args_callable(obj)
        return False

    # --- Helpers ---

    @staticmethod
    def _maybe_uncomment(text: str) -> str:
        lines = text.split('\n')
        if all(line.startswith('#') for line in lines if line.strip()):
            return '\n'.join(line[1:] if line.startswith('#') else line for line in lines)
        return text
