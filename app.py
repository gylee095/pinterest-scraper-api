from flask import Flask, request, jsonify
import asyncio
from playwright.async_api import async_playwright
import traceback

app = Flask(__name__)

def fix_image_url(url: str) -> str:
    size_tokens = ["/60x60/", "/236x/", "/474x/", "/564x/", "/736x/"]
    for token in size_tokens:
        if token in url:
            return url.replace(token, "/originals/")
    return url

async def collect_highres_image_urls(keyword: str, max_images: int = 10) -> list:
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=[
                "--no-sandbox",
                "--disable-dev-shm-usage",
                "--disable-extensions",
                "--disable-gpu",
                "--disable-setuid-sandbox"
            ]
        )
        context = await browser.new_context()
        page = await context.new_page()
        await page.route("**/*", lambda route, request: route.abort() if request.resource_type in ["stylesheet", "font", "script"] else route.continue_())

        search_url = f"https://www.pinterest.com/search/pins/?q={keyword}"
        await page.goto(search_url, timeout=60000)

        image_urls = set()
        previous_height = 0

        while len(image_urls) < max_images:
            await page.mouse.wheel(0, 2000)
            await page.wait_for_timeout(2000)

            images = await page.query_selector_all("img")
            for img in images:
                src = await img.get_attribute("src") or await img.get_attribute("srcset")
                if src:
                    src = src.split()[0]  # srcset 대응
                    if "pinimg.com" in src:
                        image_urls.add(fix_image_url(src))
                if len(image_urls) >= max_images:
                    break

            new_height = await page.evaluate("document.body.scrollHeight")
            if new_height == previous_height:
                break
            previous_height = new_height

        await browser.close()
        return list(image_urls)

@app.route("/scrape", methods=["POST"])
def scrape():
    try:
        keyword = request.json.get("keyword", "")
        if not keyword:
            return jsonify({
                "status": "error",
                "message": "keyword is required"
            }), 400

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        image_urls = loop.run_until_complete(collect_highres_image_urls(keyword, max_images=10))

        return jsonify({
            "status": "ok",
            "data": {
                "images": image_urls
            }
        }), 200

    except Exception as e:
        print("🛑 예외 발생:", e)
        traceback.print_exc()
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
