import requests
import datetime
import logging
import time
from aiogram import Bot, Dispatcher, executor, types
import openai
from bs4 import BeautifulSoup
from openexchangerate import OpenExchangeRates
 
client = OpenExchangeRates(api_key="a9f703b216bb4ae892dfe9c852de596f")
 
 


open_weather_token='8725811879ec8424cd3a8e950f0011b9'
#погода токен 


bot_token = '6282024430:AAHlACtH9Grplwr0GJZijhsPN6rWc_lI0Po'# токен телеграмм бота

api_key = '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'  #api openai для генерации картинок(dall-e) и gpt
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
        await message.answer(f"Привет,я чат бот ,у меня есть несколько функций: /n  /image ...-нартсовать рисунок /n /gpt... -спросить вопрос /n /weather 'город' - прогноз погоды /n /money -курс валют")
    except Exception as e:
        logging.error('Error')

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
        await message.reply('incorrect input')


#курс валюты /money
@dp.message_handler(commands=['money'])
async def kurs_valut(message: types.Message):
    try:
        price=dict(client.latest().dict)
        x=[]
        vvod=message.text
        vvod=vvod.replace('/money ','')
        x=vvod.split('; ')
        name_value=x[0]
        kolizhestvo=x[1]
        vivod=int(price[name_value])*int(kolizhestvo)
        await message.reply(vivod)
    except:
        await message.reply('incorrect input')
    
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
             wd = "ошибка" 
  
         humidity = data["main"]["humidity"] 
         pressure = data["main"]["pressure"] 
         wind = data["wind"]["speed"] 
         sunrise_timestamp = datetime.datetime.fromtimestamp(data["sys"]["sunrise"]) 
         sunset_timestamp = datetime.datetime.fromtimestamp(data["sys"]["sunset"]) 
         length_of_the_day = datetime.datetime.fromtimestamp(data["sys"]["sunset"]) - datetime.datetime.fromtimestamp( 
             data["sys"]["sunrise"]) 
  
         await message.reply(f"***{datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}***\n" 
               f"городе: {city}\nТемпература: {cur_weather}C° {wd}\n" 
               f"Влажность: {humidity}%\nДавление: {pressure} мм.рт.ст\nВетер: {wind} м/с\n" 
               f"Восход: {sunrise_timestamp}\nЗакат: {sunset_timestamp}\nПродолжительность дня: {length_of_the_day}\n" 
               f"Удачи)
               ) 
 
    except: 
         await message.reply("такого города нету") 


#старт бота 
if __name__ == '__main__':
    executor.start_polling(dp)