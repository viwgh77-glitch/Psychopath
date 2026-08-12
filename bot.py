import requests
import random

# ====== НАСТРОЙКИ ======
BOT_TOKEN = "8363120199:AAH3qM5EDvWWj52x1jcjO5_rZDLYoe3BfLw"
GEMINI_API_KEY = "AQ.Ab8RN6LLzus-ZK96YRJwp-xing1TkZwewW9zcJgVHtJTRw2nfQ"
CHANNEL_ID = -1004395824456
# =====================

TOPICS = [
    "тревожность", "прокрастинация", "самооценка", "отношения",
    "детские травмы", "эмоциональный интеллект", "границы личности",
    "принятие себя", "страх неудачи", "одиночество", "перфекционизм",
    "выгорание", "мотивация", "привычки", "осознанность",
    "внутренний критик", "зависимость от чужого мнения", "обида",
    "чувство вины", "жизненный сценарий",
]

def generate_content(prompt):
    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-latest:generateContent"
    headers = {
        "Content-Type": "application/json",
        "X-goog-api-key": GEMINI_API_KEY,
    }
    data = {
        "contents": [{"parts": [{"text": prompt}]}]
    }
    try:
        r = requests.post(url, headers=headers, json=data, timeout=30)
        if r.status_code == 200:
            return r.json()["candidates"][0]["content"]["parts"][0]["text"].strip()
        else:
            print(f"Gemini error: {r.status_code} - {r.text[:200]}")
            return None
    except Exception as e:
        print(f"Gemini error: {e}")
        return None

def create_post():
    topic = random.choice(TOPICS)
    quote = generate_content(f"Напиши психологическую цитату на тему «{topic}». Только цитата, 1-2 предложения, без автора.")
    post_text = generate_content(f"Напиши короткий пост для психоблога на тему «{topic}». 5-8 предложений. Тепло, профессионально. Без вступлений.")
    
    if not quote or not post_text:
        return None
    return f"{quote}\n\n{post_text}\n\n#психология #самопознание #{topic.replace(' ', '_')}"

def publish_post(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    try:
        r = requests.post(url, json={"chat_id": CHANNEL_ID, "text": text}, timeout=30)
        if r.status_code == 200:
            print(f"Опубликовано: {text[:80]}...")
            return True
        else:
            print(f"Telegram error: {r.text}")
            return False
    except Exception as e:
        print(f"Telegram error: {e}")
        return False

print("Генерирую пост...")
post = create_post()
if post:
    publish_post(post)
    print("Готово.")
else:
    print("Ошибка генерации.")