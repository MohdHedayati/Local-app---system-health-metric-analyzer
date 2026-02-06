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
from PyQt5.QtCore import QUrl,Qt, QThread, pyqtSignal, QTimer
import subprocess
from utils.constants import TOKEN_FILE
from PyQt5.QtGui import QFont, QColor, QPainter,QDesktopServices, QIcon

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


class UploadIndicator(QWidget):
    """Small centered widget that indicates an upload is in progress."""
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowFlags(
            Qt.WindowStaysOnTopHint |
            Qt.FramelessWindowHint |
            Qt.Tool
        )
        self.setAttribute(Qt.WA_TranslucentBackground)

        self.label = QLabel(
            "Uploading, Do Not Close the App, Please Wait 2-3 minutes...",
            self
        )
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setWordWrap(True)

        font = QFont()
        font.setPointSize(12)
        font.setBold(True)
        self.label.setFont(font)

        layout = QVBoxLayout(self)
        layout.addWidget(self.label)
        layout.setContentsMargins(12, 12, 12, 12)

        # Optional: control wrapping width
        self.label.setMaximumWidth(320)

        # Resize widget to fit contents
        self.adjustSize()

        self.center(parent)
    def center(self, parent=None):
        if parent:
            rect = parent.geometry()
        else:
            rect = QApplication.primaryScreen().geometry()

        self.move(
            rect.center().x() - self.width() // 2,
            rect.center().y() - self.height() // 2
        )



class UploadWorker(QThread):
    """Run the uploader in a separate thread and emit signals on finish."""
    success = pyqtSignal()
    failure = pyqtSignal(str)

    def run(self):
        try:
            # import inside thread to avoid blocking main thread import issues
            from utils.uploader import upload
            upload()
            self.success.emit()
        except Exception as e:
            # send stringified exception back to UI
            self.failure.emit(str(e))




class DashboardWindow(QWidget):
    def __init__(self, user_name: str):
        super().__init__()
        from utils.constants import DATA_FILE
        if os.path.exists(DATA_FILE):
            os.remove(DATA_FILE)
        self.user_name = user_name or "User"
        self.monitor_process = None
        self.indicator = None
        # Guard to prevent concurrent start attempts
        self._starting_monitor = False

        # icon
        from utils.constants import ICON_PATH
        self.setWindowIcon(QIcon(ICON_PATH))

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
        # Create the Website Button
        self.site_btn = QPushButton("Visit Our Site !")
        self.site_btn.setCursor(Qt.PointingHandCursor)
        self.site_btn.setStyleSheet("""
            QPushButton {
                background-color: #FFD700; /* Bright Golden */
                border: 2px solid #FFD700;
                color: #000000; /* Black text for high contrast on gold */
            }
            QPushButton:hover {
                background-color: #FFC107; /* Slightly darker amber/gold */
                border-color: #FFC107;
            }
            QPushButton:pressed {
                background-color: #B8860B; /* Darker golden rod when clicked */
            }
        """)

        # Connect to browser opener
        self.site_btn.clicked.connect(lambda: QDesktopServices.openUrl(QUrl("https://systemhealthmetricsanalyser-sszqxkx5onxfct2skm4c94.streamlit.app/")))
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
        layout.addWidget(self.site_btn) # <--- Added here
        layout.addSpacing(20)
        layout.addWidget(self.logout_btn)

        self.setLayout(layout)

        self.setLayout(layout)
        self.alert_timer = QTimer(self)
        self.alert_timer.setInterval(2000)  # check every 2 seconds
        self.alert_timer.timeout.connect(self.check_and_show_alert)
        self.alert_timer.start()

        self._alert_shown = False  # prevent spamming

        self.start_monitoring() # auto start on login

    def show_graphs(self):
        from pages.graphs import GraphsWindow
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
        from pages.auth import LoginWindow

        self.login_window = LoginWindow()
        self.login_window.show()
        self.close()

    def handle_upload(self):
        # Prevent multiple simultaneous uploads
        if getattr(self, "upload_worker", None) and self.upload_worker.isRunning():
            QMessageBox.information(self, "Info", "Upload already in progress.")
            return

        # Create and show the upload indicator (centered on this dashboard)
        self.upload_widget = UploadIndicator(parent=self)
        self.upload_widget.show()

        # Disable upload button while running
        self.upload_btn.setEnabled(False)

        # Start worker thread to perform upload
        self.upload_worker = UploadWorker()

        def on_success():
            self.upload_widget.close()
            self.upload_btn.setEnabled(True)
            QMessageBox.information(self, "Success", "Data uploaded successfully.")

        def on_failure(msg):
            self.upload_widget.close()
            self.upload_btn.setEnabled(True)
            QMessageBox.critical(self, "Upload Failed", msg)

        self.upload_worker.success.connect(on_success)
        self.upload_worker.failure.connect(on_failure)
        self.upload_worker.start()
    def start_monitoring(self):
        if self.monitor_process and self.monitor_process.poll() is None:
            QMessageBox.information(self, "Info", "Monitoring already running.")
            return
        from utils.constants import DATA_FILE
        if os.path.exists(DATA_FILE):
            os.remove(DATA_FILE)
        # Prevent concurrent starts
        if getattr(self, "_starting_monitor", False):
            return

        

        self._starting_monitor = True
        try:
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
        finally:
            self._starting_monitor = False


    def stop_monitoring(self):
        if self.monitor_process and self.monitor_process.poll() is None:
            self.monitor_process.terminate()
            self.monitor_process.wait()
            self.monitor_process = None
            
            if self.indicator:
                self.indicator.close()
                self.indicator = None
            
            from utils.constants import DATA_FILE
            if os.path.exists(DATA_FILE):
                os.remove(DATA_FILE)
            QMessageBox.information(self, "Stopped", "Monitoring stopped.")
        else:
            QMessageBox.information(self, "Info", "Monitoring not running.")
    
    def check_and_show_alert(self):
        if self._alert_shown:
            return

        if self.should_show_alert():
            self._alert_shown = True
            QMessageBox.information(
                self,
                "Attention Required",
                "Monitoring has Completed Minimum Quota, You May Upload Now"
            )
    def should_show_alert(self):
        from utils.constants import DATA_FILE
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, "r") as f:
                    content = json.load(f)
                    if isinstance(content, dict):
                        raw = content.get("data", {}).get("aggregates", [])
                    else:
                        raw = []
                    # print(len(raw))
                    if raw:
                        return len(raw) >= 5
                    else:
                        return False
            except Exception as e:
                print(f"Error loading: {e}")
                return False
        else:
            return False

    def closeEvent(self, event):
        # Ensure monitoring child is terminated when dashboard closes
        try:
            if self.monitor_process and self.monitor_process.poll() is None:
                try:
                    self.monitor_process.terminate()
                    self.monitor_process.wait(timeout=5)
                except Exception:
                    pass
                self.monitor_process = None
        except Exception:
            pass

        if self.indicator:
            try:
                self.indicator.close()
            except Exception:
                pass
            self.indicator = None

        event.accept()     


