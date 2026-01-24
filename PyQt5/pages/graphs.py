from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QLabel, QScrollArea, QHBoxLayout, 
    QGridLayout, QTableWidget, QTableWidgetItem, QHeaderView
)
from PyQt5.QtGui import QPainter, QPen, QColor, QFont, QBrush
from PyQt5.QtCore import Qt, QRectF
import json
import os
from utils.constants import DATA_FILE

class LineGraph(QWidget):
    def __init__(self, title, datasets, y_label="", y_max=None):
        super().__init__()
        self.title = title
        # datasets: list of dicts {'label': str, 'data': list[float], 'color': str}
        self.datasets = datasets 
        self.y_label = y_label
        self.fixed_y_max = y_max
        self.setMinimumHeight(250)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Background
        painter.fillRect(self.rect(), QColor("#1e1e1e"))

        width = self.width()
        height = self.height()
        
        margin_left = 60
        margin_right = 20
        margin_top = 50
        margin_bottom = 30

        # Title
        painter.setPen(QColor("#ffffff"))
        painter.setFont(QFont("Segoe UI", 12, QFont.Bold))
        painter.drawText(margin_left, 30, self.title)

        # Determine Range
        all_values = []
        for ds in self.datasets:
            all_values.extend(ds['data'][-50:]) # Look at last 50 points
        
        if not all_values:
            painter.drawText(self.rect(), Qt.AlignCenter, "No Data")
            return

        max_val = max(all_values) if not self.fixed_y_max else self.fixed_y_max
        if max_val == 0: max_val = 1
        
        # Draw Axes
        painter.setPen(QPen(QColor("#555555"), 2))
        painter.drawLine(margin_left, margin_top, margin_left, height - margin_bottom)
        painter.drawLine(margin_left, height - margin_bottom, width - margin_right, height - margin_bottom)

        # Draw Grid & Y-Labels
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

        # Plot Lines
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
                clamped_val = max(0, val) # Min 0
                y = (height - margin_bottom) - (clamped_val / max_val * graph_height)
                points.append((x, y))

            for i in range(len(points) - 1):
                painter.drawLine(int(points[i][0]), int(points[i][1]), int(points[i+1][0]), int(points[i+1][1]))
            
            # Legend (simplistic, just draw colored text top right)
            # This is left as an exercise for polish, but we rely on title mostly
            # We can draw a small dot + label in title area if needed
            
class PieChart(QWidget):
    def __init__(self, title, used_percent, color_used, color_free="#333333"):
        super().__init__()
        self.title = title
        self.used_percent = min(100, max(0, used_percent))
        self.color_used = color_used
        self.color_free = color_free
        self.setMinimumHeight(250)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Background
        painter.fillRect(self.rect(), QColor("#1e1e1e"))
        
        width = self.width()
        height = self.height()
        side = min(width, height) - 60
        
        rect = QRectF((width - side)/2, (height - side)/2 + 20, side, side)
        
        # Draw Title
        painter.setPen(QColor("#ffffff"))
        painter.setFont(QFont("Segoe UI", 12, QFont.Bold))
        painter.drawText(10, 30, self.title)
        
        # Draw Free Arc
        start_angle = 90 * 16
        span_angle = -360 * 16
        painter.setBrush(QColor(self.color_free))
        painter.setPen(Qt.NoPen)
        painter.drawPie(rect, start_angle, span_angle)
        
        # Draw Used Arc
        used_span = -int(360 * self.used_percent / 100 * 16)
        painter.setBrush(QColor(self.color_used))
        painter.drawPie(rect, start_angle, used_span)
        
        # Draw Center Text
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
        self.setRowCount(len(processes))
        
        # Style
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
        
        self.setWindowTitle("System Graphs")
        self.setFixedSize(1200, 900)
        self.setStyleSheet("""
            QWidget {
                background-color: #121212;
                color: #e0e0e0;
                font-family: 'Segoe UI', 'Roboto', sans-serif;
            }
            QLabel { color: #ffffff; }
            QPushButton {
                background-color: transparent;
                border: 2px solid #5f6368;
                color: #e0e0e0;
                padding: 8px 16px;
                border-radius: 4px;
            }
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

        # Data
        data = self.load_data()
        
        # Scroll Area for Content
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        content = QWidget()
        grid = QGridLayout()
        grid.setSpacing(20)
        
        # 1. CPU History (Line)
        cpu_history = [{'label': 'Usage', 'data': data['cpu_history'], 'color': '#1a73e8'}]
        grid.addWidget(LineGraph("CPU History (%)", cpu_history, y_max=100), 0, 0)
        
        # 2. Network History (Line) - Sent vs Recv
        # Need to convert raw cumulative to rate (KB/s approx)
        net_sent = self.calc_rate(data['net_sent'])
        net_recv = self.calc_rate(data['net_recv'])
        
        # Normalize to avoid huge spikes breaking scale, or just show raw
        # Let's show in KB
        net_sent_kb = [x/1024 for x in net_sent]
        net_recv_kb = [x/1024 for x in net_recv]
        
        net_datasets = [
            {'label': 'Sent', 'data': net_sent_kb, 'color': '#fbbc04'}, # Yellow
            {'label': 'Recv', 'data': net_recv_kb, 'color': '#188038'}  # Green
        ]
        grid.addWidget(LineGraph("Network I/O (KB/interval)", net_datasets, y_label="K"), 0, 1)
        
        # 3. Memory Usage (Pie)
        mem_percent = data['latest_mem']
        grid.addWidget(PieChart("Memory Usage", mem_percent, "#d93025"), 1, 0)
        
        # 4. Disk Usage (Pie)
        disk_percent = data['latest_disk']
        grid.addWidget(PieChart("Disk Usage", disk_percent, "#9c27b0"), 1, 1)
        
        # 5. Top 5 Processes (Table)
        proc_label = QLabel("Top 5 Processes (by CPU)")
        proc_label.setFont(QFont("Segoe UI", 12, QFont.Bold))
        grid.addWidget(proc_label, 2, 0, 1, 2)
        
        proc_table = ProcessTable(data['top_processes'])
        proc_table.setFixedHeight(200)
        grid.addWidget(proc_table, 3, 0, 1, 2)
        
        content.setLayout(grid)
        scroll.setWidget(content)
        layout.addWidget(scroll)
        
        self.setLayout(layout)

    def calc_rate(self, data):
        # Difference between adjacent
        if not data: return []
        deltas = []
        for i in range(1, len(data)):
            d = data[i] - data[i-1]
            deltas.append(d if d >= 0 else 0)
        return deltas

    def load_data(self):
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
                        # CPU
                        res['cpu_history'].append(s.get('cpu', {}).get('usage', 0))
                        # Network
                        net = s.get('network', {})
                        res['net_sent'].append(net.get('bytes_sent', 0))
                        res['net_recv'].append(net.get('bytes_recv', 0))
                        
                    if raw:
                        last = raw[-1]
                        res['latest_mem'] = last.get('memory', {}).get('ram', {}).get('percent', 0)
                        res['latest_disk'] = last.get('disk', {}).get('percent', 0)
                        # Top processes: Sort raw process list just in case
                        procs = last.get('processes', [])
                        # They are already sorted by CPU in get_info.py, but let's take top 5
                        res['top_processes'] = procs[:5]
                        
            except Exception as e:
                print(f"Error loading: {e}")
        return res

    def go_back(self):
        self.close()

    def closeEvent(self, event):
        if self.parent_dashboard:
            self.parent_dashboard.show()
        event.accept()
