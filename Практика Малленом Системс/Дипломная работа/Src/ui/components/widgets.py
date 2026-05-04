from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTextEdit, QPushButton, QTableWidgetItem

class PacketDetailWindow(QMainWindow):
    def __init__(self, packet, parent=None):
        super().__init__(parent)
        self.packet = packet
        self.setWindowTitle("Детальный просмотр пакета")
        self.resize(750, 600)
        
        layout = QVBoxLayout()
        self.label = QLabel("Структура пакета (Scapy View):")
        layout.addWidget(self.label)
        
        self.text_display = QTextEdit()
        self.text_display.setReadOnly(True)
        self.text_display.setPlainText(self.packet.show(dump=True))
        self.text_display.setStyleSheet("font-family: 'Courier New'; font-size: 10pt; background-color: #1e1e1e; color: #d4d4d4;")
        layout.addWidget(self.text_display)
        
        btn_layout = QHBoxLayout()
        self.btn_view_struct = QPushButton("Структура")
        self.btn_view_hex = QPushButton("HEX Дамп")
        self.btn_view_struct.clicked.connect(self.show_struct)
        self.btn_view_hex.clicked.connect(self.show_hex)
        
        btn_layout.addWidget(self.btn_view_struct)
        btn_layout.addWidget(self.btn_view_hex)
        layout.addLayout(btn_layout)
        
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def show_struct(self):
        self.label.setText("Структура пакета (Scapy View):")
        self.text_display.setPlainText(self.packet.show(dump=True))

    def show_hex(self):
        self.label.setText("HEX-представление (Offset | Hex | ASCII):")
        from scapy.utils import linehexdump
        hex_data = linehexdump(self.packet, onlyhex=0, dump=True)
        self.text_display.setPlainText(hex_data)

class NumericTableWidgetItem(QTableWidgetItem):
    def __lt__(self, other):
        try:
            return float(self.text()) < float(other.text())
        except ValueError:
            return super().__lt__(other)