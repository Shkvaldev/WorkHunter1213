import aiogram
import time
import logging
import config
from aiogram import types
import user_db
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext



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
    custom_position = State()
    operating_schedule_id = State()
    salary_from = State()
    salary_to = State()
    offer_education_id = State()
    offer_experience_year_count = State()
    age_from = State()
    age_to = State()
    is_nonresident = State()
    is_male = State()



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
        await SearchOpts.custom_position.set()
        await message.answer("Введите название  нужной вам профессии: ")
    elif lang == "en":
        await SearchOpts.custom_position.set()
        await message.answer("Enter the custom_position's class:")

# custom_position state
@dp.message_handler(state=SearchOpts.custom_position)
async def process_custom_position(message: types.Message, state: FSMContext):
	lang = users_db.lookup_user(message.from_user.id)[1]
	if lang == "ru":
		async with state.proxy() as data1:
			data1['custom_position'] = message.text
		await SearchOpts.next()
		full_day = types.KeyboardButton("Полный рабочий день")
		free_schedule = types.KeyboardButton("Свободный график")
		changeble_schedule = types.KeyboardButton("Сменный график")
		vahta_schedule = types.KeyboardButton("Вахта")
		partial_schedule = types.KeyboardButton("Частичная занятость")
		from_home_schedule = types.KeyboardButton("Удалённая работа")
		unknown_schedule = types.KeyboardButton("Не имеет значения")
		ikm = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
		ikm.add(full_day, free_schedule, changeble_schedule, vahta_schedule, partial_schedule, from_home_schedule, unknown_schedule)
		await message.answer("Выберите график работы:", reply_markup=ikm)
	elif lang == "en":
		async with state.proxy() as data1:
			data1['custom_position'] = message.text
		await SearchOpts.next()
		full_day = types.KeyboardButton("Full day")
		free_schedule = types.KeyboardButton("Free schedule")
		changeble_schedule = types.KeyboardButton("Changeble schedule")
		vahta_schedule = types.KeyboardButton("Vahta")
		partial_schedule = types.KeyboardButton("Partial schedule")
		from_home_schedule = types.KeyboardButton("Work from home")
		unknown_schedule = types.KeyboardButton("Does not matter")
		ikm = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
		ikm.add(full_day, free_schedule, changeble_schedule, vahta_schedule, partial_schedule, from_home_schedule, unknown_schedule)
		await message.answer("Choose work schedule:", reply_markup=ikm)

# Schedule processing
@dp.message_handler(state=SearchOpts.operating_schedule_id)
async def schedule_process(message: types.Message, state: FSMContext):
	lang = users_db.lookup_user(message.from_user.id)[1]
	if lang == 'ru':
		if message.text == "Полный рабочий день":
			async with state.proxy() as data1:
				data1['operating_schedule_id'] = 1
			await SearchOpts.next()
			await message.answer("Введите минимальную зарплату:")
		elif message.text == "Свободный график":
			async with state.proxy() as data1:
				data1['operating_schedule_id'] = 2
			await SearchOpts.next()
			await message.answer("Введите минимальную зарплату:")
		elif message.text == "Сменный график":
			async with state.proxy() as data1:
				data1['operating_schedule_id'] = 3
			await SearchOpts.next()
			await message.answer("Введите минимальную зарплату:")
		elif message.text == "Вахта":
			async with state.proxy() as data1:
				data1['operating_schedule_id'] = 7
			await SearchOpts.next()
			await message.answer("Введите минимальную зарплату:")
		elif message.text == "Частичная занятость":
			async with state.proxy() as data1:
				data1['operating_schedule_id'] = 5
			await SearchOpts.next()
			await message.answer("Введите минимальную зарплату:")
		elif message.text == "Удалённая работа":
			async with state.proxy() as data1:
				data1['operating_schedule_id'] = 6
			await SearchOpts.next()
			await message.answer("Введите минимальную зарплату:")
		elif message.text == "Не имеет значения":
			async with state.proxy() as data1:
				data1['operating_schedule_id'] = -100
			await SearchOpts.next()
			await message.answer("Введите минимальную зарплату:")
	elif lang == 'en':
		if message.text == "Full day":
			async with state.proxy() as data1:
				data1['operating_schedule_id'] = 1
			await SearchOpts.next()
			await message.answer("Enter min. salary:")
		elif message.text == "Free schedule":
			async with state.proxy() as data1:
				data1['operating_schedule_id'] = 2
			await SearchOpts.next()
			await message.answer("Enter min. salary:")
		elif message.text == "Changeble schedule":
			async with state.proxy() as data1:
				data1['operating_schedule_id'] = 3
			await SearchOpts.next()
			await message.answer("Enter min. salary:")
		elif message.text == "Vahta":
			async with state.proxy() as data1:
				data1['operating_schedule_id'] = 7
			await SearchOpts.next()
			await message.answer("Enter min. salary:")
		elif message.text == "Partial schedule":
			async with state.proxy() as data1:
				data1['operating_schedule_id'] = 5
			await SearchOpts.next()
			await message.answer("Enter min. salary:")
		elif message.text == "Work from home":
			async with state.proxy() as data1:
				data1['operating_schedule_id'] = 6
			await SearchOpts.next()
			await message.answer("Enter min. salary:")
		elif message.text == "Does not matter":
			async with state.proxy() as data1:
				data1['operating_schedule_id'] = -100
			await SearchOpts.next()
			await message.answer("Enter min. salary:")

