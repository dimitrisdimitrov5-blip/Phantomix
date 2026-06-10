from playwright.async_api import async_playwright
import asyncio

class BrowserController:
    def __init__(self):
        self.browser = None
        self.page = None
        self.playwright = None

    async def start(self):
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-setuid-sandbox"]
        )
        self.page = await self.browser.new_page()
        print("✅ Browser started")

    async def stop(self):
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()
        print("🛑 Browser stopped")

    async def go_to(self, url: str):
        await self.page.goto(url, wait_until="domcontentloaded")
        title = await self.page.title()
        return f"✅ Visited: {url} | Page title: {title}"

    async def get_text(self):
        text = await self.page.inner_text("body")
        return text[:3000]

    async def click(self, selector: str):
        await self.page.click(selector)
        return f"✅ Clicked: {selector}"

    async def fill_input(self, selector: str, value: str):
        await self.page.fill(selector, value)
        return f"✅ Filled {selector} with: {value}"

    async def screenshot(self, path: str = "screenshot.png"):
        await self.page.screenshot(path=path)
        return f"✅ Screenshot saved: {path}"

    async def search_google(self, query: str):
        await self.page.goto(f"https://www.google.com/search?q={query}")
        await self.page.wait_for_load_state("domcontentloaded")
        results = await self.page.query_selector_all("h3")
        titles = []
        for r in results[:5]:
            titles.append(await r.inner_text())
        return "\n".join(titles)

    async def get_links(self):
        links = await self.page.query_selector_all("a")
        hrefs = []
        for link in links[:10]:
            href = await link.get_attribute("href")
            text = await link.inner_text()
            if href and href.startswith("http"):
                hrefs.append(f"{text} -> {href}")
        return "\n".join(hrefs)
