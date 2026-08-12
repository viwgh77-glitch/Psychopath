import asyncio
import random
from openai import OpenAI
from telegram import Bot
from telegram.error import TelegramError
from flask import Flask
import threading

# ====== НАСТРОЙКИ ======
BOT_TOKEN = "8363120199:AAH3qM5EDvWWj52x1jcjO5_rZDLYoe3BfLw"
DEEPSEEK_API_KEY = "sk-0784000aa9094537b1338f60f1f9bf39"
CHANNEL_ID = -1004395824456
# =====================

app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running!"

client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url="https://api.deepseek.com")

TOPICS = [
    "тревожность", "прокрастинация", "самооценка", "отношения",
    "детские травмы", "эмоциональный интеллект", "границы личности",
    "принятие себя", "страх неудачи", "одиночество", "перфекционизм",
    "выгорание", "мотивация", "привычки", "осознанность",
    "внутренний критик", "зависимость от чужого мнения", "обида",
    "чувство вины", "жизненный сценарий",
]

SYSTEM_PROMPT = (
    "Ты — автор психологического блога. Отвечай ТОЛЬКО готовым постом. "
    "Никаких «Хорошо», «Вот ваш пост», «Как скажете», «Будет сделано» или других вступлений. "
    "Никаких комментариев до или после поста. Сразу текст."
)

def generate_content(prompt):
    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
            temperature=0.9,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"DeepSeek error: {e}")
        return None

def create_post():
    topic = random.choice(TOPICS)
    quote_prompt = f"Напиши одну психологическую цитату на тему «{topic}». Только цитата, 1-2 предложения, без имени автора. Без вступлений и комментариев."
    post_prompt = f"Напиши короткий пост для психологического блога на тему «{topic}».\n5-8 предложений.\nСтруктура: заголовок-вопрос, суть проблемы, один практический совет, тёплая поддержка.\nТон: профессиональный, заботливый, без осуждения.\nБез нумерации и списков.\nСразу текст поста, без вступлений."

    quote = generate_content(quote_prompt)
    post_text = generate_content(post_prompt)

    if not quote or not post_text:
        return None

    return f"{quote}\n\n{post_text}\n\n#психология #самопознание #{topic.replace(' ', '_')}"

def publish_post_sync(text):
    """Синхронная отправка поста"""
    import requests
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {"chat_id": CHANNEL_ID, "text": text}
    try:
        r = requests.post(url, json=data, timeout=30)
        if r.status_code == 200:
            print(f"Опубликовано: {text[:80]}...")
        else:
            print(f"Telegram error: {r.text}")
    except Exception as e:
        print(f"Telegram error: {e}")

def bot_loop():
    print("Бот автопостинга запущен...")
    while True:
        post = create_post()
        if post:
            publish_post_sync(post)
            print("Следующий пост через 12 часов...")
            import time
            time.sleep(43200)
        else:
            print("Ошибка генерации. Повтор через минуту.")
            import time
            time.sleep(60)

if __name__ == "__main__":
    t = threading.Thread(target=bot_loop, daemon=True)
    t.start()
    print("Поток бота запущен, запускаю Flask...")
    app.run(host="0.0.0.0", port=10000)