# Min salary process
@dp.message_handler(state=SearchOpts.salary_from)
async def salary_from_process(message: types.Message, state: FSMContext):
    lang = users_db.lookup_user(message.from_user.id)[1]
    if lang == 'ru':
        async with state.proxy() as data1:
            data1['slary_from'] = message.text
        await SearchOpts.next()
        await message.answer("Введите максимальную зарплату:")
    if lang == 'en':
        async with state.proxy() as data1:
            data1['slary_from'] = message.text
        await SearchOpts.next()
        await message.answer("Enter max. salary")

# Max salary process
@dp.message_handler(state=SearchOpts.salary_to)
async def salary_to_process(message: types.Message, state: FSMContext):
	lang = users_db.lookup_user(message.from_user.id)[1]
	if lang == "ru":
		async with state.proxy() as data1:
			data1['salary_to'] = message.text
		await SearchOpts.next()
		anything_education = types.KeyboardButton("Любое образование")
		higher_education = types.KeyboardButton("Высшее образование")
		not_full_highter_education = types.KeyboardButton("Неполное вышнее образование")
		secondary_education = types.KeyboardButton("Среднее образование")
		secondary_professional_education = types.KeyboardButton("Среднее профессиональное образование")
		higher_bakalavr_education = types.KeyboardButton("Высшее(бакалавр)")
		higher_special_education = types.KeyboardButton("Высшее(специалист)")
		higher_magistr_education = types.KeyboardButton("Высшее(магистр)")
		the_second_highter_education = types.KeyboardButton("Второе высшее")
		refresher_courses = types.KeyboardButton("Курсы переподготовки")
		mva_education = types.KeyboardButton("МВА")
		aspirant_education = types.KeyboardButton("Аспирантура")
		doctor_education = types.KeyboardButton("Доктоторонтура")
		ikm = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
		ikm.add(doctor_education, aspirant_education, mva_education, refresher_courses, the_second_highter_education, higher_magistr_education, higher_special_education, anything_education, higher_education, not_full_highter_education, secondary_education, secondary_professional_education, higher_bakalavr_education)
		await message.answer("Выберите ваше образование:", reply_markup=ikm)
	elif lang == "en":
		async with state.proxy() as data1:
			data1['salary_to'] = message.text
		await SearchOpts.next()
		anything_education = types.KeyboardButton("Anything")
		higher_education = types.KeyboardButton("Highter education")
		not_full_highter_education = types.KeyboardButton("Not full highter education")
		secondary_education = types.KeyboardButton("Secondary education")
		secondary_professional_education = types.KeyboardButton("Secondary professional education")
		higher_bakalavr_education = types.KeyboardButton("Highter(bachelor)")
		higher_special_education = types.KeyboardButton("Highter(expert)")
		higher_magistr_education = types.KeyboardButton("Highter(master)")
		the_second_highter_education = types.KeyboardButton("the second highter")
		refresher_courses = types.KeyboardButton("Refresher courses")
		mva_education = types.KeyboardButton("МВА")
		aspirant_education = types.KeyboardButton("Graduate school")
		doctor_education = types.KeyboardButton("Doctor")
		ikm = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
		ikm.add(doctor_education, aspirant_education, mva_education, refresher_courses, the_second_highter_education, higher_magistr_education, higher_special_education, anything_education, higher_education, not_full_highter_education, secondary_education, secondary_professional_education, higher_bakalavr_education)
		await message.answer("Choose your education:", reply_markup=ikm)


