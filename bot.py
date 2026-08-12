import asyncio
import random
from openai import OpenAI
from telegram import Bot
from telegram.error import TelegramError

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

    quote_prompt = (
        f"Напиши одну психологическую цитату на тему «{topic}». "
        "Только цитата, 1-2 предложения, без имени автора. Без вступлений и комментариев."
    )

    post_prompt = (
        f"Напиши короткий пост для психологического блога на тему «{topic}».\n"
        "5-8 предложений.\n"
        "Структура: заголовок-вопрос, суть проблемы, один практический совет, тёплая поддержка.\n"
        "Тон: профессиональный, заботливый, без осуждения.\n"
        "Без нумерации и списков.\n"
        "Сразу текст поста, без вступлений."
    )

    quote = generate_content(quote_prompt)
    post_text = generate_content(post_prompt)

    if not quote or not post_text:
        return None

    for phrase in ["хорошо", "вот ваш пост", "вот цитата", "как скажете", "будет сделано", "без проблем"]:
        if quote.lower().startswith(phrase):
            quote = quote[len(phrase):].strip().lstrip(":,.")
        if post_text.lower().startswith(phrase):
            post_text = post_text[len(phrase):].strip().lstrip(":,.")

    return f"{quote}\n\n{post_text}\n\n#психология #самопознание #{topic.replace(' ', '_')}"

async def publish_post(bot, text):
    try:
        if len(text) <= 4000:
            await bot.send_message(chat_id=CHANNEL_ID, text=text)
        else:
            parts = [text[i:i+4000] for i in range(0, len(text), 4000)]
            for part in parts:
                await bot.send_message(chat_id=CHANNEL_ID, text=part)
        print(f"Опубликовано: {text[:80]}...")
        return True
    except TelegramError as e:
        print(f"Telegram error: {e}")
        return False

async def main():
    bot = Bot(token=BOT_TOKEN)
    print("Бот автопостинга запущен...")

    while True:
        post = create_post()
        if post:
            success = await publish_post(bot, post)
            if success:
                print("Следующий пост через 12 часов...")
                await asyncio.sleep(43200)
            else:
                print("Ошибка публикации. Повтор через час.")
                await asyncio.sleep(3600)
        else:
            print("Ошибка генерации. Повтор через 5 минут.")
            await asyncio.sleep(300)

if __name__ == "__main__":
    asyncio.run(main())