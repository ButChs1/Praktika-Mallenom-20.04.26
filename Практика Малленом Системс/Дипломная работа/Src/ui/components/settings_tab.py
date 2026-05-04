from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QGroupBox, QFormLayout, 
                             QComboBox, QPushButton, QMessageBox)
from PyQt6.QtCore import pyqtSignal

from utils.config_manager import ConfigManager

class SettingsTab(QWidget):
    clear_data_requested = pyqtSignal()
    theme_changed = pyqtSignal(str)
    lang_changed = pyqtSignal(str)

    def __init__(self, parent=None, tr=None):
        super().__init__(parent)
        self.tr = tr
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        group_ui = QGroupBox(self.tr["group_ui"])
        form_ui = QFormLayout()
        
        self.combo_lang = QComboBox()
        self.combo_lang.addItems(["Русский", "English"])
        
        current_config = ConfigManager.load_config()
        if current_config.get("language") == "en":
            self.combo_lang.setCurrentIndex(1)
        else:
            self.combo_lang.setCurrentIndex(0)
            
        self.combo_lang.currentTextChanged.connect(self.lang_changed.emit)
        form_ui.addRow(self.tr["lang_label"], self.combo_lang)
        
        self.btn_save_settings = QPushButton(self.tr["btn_save_config"])
        self.btn_save_settings.clicked.connect(self.save_settings_to_file)
        form_ui.addRow(self.btn_save_settings)
        
        group_ui.setLayout(form_ui)

        group_data = QGroupBox(self.tr["group_data"])
        layout_data = QVBoxLayout()
        
        self.btn_clear = QPushButton(self.tr["btn_clear_all"])
        self.btn_clear.setStyleSheet("background-color: #5a1818; color: white; font-weight: bold; padding: 10px; border-radius: 5px;")
        self.btn_clear.clicked.connect(self.request_clear)
        layout_data.addWidget(self.btn_clear)
        group_data.setLayout(layout_data)

        layout.addWidget(group_ui)
        layout.addWidget(group_data)
        layout.addStretch()

    def request_clear(self):
        reply = QMessageBox.question(
            self, 
            self.tr["confirm_title"], 
            self.tr["confirm_text"], 
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.clear_data_requested.emit()
            
    def save_settings_to_file(self):
        lang_code = "ru" if self.combo_lang.currentIndex() == 0 else "en"
        
        ConfigManager.save_config({
            "language": lang_code,
            "theme": "dark"
        })
        
        QMessageBox.information(self, "Успех", self.tr["status_saved"])