# Education processing
@dp.message_handler(state=SearchOpts.offer_education_id)
async def process_offer_education_id(message: types.Message, state: FSMContext):
	lang = users_db.lookup_user(message.from_user.id)[1]
	if lang == 'ru':
		await SearchOpts.next()
		if message.text == "Любое образование":
			async with state.proxy() as data1:
				data1['offer_education_id'] = 0
			await SearchOpts.next()
			await message.answer("Введите опыт работы: ")
		elif message.text == "Высшее образование":
			async with state.proxy() as data1:
				data1['offer_education_id'] = 4
			await SearchOpts.next()
			await message.answer("Введите опыт работы: ")
		elif message.text == "Неполное вышнее образование":
			async with state.proxy() as data1:
				data1['offer_education_id'] = 3
			await SearchOpts.next()
			await message.answer("Введите опыт работы: ")
		elif message.text == "Среднее образование":
			async with state.proxy() as data1:
				data1['offer_education_id'] = 1
			await SearchOpts.next()
			await message.answer("Введите опыт работы: ")
		elif message.text == "Среднее профессиональное образование":
			async with state.proxy() as data1:
				data1['offer_education_id'] = 2
			await SearchOpts.next()
			await message.answer("Введите опыт работы: ")
		elif message.text == "Высшее(бакалавр)":
			async with state.proxy() as data1:
				data1['offer_education_id'] = 14
			await SearchOpts.next()
			await message.answer("Введите опыт работы: ")
		elif message.text == "Высшее(специалист)":
			async with state.proxy() as data1:
				data1['offer_education_id'] = 8
			await SearchOpts.next()
			await message.answer("Введите опыт работы: ")
		elif message.text == "Высшее(магистр)":
			async with state.proxy() as data1:
				data1['offer_education_id'] = 9
			await SearchOpts.next()
			await message.answer("Введите опыт работы: ")
		elif message.text == "Второе высшее":
			async with state.proxy() as data1:
				data1['offer_education_id'] = 12
			await SearchOpts.next()
			await message.answer("Введите опыт работы: ")
		elif message.text == "Курсы переподготовки":
			async with state.proxy() as data1:
				data1['offer_education_id'] = 11
			await SearchOpts.next()
			await message.answer("Введите опыт работы: ")
		elif message.text == "МВА":
			async with state.proxy() as data1:
				data1['offer_education_id'] = 10
			await SearchOpts.next()
			await message.answer("Введите опыт работы: ")
		elif message.text == "Аспирантура":
			async with state.proxy() as data1:
				data1['offer_education_id'] = 15
			await SearchOpts.next()
			await message.answer("Введите опыт работы: ")
		elif message.text == "Доктоторонтура":
			async with state.proxy() as data1:
				data1['offer_education_id'] = 13
			await SearchOpts.next()
			await message.answer("Введите опыт работы: ")
	elif lang == 'en':
		if message.text == "Anything":
			async with state.proxy() as data1:
				data1['offer_education_id'] = 0
			await SearchOpts.next()
			await message.answer("Enter the work experients:")
		elif message.text == "Highter education":
			async with state.proxy() as data1:
				data1['offer_education_id'] = 4
			await SearchOpts.next()
			await message.answer("Enter the work experients:")
		elif message.text == "Not full highter education":
			async with state.proxy() as data1:
				data1['offer_education_id'] = 3
			await SearchOpts.next()
			await message.answer("Enter the work experients:")
		elif message.text == "Secondary education":
			async with state.proxy() as data1:
				data1['offer_education_id'] = 1
			await SearchOpts.next()
			await message.answer("Enter the work experients:")
		elif message.text == "Secondary professional education":
			async with state.proxy() as data1:
				data1['offer_education_id'] = 2
			await SearchOpts.next()
			await message.answer("Enter the work experients:")
		elif message.text == "Highter(bachelor)":
			async with state.proxy() as data1:
				data1['offer_education_id'] = 14
			await SearchOpts.next()
			await message.answer("Enter the work experients:")
		elif message.text == "Highter(expert)":
			async with state.proxy() as data1:
				data1['offer_education_id'] = 8
			await SearchOpts.next()
			await message.answer("Enter the work experients:")
		elif message.text == "Highter(master)":
			async with state.proxy() as data1:
				data1['offer_education_id'] = 9
			await SearchOpts.next()
			await message.answer("Enter the work experients:")
		elif message.text == "the second highter":
			async with state.proxy() as data1:
				data1['offer_education_id'] = 12
			await SearchOpts.next()
			await message.answer("Enter the work experients:")
		elif message.text == "Refresher courses":
			async with state.proxy() as data1:
				data1['offer_education_id'] = 11
			await SearchOpts.next()
			await message.answer("Enter the work experients:")
		elif message.text == "МВА":
			async with state.proxy() as data1:
				data1['offer_education_id'] = 10
			await SearchOpts.next()
			await message.answer("Enter the work experients:")
		elif message.text == "Graduate school":
			async with state.proxy() as data1:
				data1['offer_education_id'] = 15
			await SearchOpts.next()
			await message.answer("Enter the work experients:")
		elif message.text == "Doctor":
			async with state.proxy() as data1:
				data1['offer_education_id'] = 13
			await SearchOpts.next()
			await message.answer("Enter the work experients:")

