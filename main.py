import requests
import datetime
import logging
import time
from aiogram import Bot, Dispatcher, executor, types
import openai
from openexchangerate import OpenExchangeRates
 
client = OpenExchangeRates(api_key="a9f703b216bb4ae892dfe9c852de596f")
 
 


open_weather_token='8725811879ec8424cd3a8e950f0011b9'
#погода токен 


bot_token = '6282024430:AAHlACtH9Grplwr0GJZijhsPN6rWc_lI0Po'# токен телеграмм бота

api_key = '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' #api openai для генерации картинок(dall-e) и gpt
logging.basicConfig(level=logging.INFO)

bot = Bot(token=bot_token)
dp = Dispatcher(bot)

openai.api_key = api_key #api openai для генерации картинок(dall-e) и gpt
messages = {} #для сохранения разговора в /gpt

#функция жля генерации картинок:
async def generate_image(prompt):
    response = openai.Image.create(
        prompt=prompt,
        n=1,
        size="512x512", 
        response_format="url",
    )

    return response['data'][0]['url']



#/start
@dp.message_handler(commands=['start'])
async def start_cmd(message: types.Message):
    try:
        username = message.from_user.username
        messages[username] = []
        await message.answer(f"Привет {username},я чат бот ,у меня есть несколько функций: \n /image ...-нартсовать рисунок(в разработке) \n /gpt... -спросить вопрос(в разработке) \n /weather - прогноз погоды  \n /money -курс валют \n /poll -создать опрос\n/dice -поиграть\n/donate -сылочка на донат \n/dict -переводчик\n/fix-исправить фразу")
    except Exception as e:
        logging.error('Error')
        
#/donate
@dp.message_handler(commands=['donate'])
async def donate(message: types.Message):
        await message.answer(f"Пожалуста скинь денюжек\nЭто ускорит выход обновения\nhttps://www.sberbank.com/ru/person/dl/jc?linkname=mK3yKz8m4Ti45aCt0")

#/fix
@dp.message_handler(commands=["fix"])

async def fix(message: types.Message):
    mess=message.text
    mess=mess.replace("/fix ","")
    mess=mess.replace(" ","+")
    rek=requests.get(f"https://predictor.yandex.net/api/v1/predict.json/complete?key=pdct.1.1.20230502T171116Z.a00397515ddc2594.7b67794b02491b24599de994409e35970f46912e&q={mess}&lang=en")
    fixe=rek.json()
    fixi=fixe["text"]
    chekat=fixe["endOfWord"]
    if chekat==False:
        await message.reply(f"исправленная фраза:{fixi}")
    else:
        await message.reply(f"слово и так целое либо ошибка\nПример использования:\n/fix appl")
          
#/dict
@dp.message_handler(commands=['dict'])
async def dict(message: types.Message):
    try:
        eng=message.text
        eng =eng.replace("/dict ","")
        perevod = requests.get(f"https://dictionary.yandex.net/api/v1/dicservice.json/lookup?key=dict.1.1.20230501T154127Z.ac561c32271cd3d6.c83f81519cddcb667b3dcf6d208597a1940269d2&lang=en-ru&text={eng}") 
        translate=perevod.json()
        qaz=translate["def"]
        xer=list(qaz)
        zxlol=xer[0]
        nae=list(zxlol.get("tr"))
        nal=nae[0]
        rus=nal.get("text")
        await message.reply(rus)
    except:
        await message.reply("Ошибка перевода\nПример использования:\n/dict apple\nПока что можно переводить только по 1 слову")

#/dice 1...6
@dp.message_handler(commands=["dice"])
async def cmd_dice(message: types.Message):
    game=message.text
    game=game.replace("/dice ","")

    if game=="1":
        await message.answer_dice(emoji="🎲")
    elif game=="2":
        await message.answer_dice(emoji="🎯")
    elif game=="3":
        await message.answer_dice(emoji="🏀")
    elif game=="4":
        await message.answer_dice(emoji="⚽")
    elif game =="5":
        await message.answer_dice(emoji="🎰")
    elif game=="6":
        await message.answer_dice(emoji="🎳")
    else:
        await message.reply('Неправильный ввод\nПример:\n/dice 1\n1-кубик, 2-дартс\n3-баскетбольный мяч\n4-футбольный мяч\n5-слот машина\n6-боулинг')
        

#опросы /poll
@dp.message_handler(commands=['poll'])
async def poll(message: types.Message):
    try:
        qwert=message.text
        qwert=qwert.replace('/poll ','')
        qwer=[]
        qwer=qwert.split('; ')
        await message.answer_poll(question=qwer[0],
                                  options=qwer[1:],
                                  type='regular',
                                  is_anonymous=False)
    except:
        await message.reply('Неправильный ввод\nПример ввода:\n/poll вопрос; ответ1; ответ2')


