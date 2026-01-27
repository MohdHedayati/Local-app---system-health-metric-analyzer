from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QLabel, QScrollArea, QHBoxLayout, 
    QGridLayout, QTableWidget, QTableWidgetItem, QHeaderView
)
from PyQt5.QtGui import QPainter, QPen, QColor, QFont, QBrush, QIcon
from PyQt5.QtCore import Qt, QRectF, QTimer
import json
import os
from utils.constants import DATA_FILE

class LineGraph(QWidget):
    def __init__(self, title, datasets, y_label="", y_max=None):
        super().__init__()
        self.title = title
        self.datasets = datasets 
        self.y_label = y_label
        self.fixed_y_max = y_max
        self.setMinimumHeight(250)

    # --- NEW METHOD ---
    def update_data(self, datasets):
        self.datasets = datasets
        self.update()  # Triggers paintEvent

    def paintEvent(self, event):
        # ... (Keep your existing paintEvent logic exactly as it was) ...
        # (For brevity, I'm assuming you keep the paint logic you pasted previously)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.fillRect(self.rect(), QColor("#1e1e1e"))
        # ... rest of your paint code ...
        # Ensure you keep the logic that handles empty data!
        width = self.width()
        height = self.height()
        margin_left = 60
        margin_right = 20
        margin_top = 50
        margin_bottom = 30
        painter.setPen(QColor("#ffffff"))
        painter.setFont(QFont("Segoe UI", 12, QFont.Bold))
        painter.drawText(margin_left, 30, self.title)
        
        all_values = []
        for ds in self.datasets:
            all_values.extend(ds['data'][-50:]) 
        
        if not all_values:
            painter.drawText(self.rect(), Qt.AlignCenter, "No Data")
            return

        max_val = max(all_values) if not self.fixed_y_max else self.fixed_y_max
        if max_val == 0: max_val = 1

        # Axes
        painter.setPen(QPen(QColor("#555555"), 2))
        painter.drawLine(margin_left, margin_top, margin_left, height - margin_bottom)
        painter.drawLine(margin_left, height - margin_bottom, width - margin_right, height - margin_bottom)

        # Grid
        painter.setPen(QColor("#444444"))
        painter.setFont(QFont("Segoe UI", 8))
        steps = 5
        for i in range(steps + 1):
            y_ratio = i / steps
            y = (height - margin_bottom) - (y_ratio * (height - margin_top - margin_bottom))
            val = y_ratio * max_val
            painter.setPen(QColor("#444444"))
            painter.drawLine(margin_left, int(y), width - margin_right, int(y))
            painter.setPen(QColor("#aaaaaa"))
            label = f"{val:.1f}{self.y_label}"
            painter.drawText(5, int(y) + 5, label)

        # Lines
        graph_width = width - margin_left - margin_right
        graph_height = height - margin_top - margin_bottom
        for ds in self.datasets:
            data = ds['data'][-50:]
            if len(data) < 2: continue
            step_x = graph_width / (len(data) - 1)
            path_color = QColor(ds['color'])
            pen = QPen(path_color, 2)
            painter.setPen(pen)
            points = []
            for i, val in enumerate(data):
                x = margin_left + i * step_x
                clamped_val = max(0, val)
                y = (height - margin_bottom) - (clamped_val / max_val * graph_height)
                points.append((x, y))
            for i in range(len(points) - 1):
                painter.drawLine(int(points[i][0]), int(points[i][1]), int(points[i+1][0]), int(points[i+1][1]))


