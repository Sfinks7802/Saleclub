import requests
import re


def is_correct_wb_url(url):
    # Проверяет, является ли ссылка корректной ссылкой Wildberries
    # Основные домены Wildberries
    wb_domains = [
        "wildberries.ru",
        "www.wildberries.ru",
        "wb.ru",
        "www.wb.ru",
        "wildberries.kg",
        "www.wildberries.kg",
        "wildberries.kz",
        "www.wildberries.kz",
        "wildberries.by",
        "www.wildberries.by",
    ]

    # Проверяем, что ссылка начинается с http/https
    if not url.startswith(("http://", "https://")):
        return False

    # Проверяем, что это домен Wildberries
    is_wb_domain = any(domain in url for domain in wb_domains)
    if not is_wb_domain:
        return False

    # Проверяем, что ссылка содержит путь к товару
    valid_paths = ["/catalog/", "/card/"]
    has_valid_path = any(path in url for path in valid_paths)
    if not has_valid_path:
        return False

    # Проверяем, что в ссылке есть числовой артикул
    numbers = re.findall(r"\d+", url)
    if not numbers:
        return False

    # Ищем достаточно длинное число (артикул обычно от 6 цифр)
    long_numbers = [num for num in numbers if len(num) >= 6]
    if not long_numbers:
        return False

    return True


def extract_product_id(url):
    # Извлекает артикул товара из ссылки
    try:
        if "/catalog/" in url:
            # https://www.wildberries.ru/catalog/12345678/detail.aspx
            id = url.split("/catalog/")[1].split("/")[0]
        elif "/card/" in url:
            # https://www.wildberries.ru/card/12345678
            id = url.split("/card/")[1].split("?")[0].split("/")[0]
        else:
            # Резервный метод: ищем самое длинное число
            numbers = re.findall(r"\d+", url)
            if numbers:
                id = max(numbers, key=len)
            else:
                return None

        # Проверяем, что артикул состоит только из цифр и имеет достаточную длину
        if id.isdigit() and len(id) >= 6:
            return id
        else:
            return None
    except Exception:
        return None


def get_reviews_from_wb(product_url):
    # Получаем ссылку на товар от пользователя
    product_url = product_url.strip()

    # Проверяем корректность ссылки
    if not is_correct_wb_url(product_url):
        return [1, "Неверная ссылка Wildberries!"]
        #    Примеры корректных ссылок:
        #  https://www.wildberries.ru/catalog/12345678/detail.aspx...
        #  https://wildberries.ru/card/87654321...
        #  https://www.wb.ru/catalog/12345678/detail.aspx...

    # Извлекаем артикул товара
    id = extract_product_id(product_url)
    if not id:
        return [1, "Не удалось извлечь артикул товара из ссылки"]

    # Вычисляем part и vol для формирования URL
    try:
        part = id[:-3]
        vol = part[:-2]
    except:
        print("Ошибка при вычислении part и vol")
        return [1, "Ошибка при вычислении part и vol"]

    id_product = ""
    # Перебираем различные корзины для поиска основного ID товара
    for i in range(1, 100):
        number_of_basket = f"{i:02d}"  # Форматируем с ведущими нулями: 01, 02, ..., 99

        try:
            # Пробуем получить JSON с информацией о товаре из CDN
            url_for_id = f"https://basket-{number_of_basket}.wbcontent.net/vol{vol}/part{part}/{id}/info/ru/card.json"
            response = requests.get(url_for_id, timeout=5)

            if response.status_code == 200:
                product_data = response.json()
                imt_id = product_data.get("imt_id")

                if imt_id:
                    id_product = str(imt_id)
                    break

        except:
            continue

    # Если не нашли основной ID товара
    if not id_product:
        return [1, "Не удалось найти информацию о товаре"]

    try:
        # Формируем URL для получения отзывов (последние 1000 отзывов)
        urls_to_try = [
            f"https://feedbacks1.wb.ru/feedbacks/v1/{id_product}",
            f"https://feedbacks2.wb.ru/feedbacks/v1/{id_product}",
            f"https://feedbacks1.wb.ru/feedbacks/v2/{id_product}",
            f"https://feedbacks2.wb.ru/feedbacks/v2/{id_product}",
        ]

        feedbacks_data = None
        working_url = ""

        for url in urls_to_try:
            try:
                response = requests.get(url, timeout=10)
                if response.status_code == 200:
                    feedbacks_data = response.json()
                    working_url = url
                    break
            except:
                continue

        if not feedbacks_data:
            return [1, "Не удалось получить данные об отзывах"]
        # Обрабатываем каждый отзыв
        feedbacks = feedbacks_data.get("feedbacks", [])
        if not feedbacks:
            return [1, "Отзывов еще нет."]

        # Фильтруем только отзывы с текстом и формируем список
        feedbacks_list = []

        for feedback in feedbacks:
            pros = feedback.get("pros", "") or ""
            text = feedback.get("text", "") or ""
            cons = feedback.get("cons", "") or ""
            product_valuation = feedback.get("productValuation", "")

            # Проверяем, есть ли текст в отзыве
            if pros or text or cons:
                # Формируем полный текст отзыва
                full_text = ""
                if pros:
                    full_text += f"Достоинства: {pros}. "
                if text:
                    full_text += f"Комментарий: {text}. "
                if cons:
                    full_text += f"Недостатки: {cons}"

                full_text = full_text.strip()
                # Добавляем отзыв в список
                feedbacks_list.append(f"Оценка: {product_valuation}/5 - {full_text}")

        if not feedbacks_list:
            return [1, "Нет отзывов с текстом."]
        # Результат в формате [0, [список отзывов(str)]]
        return [0, feedbacks_list]

    except Exception:
        return [1, "Произошла ошибка при обработке отзывов."]
