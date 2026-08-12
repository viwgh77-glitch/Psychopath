import requests
import random
import time
import os

# ====== НАСТРОЙКИ ======
BOT_TOKEN = os.environ.get("BOT_TOKEN", "8363120199:AAH3qM5EDvWWj52x1jcjO5_rZDLYoe3BfLw")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")
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
    if not GROQ_API_KEY:
        print("No API key")
        return None
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json",
    }
    data = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "system", "content": "Ты автор психологического блога. Отвечай только готовым текстом, без вступлений и комментариев."},
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.9,
    }
    try:
        r = requests.post(url, headers=headers, json=data, timeout=30)
        if r.status_code == 200:
            return r.json()["choices"][0]["message"]["content"].strip()
        else:
            print(f"Groq error: {r.status_code} - {r.text[:200]}")
            return None
    except Exception as e:
        print(f"Groq error: {e}")
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

TIMESTAMP_FILE = "/tmp/last_post.txt"

def should_post():
    if not os.path.exists(TIMESTAMP_FILE):
        return True
    try:
        with open(TIMESTAMP_FILE, "r") as f:
            last = float(f.read().strip())
        return time.time() - last >= 43200
    except:
        return True

def save_timestamp():
    with open(TIMESTAMP_FILE, "w") as f:
        f.write(str(time.time()))

print("Проверяю время последнего поста...")
if should_post():
    print("Генерирую пост...")
    post = create_post()
    if post:
        publish_post(post)
        save_timestamp()
        print("Готово.")
    else:
        print("Ошибка генерации.")
else:
    print("Ещё рано. Жду.")