class PieChart(QWidget):
    def __init__(self, title, used_percent, color_used, color_free="#333333"):
        super().__init__()
        self.title = title
        self.used_percent = min(100, max(0, used_percent))
        self.color_used = color_used
        self.color_free = color_free
        self.setMinimumHeight(250)

    # --- NEW METHOD ---
    def update_data(self, used_percent):
        self.used_percent = min(100, max(0, used_percent))
        self.update() # Triggers paintEvent

    def paintEvent(self, event):
        # ... (Keep your existing paintEvent logic) ...
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.fillRect(self.rect(), QColor("#1e1e1e"))
        width = self.width()
        height = self.height()
        side = min(width, height) - 60
        rect = QRectF((width - side)/2, (height - side)/2 + 20, side, side)
        painter.setPen(QColor("#ffffff"))
        painter.setFont(QFont("Segoe UI", 12, QFont.Bold))
        painter.drawText(10, 30, self.title)
        start_angle = 90 * 16
        span_angle = -360 * 16
        painter.setBrush(QColor(self.color_free))
        painter.setPen(Qt.NoPen)
        painter.drawPie(rect, start_angle, span_angle)
        used_span = -int(360 * self.used_percent / 100 * 16)
        painter.setBrush(QColor(self.color_used))
        painter.drawPie(rect, start_angle, used_span)
        painter.setPen(QColor("#ffffff"))
        painter.setFont(QFont("Segoe UI", 16, QFont.Bold))
        painter.drawText(rect, Qt.AlignCenter, f"{self.used_percent:.1f}%")


class ProcessTable(QTableWidget):
    def __init__(self, processes):
        super().__init__()
        self.setColumnCount(4)
        self.setHorizontalHeaderLabels(["PID", "Name", "CPU %", "Mem %"])
        self.verticalHeader().setVisible(False)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        # Style (Keep your existing style)
        self.setStyleSheet("""
            QTableWidget {
                background-color: #1e1e1e;
                color: #e0e0e0;
                gridline-color: #333333;
                border: none;
            }
            QHeaderView::section {
                background-color: #2c2c2c;
                color: #ffffff;
                padding: 4px;
                border: 1px solid #333333;
            }
        """)
        self.update_table(processes)

    # --- NEW METHOD ---
    def update_table(self, processes):
        self.setRowCount(len(processes))
        for r, proc in enumerate(processes):
            self.setItem(r, 0, QTableWidgetItem(str(proc.get('pid', ''))))
            self.setItem(r, 1, QTableWidgetItem(str(proc.get('name', ''))))
            self.setItem(r, 2, QTableWidgetItem(f"{proc.get('cpu_percent', 0):.1f}"))
            self.setItem(r, 3, QTableWidgetItem(f"{proc.get('memory_percent', 0):.1f}"))

