import aiogram
import time
import logging
import config
from aiogram import types
import user_db
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from parser import hhparser


# Creating logger
logging.basicConfig(filename="WorkScrapper.log", level=logging.DEBUG)
logger = logging.getLogger("WorkScrapper")
# Initialization Bot
try:
    storage = MemoryStorage()
    bot = aiogram.Bot(config.API_TOKEN)
    dp = aiogram.Dispatcher(bot, storage = storage)
    logger.info(f"[{time.strftime('%D %H:%M:%S')}] Bot was initializated successfuly")
except Exception as e:
    print(e)
    logger.error(f"[{time.strftime('%D %H:%M:%S')}] Bot was not initializated due to error: {e}")

# Creating basic users database

users_db = user_db.Users_db("users.db")

# Listenning


class SearchOpts(StatesGroup):
    profession = State()
    experience = State()
    area = State()
    currency = State()
    salary = State()
    
# Welcome func callback ru processing
@dp.callback_query_handler(lambda callback: callback.data == 'ru_lang')
async def welcome_ru_callback(callback_query: types.CallbackQuery):
    users_db.add_user([callback_query.from_user.id, 'ru'])
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(callback_query.from_user.id, 'Русский успешно установлен ✅')
    await bot.delete_message(chat_id=callback_query.from_user.id, message_id=callback_query.message.message_id)

# Welcome func callback en processing
@dp.callback_query_handler(lambda callback: callback.data == 'en_lang')
async def welcome_en_callback(callback_query: types.CallbackQuery):
    users_db.add_user([callback_query.from_user.id, 'en'])
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(callback_query.from_user.id, 'English was successfully set up ✅')
    await bot.delete_message(chat_id=callback_query.from_user.id, message_id=callback_query.message.message_id)

# Search processing   

# Welcome func
@dp.message_handler(commands=['start'])
async def welcome(message: types.Message):
    data = users_db.lookup_user(message.from_user.id)
    if data == None:
        rus_button = types.KeyboardButton("Русский 🇷🇺", callback_data="ru_lang")
        eng_button = types.KeyboardButton("English 🇬🇧", callback_data="en_lang")
        ikm = types.InlineKeyboardMarkup()
        ikm.add(rus_button)
        ikm.add(eng_button)
        await message.answer("Hello! Please choose the language:", reply_markup=ikm)
    else:
        if data[1] == 'ru':
            await message.answer(f"Здравствуйте, {message.from_user.username}! Для того, чтобы подобрать вакансии, вам нужно начать поиск командой /search")
        elif data[1] == 'en':
            await message.answer(f"Hello, {message.from_user.username}! To look for job, you need to start searching with command /search")

# Help func
@dp.message_handler(commands=['help'])
async def help_func(message: types.Message):
    lang = users_db.lookup_user(message.from_user.id)[1]
    if lang == 'ru':
        await message.answer("Вы можете воспользоваться этими командами:\n/start - Начать работу с ботом\n/change_lang - Сменить язык профиля\n/delete_me - Удалить свой аккаунт\n/search - Искать вакансии")
    elif lang == 'en':
        await message.answer("You can use thus commands:\n/start - Start working with bot\n/change_lang - Change profile language\n/delete_me - Delete your account\n/search - Look for job")


# Change language func
@dp.message_handler(commands=['change_lang'])
async def change_lang(message: types.Message):
    action = users_db.change_lang(message.from_user.id)
    if type(action) == dict:
        if action['lang'] == 'ru':
            await message.answer(f"Ваш язык был успешно изменён на русский ✅")
        elif action['lang'] == 'en':
            await message.answer(f"Your language was successuflly changed ✅")
    else: 
        logger.error(action)
        print(action)

