from flask import Flask, request, jsonify
from playwright.sync_api import sync_playwright
import traceback

app = Flask(__name__)

# ✅ 리소스 차단 함수 (CSS, JS, 폰트 차단)
def block_resources(route, request):
    if request.resource_type in ["stylesheet", "font", "script"]:
        route.abort()
    else:
        route.continue_()

@app.route("/scrape", methods=["POST"])
def scrape():
    try:
        keyword = request.json.get("keyword", "")
        if not keyword:
            return jsonify({
                "status": "error",
                "message": "keyword is required"
            }), 400

        search_url = f"https://www.pinterest.com/search/pins/?q={keyword}"
        image_urls = []

        with sync_playwright() as p:
            browser = p.chromium.launch(
                headless=True,
                args=[
                    "--no-sandbox",
                    "--disable-dev-shm-usage",
                    "--disable-extensions",
                    "--disable-gpu",
                    "--disable-setuid-sandbox"
                ]
            )
            page = browser.new_page()
            page.route("**/*", block_resources)  # ✅ 리소스 차단 훅 등록
            page.goto(search_url, timeout=15000)
            page.wait_for_selector("img", timeout=8000)  # ✅ 이미지 로딩 대기

            images = page.query_selector_all("img")
            for img in images:
                src = img.get_attribute("src")
                if src and "pinimg.com" in src:
                    image_urls.append(fix_image_url(src))
                if len(image_urls) >= 3:  # ✅ 이미지 수 줄이기
                    break

            browser.close()

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

def fix_image_url(url: str) -> str:
    size_tokens = ["/60x60/", "/236x/", "/474x/", "/564x/", "/736x/"]
    for token in size_tokens:
        if token in url:
            return url.replace(token, "/originals/")
    return url

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
