import requests

rotation_url = "http://node-de-19.astroproxy.com:10163/api/changeIP?apiToken=d83b3f402d18f6f9"

def change_proxy_ip():
    try:
        response = requests.get(rotation_url)
        print(f"Статус смены IP: {response.status_code}, Ответ: {response.text}")
    except Exception as e:
        print(f"Ошибка при смене IP: {e}")

# 2. Настройка самих прокси
# Формат: http://user:password@host:port


if __name__ == "__main__":
    change_proxy_ip()
    proxy_auth = "ShoweltomxO3:d25f03xL5@162.19.151.194:10163"
    proxies = {
        "http": f"http://{proxy_auth}",
        "https": f"http://{proxy_auth}"
    }