# Change language func
@dp.message_handler(commands=['delete_me'])
async def delete_user(message: types.Message):
    lang = users_db.lookup_user(message.from_user.id)[1]
    req = users_db.delete_user(message.from_user.id)
    if req == "Ok":
        if lang == "ru":
            await message.answer(f"Вы удалили свой аккаунт ✅ Чтобы возобновить работу, используйте /start")
        elif lang == "en":
            await message.answer(f"You have deleted your accout ✅ To restart working, use /start")
    else:
        logger.error(req)
        print(req)

# Search func
@dp.message_handler(commands=['search'])
async def search(message: types.Message):
    lang = users_db.lookup_user(message.from_user.id)[1]
    if lang == "ru":
        await SearchOpts.profession.set()
        await message.answer("Введите название  нужной вам профессии: ")
    elif lang == "en":
        await SearchOpts.profession.set()
        await message.answer("Enter the profession's class:")

# Profession state
@dp.message_handler(state=SearchOpts.profession)
async def process_profession(message: types.Message, state: FSMContext):
    lang = users_db.lookup_user(message.from_user.id)[1]
    if lang == "ru":
        async with state.proxy() as data1:
            data1['profession'] = message.text
        await SearchOpts.next()
        from_zero = types.KeyboardButton("0️⃣")
        between_one_and_three = types.KeyboardButton("1️⃣ - 3️⃣")
        between_three_and_six = types.KeyboardButton("3️⃣ - 6️⃣")
        more_than_six = types.KeyboardButton("> 6️⃣")
        ikm = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        ikm.add(from_zero, between_one_and_three, between_three_and_six, more_than_six)
        await message.answer("Выберите опыт работы:", reply_markup=ikm)
    elif lang == "en":
        async with state.proxy() as data1:
            data1['profession'] = message.text
        await SearchOpts.next()
        from_zero = types.KeyboardButton("0️⃣")
        between_one_and_three = types.KeyboardButton("1️⃣ - 3️⃣")
        between_three_and_six = types.KeyboardButton("3️⃣ - 6️⃣")
        more_than_six = types.KeyboardButton("> 6️⃣")
        ikm = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        ikm.add(from_zero, between_one_and_three, between_three_and_six, more_than_six)
        await message.answer("Choose work experience:", reply_markup=ikm)
        
# Experience processing
@dp.message_handler(state=SearchOpts.experience)
async def experience_process(message: types.Message, state: FSMContext):
    if message.text == "0️⃣":
        async with state.proxy() as data1:
            data1['experience'] = "noExperience"
        await SearchOpts.next()
        area_russia = types.KeyboardButton("Россия 🇷🇺")
        area_ukraine = types.KeyboardButton("Украина 🇺🇦")
        ikm = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        ikm.add(area_russia, area_ukraine)
        await message.answer("Выберите регион:", reply_markup=ikm)
    elif message.text == "1️⃣ - 3️⃣":
        async with state.proxy() as data1:
            data1['experience'] = "between1And3"
        await SearchOpts.next()
        area_russia = types.KeyboardButton("Россия 🇷🇺")
        area_ukraine = types.KeyboardButton("Украина 🇺🇦")
        ikm = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        ikm.add(area_russia, area_ukraine)
        await message.answer("Выберите регион:", reply_markup=ikm)
    elif message.text == "3️⃣ - 6️⃣":
        async with state.proxy() as data1:
            data1['experience'] = "between3And6"
        await SearchOpts.next()
        area_russia = types.KeyboardButton("Россия 🇷🇺")
        area_ukraine = types.KeyboardButton("Украина 🇺🇦")
        ikm = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        ikm.add(area_russia, area_ukraine)
        await message.answer("Выберите регион:", reply_markup=ikm)
    elif message.text == "> 6️⃣":
        async with state.proxy() as data1:
            data1['experience'] = "moreThan6"
        await SearchOpts.next()
        area_russia = types.KeyboardButton("Россия 🇷🇺")
        area_ukraine = types.KeyboardButton("Украина 🇺🇦")
        ikm = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        ikm.add(area_russia, area_ukraine)
        await message.answer("Выберите регион:", reply_markup=ikm)


