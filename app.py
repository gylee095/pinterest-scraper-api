from flask import Flask, request, jsonify
from playwright.sync_api import sync_playwright

app = Flask(__name__)

@app.route("/scrape", methods=["POST"])
def scrape():
    keyword = request.json.get("keyword", "")
    if not keyword:
        return jsonify({"error": "keyword is required"}), 400

    search_url = f"https://www.pinterest.com/search/pins/?q={keyword}"
    image_urls = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(search_url, timeout=60000)
        page.mouse.wheel(0, 3000)
        page.wait_for_timeout(3000)

        images = page.query_selector_all("img")
        for img in images:
            src = img.get_attribute("src")
            if src and "pinimg.com" in src:
                fixed = fix_image_url(src)
                image_urls.append(fixed)
            if len(image_urls) >= 10:
                break

        browser.close()

    return jsonify({
    "status": "ok",
    "data": {
        "images": image_urls
    }
})



def fix_image_url(url: str) -> str:
    size_tokens = ["/60x60/", "/236x/", "/474x/", "/564x/", "/736x/"]
    for token in size_tokens:
        if token in url:
            return url.replace(token, "/originals/")
    return url


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
