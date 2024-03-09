from pyrogram import Client,filters
from pyrogram.types import User, Message,ReplyKeyboardMarkup
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
import redis
import requests
import json


# tellegrom authorization 
# must be in invirment variable!!!!!!!!!!!!!!!!!!!!!!!!!!

api_id = 1500016
api_hash = "e07225f6d40b6208ea372b72c613d04c"
bot_token = "6541504105:AAHsRnVkr8pbbbCkXEmvdQXqPsG01Po03gE"
proxy = { "scheme": "socks5","hostname": "localhost","port": 20801}


# redis database for level partitioning

bot_database = redis.Redis(host='localhost', port=6379, decode_responses=True)

# bot object

bot = Client(
    "hiboo",
    api_id=api_id, api_hash=api_hash,
    bot_token=bot_token,
    proxy=proxy,
)

# section 1: private chats
 
#   part 1: chat creation & deffenitions 

@bot.on_message(filters.command('start') & filters.private)
def start(bot, message):
    global reply_keyboard_buttom, inline_keyboard_buttoms, back_to_menu

    # keyboard buttoms creater
    def reply_keyboard_buttom(text, buttoms, one_time_being):

        message.reply(
            text=text,
            reply_markup = ReplyKeyboardMarkup(
                buttoms,
                one_time_keyboard=one_time_being,
                resize_keyboard=True
                )
        )

    # inline buttoms creater
    def inline_keyboard_buttoms(text, buttoms):

        a = message.reply(
            text = text,
            reply_markup = InlineKeyboardMarkup(buttoms)
        )

        return a
        

    # buttom in keyboard for return to home
    def back_to_menu(text):

        bottoms = [
            [
            ('برگرد به منو'),
            ]
        ]

        reply_keyboard_buttom(text, bottoms)
        bot_database.set(message.chat.id, 'start')

    # def send_inline_buttoms()

    # hello message and menu
    user_name = message.chat.username
    text = f'سلام {user_name} عزیز 🖐🏻' + '\n \n اسم جزوه ای که میخوای رو بهم بگو 🤓 \n یا حتی اسم استادش :)😲 \n \n از منو پایین هم میتونی به قسمت های دیگه ربات دسترسی پیدا کنید😊 \n \n هیبو | دستیار آموزشی تو🦉'
    buttoms = [
        [
            ('میخوام جزوه آپلود کنم')
        ],
        [
            ('راهنما ربات'), ('هیبو چیه')
        ]
    ]
    reply_keyboard_buttom(text, buttoms,False)


#   part 2: find word in website & response to keyboard buttoms
    
@bot.on_message(filters.private)
def body(bot, message):

    level = message.text
    # answer to buttoms
    if level == 'میخوام جزوه آپلود کنم':

        bot.send_message(message.chat.id, 'متاسفانه این قابلیت هنوز تکمیل نشده \n بزودی این امکان هم به ربات اضافه میشه 😀')

    elif level == 'راهنما ربات':

        bot.send_message(message.chat.id, 'هیبو بات هستم 🤖\n\nهر جای چت که هستی میتونی اسم درست یا استادی که میخوای رو برام بنویسی 🤓\nمن برات میگردم و همه نتایجی که پیدا کردم رو نشون میدم😉\nهمینطور از دکمه های منو میتونی هم منابع درسی خودت رو آپلود کنی هم به وبسایت وصل بشی💯\n\nامیدوارم تونسته باشم خوب راهنماییت کنم✌️')
    
    elif level == 'هیبو چیه':
        
        bot.send_message(message.chat.id, 'اینو محسن بگه میگم بت')

    # serach for data in website
    else:
        
        # first message to tell client please wait
        sent_message = bot.send_message(message.chat.id, 'صبر کن ببینم چی داریم 🤔')

        # request to website backend
        wanted_word = message.text
        website_response = requests.get(f"https://hiboo.ir/api/v1/search/?s={wanted_word}")

        global final_response
        final_response = json.loads(website_response.text)

        # delete sent message
        bot.delete_messages(message.chat.id, sent_message.id)

        # condition for if there wasn't any data to return
        if len(final_response) == 0:

            bot.send_message(message.chat.id, 'متاسفانه چیزی پیدا نکردم!🥲\nبا کلمه کلیدی دیگه ای در موردش امتحان کن\n\nمیتونی اگه جزوه یا منبع درسی ای تو این موضوع پیدا کردی با آپلودش توی سایت به بقیه کمک کنی❤️')
        
        # show found result in inline buttoms
        else:
        
            bot.send_message(message.chat.id, f'🟡 این {len(final_response)} تا رو پیدا کردم :👇')

            global number_of_sent_response
            number_of_sent_response = 0
            for i in final_response:

                if number_of_sent_response <= 4:

                    buttom = []
                    text = '🟣' + str(i['title']) + ' | ' + str(i['teacher']['name'])

                    buttom.append([InlineKeyboardButton('دیدن جزئیات', callback_data = str(number_of_sent_response))])
                    number_of_sent_response += 1

                    inline_keyboard_buttoms(text, buttom)

                else:

                    more_buttom = [
                        [InlineKeyboardButton('نتایج بیشتر ...', callback_data = 'more_data')]
                    ]
                    more_text = 'نتایج بیشتری هم هست 👇'
                    global more_data_details
                    more_data_details = inline_keyboard_buttoms(more_text, more_buttom)
                    break

#   part 3: response to choosen inline buttom 
@bot.on_callback_query()
def response_to_inlinebuttoms(Client, CallbackQuery):
    global number_of_sent_response, final_response, more_data_details
    
    # set choosen_one for data returned of buttoms
    choosen_one = CallbackQuery.data
    
    # button of show more results
    if choosen_one == 'more_data':

        second_counter = 0
        for i in final_response:
            
            bot.delete_messages(CallbackQuery.from_user.id, more_data_details.id)
            if second_counter == number_of_sent_response:

                buttoms = []
                text = '🟣' + str(i['title']) + ' | ' + str(i['teacher']['name'])

                buttoms.append([InlineKeyboardButton('دیدن جزئیات', callback_data = str(number_of_sent_response))])
                number_of_sent_response += 1

                inline_keyboard_buttoms(text, buttoms)

            second_counter += 1

    # buttons of showed results
    else:
        
        # create caption to send with preview photo
        caption = '🟠 ' + final_response[int(CallbackQuery.data)]['title']
        caption += '\n' + '👨🏻‍🏫 نام استاد: ' + final_response[int(CallbackQuery.data)]['teacher']['name']
        caption += '\n' + '🎒 دانشگاه: ' + final_response[int(CallbackQuery.data)]['university']['name']

        # send result with preview, caption and a button to download
        bot.send_photo(

            # where to send
            CallbackQuery.from_user.id,
            
            # photo 
            final_response[int(CallbackQuery.data)]['preview']['file'],

            # caption
            caption = caption,

            # button that linked to source in website
            reply_markup = InlineKeyboardMarkup(
                [
                    [InlineKeyboardButton('دانلود',
                    url=f'https://hiboo.ir/hub/sources/{final_response[int(CallbackQuery.data)]["slug"]}/download/')]
                ]
            )
        )


# lets run:)
bot.run()
