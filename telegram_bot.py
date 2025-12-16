import os
import logging
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from dotenv import load_dotenv

# Загрузка переменных окружения
load_dotenv()

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Данные об авторах
AUTHORS = {
    "chomsky": {
        "name": "Ноам Хомский",
        "bio": "Американский лингвист, философ, политический активист и теоретик. Профессор лингвистики Массачусетского технологического института."
    },
    "zinn": {
        "name": "Говард Зинн",
        "bio": "Американский историк, писатель и общественный деятель. Автор книги 'Народная история США'."
    },
    "blum": {
        "name": "Уильям Блум",
        "bio": "Американский писатель, историк и критик внешней политики США. Автор книги 'Убийство надежды'."
    },
    "parenti": {
        "name": "Майкл Паренти",
        "bio": "Американский политолог и историк. Специализируется на критическом анализе американской политики и медиа."
    },
    "pilger": {
        "name": "Джон Пилджер",
        "bio": "Австралийский журналист и документалист. Известен критическими работами о внешней политике западных стран."
    }
}

# Исторические события
EVENTS = [
    {"date": "1953-08-19", "event": "Операция 'Аякс': свержение премьер-министра Ирана Мохаммеда Мосаддыка", "author": "chomsky"},
    {"date": "1954-06-18", "event": "Операция в Гватемале: свержение президента Хакобо Арбенса", "author": "zinn"},
    {"date": "1961-04-17", "event": "Вторжение в заливе Свиней на Кубе", "author": "blum"},
    {"date": "1973-09-11", "event": "Военный переворот в Чили: свержение президента Сальвадора Альенде", "author": "parenti"},
    {"date": "1983-10-25", "event": "Вторжение США в Гренаду", "author": "pilger"},
]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start"""
    keyboard = [
        [InlineKeyboardButton("📅 События по датам", callback_data='dates')],
        [InlineKeyboardButton("✍️ Авторы", callback_data='authors')],
        [InlineKeyboardButton("ℹ️ О боте", callback_data='about')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        '👋 Добро пожаловать!\n\n'
        'Этот бот предоставляет информацию об исторических событиях и их авторах.\n\n'
        'Выберите действие:',
        reply_markup=reply_markup
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик нажатий на кнопки"""
    query = update.callback_query
    await query.answer()
    
    if query.data == 'dates':
        await show_dates(query)
    elif query.data == 'authors':
        await show_authors(query)
    elif query.data == 'about':
        await show_about(query)
    elif query.data.startswith('event_'):
        event_index = int(query.data.split('_')[1])
        await show_event_detail(query, event_index)
    elif query.data.startswith('author_'):
        author_key = query.data.split('_')[1]
        await show_author_detail(query, author_key)
    elif query.data == 'back_main':
        await back_to_main(query)

async def show_dates(query):
    """Показать события по датам"""
    keyboard = []
    for i, event in enumerate(EVENTS):
        date_obj = datetime.strptime(event['date'], '%Y-%m-%d')
        formatted_date = date_obj.strftime('%d.%m.%Y')
        keyboard.append([InlineKeyboardButton(
            f"{formatted_date} - {event['event'][:40]}...",
            callback_data=f'event_{i}'
        )])
    keyboard.append([InlineKeyboardButton("◀️ Назад", callback_data='back_main')])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(
        '📅 *События по датам:*\n\nВыберите событие для подробной информации:',
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def show_authors(query):
    """Показать список авторов"""
    keyboard = []
    for key, author in AUTHORS.items():
        keyboard.append([InlineKeyboardButton(
            author['name'],
            callback_data=f'author_{key}'
        )])
    keyboard.append([InlineKeyboardButton("◀️ Назад", callback_data='back_main')])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(
        '✍️ *Авторы:*\n\nВыберите автора для просмотра биографии:',
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def show_about(query):
    """Показать информацию о боте"""
    keyboard = [[InlineKeyboardButton("◀️ Назад", callback_data='back_main')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        'ℹ️ *О боте*\n\n'
        'Этот бот предоставляет информацию об исторических событиях '
        'и известных авторах, изучающих эти темы.\n\n'
        'Разработано для образовательных целей.',
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def show_event_detail(query, event_index):
    """Показать подробности события"""
    event = EVENTS[event_index]
    author = AUTHORS[event['author']]
    date_obj = datetime.strptime(event['date'], '%Y-%m-%d')
    formatted_date = date_obj.strftime('%d.%m.%Y')
    
    keyboard = [[InlineKeyboardButton("◀️ Назад к датам", callback_data='dates')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    text = f"📅 *Дата:* {formatted_date}\n\n"
    text += f"📌 *Событие:*\n{event['event']}\n\n"
    text += f"✍️ *Автор:* {author['name']}"
    
    await query.edit_message_text(
        text,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def show_author_detail(query, author_key):
    """Показать подробности об авторе"""
    author = AUTHORS[author_key]
    
    # Найти события этого автора
    author_events = [e for e in EVENTS if e['author'] == author_key]
    
    keyboard = [[InlineKeyboardButton("◀️ Назад к авторам", callback_data='authors')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    text = f"✍️ *{author['name']}*\n\n"
    text += f"{author['bio']}\n\n"
    
    if author_events:
        text += f"*Связанные события ({len(author_events)}):*\n"
        for event in author_events:
            date_obj = datetime.strptime(event['date'], '%Y-%m-%d')
            formatted_date = date_obj.strftime('%d.%m.%Y')
            text += f"• {formatted_date}: {event['event']}\n"
    
    await query.edit_message_text(
        text,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def back_to_main(query):
    """Вернуться в главное меню"""
    keyboard = [
        [InlineKeyboardButton("📅 События по датам", callback_data='dates')],
        [InlineKeyboardButton("✍️ Авторы", callback_data='authors')],
        [InlineKeyboardButton("ℹ️ О боте", callback_data='about')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        '👋 Добро пожаловать!\n\n'
        'Этот бот предоставляет информацию об исторических событиях и их авторах.\n\n'
        'Выберите действие:',
        reply_markup=reply_markup
    )

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик ошибок"""
    logger.error(f"Произошла ошибка: {context.error}")

def main():
    """Запуск бота"""
    # Получение токена из переменных окружения
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    
    if not token:
        logger.error("TELEGRAM_BOT_TOKEN не найден в переменных окружения!")
        return
    
    # Создание приложения
    application = Application.builder().token(token).build()
    
    # Добавление обработчиков
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button_handler))
    application.add_error_handler(error_handler)
    
    # Запуск бота
    logger.info("Бот запущен...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
