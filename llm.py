import requests
import base64
import urllib3

# Отключаем предупреждения SSL
urllib3.disable_warnings()


# автоматическое получение токена GigaChat
def get_gigachat_token(client_id, client_secret):
    auth_data = f"{client_id}:{client_secret}".encode("utf-8")
    auth_header = base64.b64encode(auth_data).decode("utf-8")

    headers = {
        "Authorization": f"Basic {auth_header}",
        "RqUID": "123e4567-e89b-12d3-a456-426614174000",
        "Content-Type": "application/x-www-form-urlencoded",
    }

    data = {"scope": "GIGACHAT_API_PERS"}

    response = requests.post(
        "https://ngw.devices.sberbank.ru:9443/api/v2/oauth",
        headers=headers,
        data=data,
        verify=False,
    )
    response.raise_for_status()
    return response.json()["access_token"]


#  Анализ отзывов через GigaChat
def analyze_reviews_with_gigachat(token: str, reviews: list[str]) -> str:
    messages = [
        {
            "role": "system",
            "content": "Сделай анализ: плюсы, минусы, тональность, рекомендации производителю",
        },
        {"role": "user", "content": "\n\n".join(reviews)},
    ]

    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    data = {"model": "GigaChat", "messages": messages, "temperature": 0.7}

    response = requests.post(
        "https://gigachat.devices.sberbank.ru/api/v1/chat/completions",
        headers=headers,
        json=data,
        verify=False,
    )

    response.raise_for_status()
    return response.json()["choices"][0]["message"]["content"]


client_id = "019a2b36-6cae-738d-a3bd-fe66c938e28e"
client_secret = "8ff99395-d870-4adc-9617-f6a42d9e8730"
token = get_gigachat_token(client_id, client_secret)
