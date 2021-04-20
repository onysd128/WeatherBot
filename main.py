from pyowm import OWM
from pyowm.utils.config import get_default_config
from PIL import Image,ImageDraw,ImageFont
import requests
from datetime import datetime
from datetime import timedelta
import telebot
import sqlite3

bot=telebot.TeleBot('1561780267:AAHdNoaHSk9h_O0LwuwTTxlMoJWYGF_sYX8',skip_pending=True)

def AddUser(message):

    db = sqlite3.connect('weatherbot.db')
    sql = db.cursor()
    sql.execute(f"SELECT TelegramID FROM users WHERE TelegramID={message.chat.id}")
    if sql.fetchall():
        pass
    else:
        sql.execute("INSERT INTO users VALUES(?,?)", (message.chat.id, message.from_user.first_name))
    db.commit()

def AddMessage(message):
    db = sqlite3.connect('weatherbot.db')
    sql = db.cursor()
    sql.execute("INSERT INTO messages VALUES(?,?,?,?,?)", (message.id, message.chat.id, message.from_user.first_name,message.text,str(datetime.now())[:19]))
    db.commit()

print('WeatherBot UP!')


@bot.message_handler(commands=['users'])
def users(message):
    AddMessage(message)
    k=''
    db = sqlite3.connect('weatherbot.db')
    sql = db.cursor()
    sql.execute(f"SELECT * FROM users")
    for i in sql.fetchall():
        k+=f'ID: {i[0]} FirstName: {i[1]}\n\n'
    bot.send_message(message.chat.id,k)

@bot.message_handler(commands=['messages'])
def messages(message):
    AddMessage(message)
    try:
        m = message.text.split()
        db = sqlite3.connect('weatherbot.db')
        sql = db.cursor()
        f=sql.execute(f"SELECT * FROM messages WHERE UserID={int(m[1])}")
        k = ''
        for i in f:
            k+=i[4]+'\n'+i[3]+'\n\n'
        bot.send_message(message.chat.id,text=k)
    except:
        bot.reply_to(message,'В данного користувача нема повідомленнь')

@bot.message_handler(commands=['start'])
def start(message):
    AddUser(message)
    AddMessage(message)
    bot.send_message(message.chat.id, 'Привіт! Хочеш підкажу погоду?\nВкажи назву свого міста!')
