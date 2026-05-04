import io
import traceback
import contextlib
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QTextEdit, QLabel, QSplitter)
from PyQt6.QtCore import QThread, pyqtSignal, Qt

class ScriptRunnerThread(QThread):
    output_ready = pyqtSignal(str)

    def __init__(self, code):
        super().__init__()
        self.code = code

    def run(self):
        stdout_io = io.StringIO()
        stderr_io = io.StringIO()

        with contextlib.redirect_stdout(stdout_io), contextlib.redirect_stderr(stderr_io):
            try:
                exec_globals = {}
                exec("from scapy.all import *", exec_globals)
                exec(self.code, exec_globals)
            except Exception as e:
                traceback.print_exc()

        output = stdout_io.getvalue() + stderr_io.getvalue()
        if not output.strip():
            output = "[Скрипт выполнен без текстового вывода]"
            
        self.output_ready.emit(output)

class TerminalTab(QWidget):
    def __init__(self, parent=None, tr=None):
        super().__init__(parent)
        self.tr = tr or {}
        self.runner_thread = None
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        
        splitter = QSplitter(Qt.Orientation.Vertical)
        
        code_widget = QWidget()
        code_layout = QVBoxLayout(code_widget)
        code_layout.setContentsMargins(0, 0, 0, 0)
        
        code_layout.addWidget(QLabel(self.tr["code_label"]))
        
        self.code_editor = QTextEdit()
        self.code_editor.setStyleSheet("font-family: 'Consolas'; font-size: 11pt; background-color: #1e1e1e; color: #d4d4d4;")
        self.code_editor.setPlainText(self.tr["default_code"])
        code_layout.addWidget(self.code_editor)
        
        btn_layout = QHBoxLayout()
        self.btn_run = QPushButton(self.tr["btn_run"])
        self.btn_run.setStyleSheet("background-color: #2b5c2b; color: white; font-weight: bold; padding: 6px;")
        self.btn_run.clicked.connect(self.run_script)
        
        self.btn_clear = QPushButton(self.tr["btn_clear"])
        self.btn_clear.clicked.connect(lambda: self.console.clear())
        
        btn_layout.addWidget(self.btn_run)
        btn_layout.addWidget(self.btn_clear)
        btn_layout.addStretch()
        code_layout.addLayout(btn_layout)
        
        console_widget = QWidget()
        console_layout = QVBoxLayout(console_widget)
        console_layout.setContentsMargins(0, 0, 0, 0)
        
        console_layout.addWidget(QLabel(self.tr["console_label"]))
        self.console = QTextEdit()
        self.console.setReadOnly(True)
        self.console.setStyleSheet("background-color: #0c0c0c; color: #00ff00; font-family: 'Consolas'; font-size: 10pt;")
        console_layout.addWidget(self.console)
        
        splitter.addWidget(code_widget)
        splitter.addWidget(console_widget)
        
        layout.addWidget(splitter)
        
    def run_script(self):
        code = self.code_editor.toPlainText()
        
        self.btn_run.setEnabled(False)
        self.btn_run.setText(self.tr["running"])
        
        self.runner_thread = ScriptRunnerThread(code)
        self.runner_thread.output_ready.connect(self.on_output)
        self.runner_thread.finished.connect(self.on_finished)
        self.runner_thread.start()
        
    def on_output(self, text):
        self.console.append(text)
        
    def on_finished(self):
        self.btn_run.setEnabled(True)
        self.btn_run.setText(self.tr["btn_run"])