from flask import Flask, render_template, request, jsonify
from g4f.client import Client
import random
import string
import requests
import certifi
import fake_useragent
from requests.packages.urllib3.exceptions import InsecureRequestWarning
import os
import glob
from telethon import TelegramClient, functions
import asyncio
import re

# Игнорируем предупреждения о незащищенных запросах
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

app = Flask(__name__, static_url_path='/static')

def generate_random_email():
    domains = ["gmail.com", "hotmail.com"]
    name = ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))
    return f"{name}@{random.choice(domains)}"

def generate_random_phone_number():
    prefixes = ['+7', '+380']
    number = ''.join(random.choices(string.digits, k=10))
    return f"{random.choice(prefixes)}{number}"

def generate_user_agent():
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.1 Safari/605.1.15",
    ]
    return random.choice(user_agents)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/activate', methods=['POST'])
def activate():
    data = request.get_json()
    number = data.get('phone')
    user = fake_useragent.UserAgent().random
    headers = {'user-agent': user}

    # Выполнение запросов с использованием прокси
    try:
        response1 = requests.post(
            'https://oauth.telegram.org/auth/request?bot_id=1852523856&origin=https%3A%2F%2Fcabinet.presscode.app&embed=1&return_to=https%3A%2F%2Fcabinet.presscode.app%2Flogin',
            headers=headers,
            data={'phone': number},
        )
        print(f"Response from first request: {response1.status_code}, {response1.text}")

        response2 = requests.post(
            'https://translations.telegram.org/auth/request',
            headers=headers,
            data={'phone': number},
        )
        print(f"Response from second request: {response2.status_code}, {response2.text}")

        response3 = requests.post(
            'https://translations.telegram.org/auth/request',
            headers=headers,
            data={'phone': number},
        )
        print(f"Response from third request: {response3.status_code}, {response3.text}")

        response4 = requests.post(
            'https://oauth.telegram.org/auth/request?bot_id=1093384146&origin=https%3A%2F%2Foff-bot.ru&embed=1&request_access=write&return_to=https%3A%2F%2Foff-bot.ru%2Fregister%2Fconnected-accounts%2Fsmodders_telegram%2F%3Fsetup%3D1',
            headers=headers,
            data={'phone': number},
        )
        print(f"Response from fourth request: {response4.status_code}, {response4.text}")

        response5 = requests.post(
            'https://oauth.telegram.org/auth/request?bot_id=466141824&origin=https%3A%2F%2Fmipped.com&embed=1&request_access=write&return_to=https%3A%2F%2Fmipped.com%2Ff%2Fregister%2Fconnected-accounts%2Fsmodders_telegram%2F%3Fsetup%3D1',
            headers=headers,
            data={'phone': number},
        )
        print(f"Response from fifth request: {response5.status_code}, {response5.text}")

        response6 = requests.post(
            'https://oauth.telegram.org/auth/request?bot_id=5463728243&origin=https%3A%2F%2Fwww.spot.uz&return_to=https%3A%2F%2Fwww.spot.uz%2Fru%2F2022%2F04%2F29%2Fyoto%2F%23',
            headers=headers,
            data={'phone': number},
        )
        print(f"Response from sixth request: {response6.status_code}, {response6.text}")

        response7 = requests.post(
            'https://oauth.telegram.org/auth/request?bot_id=1733143901&origin=https%3A%2F%2Ftbiz.pro&embed=1&request_access=write&return_to=https%3A%2F%2Ftbiz.pro%2Flogin',
            headers=headers,
            data={'phone': number},
        )
        print(f"Response from seventh request: {response7.status_code}, {response7.text}")

        response8 = requests.post(
            'https://oauth.telegram.org/auth/request?bot_id=319709511&origin=https%3A%2F%2Ftelegrambot.biz&embed=1&return_to=https%3A%2F%2Ftelegrambot.biz%2F',
            headers=headers,
            data={'phone': number},
        )
        print(f"Response from eighth request: {response8.status_code}, {response8.text}")

        response9 = requests.post(
            'https://oauth.telegram.org/auth/request?bot_id=1199558236&origin=https%3A%2F%2Fbot-t.com&embed=1&return_to=https%3A%2F%2Fbot-t.com%2Flogin',
            headers=headers,
            data={'phone': number},
        )
        print(f"Response from ninth request: {response9.status_code}, {response9.text}")

        response10 = requests.post(
            'https://oauth.telegram.org/auth/request?bot_id=1803424014&origin=https%3A%2F%2Fru.telegram-store.com&embed=1&request_access=write&return_to=https%3A%2F%2Fru.telegram-store.com%2Fcatalog%2Fsearch',
            headers=headers,
            data={'phone': number},
        )
        print(f"Response from tenth request: {response10.status_code}, {response10.text}")

        response11 = requests.post(
            'https://oauth.telegram.org/auth/request?bot_id=210944655&origin=https%3A%2F%2Fcombot.org&embed=1&request_access=write&return_to=https%3A%2F%2Fcombot.org%2Flogin',
            headers=headers,
            data={'phone': number},
        )
        print(f"Response from eleventh request: {response11.status_code}, {response11.text}")

        response12 = requests.post(
            'https://my.telegram.org/auth/send_password',
            headers=headers,
            data={'phone': number},
        )
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return jsonify(success=False, error=str(e)), 500
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return jsonify(success=False, error=str(e)), 500

