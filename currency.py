import requests

API_KEY = "Вставте токен сайта сюда"

def get_exchange_rate(base_currency, target_currency):
    url = f"https://v6.exchangerate-api.com/v6/{API_KEY}/latest/{base_currency}"

    try:
        response = requests.get(url, timeout=5)
        data = response.json()

        if response.status_code == 200:
            return data["conversion_rates"].get(target_currency)

    except Exception:
        return None

    return None