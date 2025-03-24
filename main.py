from playwright.sync_api import sync_playwright

def collect_highres_image_urls(keyword: str, max_images: int = 10) -> list:
    image_urls = []
    search_url = f"https://www.pinterest.com/search/pins/?q={keyword}"

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()

        page.goto(search_url)
        page.wait_for_timeout(5000)

        img_elements = page.query_selector_all("img")
        for img in img_elements:
            src = img.get_attribute("src")
            if src and "http" in src and src not in image_urls:
                image_urls.append(src)
            if len(image_urls) >= max_images:
                break

        browser.close()

    return image_urls