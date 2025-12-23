import os
import sys

# 1. GPU FLAGS
os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] = (
    "--ignore-gpu-blocklist "
    "--enable-gpu-rasterization "
    "--enable-webgl "
    "--enable-webgl2-compute-context "
    "--use-gl=desktop"
)

from PyQt6.QtCore import QUrl, QTimer, QPoint, Qt
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QMessageBox
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEngineProfile, QWebEngineSettings
from PyQt6.QtTest import QTest

# --- CONFIGURATION ---
TARGET_URL = "https://www.flightradar24.com/45.33,-75.67/13"
WINDOW_SIZE = (480, 320)
ZOOM_LEVEL = 0.8 

CLEAN_CSS = """
    header, footer, .side-panel, .header-container, 
    #search-container, .gm-style-cc, .ads-container, 
    #premium-signup-banner, .map-controls, .ov-control,
    #social-sharing, .filters-container, .tool-panel { display: none !important; }
    
    .fc-consent-root, .fc-dialog-container, .modal-backdrop, 
    .modal, #login-modal, .login-popup, #cookie-consent { 
        display: none !important; visibility: hidden !important; pointer-events: none !important;
    }
    
    body, html { overflow: hidden !important; margin: 0 !important; background: black; }
    
    #map-container, #map { 
        position: fixed !important; top: 0 !important; left: 0 !important;
        width: 480px !important; height: 320px !important; z-index: 9999 !important;
    }
"""
class RadarWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setFixedSize(WINDOW_SIZE[0], WINDOW_SIZE[1])
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)

        # --- BROWSER SETUP ---
        self.browser = QWebEngineView(self)
        browser_settings = self.browser.settings()
        browser_settings.setAttribute(QWebEngineSettings.WebAttribute.WebGLEnabled, True)
        self.browser.setZoomFactor(ZOOM_LEVEL)
        self.browser.setUrl(QUrl(TARGET_URL))
        self.setCentralWidget(self.browser)

        # --- BUTTON OVERLAY ---
        self.overlay = QWidget(self)
        self.overlay.setGeometry(410, 10, 60, 90) 
        layout = QVBoxLayout(self.overlay)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)

        # Style for buttons
        btn_style = "background-color: rgba(40, 40, 40, 180); color: white; border: 1px solid white; border-radius: 8px; font-size: 14px; font-weight: bold;"

        self.btn_close = QPushButton("X", self.overlay)
        self.btn_close.setFixedSize(40, 40)
        self.btn_close.setStyleSheet(btn_style.replace("white", "#ff4444"))
        self.btn_close.clicked.connect(self.close)
        layout.addWidget(self.btn_close)

        self.btn_reboot = QPushButton("R", self.overlay)
        self.btn_reboot.setFixedSize(40, 40)
        self.btn_reboot.setStyleSheet(btn_style)
        self.btn_reboot.clicked.connect(self.reboot_pi)
        layout.addWidget(self.btn_reboot)

        # Timers
        self.cleanup_timer = QTimer()
        self.cleanup_timer.timeout.connect(self.run_cleaner)
        self.cleanup_timer.start(2000) 

        self.click_timer = QTimer()
        self.click_timer.setSingleShot(True)
        self.click_timer.timeout.connect(self.click_center)
        self.click_timer.start(10000) # Wait 10s for slow loads

    def reboot_pi(self):
        reply = QMessageBox.question(self, 'Reboot', "Restart FlightBox?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            os.system('sudo reboot')

    def click_center(self):
        center_point = QPoint(int(WINDOW_SIZE[0] / 2), int(WINDOW_SIZE[1] / 2))
        QTest.mouseClick(self.browser.focusProxy(), Qt.MouseButton.LeftButton, pos=center_point)

    def run_cleaner(self):
        # JavaScript with SCROLL-TO-BOTTOM and CLICK logic
        script = f"""
            (function() {{
                // 1. Find buttons that look like "Agree" or "Accept"
                var buttons = document.querySelectorAll('button, a, span');
                buttons.forEach(btn => {{
                    var text = btn.innerText.toUpperCase();
                    if (text.includes('AGREE') || text.includes('ACCEPT') || text.includes('CONSENT')) {{
                        // Scroll the parent container to the bottom to "read" terms
                        var scrollParent = btn.parentElement;
                        while (scrollParent) {{
                            scrollParent.scrollTop = scrollParent.scrollHeight;
                            scrollParent = scrollParent.parentElement;
                            if (scrollParent === document.body) break;
                        }}
                        btn.click();
                    }}
                }});

                // 2. Remove the gray overlay roots
                var trash = document.querySelectorAll('.fc-consent-root, .fc-dialog-container, #sp_message_container');
                trash.forEach(el => el.remove());

                // 3. Inject Kiosk CSS
                var style = document.getElementById('kiosk-style');
                if (!style) {{
                    style = document.createElement('style');
                    style.id = 'kiosk-style';
                    document.head.appendChild(style);
                }}
                style.innerHTML = `{CLEAN_CSS}`;
            }})();
        """
        self.browser.page().runJavaScript(script)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            self.close()

if __name__ == "__main__":
    os.environ["QT_XCB_GL_INTEGRATION"] = "xcb_egl"
    app = QApplication(sys.argv)
    app.setAttribute(Qt.ApplicationAttribute.AA_UseDesktopOpenGL)
    window = RadarWindow()
    window.show()
    sys.exit(app.exec())