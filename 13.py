import logging
import sqlite3
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, CallbackQueryHandler, ConversationHandler, MessageHandler, filters
from datetime import datetime, timedelta

# Токен бота
TOKEN = '1111111'

# Список ID администраторов
ADMIN_IDS = [100000000]  # Замените на ваши ID

# Настройка логирования
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

logger = logging.getLogger(__name__)

# Подключение к базе данных
conn = sqlite3.connect('subscriptions.db', check_same_thread=False)
cursor = conn.cursor()

# Создание таблицы, если она не существует
cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    username TEXT,
    subscription_end DATETIME
)
''')

# Создание таблицы для отслеживания всех пользователей
cursor.execute('''
CREATE TABLE IF NOT EXISTS user_actions (
    user_id INTEGER,
    action_time DATETIME DEFAULT CURRENT_TIMESTAMP
)
''')
conn.commit()

# Состояния для ConversationHandler
ID, DURATION, CONFIRMATION, REMOVE_ID, REMOVE_CONFIRMATION, BROADCAST = range(6)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    username = update.effective_user.username

    # Записываем информацию о пользователе
    cursor.execute('INSERT INTO user_actions (user_id) VALUES (?)', (user_id,))
    conn.commit()

    # Проверка подписки на канал
    try:
        user_status = await context.bot.get_chat_member(chat_id='@tmdleg', user_id=user_id)
        if user_status.status not in ['member', 'administrator', 'creator']:
            await update.message.reply_text('❌ Пожалуйста, подпишитесь на канал @tmdleg, чтобы пользоваться ботом.')
            return
    except Exception as e:
        await update.message.reply_text(f'⚠️ Ошибка при проверке подписки: {e}')
        return

    # Проверка наличия подписки
    cursor.execute('SELECT subscription_end FROM users WHERE user_id = ?', (user_id,))
    result = cursor.fetchone()
    if result:
        subscription_end = datetime.strptime(result[0], '%Y-%m-%d %H:%M:%S')
        if subscription_end > datetime.now():
            # Если подписка активна, показываем основное меню с веб-приложением
            keyboard = [
                [InlineKeyboardButton("▶️ Запустить", web_app={"url": "нгрок"})],
                [InlineKeyboardButton("🆘 Поддержка", callback_data='support')],
                [InlineKeyboardButton("💰 Прайс", callback_data='price')],
                [InlineKeyboardButton("🛒 Купить подписку", callback_data='buy_subscription')]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_text('👋 Добро пожаловать! Выберите действие:', reply_markup=reply_markup)
        else:
            keyboard = [
                [InlineKeyboardButton("💰 Прайс", callback_data='price')],
                [InlineKeyboardButton("🛒 Купить подписку", callback_data='buy_subscription')]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_text('⚠️ Ваша подписка истекла. Пожалуйста, продлите подписку:', 
                                          reply_markup=reply_markup)
    else:
        # Если подписки нет, показываем ограниченное меню
        keyboard = [
            [InlineKeyboardButton("💰 Прайс", callback_data='price')],
            [InlineKeyboardButton("🛒 Купить подписку", callback_data='buy_subscription')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text('❌ У вас нет активной подписки. Пожалуйста, приобретите подписку:', 
                                      reply_markup=reply_markup)

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    

    if query.data == 'support':
        await query.edit_message_text(text="🆘 Свяжитесь с поддержкой: @TYNDROV")
    elif query.data == 'price':
        await query.edit_message_text(text="💰 Цены на подписку:\n1 день - $2.8\n1 неделя - $7.3\n1 месяц - $13.5\n1 год - $35\nНавсегда - $50")
    elif query.data == 'buy_subscription':
        await query.edit_message_text(text="🛒 Для покупки подписки свяжитесь с @TYNDROV")
async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_id = update.effective_user.id
    if user_id not in ADMIN_IDS:
        await update.message.reply_text('❌ У вас нет доступа к этой команде.')
        return ConversationHandler.END

    keyboard = [
        [InlineKeyboardButton("✅ Выдать подписку", callback_data='grant_subscription')],
        [InlineKeyboardButton("❌ Снять подписку", callback_data='revoke_subscription')],
        [InlineKeyboardButton("📋 Список пользователей", callback_data='list_users')],
        [InlineKeyboardButton("📢 Рассылка", callback_data='broadcast')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text('👨‍💻 Админ панель:', reply_markup=reply_markup)
    return ID

async def grant_subscription(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    keyboard = [[InlineKeyboardButton("« Назад", callback_data='back_to_admin')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.callback_query.answer()
    await update.callback_query.edit_message_text(
        text="📝 Введите ID пользователя для выдачи подписки:",
        reply_markup=reply_markup
    )
    return DURATION

async def duration_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    try:
        user_id = int(update.message.text)
        context.user_data['grant_user_id'] = user_id
        keyboard = [[InlineKeyboardButton("« Назад", callback_data='back_to_admin')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            '⏳ Введите длительность подписки (например, 1d, 1m, 1y):',
            reply_markup=reply_markup
        )
        return CONFIRMATION
    except ValueError:
        await update.message.reply_text('❌ Пожалуйста, введите корректный ID пользователя (только цифры)')
        return DURATION
async def confirmation_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    duration = update.message.text
    user_id = context.user_data['grant_user_id']
    now = datetime.now()

    if duration.endswith('d'):
        days = int(duration[:-1])
        subscription_end = now + timedelta(days=days)
    elif duration.endswith('m'):
        months = int(duration[:-1])
        subscription_end = now + timedelta(days=30*months)
    elif duration.endswith('y'):
        years = int(duration[:-1])
        subscription_end = now + timedelta(days=365*years)
    else:
        await update.message.reply_text('❌ Неверный формат длительности. Попробуйте снова.')
        return DURATION

    cursor.execute('''INSERT OR REPLACE INTO users 
                     (user_id, username, subscription_end) 
                     VALUES (?, ?, ?)''',
                  (user_id, None, subscription_end.strftime('%Y-%m-%d %H:%M:%S')))
    conn.commit()

    try:
        await context.bot.send_message(
            chat_id=user_id,
            text=f'✅ Вам выдана подписка до {subscription_end.strftime("%Y-%m-%d %H:%M:%S")}. \n'
                 f'Используйте /start для доступа к функциям бота.'
        )
    except Exception as e:
        logger.error(f"❌ Ошибка при отправке уведомления пользователю {user_id}: {e}")

    await update.message.reply_text(
        f'✅ Подписка выдана пользователю {user_id} до {subscription_end.strftime("%Y-%m-%d %H:%M:%S")}.'
    )
    return ConversationHandler.END


async def revoke_subscription(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    keyboard = [[InlineKeyboardButton("« Назад", callback_data='back_to_admin')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.callback_query.answer()
    await update.callback_query.edit_message_text(
        text="📝 Введите ID пользователя для снятия подписки:",
        reply_markup=reply_markup
    )
    return REMOVE_CONFIRMATION

async def remove_confirmation_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    try:
        user_id = int(update.message.text)
        cursor.execute('DELETE FROM users WHERE user_id = ?', (user_id,))
        conn.commit()

        try:
            await context.bot.send_message(
                chat_id=user_id,
                text='❌ Ваша подписка была отменена администратором.'
            )
        except Exception as e:
            logger.error(f"Ошибка при отправке уведомления пользователю {user_id}: {e}")

        await update.message.reply_text(f'✅ Подписка снята у пользователя {user_id}.')
        return ConversationHandler.END
    except ValueError:
        await update.message.reply_text('❌ Пожалуйста, введите корректный ID пользователя.')
        return REMOVE_CONFIRMATION
async def list_users(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.callback_query.answer()
    
    # Получаем всех пользователей с подпиской
    cursor.execute('SELECT user_id, username, subscription_end FROM users')
    subscribed_users = cursor.fetchall()
    
    # Получаем всех пользователей, которые запускали бота
    cursor.execute('SELECT DISTINCT user_id FROM user_actions')  # Нужно создать эту таблицу
    all_users = cursor.fetchall()
    
    message_text = "📋 Список пользователей:\n\n"
    
    if not all_users:
        message_text = "📝 Список пользователей пуст"
    else:
        # Создаем словарь пользователей с подпиской для быстрого поиска
        subscribed_dict = {user[0]: user for user in subscribed_users}
        
        for user_id in all_users:
            user_id = user_id[0]
            if user_id in subscribed_dict:
                # Пользователь с подпиской
                user = subscribed_dict[user_id]
                message_text += f"🆔 ID: {user[0]}\n"
                message_text += f"👤 Username: {user[1] or 'Не указан'}\n"
                message_text += f"⏳ Подписка до: {user[2]}\n"
            else:
                # Пользователь без подписки
                message_text += f"🆔 ID: {user_id}\n"
                message_text += f"❌ Без подписки\n"
            message_text += "➖" * 20 + "\n"

    keyboard = [[InlineKeyboardButton("« Назад", callback_data='back_to_admin')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    try:
        await update.callback_query.edit_message_text(
            text=message_text,
            reply_markup=reply_markup
        )
    except Exception as e:
        await update.callback_query.edit_message_text(
            text="❌ Список слишком длинный. Попробуйте позже.",
            reply_markup=reply_markup
        )
    return ID
async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    keyboard = [[InlineKeyboardButton("« Назад", callback_data='back_to_admin')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.callback_query.answer()
    await update.callback_query.edit_message_text(
        text="📢 Введите сообщение для рассылки:",
        reply_markup=reply_markup
    )
    return BROADCAST


async def broadcast_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    message = update.message.text
    cursor.execute('SELECT user_id FROM users')
    user_ids = cursor.fetchall()
    success_count = 0
    fail_count = 0
    
    for user_id in user_ids:
        try:
            await context.bot.send_message(chat_id=user_id[0], text=message)
            success_count += 1
        except Exception as e:
            logger.error(f"❌ Ошибка при отправке сообщения пользователю {user_id[0]}: {e}")
            fail_count += 1

    await update.message.reply_text(
        f'📊 Рассылка завершена\n'
        f'✅ Успешно отправлено: {success_count}\n'
        f'❌ Ошибок отправки: {fail_count}'
    )
    return ConversationHandler.END

async def back_to_admin(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    keyboard = [
        [InlineKeyboardButton("✅ Выдать подписку", callback_data='grant_subscription')],
        [InlineKeyboardButton("❌ Снять подписку", callback_data='revoke_subscription')],
        [InlineKeyboardButton("📋 Список пользователей", callback_data='list_users')],
        [InlineKeyboardButton("📢 Рассылка", callback_data='broadcast')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.callback_query.edit_message_text('👨‍💻 Админ панель:', reply_markup=reply_markup)
    return ID

def main() -> None:
    app = ApplicationBuilder().token(TOKEN).build()

    start_handler = CommandHandler('start', start)
    admin_handler = CommandHandler('admin', admin_panel)

    conv_handler = ConversationHandler(
        entry_points=[admin_handler],
        states={
            ID: [
                CallbackQueryHandler(grant_subscription, pattern='^grant_subscription$'),
                CallbackQueryHandler(revoke_subscription, pattern='^revoke_subscription$'),
                CallbackQueryHandler(list_users, pattern='^list_users$'),
                CallbackQueryHandler(broadcast, pattern='^broadcast$'),
                CallbackQueryHandler(back_to_admin, pattern='^back_to_admin$')
            ],
            DURATION: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, duration_handler),
                CallbackQueryHandler(back_to_admin, pattern='^back_to_admin$')
            ],
            CONFIRMATION: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, confirmation_handler),
                CallbackQueryHandler(back_to_admin, pattern='^back_to_admin$')
            ],
            REMOVE_CONFIRMATION: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, remove_confirmation_handler),
                CallbackQueryHandler(back_to_admin, pattern='^back_to_admin$')
            ],
            BROADCAST: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, broadcast_handler),
                CallbackQueryHandler(back_to_admin, pattern='^back_to_admin$')
            ]
        },
        fallbacks=[CommandHandler('admin', admin_panel)]
    )

    app.add_handler(start_handler)
    app.add_handler(conv_handler)
    app.add_handler(CallbackQueryHandler(button_handler))

    logger.info("🚀 Бот запущен!")
    app.run_polling()

if __name__ == '__main__':
    main()

