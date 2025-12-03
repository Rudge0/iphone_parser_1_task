import pprint

import requests
from bs4 import BeautifulSoup
import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "iphone_parser_project.settings")
django.setup()

from parser_app.models import Product, ProductPhoto, ProductCharacteristic


def fetch_page(url: str) -> str:
    response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
    response.raise_for_status()
    return response.text



def parse_price(text: str) -> float:
    clean = (text
             .replace("₴", "")
             .replace(" ", "")
             .replace("грн", '')
             .strip()
             )
    try:
        return float(clean)
    except:
        return None


def scrape_product(url: str) -> Product:
    html = fetch_page(url)
    soup = BeautifulSoup(html, "html.parser")

    # Product main
    full_name_tag = soup.find("h1", class_="desktop-only-title")
    full_name = full_name_tag.text.strip() if full_name_tag else "Без назви"

    # Color and memory
    color = None
    memory = None

    parts = full_name.split()
    for p in parts:
        if "gb" in p.lower() or "GB" in p.lower():
            memory = p.upper()
        if p.lower() in ["black", "white", "blue", "gold", "titanium", "green"]:
            color = p.capitalize()


    # Price
    price_regular = parse_price(soup.find("div", class_="price-wrapper").text)

    try:
        price_discount = parse_price(soup.find("span", class_="red-price").text)
        print(price_discount)
    except:
        price_discount = None


    # Product code
    code_tag = soup.find("span", class_="br-pr-code-val")
    product_code = code_tag.text.strip() if code_tag else None


    # Reviews amount
    reviews_count = 0
    try:
        reviews_link = (soup.select_one('a.scroll-to-element[href="#reviews-list"]')
                        .get_text(strip=True)
                        .replace("Відгуки (", "")
                        .replace(")", "")
                        .strip()
                        )

        reviews_count = int(reviews_link)
    except:
        reviews_count = 0

    # Characteristics
    characteristics = {}
    sections = soup.select("div.br-pr-chr-item")

    for section in sections:
        actual = section.select("span")
        for i in range (0, len(actual), 2):
            name = actual[i].get_text(strip=True)
            link = actual[i + 1].get_text(strip=True).replace("                                ", "")

            characteristics[name] = link


    # Screen diagonal
    screen_diagonal = characteristics.get("Діагональ екрану")

    # Screen resolution
    screen_resolution = characteristics.get("Роздільна здатність екрану")

    # Manufacturer
    manufacturer = characteristics.get("Виробник")

    # Creating product
    product = Product.objects.create(
        url=url,
        full_name=full_name,
        color=color,
        memory=memory,
        manufacturer=manufacturer,
        price_regular=price_regular,
        price_discount=price_discount,
        product_code=product_code,
        reviews_count=reviews_count,
        screen_diagonal=screen_diagonal,
        screen_resolution=screen_resolution,
    )

    # Storing characteristics
    for name, value in characteristics.items():
        if not name or not value:
            continue

        ProductCharacteristic.objects.create(
            product=product,
            name=name,
            value=value
        )

    # Product`s photos
    photo_urls = []

    # main photos
    main_images = soup.find_all("img", class_="br-main-img")
    for img in main_images:
        src = img.get("src")
        if src:
            if src.startswith("//"):
                src = "https:" + src
            elif src.startswith("/"):
                src = "https://brain.com.ua" + src
            photo_urls.append(src)

    # Preview`s photos
    preview_images = soup.find_all("img", class_="br-pr-img")
    for img in preview_images:
        src = img.get("src")
        if src:
            if src.startswith("//"):
                src = "https:" + src
            elif src.startswith("/"):
                src = "https://brain.com.ua" + src
            photo_urls.append(src)

    # Storing into bd
    for url in photo_urls:
        ProductPhoto.objects.create(product=product, url=url)

    print(f"Створено продукт: {product.full_name}")
    print(f"Колір: {color}")
    print(f"Об'єм пам'яті: {memory}")
    print(f"Виробник: {manufacturer}")
    print(f"Звичайна ціна: {price_regular}")
    if price_discount:
        print(f"Ціна зі знижкою: {price_discount}")
    print(f"Код товару: {product_code}")
    print(f"Кількість відгуків: {reviews_count}")
    print(f"Діагональ екрану: {screen_diagonal}")
    print(f"Розширення дисплею: {screen_resolution}")

    pprint.pprint(characteristics)

    return product

if __name__ == "__main__":
    test_url = "https://brain.com.ua/ukr/Mobilniy_telefon_Apple_iPhone_16_Pro_Max_256GB_Black_Titanium-p1145443.html"
    scrape_product(test_url)
