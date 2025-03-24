import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options


def setup_driver(headless=True):
    options = Options()
    if headless:
        options.add_argument("--headless=new")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)


def fix_image_url(url):
    size_tokens = ["/60x60/", "/236x/", "/474x/", "/564x/", "/736x/"]
    for token in size_tokens:
        if token in url:
            return url.replace(token, "/originals/")
    return url


def collect_highres_image_urls(keyword, max_images=10):
    print(f"[🔍] '{keyword}' 고화질 이미지 URL 수집 중...")

    driver = setup_driver(headless=True)
    search_url = f"https://www.pinterest.com/search/pins/?q={keyword}"
    driver.get(search_url)

    image_urls = set()
    last_height = driver.execute_script("return document.body.scrollHeight")

    while len(image_urls) < max_images:
        images = driver.find_elements(By.TAG_NAME, "img")
        for img in images:
            src = img.get_attribute("src")
            if src and "pinimg.com" in src:
                highres = fix_image_url(src)
                image_urls.add(highres)
            if len(image_urls) >= max_images:
                break

        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)

        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

    driver.quit()
    return list(image_urls)