# Area(region) process
@dp.message_handler(state=SearchOpts.area)
async def area_process(message: types.Message, state: FSMContext):
    if message.text == "Россия 🇷🇺":
        async with state.proxy() as data1:
            data1['area'] = 113
        await SearchOpts.next()
        currency_rub = types.KeyboardButton("Рубль")
        currency_uah = types.KeyboardButton("Гривна")
        ikm = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        ikm.add(currency_rub, currency_uah)
        await message.answer("Выберите валюту:", reply_markup=ikm)
    elif message.text == "Украина 🇺🇦":
        async with state.proxy() as data1:
            data1['area'] = 5
        await SearchOpts.next()
        currency_rub = types.KeyboardButton("Рубль")
        currency_uah = types.KeyboardButton("Гривна")
        ikm = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        ikm.add(currency_rub, currency_uah)
        await message.answer("Выберите валюту:", reply_markup=ikm)


# Currency process
@dp.message_handler(state=SearchOpts.currency)
async def currency_process(message: types.Message, state: FSMContext):
    lang = users_db.lookup_user(message.from_user.id)[1]
    if message.text == "Рубль":
        async with state.proxy() as data1:
            data1['currency'] = "RUR"
        await SearchOpts.next()
        if lang == 'ru':
            await message.answer("Введите размер з/п:")
        elif lang == 'en':
            await message.answer("Enter salary size:")           
    elif message.text == 'Гривна':
        async with state.proxy() as data1:
            data1['currency'] = "UAH"
        await SearchOpts.next()
        if lang == 'ru':
            await message.answer("Введите размер з/п:")
        elif lang == 'en':
            await message.answer("Enter salary size:")           
   
# Salary state and finish state
@dp.message_handler(state=SearchOpts.salary)
async def process_salary(message: types.Message, state: FSMContext):
    lang = users_db.lookup_user(message.from_user.id)[1]
    async with state.proxy() as data1:
        data1['salary'] = message.text
        try:
            hhdata = hhparser.get_vacancies(data1)
        except Exception as e:
            print(e)
        if hhdata['status'] == 200:
            # Sending info(data1 array) to nueral network here with function 
            # Now fake func, delete it pls :)
            if lang == "ru":
                await message.answer(f"Вы ввели: \nПрофессию: {data1['profession']} \nОпыт: {data1['experience']} \nРегион: {data1['area']} \nВалюту: {data1['currency']} \nЗ/п: {data1['salary']}")
                await message.answer(f"Найдено {hhdata['pages']} страниц ✔️ Выведено первые 10 вакансий:")
                for i in range(10):
                    await message.answer(f"Источник: {hhdata['items'][i]['url']} \n Должность: {hhdata['items'][i]['name']} \n Регион: {hhdata['items'][i]['area']['name']} \n Минимальная зарплата: {hhdata['items'][i]['salary']['from']} \n Максимальная зарплата: {hhdata['items'][i]['salary']['to']}")
            elif lang == "en":
                await message.answer(f"You entered: \nProfession: {data1['profession']} \nExperience: {data1['experience']} \nRegion: {data1['area']} \nCurrency: {data1['currency']} \nSalary: {data1['salary']}")
                await message.answer(f"Found {hhdata['pages']} pages ✔️ Printed first ten vacancies:")
                for i in range(10):
                    await message.answer(f"Source: {hhdata['items'][i]['url']} \n Profession: {hhdata['items'][i]['name']} \n Region: {hhdata['items'][i]['area']['name']} \n Maximal salary: {hhdata['items'][i]['salary']['from']} \n Minimal salary: {hhdata['items'][i]['salary']['to']}")
        else:
            await message.answer(f"Unknown error: {hhdata['status']}")
        # Sending info(data1 array) to nueral network here with function 
        # Now fake func, delete it pls :)
    # End dialog here
    await state.finish()
    

if __name__ == '__main__':
    aiogram.executor.start_polling(dp, skip_updates=True)

