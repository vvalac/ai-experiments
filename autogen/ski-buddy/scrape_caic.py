import sys
import os, base64, json
from playwright.sync_api import sync_playwright

def main(lat: float, lng: float) -> None:
    """Fetch and save avalanche conditions screenshot (Sync version)."""
    os.makedirs('images', exist_ok=True)
    
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=[
                '--no-sandbox',
                '--disable-gpu',
                '--disable-dev-shm-usage'
            ]
        )
        context = browser.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            viewport={'width': 1280, 'height': 720},
            java_script_enabled=True,
        )
        
        page = context.new_page()
        page.goto(f'https://avalanche.state.co.us/?lat={lat}&lng={lng}')
        
        # Equivalent of "sleep" in async world
        page.wait_for_timeout(4000)  # 4 seconds
        
        page.screenshot(path='images/avalanche.png')
        browser.close()
        with open('images/avalanche.png', "rb") as f:
            encoded = base64.b64encode(f.read()).decode("utf-8")
        print(json.dumps({"image_base64": encoded}))        

if __name__ == "__main__":
    # Optionally read lat/lng from command line, or just hardcode defaults
    if len(sys.argv) == 3:
        lat_arg = float(sys.argv[1])
        lng_arg = float(sys.argv[2])
    else:
        # Fallback to a default coordinate if none provided
        lat_arg = 39.6427
        lng_arg = -105.8718
    
    main(lat_arg, lng_arg)
