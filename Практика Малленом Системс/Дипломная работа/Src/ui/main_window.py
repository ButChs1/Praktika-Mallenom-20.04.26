from PyQt6.QtWidgets import QMainWindow, QTabWidget, QVBoxLayout, QWidget

from ui.components.sniffer_tab import SnifferTab
from ui.components.analytics_tab import AnalyticsTab
from ui.components.generator_tab import GeneratorTab
from ui.components.settings_tab import SettingsTab
from ui.components.terminal_tab import TerminalTab

from utils.config_manager import ConfigManager

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.config = ConfigManager.load_config()
        self.tr = ConfigManager.get_translations(self.config["language"])
        
        self.setWindowTitle(self.tr["main"]["title"])
        self.setMinimumSize(900, 700)
        
        self.init_ui()

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        self.tabs = QTabWidget()
        
        self.tab_sniffer = SnifferTab(self, self.tr["sniffer"])
        self.tab_analytics = AnalyticsTab(self, self.tr["analytics"])
        self.tab_generator = GeneratorTab(self, self.tr["generator"])
        self.tab_terminal = TerminalTab(self, self.tr.get("terminal", {}))
        self.settings_tab = SettingsTab(self, self.tr["settings"])
        
        self.tabs.addTab(self.tab_sniffer, self.tr["main"]["tab_sniffer"])
        self.tabs.addTab(self.tab_analytics, self.tr["main"]["tab_analytics"])
        self.tabs.addTab(self.tab_generator, self.tr["main"]["tab_generator"])
        self.tabs.addTab(self.tab_terminal, self.tr["main"]["tab_terminal"])
        self.tabs.addTab(self.settings_tab, self.tr["main"]["tab_settings"])
        
        main_layout.addWidget(self.tabs)
        
        self.tab_sniffer.sniffer_thread.stats_updated.connect(self.tab_analytics.update_data)
        
        self.settings_tab.clear_data_requested.connect(self.clear_all_data)
        
    def clear_all_data(self):
        if self.tab_sniffer.sniffer_thread.isRunning():
            self.tab_sniffer.toggle_sniffing()
            
        self.tab_sniffer.table.setRowCount(0)
        self.tab_sniffer.raw_packets.clear()
        self.tab_sniffer.packet_buffer.clear()
        
        self.tab_sniffer.sniffer_thread.stats = {"TCP": 0, "UDP": 0, "ICMP": 0, "Total": 0}
        self.tab_sniffer.update_stats_label(self.tab_sniffer.sniffer_thread.stats)
        
        self.tab_analytics.update_data(self.tab_sniffer.sniffer_thread.stats)
        self.tab_analytics.pps_history.extend([0] * self.tab_analytics.history_len) 
        self.tab_analytics.last_total = 0
        
        self.statusBar().showMessage(self.tr["settings"]["status_cleared"], 5000)