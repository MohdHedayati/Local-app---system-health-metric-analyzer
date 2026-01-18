import os
import json
import sys

from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QMessageBox,
    QApplication,
)
from PyQt5.QtCore import Qt
import subprocess
from constants import TOKEN_FILE
from PyQt5.QtGui import QFont, QColor, QPainter

class MonitoringIndicator(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedSize(30, 30)
        
        # Position: Top Right (adjust based on screen width)
        desktop = QApplication.desktop()
        screen_rect = desktop.screenGeometry(desktop.primaryScreen())
        self.move(screen_rect.width() - 60, 60)
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setBrush(QColor("#00ff00")) # Bright Green
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(0, 0, 30, 30)




class DashboardWindow(QWidget):
    def __init__(self, user_name: str):
        super().__init__()
        self.user_name = user_name or "User"
        self.monitor_process = None
        self.indicator = None

        self.setWindowTitle("Device Health Dashboard")
        self.setFixedSize(1200, 900)

        # Apply Dark Mode Stylesheet
        self.setStyleSheet("""
            QWidget {
                background-color: #121212;
                color: #e0e0e0;
                font-family: 'Segoe UI', 'Futura', sans-serif;
            }
            QLabel {
                font-size: 36px;
                font-weight: bold;
                color: #ffffff;
                margin-bottom: 30px;
            }
            QPushButton {
                background-color: #333333;
                border: 2px solid #333333;
                color: white;
                padding: 12px 24px;
                font-size: 26px;
                border-radius: 8px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #424242;
                border-color: #424242;
            }
            QPushButton:pressed {
                background-color: #212121;
            }
        """)

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)
        layout.setContentsMargins(50, 50, 50, 50)
        layout.setSpacing(20)

        self.hello_label = QLabel(f"Hello, {self.user_name}!")
        self.hello_label.setAlignment(Qt.AlignCenter)

        self.start_btn = QPushButton("Start Monitoring")
        self.start_btn.setCursor(Qt.PointingHandCursor)
        self.start_btn.setStyleSheet("""
            QPushButton {
                background-color: #1a73e8;
                border: 2px solid #1a73e8;
            }
            QPushButton:hover {
                background-color: #1557b0;
                border-color: #1557b0;
            }
        """)

        self.stop_btn = QPushButton("Stop Monitoring")
        self.stop_btn.setCursor(Qt.PointingHandCursor)
        self.stop_btn.setStyleSheet("""
            QPushButton {
                background-color: #d93025;
                border: 2px solid #d93025;
            }
            QPushButton:hover {
                background-color: #a50e0e;
                border-color: #a50e0e;
            }
        """)

        self.upload_btn = QPushButton("Upload Data")
        self.upload_btn.setCursor(Qt.PointingHandCursor)
        self.upload_btn.setStyleSheet("""
            QPushButton {
                background-color: #188038;
                border: 2px solid #188038;
            }
            QPushButton:hover {
                background-color: #137333;
                border-color: #137333;
            }
        """)

        self.logout_btn = QPushButton("Logout")
        self.logout_btn.setCursor(Qt.PointingHandCursor)
        self.logout_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: 2px solid #5f6368;
                color: #e0e0e0;
            }
            QPushButton:hover {
                background-color: #333333;
                border-color: #e0e0e0;
            }
        """)

        self.graphs_btn = QPushButton("View Graphs")
        self.graphs_btn.setCursor(Qt.PointingHandCursor)
        self.graphs_btn.setStyleSheet("""
            QPushButton {
                background-color: #6200ea;
                border: 2px solid #6200ea;
            }
            QPushButton:hover {
                background-color: #3700b3;
                border-color: #3700b3;
            }
        """)

        self.start_btn.clicked.connect(self.start_monitoring)
        self.stop_btn.clicked.connect(self.stop_monitoring)
        self.upload_btn.clicked.connect(self.handle_upload)
        self.graphs_btn.clicked.connect(self.show_graphs)
        self.logout_btn.clicked.connect(self.handle_logout)

        layout.addWidget(self.hello_label)
        layout.addWidget(self.start_btn)
        layout.addWidget(self.stop_btn)
        layout.addWidget(self.upload_btn)
        layout.addWidget(self.graphs_btn)
        layout.addSpacing(20)
        layout.addWidget(self.logout_btn)

        self.setLayout(layout)

    def show_graphs(self):
        from graphs import GraphsWindow
        self.graphs_window = GraphsWindow(self.user_name, parent_dashboard=self)
        self.graphs_window.show()
        self.hide()


    def handle_logout(self):
        # Delete local token file  so next launch shows login
        if os.path.exists(TOKEN_FILE):
            try:
                os.remove(TOKEN_FILE)
            except Exception as e:
                QMessageBox.warning(
                    self,
                    "Logout Warning",
                    f"Could not delete token file:\n{e}",
                )

        QMessageBox.information(self, "Logged Out", "You have been logged out.")
        if self.monitor_process and self.monitor_process.poll() is None:
            self.monitor_process.terminate()
            self.monitor_process.wait()
        
        if self.indicator:
            self.indicator.close()
            self.indicator = None
        # After logout, close dashboard and reopen login window
        from auth import LoginWindow

        self.login_window = LoginWindow()
        self.login_window.show()
        self.close()

    def handle_upload(self):
        try:
            from uploader import upload
            upload()
            QMessageBox.information(self, "Success", "Data uploaded successfully.")
        except Exception as e:
            QMessageBox.critical(self, "Upload Failed", str(e))
    def start_monitoring(self):
        if self.monitor_process and self.monitor_process.poll() is None:
            QMessageBox.information(self, "Info", "Monitoring already running.")
            return

        args = [sys.executable, sys.argv[0], "--child-get-info"]
        kwargs = {
            "stdout": subprocess.DEVNULL,
            "stderr": subprocess.DEVNULL,
            "close_fds": True
        }
        # Hide console on Windows
        if sys.platform == "win32" and hasattr(subprocess, "CREATE_NO_WINDOW"):
            kwargs["creationflags"] = subprocess.CREATE_NO_WINDOW

        self.monitor_process = subprocess.Popen(args, **kwargs)

        self.indicator = MonitoringIndicator()
        self.indicator.show()

        QMessageBox.information(self, "Started", "System monitoring started.")


    def stop_monitoring(self):
        if self.monitor_process and self.monitor_process.poll() is None:
            self.monitor_process.terminate()
            self.monitor_process.wait()
            self.monitor_process = None
            
            if self.indicator:
                self.indicator.close()
                self.indicator = None
                
            file_path = "data/history.json"
            if os.path.exists(file_path):
                os.remove(file_path)
            QMessageBox.information(self, "Stopped", "Monitoring stopped.")
        else:
            QMessageBox.information(self, "Info", "Monitoring not running.")



