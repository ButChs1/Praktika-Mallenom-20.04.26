from PyQt6.QtWidgets import (QVBoxLayout, QWidget, QFormLayout, 
                             QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox, 
                             QPushButton, QTextEdit, QGroupBox, QHBoxLayout, QCheckBox)
from core.generator import GeneratorThread

class GeneratorTab(QWidget):
    def __init__(self, parent=None, tr=None):
        super().__init__(parent)
        self.tr = tr
        self.main_window = parent
        self.generator_thread = GeneratorThread()
        
        self.generator_thread.log_ready.connect(self.log_message)
        self.generator_thread.status_message.connect(self.show_status)
        self.generator_thread.finished.connect(self.on_generation_finished)
        
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout(self) 

        group_dst = QGroupBox(self.tr["group_dst"])
        layout_dst = QFormLayout()
        self.edit_dst_ip = QLineEdit("127.0.0.1")
        self.spin_dst_port = QSpinBox()
        self.spin_dst_port.setRange(1, 65535)
        self.spin_dst_port.setValue(80)
        layout_dst.addRow(self.tr["ip_dst"], self.edit_dst_ip)
        layout_dst.addRow(self.tr["port_dst"], self.spin_dst_port)
        group_dst.setLayout(layout_dst)

        group_src = QGroupBox(self.tr["group_src"])
        layout_src = QFormLayout()
        
        ip_layout = QHBoxLayout()
        self.edit_src_ip = QLineEdit("192.168.1.100")
        self.chk_rand_ip = QCheckBox(self.tr["chk_rand_ip"])
        self.chk_rand_ip.stateChanged.connect(lambda: self.edit_src_ip.setDisabled(self.chk_rand_ip.isChecked()))
        ip_layout.addWidget(self.edit_src_ip)
        ip_layout.addWidget(self.chk_rand_ip)
        
        port_layout = QHBoxLayout()
        self.spin_src_port = QSpinBox()
        self.spin_src_port.setRange(1, 65535)
        self.spin_src_port.setValue(12345)
        self.chk_rand_port = QCheckBox(self.tr["chk_rand_port"])
        self.chk_rand_port.stateChanged.connect(lambda: self.spin_src_port.setDisabled(self.chk_rand_port.isChecked()))
        port_layout.addWidget(self.spin_src_port)
        port_layout.addWidget(self.chk_rand_port)

        layout_src.addRow(self.tr["ip_src"], ip_layout)
        layout_src.addRow(self.tr["port_src"], port_layout)
        group_src.setLayout(layout_src)

        group_packet = QGroupBox(self.tr["group_packet"])
        layout_packet = QFormLayout()
        
        self.combo_proto = QComboBox()
        self.combo_proto.addItems(["TCP", "UDP", "ICMP"])
        self.combo_proto.currentTextChanged.connect(self.on_proto_changed)
        
        self.flags_widget = QWidget()
        flags_layout = QHBoxLayout(self.flags_widget)
        flags_layout.setContentsMargins(0, 0, 0, 0) # Убираем лишние отступы
        
        self.chk_syn = QCheckBox("SYN (S)")
        self.chk_ack = QCheckBox("ACK (A)")
        self.chk_fin = QCheckBox("FIN (F)")
        self.chk_rst = QCheckBox("RST (R)")
        self.chk_psh = QCheckBox("PSH (P)")
        self.chk_urg = QCheckBox("URG (U)")
        
        for chk in [self.chk_syn, self.chk_ack, self.chk_fin, self.chk_rst, self.chk_psh, self.chk_urg]:
            flags_layout.addWidget(chk)
            
        self.edit_payload = QLineEdit("Test Payload")
        
        layout_packet.addRow(self.tr["protocol"], self.combo_proto)
        layout_packet.addRow(self.tr["tcp_flags"], self.flags_widget)
        layout_packet.addRow(self.tr["payload"], self.edit_payload)
        group_packet.setLayout(layout_packet)

        group_send = QGroupBox(self.tr["group_send"])
        layout_send = QHBoxLayout()
        
        self.spin_count = QSpinBox()
        self.spin_count.setRange(1, 10000)
        self.spin_count.setPrefix(self.tr["count_prefix"])
        
        self.spin_delay = QDoubleSpinBox()
        self.spin_delay.setRange(0.0, 10.0)
        self.spin_delay.setSingleStep(0.1)
        self.spin_delay.setValue(1.0)
        self.spin_delay.setPrefix(self.tr["delay_prefix"])
        self.spin_delay.setSuffix(self.tr["delay_suffix"])

        self.btn_send = QPushButton(self.tr["btn_start"])
        self.btn_send.setStyleSheet("background-color: #5a1818; font-weight: bold;")
        self.btn_send.clicked.connect(self.toggle_generation)
        
        layout_send.addWidget(self.spin_count)
        layout_send.addWidget(self.spin_delay)
        layout_send.addWidget(self.btn_send)
        group_send.setLayout(layout_send)

        main_layout.addWidget(group_dst)
        main_layout.addWidget(group_src)
        main_layout.addWidget(group_packet)
        main_layout.addWidget(group_send)
        
        self.log_console = QTextEdit()
        self.log_console.setReadOnly(True)
        self.log_console.setStyleSheet("background-color: #0c0c0c; color: #00ff00; font-family: 'Consolas'; font-size: 10pt;")
        main_layout.addWidget(self.log_console)
        
    def on_proto_changed(self, text):
        """Адаптирует интерфейс под выбранный протокол"""
        self.flags_widget.setVisible(text == "TCP")
        
        need_ports = text in ["TCP", "UDP"]
        
        self.spin_dst_port.setEnabled(need_ports)
        self.chk_rand_port.setEnabled(need_ports)
        
        if not need_ports:
            self.spin_src_port.setEnabled(False)
        else:
            self.spin_src_port.setEnabled(not self.chk_rand_port.isChecked())
        
    def log_message(self, message):
        self.log_console.append(f"> {message}")
        self.log_console.ensureCursorVisible()
        
    def show_status(self, message):
        if self.main_window:
            self.main_window.statusBar().showMessage(message, 5000)
            
    def toggle_generation(self):
        if not self.generator_thread.isRunning():
            self.generator_thread.dst_ip = self.edit_dst_ip.text()
            self.generator_thread.dst_port = self.spin_dst_port.value()
            
            self.generator_thread.src_ip = self.edit_src_ip.text()
            self.generator_thread.src_port = self.spin_src_port.value()
            self.generator_thread.rand_src_ip = self.chk_rand_ip.isChecked()
            self.generator_thread.rand_src_port = self.chk_rand_port.isChecked()
            
            flags = ""
            if self.chk_syn.isChecked(): flags += "S"
            if self.chk_ack.isChecked(): flags += "A"
            if self.chk_fin.isChecked(): flags += "F"
            if self.chk_rst.isChecked(): flags += "R"
            if self.chk_psh.isChecked(): flags += "P"
            if self.chk_urg.isChecked(): flags += "U"
            self.generator_thread.tcp_flags = flags
            
            # Настройки пакета
            self.generator_thread.proto = self.combo_proto.currentText()
            self.generator_thread.payload = self.edit_payload.text()
            self.generator_thread.count = self.spin_count.value()
            self.generator_thread.delay = self.spin_delay.value()
            
            self.btn_send.setText(self.tr["btn_stop"])
            self.btn_send.setStyleSheet("background-color: #8a6a00; font-weight: bold;")
            self.generator_thread.start()
        else:
            self.generator_thread.stop()
            self.btn_send.setEnabled(False)

    def on_generation_finished(self):
        self.btn_send.setEnabled(True)
        self.btn_send.setText(self.tr["log_title"])
        self.btn_send.setStyleSheet("background-color: #5a1818; font-weight: bold;")