# offer_experience_year_count processing
@dp.message_handler(state=SearchOpts.offer_experience_year_count)
async def process_offer_experience_year_count(message: types.Message, state: FSMContext):
	lang = users_db.lookup_user(message.from_user.id)[1]
	async with state.proxy() as data1:
		data1['offer_experience_year_count'] = message.text
		if lang == 'ru':
			await SearchOpts.next()
			await message.answer("Введите минимальный возраст:")
		elif lang == 'en':
			await SearchOpts.next()
			await message.answer("Enter min age:")


# age_from processing
@dp.message_handler(state=SearchOpts.age_from)
async def process_age_from(message: types.Message, state: FSMContext):
	lang = users_db.lookup_user(message.from_user.id)[1]
	async with state.proxy() as data1:
		data1['age_from'] = message.text
		if lang == 'ru':
			await SearchOpts.next()
			await message.answer("Введите максимальный возраст:")
		elif lang == 'en':
			await SearchOpts.next()
			await message.answer("Enter max age:")

# age_to processing
@dp.message_handler(state=SearchOpts.age_to)
async def process_age_to(message: types.Message, state: FSMContext):
	lang = users_db.lookup_user(message.from_user.id)[1]
	async with state.proxy() as data1:
		data1['age_to'] = message.text
	if lang == 'ru':
		await SearchOpts.next()
		true_resident = types.KeyboardButton("Да, являюсь")
		false_resident = types.KeyboardButton("Нет, не являюсь")
		ikm = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
		ikm.add(true_resident, false_resident)
		await message.answer("Являетесь ли вы иностранным гражданином:", reply_markup = ikm)
	elif lang == 'en':
		await SearchOpts.next()
		true_resident = types.KeyboardButton("Yes")
		false_resident = types.KeyboardButton("No")
		ikm = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
		ikm.add(true_resident, false_resident)
		await message.answer("Are you a resident:", reply_markup = ikm)


# is_nonresident processing
@dp.message_handler(state=SearchOpts.is_nonresident)
async def process_is_nonresident(message: types.Message, state: FSMContext):
	if message.text == "Да, являюсь":
			async with state.proxy() as data1:
				data1['is_nonresident'] = True
			await SearchOpts.next()
			true_male = types.KeyboardButton("Да, являюсь")
			false_male = types.KeyboardButton("Нет, не являюсь")
			ikm = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
			ikm.add(true_male, false_male)
			await message.answer("Являетесь ли вы мужчиной:", reply_markup = ikm)
	elif message.text == "Yes":
			async with state.proxy() as data1:
				data1['is_nonresident'] = True
			await SearchOpts.next()
			true_male = types.KeyboardButton("Yes")
			false_male = types.KeyboardButton("No")
			ikm = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
			ikm.add(true_male, false_male)
			await message.answer("Are you a male:", reply_markup = ikm)
	elif message.text == "Нет, не являюсь":
			async with state.proxy() as data1:
				data1['is_nonresident'] = False
			await SearchOpts.next()
			true_male = types.KeyboardButton("Да, являюсь")
			false_male = types.KeyboardButton("Нет, не являюсь")
			ikm = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
			ikm.add(true_male, false_male)
			await message.answer("Являетесь ли вы мужчиной:", reply_markup = ikm)
	elif message.text == "No":
			async with state.proxy() as data1:
				data1['is_nonresident'] = False
			await SearchOpts.next()
			true_male = types.KeyboardButton("Yes")
			false_male = types.KeyboardButton("No")
			ikm = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
			ikm.add(true_male, false_male)
			await message.answer("Are you a male:", reply_markup = ikm)

# is_male state and finish state
@dp.message_handler(state=SearchOpts.is_male)
async def process_is_male(message: types.Message, state: FSMContext):
	lang = users_db.lookup_user(message.from_user.id)[1]
	if message.text == "Да, являюсь":
			async with state.proxy() as data1:
				data1['is_male'] = True
				# Making request here
				message.answer(f'Здесь должны быть данные из нейросети :)')
			await state.finish()
	elif message.text == "Yes":
			async with state.proxy() as data1:
				data1['is_male'] = True
				# Making request here
				message.answer(f'Здесь должны быть данные из нейросети :)')
			await state.finish()
	elif message.text == "Нет, не являюсь":
			async with state.proxy() as data1:
				data1['is_male'] = False
				# Making request here
				message.answer(f'Здесь должны быть данные из нейросети :)')
			await state.finish()
	elif message.text == "No":
			async with state.proxy() as data1:
				data1['is_male'] = False
				# Making request here
				message.answer(f'Здесь должны быть данные из нейросети :)')
			await state.finish()


if __name__ == '__main__':
	aiogram.executor.start_polling(dp, skip_updates=True)
