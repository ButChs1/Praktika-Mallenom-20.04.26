from PyQt6.QtWidgets import QWidget, QVBoxLayout
from PyQt6.QtCore import QTimer
import matplotlib
matplotlib.use('QtAgg')
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.lines as lines
import collections

class AnalyticsTab(QWidget):
    def __init__(self, parent=None, tr=None):
        super().__init__(parent)
        self.main_window = parent
        self.tr = tr
        
        self.bg_color = '#2b2b2b'
        self.text_color = 'white'
        self.grid_color = '#555555'
        
        self.current_stats = {"TCP": 0, "UDP": 0, "ICMP": 0, "Total": 0}
        self.last_total = 0
        
        self.history_len = 60
        self.pps_history = collections.deque([0]*self.history_len, maxlen=self.history_len)

        self.init_ui()

        self.render_timer = QTimer(self)
        self.render_timer.timeout.connect(self.render_dashboard)
        self.render_timer.start(1000)

    def init_ui(self):
        layout = QVBoxLayout(self)

        self.figure = Figure(facecolor=self.bg_color)
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)

        self.ax_pie = self.figure.add_subplot(221)
        self.ax_line = self.figure.add_subplot(222)
        self.ax_bar = self.figure.add_subplot(223)  
        self.ax_flags = self.figure.add_subplot(224)

        for ax in [self.ax_pie, self.ax_line, self.ax_bar, self.ax_flags]:
            ax.set_facecolor(self.bg_color)
            ax.tick_params(colors=self.text_color)
            for spine in ax.spines.values():
                spine.set_color(self.grid_color)

        self.figure.tight_layout(pad=3.0)
        
        line_v = lines.Line2D([0.5, 0.5], [0, 1], transform=self.figure.transFigure, color=self.grid_color, linewidth=2)
        self.figure.add_artist(line_v)
        
        line_h = lines.Line2D([0, 1], [0.5, 0.5], transform=self.figure.transFigure, color=self.grid_color, linewidth=2)
        self.figure.add_artist(line_h)

    def update_data(self, stats):
        self.current_stats = stats.copy()

    def render_dashboard(self):
        current_total = self.current_stats.get("Total", 0)
        pps = current_total - self.last_total
        self.last_total = current_total
        self.pps_history.append(pps)

        self.draw_pie_chart(self.current_stats)
        self.draw_line_chart()
        self.draw_bar_chart()
        self.draw_flags_chart()
        
        self.canvas.draw()

    def draw_pie_chart(self, stats):
        self.ax_pie.clear()
        labels = []
        sizes = []
        colors_map = {"TCP": "#4A90E2", "UDP": "#50E3C2", "ICMP": "#E02020"}
        colors = []

        for proto in ["TCP", "UDP", "ICMP"]:
            if stats.get(proto, 0) > 0:
                labels.append(proto)
                sizes.append(stats[proto])
                colors.append(colors_map[proto])

        self.ax_pie.set_title(self.tr["title_protocols"], color=self.text_color, pad=10)

        if not sizes:
            self.ax_pie.pie([1], labels=[self.tr["no_data"]], colors=[self.grid_color])
        else:
            wedges, texts, autotexts = self.ax_pie.pie(
                sizes, labels=labels, colors=colors,
                autopct='%1.1f%%', startangle=90,
                wedgeprops={'edgecolor': '#2b2b2b', 'linewidth': 1}
            )
            for text in texts:
                text.set_color('white')
                text.set_fontsize(10)
            for autotext in autotexts:
                autotext.set_color('white')
                autotext.set_fontweight('bold')

    def draw_line_chart(self):
        self.ax_line.clear()
        self.ax_line.set_title(self.tr["title_activity"], color=self.text_color, pad=10)

        x_data = list(range(-self.history_len + 1, 1))
        
        self.ax_line.plot(x_data, self.pps_history, color='#F8E71C', linewidth=2)
        
        self.ax_line.fill_between(x_data, self.pps_history, color='#F8E71C', alpha=0.2)

        self.ax_line.set_xlim(-self.history_len + 1, 0)
        self.ax_line.set_ylim(bottom=0)
        self.ax_line.grid(True, linestyle='--', alpha=0.3, color='gray')
        
    def draw_bar_chart(self):
        self.ax_bar.clear()
        self.ax_bar.set_title(self.tr["title_top_ip"], color=self.text_color, pad=10)
        
        ip_data = self.current_stats.get("ips", {})
        if not ip_data:
            self.ax_bar.text(0.5, 0.5, self.tr["no_data"], color=self.grid_color, ha='center', va='center')
            
            self.ax_bar.set_xticks([])
            self.ax_bar.set_yticks([])
            return

        top_5 = sorted(ip_data.items(), key=lambda x: x[1], reverse=True)[:5]
        
        ips = [item[0] for item in reversed(top_5)]
        counts = [item[1] for item in reversed(top_5)]

        bars = self.ax_bar.barh(ips, counts, color='#50E3C2', height=0.6)
        
        for bar in bars:
            width = bar.get_width()
            padding = max(counts) * 0.01 
            self.ax_bar.text(width + padding, bar.get_y() + bar.get_height()/2, 
                             f'{width}', va='center', color=self.text_color, fontsize=9)

        self.ax_bar.tick_params(colors='white', axis='y', labelsize=9)
        
        self.ax_bar.get_xaxis().set_visible(False) 
        
        self.ax_bar.spines['top'].set_visible(False)
        self.ax_bar.spines['right'].set_visible(False)
        self.ax_bar.spines['bottom'].set_visible(False)
        self.ax_bar.spines['left'].set_color(self.grid_color)
        
    def draw_flags_chart(self):
        self.ax_flags.clear()
        self.ax_flags.set_title(self.tr["title_flags"], color=self.text_color, pad=10)
        
        flags_data = self.current_stats.get("flags", {})
        if not flags_data:
            self.ax_flags.text(0.5, 0.5, self.tr["no_data"], color=self.grid_color, ha='center', va='center')
            
            self.ax_flags.set_xticks([])
            self.ax_flags.set_yticks([])
            return

        top_flags = sorted(flags_data.items(), key=lambda x: x[1], reverse=True)[:6]
        
        labels = [item[0] for item in top_flags]
        counts = [item[1] for item in top_flags]

        bars = self.ax_flags.bar(labels, counts, color='#E02020', width=0.5)

        for bar in bars:
            height = bar.get_height()
            self.ax_flags.text(bar.get_x() + bar.get_width()/2, height + (max(counts)*0.02),
                               f'{height}', ha='center', va='bottom', color=self.text_color, fontsize=9)

        self.ax_flags.tick_params(colors='white', axis='x', labelsize=9)
        self.ax_flags.set_yticks([])
        
        self.ax_flags.spines['top'].set_visible(False)
        self.ax_flags.spines['right'].set_visible(False)
        self.ax_flags.spines['left'].set_visible(False)
        self.ax_flags.spines['bottom'].set_color(self.grid_color)