@app.route('/submit', methods=['POST'])
def submit():
    nickname = request.form['nickname']
    complaint_type = request.form['complaint_type']
    
    # Генерация сообщения с помощью AI
    client = Client()
    prompt = f"Дополни и улучши текст: Здравствуйте техническая поддержка телеграмма! Я наткнулся на пользователя с никнеймом: {nickname} он нарушает такое правило в Telegram как: {complaint_type}. Таким образом он мешает окружающим пользователям, нарушая правила ToS Telegram, пожалуйста, примите меры против этого пользователя и заблокируйте его аккаунт, заранее спасибо, С уважением, Артур"
    
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}]
    )
    
    message = response.choices[0].message.content  # Сгенерированное сообщение ИИ
    print(message)  # Выводим сообщение в консоль

    url = "https://telegram.org/support?setln=ru"
    subject = "Жалоба на пользователя"
    message_count = 30  # Укажите количество жалоб, которые хотите отправить

    for _ in range(message_count):
        email = generate_random_email()  # Сгенерированный email
        phone = generate_random_phone_number()  # Сгенерированный номер телефона
        
        # Генерация случайного пользовательского агента
        user_agent = generate_user_agent()

        payload = {
            "subject": subject,
            "message": message,  # Сгенерированное сообщение ИИ
            "email": email,      # Сгенерированный EMail
            "phone": phone       # Сгенерированный номер телефона
        }

        # Настройка заголовков для запроса
        headers = {
            "User-Agent": user_agent
        }

        try:
            # Отправка POST-запроса без использования прокси
            response = requests.post(url, data=payload, headers=headers, verify=certifi.where())
            print(f"Ответ от сервера: {response.status_code}")  # Выводим статус ответа
            print(f"Тело ответа: {response.text}")  # Выводим тело ответа для отладки
        except requests.exceptions.RequestException as e:
            print(f"Ошибка при отправке запроса: {e}")

    return jsonify({"success": True, "message": message})

@app.route('/unban', methods=['POST'])
def unban():
    data = request.get_json()
    phone_number = data.get('phone_number')

    if not phone_number:
        return jsonify({"success": False, "message": "Номер телефона не указан."}), 400

    complaint_texts = [
        "Здравствуйте Telegram поддержка! Мой номер телефона {phone_number} был заблокирован на вашей площадке Telegram. Я не нарушал правила ToS и мой Telegram аккаунт никак не был связан с нарушением правил Telegram. Пожалуйста разберитесь с этим как можно скорей, и разблокируйте мой Telegram аккаунт."
    ]

    url = "https://telegram.org/support?setln=ru"
    subject = "Жалоба на пользователя"
    message_count = 30 

    for _ in range(message_count):
        user_agent = generate_user_agent()

        for complaint_text in complaint_texts:
            payload = {
                "subject": subject,
                "message": complaint_text.format(phone_number=phone_number),  # Сообщение
                "email": generate_random_email(),  # Сгенерированный email
                "phone": phone_number  # Используем номер телефона из запроса
            }

            try:
                # Отправка POST-запроса
                response = requests.post(url, data=payload, headers={"User-Agent": user_agent}, verify=certifi.where())
                print(f"Ответ от сервера: {response.status_code}")  # Выводим статус ответа
                print(f"Тело ответа: {response.text}")  
            except requests.exceptions.RequestException as e:
                print(f"Ошибка при отправке запроса: {e}")

    return jsonify({"success": True, "message": "Запросы на разбан были успешно отправлены."})

@app.route('/report', methods=['POST'])
def report():
    data = request.get_json()
    link = data.get('link')
    reason = data.get('reason', 'SPAM')  

    api_id = '24641445'  
    api_hash = 'cbd16f1ca6464bf64338e45abd85ccdf'  

    session_files = glob.glob('SESSION/*.session')

    async def send_complaint(session_file):
        client = TelegramClient(
            session_file,
            api_id,
            api_hash,
            device_model='Android',
            system_version='10',
            app_version='9.0',
            lang_code='ru'
        )

        async with client:
            await client.start()

            match = re.match(r'https://t.me/([^/]+)/(\d+)', link)
            if match:
                chat_username = match.group(1)  
                chat = await client.get_entity(chat_username)

                await client(functions.messages.ReportSpamRequest(
                    peer=chat
                ))
                return 1  
            else:
                print("Invalid message link.")
                return 0  

    async def main():
        tasks = [send_complaint(session_file) for session_file in session_files]
        results = await asyncio.gather(*tasks)
        return sum(results)  

    count = asyncio.run(main())

    return jsonify({'success': True, 'count': count})

if __name__ == '__main__':
    app.run(debug=True)
