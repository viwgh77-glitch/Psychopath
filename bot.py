import requests
import random
from openai import OpenAI

# ====== НАСТРОЙКИ ======
BOT_TOKEN = "8363120199:AAH3qM5EDvWWj52x1jcjO5_rZDLYoe3BfLw"
DEEPSEEK_API_KEY = "sk-0784000aa9094537b1338f60f1f9bf39"
CHANNEL_ID = -1004395824456
# =====================

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
    "Никаких «Хорошо», «Вот ваш пост», «Как скажете», «Будет сделано». "
    "Сразу текст."
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

# Основной код — без Flask, без потоков
print("Генерирую пост...")
post = create_post()
if post:
    publish_post(post)
    print("Готово. Следующий пост через 12 часов.")
else:
    print("Ошибка генерации.")

# Завершаемся. Render перезапустит через минуту.