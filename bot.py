from pyrogram import Client,filters
from pyrogram.types import User, Message,ReplyKeyboardMarkup
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
import redis
import requests
import json
import time

api_id = 1500016
api_hash = "e07225f6d40b6208ea372b72c613d04c"
bot_token = "6682821979:AAGf8Sl_MwxEz44XWLMGOENsXCkLynUypIM"
proxy = { "scheme": "socks5","hostname": "localhost","port": 20801}

bot_database = redis.Redis(host='localhost', port=6379, decode_responses=True)


bot = Client(
    "my_bot",
    api_id=api_id, api_hash=api_hash,
    proxy=proxy,
    bot_token=bot_token
)


@bot.on_message(filters.command('start' or 'برگرد به منو') & filters.private)
def hello(bot, message):
    bottoms = [
        [
            # ('uplode'),
            ('جزوه میخوام🤓'),
            ('هیبو چیه؟')
        ]
    ]
    reply_text = 'هیبو بات هستم🤖 \n آمادم که بهم بگی چیکار کنم:👇'

    mess_markup = ReplyKeyboardMarkup(bottoms,one_time_keyboard=True,resize_keyboard=True)
    message.reply(
        text=reply_text,
        reply_markup=mess_markup
    )
    bot_database.set(message.chat.id, 'start')


    user_name = message.chat.username
    text = f'سلام {user_name} عزیز 🖐🏻' + '\n \n اسم جزوه ای که میخوای رو بهم بگو 🤓 \n یا حتی اسم استادش :)😲 \n \n از منو پایین هم میتونی به قسمت های دیگه ربات دسترسی پیدا کنید😊 \n \n هیبو | دستیار آموزشی تو🦉'
    bot.send_message(message.chat.id, text)


    global back_to_menu
    def back_to_menu(text):
        bottoms1 = [
            [
            ('برگرد به منو'),
            ]
        ]
        reply_text = text
        message.reply(
            text = reply_text,
            reply_markup = ReplyKeyboardMarkup(bottoms1, one_time_keyboard=True, resize_keyboard=True)
        )
        bot_database.set(message.chat.id, 'start')
    

@bot.on_message(filters.private)
def body(bot, message):
    global output, count
    level = bot_database.get(message.chat.id)

    if level == 'start':
        # if message.text == 'uplode':

        #     bot.send_message(message.chat.id, 'رفیق میخوی عکس بدی بهم یا فایل پی دی اف؟')
        #     bot_database.set(message.chat.id, 'uplode setting')

        # elif message.text == 'uplode setting':
        
        if message.text == 'جزوه میخوام🤓':

            bot.send_message(message.chat.id, 'بوگو اسم جزوه ای که میخوایو')
            bot_database.set(message.chat.id, 'download')

        elif message.text == 'هیبو چیه؟':
            
            bot_database.set(message.chat.id, 'aboutus')


            back_to_menu('به تو چه')




    elif level == 'download':
        bot_database.set(message.chat.id, 'search')
        sent_message = bot.send_message(message.chat.id, 'دارم میگردم، یخ وییسه')

        var = message.text
        a = requests.get(f"https://thedana.ir/api/v1/search/?s={var}")
        output = json.loads(a.text)

        bot.delete_messages(message.chat.id, sent_message.id)

        bot.send_message(message.chat.id, f'این {len(output)} تا رو پیدا کردم')

        count = 0
        for i in output:
            
            butt = []
            text = str(i['title']) + ' | ' + str(i['teacher']['name'])

            butt.append([InlineKeyboardButton('دیدن جزئیات', callback_data = str(count))])
            count += 1

            reply_markup = InlineKeyboardMarkup(butt)
            message.reply(
                text = text,
                reply_markup = reply_markup,
            )

        back_to_menu('lk,')
        
        
    elif level == 'aboutus':

        hello(bot, message)


@bot.on_callback_query()
def response_to_buttoms(Client, CallbackQuery):
    
    level = bot_database.get(CallbackQuery.from_user.id)

    if level == 'search':
        bot_database.set(CallbackQuery.from_user.id, 'choosen')

        caption = output[int(CallbackQuery.data)]['title'] + '\n' + 'نام استاد : ' + output[int(CallbackQuery.data)]['teacher']['name'] + '\n' + 'دانشگاه : ' + output[int(CallbackQuery.data)]['university']['name']

        bot.send_photo(
            CallbackQuery.from_user.id,
            output[int(CallbackQuery.data)]['preview']['file'],
            caption = caption,
            reply_markup = InlineKeyboardMarkup(
                [
                    [InlineKeyboardButton('دانلود',
                    url=f'https://thedana.ir/hub/sources/{output[int(CallbackQuery.data)]["slug"]}/download/')]
                ]
            )
        )

        print("hess")

bot.run()