@bot.message_handler(content_types=['text'])
def weather(message):
    AddUser(message)
    AddMessage(message)
    #print(f'Хтось користується ботом: {message.chat.id}, {message.from_user.first_name}')
    try:
        config_dict = get_default_config()
        config_dict['language'] = 'ua'

        owm = OWM('5c6c1f1f8dd5f79886a516e4e6ed04e4',config_dict)
        mgr = owm.weather_manager()

        city=message.text.title()
        weather_today=mgr.weather_at_place(city).weather
        weather_forecast=mgr.forecast_at_place(city,'3h')

        today = datetime.date(datetime.today())
        tomorrow = today+timedelta(days=1)

        weather_hours=['03','08','15','20']

        weather_tommorow= []
        weather_tommorow_icons_url=[]

        #get weather and icons url's
        for i in weather_hours:
           weather_tommorow.append(weather_forecast.get_weather_at(f"{tomorrow} {i}:00:00+00:00"))
           weather_tommorow_icons_url.append(weather_tommorow[len(weather_tommorow)-1].weather_icon_url())


        #r=requests.get(wi[:36]+'@4x.png',stream=True).raw

        bg=Image.open('bg.jpg')
        draw=ImageDraw.Draw(bg,mode='RGBA')

        tsx1=80
        tsy1=400
        tsx2=280
        tsy2=600

        city_font=ImageFont.truetype('20011.ttf',100)
        day_font=ImageFont.truetype('20011.ttf',80)
        ds_font = ImageFont.truetype('20011.ttf',45)
        ds_font2 = ImageFont.truetype('20011.ttf',45)

        draw.text((20,2000),text='@beatvin_weather_bot',fill=None,font=day_font)
        draw.text((100,100),text=city,fill=None,font=city_font)

        draw.text((tsx1,tsy1-100),text='Сьогодні',fill=None,font=day_font)
        draw.text((tsx1+600,tsy1-100),text='Завтра',fill=None,font=day_font)

        ###
        draw.rectangle((tsx1,tsy1+250,tsx2+350,tsy2+750),fill=(0,0,0,100),outline='black')
        draw.rectangle((tsx1,tsy1,tsx2,tsy2),fill=(255,255,255,100))

        wi=weather_today.weather_icon_url()

        r=requests.get(wi[:36]+'@4x.png',stream=True).raw
        weather_icon=Image.open(r).resize((200,200))
        weather_icon_mask = weather_icon.convert("RGBA")
        bg.paste(weather_icon,(tsx1,tsy1),weather_icon_mask)

        draw.rectangle((tsx1+220,tsy1,tsx2+350,tsy2),fill=(0,0,0,100))

        draw.multiline_text((tsx1+225,tsy1+10),text=f"{str(weather_today.detailed_status).title()}\n{today}",fill=None,font=ds_font,spacing=50)
        draw.multiline_text((tsx1+20,tsy1+315),text=f"Вітер: {weather_today.wind()['speed']}м/с; {weather_today.wind()['deg']}°;\n"
                                                    f"Темп.: {weather_today.temperature('celsius')['temp']}°C;\n"
                                                    f"Вологість: {weather_today.humidity}%\n"
                                                    f"Захмареність: {weather_today.clouds}%\n"                                            
                                                    f"Атмосферний тиск: {weather_today.pressure['press']}\n",fill=None,font=ds_font2,spacing=90)
        ###

        ###
        draw.rectangle((tsx1+600,tsy1,tsx2+600,tsy2),fill=(255,255,255,100))

        wi=weather_tommorow_icons_url[0]
        r=requests.get(wi[:36]+'@4x.png',stream=True).raw
        weather_icon=Image.open(r).resize((200,200))
        weather_icon_mask = weather_icon.convert("RGBA")
        bg.paste(weather_icon,(tsx1+600,tsy1),weather_icon_mask)
        draw.rectangle((tsx1+600+220,tsy1,tsx2+600+250+200,tsy2),fill=(0,0,0,100))

        draw.multiline_text((tsx1+225+600,tsy1+10),text=f"{weather_hours[0]}:00, T: {round(weather_tommorow[0].temperature('celsius')['temp'])} °C\nВітер: {str(weather_tommorow[0].wind()['speed'])} м/с\n{str(weather_tommorow[0].detailed_status.title()) }",fill=None,font=ds_font,spacing=30)
        #####
        draw.rectangle((tsx1+600,tsy1+250,tsx2+600,tsy2+250),fill=(255,255,255,100))

        wi=weather_tommorow_icons_url[1]
        r=requests.get(wi[:36]+'@4x.png',stream=True).raw
        weather_icon=Image.open(r).resize((200,200))
        weather_icon_mask = weather_icon.convert("RGBA")
        bg.paste(weather_icon,(tsx1+600,tsy1+250),weather_icon_mask)

        draw.rectangle((tsx1+600+220,tsy1+250,tsx2+600+250+200,tsy2+250),fill=(0,0,0,100))
        draw.multiline_text((tsx1+225+600,tsy1+10+250),text=f"{weather_hours[1]}:00, T: {round(weather_tommorow[1].temperature('celsius')['temp'])} °C\nВітер: {str(weather_tommorow[1].wind()['speed'])} м/с\n{str(weather_tommorow[1].detailed_status.title()) }",fill=None,font=ds_font,spacing=30)
        #####
        draw.rectangle((tsx1+600,tsy1+500,tsx2+600,tsy2+500),fill=(255,255,255,100))

        wi=weather_tommorow_icons_url[2]
        r=requests.get(wi[:36]+'@4x.png',stream=True).raw
        weather_icon=Image.open(r).resize((200,200))
        weather_icon_mask = weather_icon.convert("RGBA")
        bg.paste(weather_icon,(tsx1+600,tsy1+500),weather_icon_mask)

        draw.rectangle((tsx1+600+220,tsy1+500,tsx2+600+250+200,tsy2+500),fill=(0,0,0,100))
        draw.multiline_text((tsx1+225+600,tsy1+10+500),text=f"{weather_hours[2]}:00, T: {round(weather_tommorow[2].temperature('celsius')['temp'])} °C\nВітер: {str(weather_tommorow[2].wind()['speed'])} м/с\n{str(weather_tommorow[2].detailed_status.title()) }",fill=None,font=ds_font,spacing=30)

        #####
        draw.rectangle((tsx1+600,tsy1+750,tsx2+600,tsy2+750),fill=(255,255,255,100))

        wi=weather_tommorow_icons_url[3]
        r=requests.get(wi[:36]+'@4x.png',stream=True).raw
        weather_icon=Image.open(r).resize((200,200))
        weather_icon_mask = weather_icon.convert("RGBA")
        bg.paste(weather_icon,(tsx1+600,tsy1+750),weather_icon_mask)

        draw.rectangle((tsx1+600+220,tsy1+750,tsx2+600+250+200,tsy2+750),fill=(0,0,0,100))
        draw.multiline_text((tsx1+225+600,tsy1+10+750),text=f"{weather_hours[3]}:00, T: {round(weather_tommorow[3].temperature('celsius')['temp'])} °C\nВітер: {str(weather_tommorow[3].wind()['speed'])} м/с\n{str(weather_tommorow[3].detailed_status.title()) }",fill=None,font=ds_font,spacing=30)

        #####
        # draw.rectangle((100,100,300,300),fill=(255,255,255,100),outline='black')
        # draw.rectangle((100,100,300,300),fill=(255,255,255,100),outline='black')


        # img=Image.open(r)
        # img.show()

        #bg.show()
        bot.send_photo(message.chat.id,bg)
    except:
        bot.reply_to(message,'Я не знаю такого міста')


bot.polling()