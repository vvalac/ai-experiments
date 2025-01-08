from playwright.async_api import async_playwright
import os
import asyncio

async def get_avalanche_info(lat: float, lng: float) -> None:
    """Fetch and save avalanche conditions screenshot."""
    os.makedirs('images', exist_ok=True)
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=[
                '--no-sandbox',
                '--disable-gpu',
                '--disable-dev-shm-usage'
            ])
        # Create context with more browser-like properties
        context = await browser.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            viewport={'width': 1280, 'height': 720},
            java_script_enabled=True,
        )
        
        page = await context.new_page()
        # Add some delay to seem more human-like
        await page.goto(f'https://avalanche.state.co.us/?lat={lat}&lng={lng}')
        await asyncio.sleep(4)  # Small delay before screenshot
        await page.screenshot(path='images/avalanche.png')
        await browser.close()

# # Test the function
if __name__ == "__main__":
    # Denver coordinates
    asyncio.run(get_avalanche_info(39.6427, -105.8718))