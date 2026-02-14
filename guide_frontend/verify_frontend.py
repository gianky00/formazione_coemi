from playwright.sync_api import sync_playwright


def verify_frontend() -> None:
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        # 1. Home Page
        try:
            page.goto("http://localhost:4173/", timeout=60000)
            page.wait_for_selector("text=Benvenuto in Intelleo", timeout=30000)
            page.screenshot(path="/home/jules/verification/home_page.png", full_page=True)
        except Exception:
            page.screenshot(path="/home/jules/verification/home_fail.png", full_page=True)

        # 2. Import Guide
        try:
            page.goto("http://localhost:4173/import", timeout=60000)
            # Try waiting for a broader selector first to ensure page load
            page.wait_for_selector("h1", timeout=30000)
            page.screenshot(path="/home/jules/verification/import_guide.png", full_page=True)
        except Exception:
            page.screenshot(path="/home/jules/verification/import_fail.png", full_page=True)

        browser.close()


if __name__ == "__main__":
    verify_frontend()