class GraphsWindow(QWidget):
    def __init__(self, user_name, parent_dashboard=None):
        super().__init__()
        self.user_name = user_name
        self.parent_dashboard = parent_dashboard
        
        # icon
        from utils.constants import ICON_PATH
        self.setWindowIcon(QIcon(ICON_PATH))

        self.setWindowTitle("System Graphs")
        self.setFixedSize(1200, 900)
        # (Keep your existing setStyleSheet here)
        self.setStyleSheet("""
            QWidget { background-color: #121212; color: #e0e0e0; font-family: 'Segoe UI'; }
            QLabel { color: #ffffff; }
            QPushButton { background-color: transparent; border: 2px solid #5f6368; color: #e0e0e0; padding: 8px; }
            QPushButton:hover { background-color: #333333; }
        """)

        layout = QVBoxLayout()
        
        # Header
        header = QHBoxLayout()
        title = QLabel(f"System Health for {self.user_name}")
        title.setFont(QFont("Segoe UI", 18, QFont.Bold))
        back_btn = QPushButton("Back")
        back_btn.setFixedSize(100, 40)
        back_btn.setCursor(Qt.PointingHandCursor)
        back_btn.clicked.connect(self.go_back)
        header.addWidget(title)
        header.addStretch()
        header.addWidget(back_btn)
        layout.addLayout(header)

        # Scroll Area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        content = QWidget()
        grid = QGridLayout()
        grid.setSpacing(20)

        # --- INITIALIZE WIDGETS (Empty or with initial data) ---
        # 1. CPU Graph
        self.cpu_graph = LineGraph("CPU History (%)", [], y_max=100)
        grid.addWidget(self.cpu_graph, 0, 0)
        
        # 2. Network Graph
        self.net_graph = LineGraph("Network I/O (KB/s)", [], y_label="K")
        grid.addWidget(self.net_graph, 0, 1)
        
        # 3. Memory Pie
        self.mem_pie = PieChart("Memory Usage", 0, "#d93025")
        grid.addWidget(self.mem_pie, 1, 0)
        
        # 4. Disk Pie
        self.disk_pie = PieChart("Disk Usage", 0, "#9c27b0")
        grid.addWidget(self.disk_pie, 1, 1)
        
        # 5. Process Table
        proc_label = QLabel("Top 5 Processes (by CPU)")
        proc_label.setFont(QFont("Segoe UI", 12, QFont.Bold))
        grid.addWidget(proc_label, 2, 0, 1, 2)
        
        self.proc_table = ProcessTable([])
        self.proc_table.setFixedHeight(200)
        grid.addWidget(self.proc_table, 3, 0, 1, 2)
        
        content.setLayout(grid)
        scroll.setWidget(content)
        layout.addWidget(scroll)
        self.setLayout(layout)

        # --- TIMER SETUP ---
        self.refresh_view() # Initial Load
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.refresh_view)
        self.timer.start(5000) # Update every 5000ms (5 seconds)

    def refresh_view(self):
        """Fetches new data and updates child widgets"""
        data = self.load_data()
        
        # 1. Update CPU
        cpu_history = [{'label': 'Usage', 'data': data['cpu_history'], 'color': '#1a73e8'}]
        self.cpu_graph.update_data(cpu_history)
        
        # 2. Update Network
        net_sent = self.calc_rate(data['net_sent'])
        net_recv = self.calc_rate(data['net_recv'])
        net_sent_kb = [x/1024 for x in net_sent]
        net_recv_kb = [x/1024 for x in net_recv]
        
        net_datasets = [
            {'label': 'Sent', 'data': net_sent_kb, 'color': '#fbbc04'},
            {'label': 'Recv', 'data': net_recv_kb, 'color': '#188038'}
        ]
        self.net_graph.update_data(net_datasets)
        
        # 3. Update Pies
        self.mem_pie.update_data(data['latest_mem'])
        self.disk_pie.update_data(data['latest_disk'])
        
        # 4. Update Table
        self.proc_table.update_table(data['top_processes'])

    def calc_rate(self, data):
        if not data: return []
        deltas = []
        for i in range(1, len(data)):
            d = data[i] - data[i-1]
            deltas.append(d if d >= 0 else 0)
        return deltas

    def load_data(self):
        # ... (Keep your exact existing load_data logic here) ...
        res = {
            'cpu_history': [],
            'net_sent': [],
            'net_recv': [],
            'latest_mem': 0,
            'latest_disk': 0,
            'top_processes': []
        }
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, "r") as f:
                    content = json.load(f)
                    if isinstance(content, dict):
                        raw = content.get("data", {}).get("recent_samples", [])
                    else:
                        raw = []
                    
                    for s in raw:
                        res['cpu_history'].append(s.get('cpu', {}).get('usage', 0))
                        net = s.get('network', {})
                        res['net_sent'].append(net.get('bytes_sent', 0))
                        res['net_recv'].append(net.get('bytes_recv', 0))
                        
                    if raw:
                        last = raw[-1]
                        res['latest_mem'] = last.get('memory', {}).get('ram', {}).get('percent', 0)
                        res['latest_disk'] = last.get('disk', {}).get('percent', 0)
                        res['top_processes'] = last.get('processes', [])[:5]
            except Exception as e:
                print(f"Error loading: {e}")
        return res

    def go_back(self):
        self.timer.stop() # Stop the timer when leaving!
        self.close()

    def closeEvent(self, event):
        self.timer.stop() # Double check timer is stopped
        if self.parent_dashboard:
            self.parent_dashboard.show()
        event.accept()