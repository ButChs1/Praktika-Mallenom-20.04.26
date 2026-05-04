from PyQt6.QtWidgets import QComboBox, QFileDialog, QHBoxLayout, QHeaderView, QLabel, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget
from PyQt6.QtCore import QTimer
from PyQt6.QtGui import QColor

from ui.components.widgets import NumericTableWidgetItem, PacketDetailWindow

from core.sniffer import SnifferThread

from utils.process_manager import get_network_processes, get_ports_by_process
from utils.network import get_available_interfaces
from utils.filters import row_matches_query
from utils.logger import TrafficLogger

class SnifferTab(QWidget):
    def __init__(self, parent=None, tr=None):
        super().__init__(parent)
        self.main_window = parent
        self.tr = tr
        self.packet_buffer = []
        self.raw_packets = []
        self.stats = {"TCP": 0, "UDP": 0, "ICMP": 0, "Total": 0}
        
        self.sniffer_thread = SnifferThread()
        self.sniffer_thread.packet_received.connect(self.add_packet_to_table)
        self.sniffer_thread.stats_updated.connect(self.update_stats_label)
        
        self.display_timer = QTimer()
        self.display_timer.timeout.connect(self.update_table_from_buffer)
        self.display_timer.start(100)
        
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        top_panel = QHBoxLayout()
        
        self.combo_iface = QComboBox()
        for desc, name in get_available_interfaces():
            self.combo_iface.addItem(desc, name)
        top_panel.addWidget(QLabel(self.tr["interface_label"]))
        top_panel.addWidget(self.combo_iface, 2)

        self.combo_process = QComboBox()
        self.combo_process.addItem(self.tr["process_all"], None)
        top_panel.addWidget(QLabel(self.tr["process_label"]))
        top_panel.addWidget(self.combo_process, 2)

        self.btn_toggle = QPushButton(self.tr["btn_start"])
        self.btn_toggle.clicked.connect(self.toggle_sniffing)
        top_panel.addWidget(self.btn_toggle, 1)

        layout.addLayout(top_panel)

        filter_layout = QHBoxLayout()
        self.edit_filter = QLineEdit()
        self.edit_filter.setPlaceholderText(self.tr["search_placeholder"])
        self.edit_filter.textChanged.connect(self.apply_filter)
        filter_layout.addWidget(QLabel(self.tr["search_label"]))
        filter_layout.addWidget(self.edit_filter)
        
        layout.addLayout(filter_layout)
        
        self.table = QTableWidget(0, 9) 
        self.table.setHorizontalHeaderLabels(
            self.tr["table_headers"]
        )
        self.table.setSortingEnabled(True)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.table)
        
        bottom_panel = QHBoxLayout()
        
        self.btn_clear = QPushButton(self.tr["btn_clear"])
        self.btn_clear.setMaximumWidth(150)
        self.btn_clear.clicked.connect(lambda: self.table.setRowCount(0))
        
        self.btn_load = QPushButton(self.tr["btn_load_pcap"])
        self.btn_load.setMaximumWidth(150)
        self.btn_load.clicked.connect(self.load_from_pcap)
        
        self.btn_save = QPushButton(self.tr["btn_save_log"])
        self.btn_save.setMaximumWidth(250)
        self.btn_save.clicked.connect(self.save_to_file)
        
        bottom_panel.addWidget(self.btn_clear)
        bottom_panel.addWidget(self.btn_load)
        bottom_panel.addWidget(self.btn_save)
        
        bottom_panel.addStretch()
        
        self.stats_label = QLabel(self.tr["stats_text"])
        self.stats_label.setStyleSheet("color: #aaaaaa; font-weight: bold;") 
        bottom_panel.addWidget(self.stats_label)

        layout.addLayout(bottom_panel)
        
        self.table.cellDoubleClicked.connect(self.show_packet_details)
        for proc in get_network_processes():
            self.combo_process.addItem(proc)
            
    def update_stats_label(self, stats):
        self.stats_label.setText(
            f"Статистика: TCP: {stats['TCP']} | UDP: {stats['UDP']} | "
            f"ICMP: {stats['ICMP']} | Всего: {stats['Total']}"
        )
        
    def toggle_sniffing(self):
        if not self.sniffer_thread.isRunning():
            self.sniffer_thread.interface = self.combo_iface.currentData()
            process_name = self.combo_process.currentText()

            if process_name == self.tr["process_all"]:
                self.sniffer_thread.target_ports = set()
            else:
                self.sniffer_thread.target_ports = get_ports_by_process(process_name)

            self.sniffer_thread.is_running = True
            self.sniffer_thread.start()
            
            self.btn_toggle.setText(self.tr["btn_stop"])
            self.combo_iface.setEnabled(False)
            self.combo_process.setEnabled(False)
            
        else:
            self.sniffer_thread.is_running = False
            self.packet_buffer.clear() 
            self.btn_toggle.setEnabled(False)
            
            try:
                self.sniffer_thread.finished.disconnect()
            except:
                pass
            self.sniffer_thread.finished.connect(self.on_sniffer_finished)

    def on_sniffer_finished(self):
        self.btn_toggle.setEnabled(True)
        self.btn_toggle.setText(self.tr["btn_start"])
        self.combo_iface.setEnabled(True)
        self.combo_process.setEnabled(True)

    def add_packet_to_table(self, packet, info):
        self.packet_buffer.append((packet, info))

    def update_table_from_buffer(self):
            if not self.packet_buffer:
                return

            self.table.setSortingEnabled(False)
            self.table.setUpdatesEnabled(False)
            
            to_process = self.packet_buffer[:50]
            self.packet_buffer = self.packet_buffer[50:]

            for packet, info in to_process:
                self.raw_packets.append(packet)
                row_count = self.table.rowCount()
                self.table.insertRow(row_count)

                columns = [
                    (str(row_count + 1), True),
                    (info["proto"], False),
                    (info["src"], False),
                    (str(info["src_port"]), True),
                    (info["dst"], False),
                    (str(info["dst_port"]), True),
                    (info["flags"], False),
                    (str(info["ttl"]), True),
                    (str(info["length"]), True)
                ]

                bg_color = None
                if info["proto"] == "TCP": bg_color = "#293642"
                elif info["proto"] == "UDP": bg_color = "#41634B"
                elif info["proto"] == "ICMP": bg_color = "#704242"

                for col, (text, is_numeric) in enumerate(columns):
                    if is_numeric:
                        item = NumericTableWidgetItem(text)
                    else:
                        item = QTableWidgetItem(text)
                    
                    if bg_color:
                        item.setBackground(QColor(bg_color))
                    self.table.setItem(row_count, col, item)

            self.table.setSortingEnabled(True)
            self.table.setUpdatesEnabled(True)
                              
    def save_to_file(self):
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Сохранить данные", "", "PCAP Files (*.pcap);;CSV Files (*.csv);;Text Files (*.txt)"
        )
        
        if file_path:
            if file_path.endswith(".pcap"):
                from scapy.all import wrpcap
                wrpcap(file_path, self.raw_packets)
                success = True
            else:
                headers = [self.table.horizontalHeaderItem(i).text() for i in range(self.table.columnCount())]
                all_data = []
                for row in range(self.table.rowCount()):
                    row_data = [self.table.item(row, col).text() if self.table.item(row, col) else "" 
                                for col in range(self.table.columnCount())]
                    all_data.append(row_data)
                success = TrafficLogger.save_data(file_path, headers, all_data)
            
            if success and self.main_window:
                success_msg = self.tr["file_saved"].format(path=file_path)
                self.main_window.statusBar().showMessage(success_msg, 5000)

    def apply_filter(self):
        query = self.edit_filter.text()
        
        if not query.strip():
            for row in range(self.table.rowCount()):
                self.table.setRowHidden(row, False)
            return

        for row in range(self.table.rowCount()):
            row_content = []
            for col in range(self.table.columnCount()):
                item = self.table.item(row, col)
                if item:
                    row_content.append(item.text())

            match = row_matches_query(query, row_content)
            
            self.table.setRowHidden(row, not match)
            
    def show_packet_details(self, row, column):
        if row < len(self.raw_packets):
            packet = self.raw_packets[row]
            self.detail_win = PacketDetailWindow(packet, self)
            self.detail_win.show()
            
    def load_from_pcap(self):
        if self.sniffer_thread.isRunning():
            if self.main_window:
                self.main_window.statusBar().showMessage(self.tr["error_stop_first"], 5000)
            return

        file_path, _ = QFileDialog.getOpenFileName(
            self, self.tr["btn_load_pcap"], "", "PCAP Files (*.pcap *.pcapng)"
        )
        
        if file_path:
            self.table.setRowCount(0)
            self.raw_packets.clear()
            self.packet_buffer.clear()
            
            self.sniffer_thread.offline_file = file_path
            self.sniffer_thread.is_running = True
            self.sniffer_thread.start()
            
            if self.main_window:
                self.main_window.statusBar().showMessage(self.tr["status_loading"].format(path=file_path), 5000)