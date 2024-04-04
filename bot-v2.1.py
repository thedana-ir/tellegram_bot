from pyrogram import Client, filters
from pyrogram.types import ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
import os
import requests
import json

# Telegram authorization
api_id = 1500016
api_hash = "e07225f6d40b6208ea372b72c613d04c"
bot_token = "6541504105:AAHsRnVkr8pbbbCkXEmvdQXqPsG01Po03gE"
proxy = None

# Bot object
bot = Client(
    "hiboo",
    api_id=api_id,
    api_hash=api_hash,
    bot_token=bot_token,
    proxy=proxy,
)

# Function to create reply keyboard buttons
def reply_keyboard_button(text, buttons, one_time_being):
    return ReplyKeyboardMarkup(
        buttons,
        one_time_keyboard=one_time_being,
        resize_keyboard=True
    )

# Function to create inline keyboard buttons
def inline_keyboard_buttons(text, buttons):
    return InlineKeyboardMarkup(buttons)

# Function to send message with inline keyboard
def send_message_with_inline_keyboard(bot, chat_id, text, buttons):
    bot.send_message(
        chat_id=chat_id,
        text=text,
        reply_markup=inline_keyboard_buttons(text, buttons)
    )

# Function to handle callback queries
@bot.on_callback_query()
def response_to_inline_buttons(bot, callback_query):
    choosen_one = callback_query.data
    final_response = callback_query.message.reply_to_message.final_response
    
    if choosen_one == 'more_data':
        number_of_sent_response = callback_query.message.reply_to_message.number_of_sent_response
        more_data_details = callback_query.message.reply_to_message.more_data_details
        bot.delete_messages(callback_query.from_user.id, more_data_details.id)
        for i in final_response[int(number_of_sent_response):]:
            buttoms = []
            text = '🟣' + str(i['title']) + ' | ' + str(i['teacher']['name'])

            buttoms.append([InlineKeyboardButton('دیدن جزئیات', callback_data = str(number_of_sent_response))])
            number_of_sent_response += 1

            inline_keyboard_buttons(text, buttoms)
    else:
        # create caption to send with preview photo
        caption = '🟠 ' + final_response[int(callback_query.data)]['title']
        caption += '\n' + '👨🏻‍🏫 نام استاد: ' + final_response[int(callback_query.data)]['teacher']['name']
        caption += '\n' + '🎒 دانشگاه: ' + final_response[int(callback_query.data)]['university']['name']

        # send result with preview, caption and a button to download
        bot.send_photo(

            # where to send
            callback_query.from_user.id,
            
            # photo 
            final_response[int(callback_query.data)]['preview']['file'],

            # caption
            caption = caption,

            # button that linked to source in website
            reply_markup = InlineKeyboardMarkup(
                [
                    [InlineKeyboardButton('دانلود',
                    url=f'https://hiboo.ir/hub/sources/{final_response[int(callback_query.data)]["slug"]}/download/')]
                ]
            )
        )

# Function to handle private messages
@bot.on_message(filters.private & filters.command('start'))
def start(bot, message):
    user_name = message.chat.username
    text = f'سلام {user_name} عزیز 🖐🏻\n\n اسم جزوه ای که میخوای رو بهم بگو 🤓 \n یا حتی اسم استادش :)😲 \n\n هیبو | دستیار آموزشی تو🦉'
    buttons = [
        [('میخوام جزوه آپلود کنم')],
        [('راهنما ربات'), ('هیبو چیه')]
    ]
    bot.send_message(
        chat_id=message.chat.id,
        text=text,
        reply_markup=reply_keyboard_button(text, buttons, False)
    )

@bot.on_message(filters.private)
def body(bot, message):
    level = message.text
    if level == 'میخوام جزوه آپلود کنم':
        bot.send_message(message.chat.id, 'متاسفانه این قابلیت هنوز تکمیل نشده \n بزودی این امکان هم به ربات اضافه میشه 😀')
    elif level == 'راهنما ربات':
        bot.send_message(message.chat.id, 'هیبو بات هستم 🤖\n\nهر جای چت که هستی میتونی اسم درست یا استادی که میخوای رو برام بنویسی 🤓\nمن برات میگردم و همه نتایجی که پیدا کردم رو نشون میدم😉\nهمینطور از دکمه های منو میتونی هم منابع درسی خودت رو آپلود کنی هم به وبسایت وصل بشی💯\n\nامیدوارم تونسته باشم خوب راهنماییت کنم✌️')
    elif level == 'هیبو چیه':
        bot.send_message(message.chat.id, 'اینو محسن بگه میگم بت')
    else:
        sent_message = bot.send_message(message.chat.id, 'صبر کن ببینم چی داریم 🤔')
        wanted_word = message.text
        website_response = requests.get(f"https://hiboo.ir/api/v1/search/?s={wanted_word}")
        final_response = json.loads(website_response.text)

        if len(final_response) == 0:
            bot.send_message(message.chat.id, 'متاسفانه چیزی پیدا نکردم!🥲\nبا کلمه کلیدی دیگه ای در موردش امتحان کن\n\nمیتونی اگه جزوه یا منبع درسی ای تو این موضوع پیدا کردی با آپلودش توی سایت به بقیه کمک کنی❤️')
        else:
            sent_message.reply_to_message.final_response = final_response
            
            bot.send_message(message.chat.id, f'🟡 این {len(final_response)} تا رو پیدا کردم :👇')

            number_of_sent_response = 0
            for i in final_response:
                if number_of_sent_response <= 4:
                    text = '🟣' + str(i['title']) + ' | ' + str(i['teacher']['name'])
                    buttons = [[InlineKeyboardButton('دیدن جزئیات', callback_data=str(number_of_sent_response))]]
                    send_message_with_inline_keyboard(bot, message.chat.id, text, buttons)
                    number_of_sent_response += 1
                else:
                    sent_message.reply_to_message.number_of_sent_response = number_of_sent_response
                    more_text = 'نتایج بیشتری هم هست 👇'
                    more_buttons = [[InlineKeyboardButton('نتایج بیشتر ...', callback_data='more_data')]]
                    sent_message.reply_to_message.more_data_details = more_buttons
                    
                    send_message_with_inline_keyboard(bot, message.chat.id, more_text, more_buttons)
                    break

# Run the bot
bot.run()
