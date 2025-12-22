import sys
import os
from PyQt6.QtCore import QUrl, QTimer, QPoint, Qt
from PyQt6.QtWidgets import QApplication, QMainWindow
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEngineProfile, QWebEnginePage
from PyQt6.QtTest import QTest # For simulating the click

# --- CONFIGURATION ---
TARGET_URL = "https://www.flightradar24.com/45.32,-75.67/13"
WINDOW_SIZE = (480, 320)
ZOOM_LEVEL = 0.8 

CLEAN_CSS = """
    header, footer, .side-panel, .header-container, 
    #search-container, .gm-style-cc, .ads-container, 
    #premium-signup-banner, .map-controls, .ov-control,
    #social-sharing, .filters-container, .tool-panel { 
        display: none !important; 
    }
    .fc-consent-root, .fc-dialog-container, .modal-backdrop, 
    .modal, #login-modal, .login-popup, #cookie-consent { 
        display: none !important; 
        visibility: hidden !important; 
        pointer-events: none !important;
    }
    body, html { overflow: hidden !important; margin: 0 !important; }
    #map-container, #map { 
        position: fixed !important; top: 0 !important; left: 0 !important;
        width: 480px !important; height: 320px !important; z-index: 9999 !important;
    }
"""

class RadarWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setFixedSize(WINDOW_SIZE[0], WINDOW_SIZE[1])
        self.setWindowTitle("FlightBox Radar")

        storage_path = os.path.join(os.path.dirname(__file__), "radar_profile")
        self.profile = QWebEngineProfile("RadarProfile", self)
        self.profile.setPersistentStoragePath(storage_path)
        self.profile.setPersistentCookiesPolicy(QWebEngineProfile.PersistentCookiesPolicy.AllowPersistentCookies)

        self.browser = QWebEngineView(self)
        self.page = QWebEnginePage(self.profile, self.browser)
        self.browser.setPage(self.page)
        
        self.browser.setZoomFactor(ZOOM_LEVEL)
        self.browser.setUrl(QUrl(TARGET_URL))
        
        # A. Cleanup Timer: Runs every 2 seconds
        self.cleanup_timer = QTimer()
        self.cleanup_timer.timeout.connect(self.run_cleaner)
        self.cleanup_timer.start(2000) 

        # B. Center Click Timer: Runs ONCE after 6 seconds
        self.click_timer = QTimer()
        self.click_timer.setSingleShot(True)
        self.click_timer.timeout.connect(self.click_center)
        self.click_timer.start(6000) 
        
        self.setCentralWidget(self.browser)

    def click_center(self):
        print("Performing auto-click to clear UI...")
        # Calculate the middle of our 480x320 window
        center_x = int(WINDOW_SIZE[0] / 2)
        center_y = int(WINDOW_SIZE[1] / 2)
        center_point = QPoint(center_x, center_y)
        
        # Simulate a left-click on the browser widget
        QTest.mouseClick(self.browser.focusProxy(), Qt.MouseButton.LeftButton, pos=center_point)

    def run_cleaner(self):
        script = f"""
            (function() {{
                var buttons = document.querySelectorAll('button');
                buttons.forEach(btn => {{
                    var text = btn.innerText.toUpperCase();
                    if (text.includes('AGREE') || text.includes('CONSENT') || text.includes('ACCEPT')) {{
                        var scrollable = btn.closest('div');
                        if (scrollable) {{ scrollable.scrollTop = scrollable.scrollHeight; }}
                        btn.click();
                    }}
                }});
                var trash = document.querySelectorAll('.fc-consent-root, .fc-dialog-container');
                trash.forEach(el => el.remove());

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

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = RadarWindow()
    
    # Use FullScreen for the Pi's LCD
    window.showFullScreen() 
    
    sys.exit(app.exec())