#курс валюты /money
@dp.message_handler(commands=['money'])
async def kurs_valut(message: types.Message):
    try:    
        price=client.latest().dict
        x=[]
        vvod=message.text
        vvod=vvod.replace('/money ','')
        x=vvod.split(' ')
        name_value=x[0]
        kolizhestvo=x[1]
        vivod=float(price[name_value])*float(kolizhestvo)
       
        await message.reply(f'{kolizhestvo} USD= {vivod} {name_value}')
    except:
        await message.reply('Неправильный ввод\nПример ввода:\n/money RUB 1')
    
#/image....
@dp.message_handler(commands=['image'])
async def send_image(message: types.Message):
    try:
        description = message.text.replace('/image', '').strip()
        if not description:
            await message.reply('Напиши что нибуть после /image' ,parse_mode='Markdown')
            return
    except Exception as e:
        logging.error(f'Error in send_image: {e}')
    try:
        image_url = await generate_image(description)
        await bot.send_photo(chat_id=message.chat.id, photo=image_url)
    except Exception as e:
        await message.reply(
            f"ERROR")





        
#/gpt...
@dp.message_handler(commands=['gpt'])
async def echo_msg(message: types.Message):
    try:
        user_message = message.text
        userid = message.from_user.username

        # добавление в историю разговоров
        if userid not in messages:
            messages[userid] = []
        messages[userid].append({"role": "user", "content": user_message})
        messages[userid].append({"role": "user",
                                 "content": f"chat: {message.chat} Сейчас {time.strftime('%d/%m/%Y %H:%M:%S')} user: {message.from_user.first_name} message: {message.text}"})
        logging.info(f'{userid}: {user_message}')

        # проверка на приход сообщения 
        should_respond = not message.reply_to_message or message.reply_to_message.from_user.id == bot.id

        if should_respond:
            # отправка временного сообщения пока ожидаем ответ от openai
            processing_message = await message.reply(
                'Бот думает,подождите...',
                parse_mode='Markdown')

            # ...печатает
            await bot.send_chat_action(chat_id=message.chat.id, action="typing")

            #модель gpt
            completion = await openai.ChatCompletion.acreate(
                model="gpt-3.5-turbo",
                messages=messages[userid],
                max_tokens=2500,
                temperature=0.7,
                frequency_penalty=0,
                presence_penalty=0,
                user=userid
            )
            chatgpt_response = completion.choices[0]['message']

            # добавление в историю разговоров 
            messages[userid].append({"role": "assistant", "content": chatgpt_response['content']})
            logging.info(f'ChatGPT response: {chatgpt_response["content"]}')

            # отправка
            await message.reply(chatgpt_response['content'])

            # удаление временного сообщения
            await bot.delete_message(chat_id=processing_message.chat.id, message_id=processing_message.message_id)

    except Exception as ex:
        if ex == "context_length_exceeded":
            await message.reply(
                'У бота закончилась память',
                parse_mode='Markdown')
            await new_topic_cmd(message)
            await echo_msg(message)




#погода 'город' 
@dp.message_handler(commands=['weather']) 
async def get_weather(message: types.Message):
    code_to_smile = { 
         "Clear": "Ясно \U00002600", 
         "Clouds": "Облачно \U00002601", 
         "Rain": "Дождь \U00002614", 
         "Drizzle": "Дождь \U00002614", 
         "Thunderstorm": "Гроза \U000026A1", 
         "Snow": "Снег \U0001F328", 
         "Mist": "Туман \U0001F32B" 
     } 
  
    try: 
         message.text=message.text.replace('/weather ','')
         r = requests.get( 
             f"http://api.openweathermap.org/data/2.5/weather?q={message.text}&appid={open_weather_token}&units=metric" 
         ) 
         data = r.json() 
  
         city = data["name"] 
         cur_weather = data["main"]["temp"] 
  
         weather_description = data["weather"][0]["main"] 
         if weather_description in code_to_smile: 
             wd = code_to_smile[weather_description] 
         else: 
             wd = "⭐️" 
  
         humidity = data["main"]["humidity"] 
         pressure = data["main"]["pressure"] 
         wind = data["wind"]["speed"] 
         sunrise_timestamp = datetime.datetime.fromtimestamp(data["sys"]["sunrise"]) 
         sunset_timestamp = datetime.datetime.fromtimestamp(data["sys"]["sunset"]) 
         length_of_the_day = datetime.datetime.fromtimestamp(data["sys"]["sunset"]) - datetime.datetime.fromtimestamp( 
             data["sys"]["sunrise"]) 
  
         await message.reply(f"***{datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}***\n" 
                                               f"Погода в городе: {city}\nТемпература: {cur_weather}C° {wd}\n" 
                                               f"Влажность: {humidity}%\nДавление: {pressure} мм.рт.ст\nВетер: {wind} м/с\n" 
                                               f"Продолжительность дня: {length_of_the_day}\n" 
                                               f"⭐️Удачного дня!⭐️" 
                                                   ) 
 
    except: 
         await message.reply("Город не найден\nПример ввода:\n/weather Kemerovo") 


#старт бота 
if __name__ == '__main__':
    executor.start_polling(dp)