import requests
import json

TOKEN = "7547307621:AAGP9iZhQPIEJGHsUJ4w0NXQoI8WNZK6me8"
CHAT_ID = -4704516258  # Ваш проблемный chat_id

# Простейший тестовый запрос
response = requests.post(
    f"https://api.telegram.org/bot{TOKEN}/sendMessage",
    json={
        "chat_id": CHAT_ID,
        "text": "Тестовое сообщение от бота"
    }
)