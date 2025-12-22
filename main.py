from playwright.sync_api import sync_playwright
import time

def run_radar():
    with sync_playwright() as p:
        # Launch browser with specific window size
        # We use 'headless=False' so you can see it on your PC
        browser = p.chromium.launch(headless=False)
        
        # Create a window at your LCD's resolution
        context = browser.new_context(
            viewport={'width': 480, 'height': 320},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
        )
        
        page = context.new_page()
        
        # Go to your specific coordinates
        print("Navigating to FlightRadar24...")
        page.goto("https://www.flightradar24.com/45.41,-75.69/11", wait_until="networkidle")

        # MAGIC PART: This CSS hides the sidebars and headers 
        # so only the map shows on your tiny screen
        page.add_style_tag(content="""
            #map-container .gm-style-cc, 
            .header-container, 
            .footer-container, 
            #search-container,
            .side-panel { display: none !important; }
            #map { width: 100vw !important; height: 100vh !important; }
        """)

        print("Radar is live. Press Ctrl+C in terminal to stop.")
        
        # Keep the window open
        while True:
            time.sleep(1)

if __name__ == "__main__":
    run_radar()