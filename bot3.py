from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler
from telegram import ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
import redis
import requests
import json
import os
import logging

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.ERROR)
logger = logging.getLogger(__name__)

# Telegram authorization
# Must be set in environment variables

bot_token = os.getenv('BOT_TOKEN')
if bot_token is None:
    print("Error: BOT_TOKEN environment variable is not set.")
    exit(1)

# Redis database for level partitioning
bot_database = redis.Redis(host='localhost', port=6379, decode_responses=True)

# Function to start the bot
def start(update, context):
    user_name = update.effective_user.username
    text = f'سلام {user_name} عزیز 🖐🏻\n\nاسم جزوه ای که میخوای رو بهم بگو 🤓 \n یا حتی اسم استادش :)😲 \n\nاز منو پایین هم میتونی به قسمت های دیگه ربات دسترسی پیدا کنید😊 \n\nهیبو | دستیار آموزشی تو🦉'
    buttons = [
        ["میخوام جزوه آپلود کنم"],
        ["راهنما ربات", "هیبو چیه"]
    ]
    reply_markup = ReplyKeyboardMarkup(buttons, resize_keyboard=True)
    update.message.reply_text(text, reply_markup=reply_markup)

# Function to handle messages
def body(update, context):
    level = update.message.text
    if level == 'میخوام جزوه آپلود کنم':
        update.message.reply_text('متاسفانه این قابلیت هنوز تکمیل نشده \n بزودی این امکان هم به ربات اضافه میشه 😀')
    elif level == 'راهنما ربات':
        update.message.reply_text('هیبو بات هستم 🤖\n\nهر جای چت که هستی میتونی اسم درست یا استادی که میخوای رو برام بنویسی 🤓\nمن برات میگردم و همه نتایجی که پیدا کردم رو نشون میدم😉\nهمینطور از دکمه های منو میتونی هم منابع درسی خودت رو آپلود کنی هم به وبسایت وصل بشی💯\n\nامیدوارم تونسته باشم خوب راهنماییت کنم✌️')
    elif level == 'هیبو چیه':
        update.message.reply_text('اینو محسن بگه میگم بت')
    else:
        sent_message = update.message.reply_text('صبر کن ببینم چی داریم 🤔')
        wanted_word = update.message.text
        website_response = requests.get(f"https://hiboo.ir/api/v1/search/?s={wanted_word}")
        final_response = json.loads(website_response.text)

        if len(final_response) == 0:
            update.message.reply_text('متاسفانه چیزی پیدا نکردم!🥲\nبا کلمه کلیدی دیگه ای در موردش امتحان کن\n\nمیتونی اگه جزوه یا منبع درسی ای تو این موضوع پیدا کردی با آپلودش توی سایت به بقیه کمک کنی❤️')
        else:
            context.user_data['final_response'] = final_response
            update.message.reply_text(f'🟡 این {len(final_response)} تا رو پیدا کردم :👇')
            number_of_sent_response = 0
            for i in final_response:
                if number_of_sent_response <= 4:
                    text = '🟣' + str(i['title']) + ' | ' + str(i['teacher']['name'])
                    keyboard = [[InlineKeyboardButton('دیدن جزئیات', callback_data=str(number_of_sent_response))]]
                    reply_markup = InlineKeyboardMarkup(keyboard)
                    update.message.reply_text(text, reply_markup=reply_markup)
                    number_of_sent_response += 1
                else:
                    context.user_data['number_of_sent_response'] = number_of_sent_response
                    more_buttom = [
                        [InlineKeyboardButton('نتایج بیشتر ...', callback_data='more_data')]
                    ]
                    more_text = 'نتایج بیشتری هم هست 👇'
                    more_data_details = InlineKeyboardMarkup(more_buttom)
                    update.message.reply_text(more_text, reply_markup=more_data_details)
                    break

def response_to_inlinebuttoms(update, context):
    query = update.callback_query
    choosen_one = query.data
    final_response = context.user_data.get('final_response')
    number_of_sent_response = context.user_data.get('number_of_sent_response')
    if choosen_one == 'more_data':
        second_counter = 0
        for i in final_response:
            query.message.delete()
            if second_counter == number_of_sent_response:
                text = '🟣' + str(i['title']) + ' | ' + str(i['teacher']['name'])
                keyboard = [[InlineKeyboardButton('دیدن جزئیات', callback_data=str(number_of_sent_response))]]
                reply_markup = InlineKeyboardMarkup(keyboard)
                query.message.reply_text(text, reply_markup=reply_markup)
            second_counter += 1
    else:
        caption = '🟠 ' + final_response[int(query.data)]['title']
        caption += '\n' + '👨🏻‍🏫 نام استاد: ' + final_response[int(query.data)]['teacher']['name']
        caption += '\n' + '🎒 دانشگاه: ' + final_response[int(query.data)]['university']['name']
        query.message.reply_photo(
            photo=final_response[int(query.data)]['preview']['file'],
            caption=caption,
            reply_markup=InlineKeyboardMarkup(
                [
                    [InlineKeyboardButton('دانلود',
                        url=f'https://hiboo.ir/hub/sources/{final_response[int(query.data)]["slug"]}/download/')]
                ]
            )
        )

def main():
    updater = Updater(bot_token, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, body))
    dp.add_handler(CallbackQueryHandler(response_to_inlinebuttoms))
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
