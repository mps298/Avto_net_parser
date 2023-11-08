import asyncio
from datetime import date
from aiogram import types, Dispatcher, Bot
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import StatesGroup, State
from os import path

from get_functions import get_data, get_keyboard, get_all_brands, get_all_models



class CarStatesGroup(StatesGroup):
    brand = State()
    model = State()
    price_min = State()
    price_max = State()
    year_min = State()
    year_max = State()
    fuel = State()
    km_min = State()
    km_max = State()
    location = State()
    transmission = State()


TOKEN = 'Your bot token'

storage = MemoryStorage()
bot = Bot(token=TOKEN)
dp = Dispatcher(bot, storage=storage)

all_brands = {}
all_models = []

result_string = ""


@dp.message_handler(commands='start')
async def start(message: types.Message) -> None:
    please_wait_message = await bot.send_message(message.chat.id, "Receiving data, please wait...")
    global result_string
    result_string = ""
    global all_brands
    all_brands = get_all_brands()
    keyboard = get_keyboard(all_brands.keys())
    await please_wait_message.delete()
    await message.answer('Choose a brand', reply_markup=keyboard)
    await CarStatesGroup.brand.set()


@dp.message_handler(content_types=['text'], state=CarStatesGroup.brand)
async def set_brand(message: types.Message, state: FSMContext):
    please_wait_message = await bot.send_message(message.chat.id, "Receiving data, please wait...")
    global all_models

    all_models = get_all_models(all_brands.get(message.text))

    keyboard = get_keyboard(all_models)

    async with state.proxy() as data:
        brand = "".join(c for c in message.text if c.isalpha() or c == ' ' or c == '-')
        brand = brand.strip()
        data['brand'] = brand
        global result_string
        result_string += f"Brand: {brand}\n"

    await please_wait_message.delete()
    await message.answer(f'Choose a model of {brand}', reply_markup=keyboard)
    await CarStatesGroup.model.set()


@dp.message_handler(content_types=['text'], state=CarStatesGroup.model)
async def set_model(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        model = "".join(c for c in message.text if c.isalpha() or c == ' ' or c == '-')
        data['model'] = model
        global result_string
        result_string += f"Model: {model}\n"

    years = []
    for i in range(9):
        years.append(str(date.today().year - i))
        years.append('Older')
    keyboard = get_keyboard(years)
    await message.answer("Year, from: ", reply_markup=keyboard)
    await CarStatesGroup.year_min.set()


@dp.message_handler(content_types=['text'], state=CarStatesGroup.year_min)
async def set_year_min(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        if message.text == "Older":
            data['year_min'] = '0'
        else:
            data['year_min'] = message.text
        global result_string
        result_string += f"Year, min: {data['year_min']}\n"
        year_min = int(data['year_min'])
    years = []
    for i in range(9):
        years.append(str(date.today().year - i))
        if date.today().year - i == year_min:
            break
        keyboard = get_keyboard(years)
    await message.answer("Year, to: ", reply_markup=keyboard)
    await CarStatesGroup.year_max.set()


@dp.message_handler(content_types=['text'], state=CarStatesGroup.year_max)
async def set_year_max(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['year_max'] = message.text
        global result_string
        result_string += f"Year, max: {data['year_max']}\n"

    fuel = ['Petrol',
            'Diesel',
            'Any'
            ]

    keyboard = get_keyboard(fuel)
    await message.answer("Fuel:", reply_markup=keyboard)
    await CarStatesGroup.fuel.set()


@dp.message_handler(content_types=['text'], state=CarStatesGroup.fuel)
async def set_fuel(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        if message.text == 'Petrol':
            data['fuel'] = '201'
        elif message.text == 'Diesel':
            data['fuel'] = '202'
        elif message.text == 'Any':
            data['fuel'] = '0'
        global result_string
        result_string += f"Fuel: {message.text}\n"

    kilometers = ['0',
                  '5000',
                  '25000',
                  '50000',
                  '100000',
                  '150000',
                  '200000',
                  '250000']
    keyboard = get_keyboard(kilometers)
    await message.answer("Kilometers, from: ", reply_markup=keyboard)
    await CarStatesGroup.km_min.set()


@dp.message_handler(content_types=['text'], state=CarStatesGroup.km_min)
async def set_km_min(message: types.Message, state: FSMContext):
    kilometers = []
    async with state.proxy() as data:
        data['km_min'] = message.text
        global result_string
        result_string += f"Km, min: {message.text}\n"

    # Starting km_max from value bigger than km_min
    start_appending = False
    for km in ('0',
               '5000',
               '25000',
               '50000',
               '100000',
               '150000',
               '200000',
               '250000'):
        if km == message.text:
            start_appending = True
            continue
        if start_appending:
            kilometers.append(km)
    kilometers.append("No limit")

    keyboard = get_keyboard(kilometers)
    await message.answer("Kilometers, to: ", reply_markup=keyboard)
    await CarStatesGroup.km_max.set()


@dp.message_handler(content_types=['text'], state=CarStatesGroup.km_max)
async def set_km_max(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        if message.text == 'No limit':
            data['km_max'] = '999999'
        else:
            data['km_max'] = message.text
        global result_string
        result_string += f"Km, max: {message.text}\n"

    locations = [
        'All Locations',
        '1000 - LJ',
        '2000 - MB',
        '3000 - CE',
        '4000 - KR',
        '5000 - GO',
        '6000 - KP',
        '8000 - NM',
        '9000 - MS'
    ]
    keyboard = get_keyboard(locations)
    await message.answer("Location: ", reply_markup=keyboard)
    await CarStatesGroup.location.set()


@dp.message_handler(content_types=['text'], state=CarStatesGroup.location)
async def set_location(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        if message.text == 'All Locations':
            data['location'] = '0'
        elif message.text == '1000 - LJ':
            data['location'] = '1'
        elif message.text == '2000 - MB':
            data['location'] = '2'
        elif message.text == '3000 - CE':
            data['location'] = '3'
        elif message.text == '4000 - KR':
            data['location'] = '4'
        elif message.text == '5000 - GO':
            data['location'] = '5'
        elif message.text == '6000 - KP':
            data['location'] = '6'
        elif message.text == '8000 - NM':
            data['location'] = '8'
        elif message.text == '9000 - MS':
            data['location'] = '9'

        global result_string
        result_string += f"Location: {message.text}\n"

    transmissions = [
        'Any',
        'Automatic',
        'Manual'
    ]
    keyboard = get_keyboard(transmissions)
    await message.answer("Transmission: ", reply_markup=keyboard)
    await CarStatesGroup.transmission.set()


@dp.message_handler(content_types=['text'], state=CarStatesGroup.transmission)
async def set_transmission(message: types.Message, state: FSMContext):
    async with state.proxy() as data:

        # transmission codes in the website link addresses : 0 - any, 1 - Automatic, 2 - Manual

        if message.text == 'Any':
            data['transmission'] = '0'
        elif message.text == 'Automatic':
            data['transmission'] = '1'
        elif message.text == 'Manual':
            data['transmission'] = '2'
        global result_string
        result_string += f"Transmission: {message.text}\n"
    # setting price_min
    prices = [
        '0',
        '1000',
        '2500',
        '5000',
        '10000',
        '15000',
        '20000',
        '30000',
        '40000',
        '50000'
    ]
    keyboard = get_keyboard(prices)
    await message.answer("Price, min: ", reply_markup=keyboard)
    await CarStatesGroup.price_min.set()


@dp.message_handler(content_types=['text'], state=CarStatesGroup.price_min)
async def set_price_min(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['price_min'] = message.text
        global result_string
        result_string += f"Price, min: {message.text}\n"

    # Starting price_max from value bigger than km_min
    prices = []
    start_appending = False
    for price in ('0',
                  '1000',
                  '2500',
                  '5000',
                  '10000',
                  '15000',
                  '20000',
                  '30000',
                  '40000',
                  '50000'):
        if price == message.text:
            start_appending = True
            continue
        if start_appending:
            prices.append(price)
    prices.append("No limit")

    keyboard = get_keyboard(prices)
    await message.answer("Price, max: ", reply_markup=keyboard)
    await CarStatesGroup.price_max.set()


@dp.message_handler(content_types=['text'], state=CarStatesGroup.price_max)
async def set_price_max(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        if message.text == "No limit":
            data['price_max'] = '999999'
        else:
            data['price_max'] = message.text
        global result_string
        result_string += f"Price, max: {message.text}\n"

        result_message = await message.answer(f"You're searching:\n{result_string}\nSearching in "
                                              f"progress\nParsing data will take some time, please wait...",
                                              reply_markup=types.ReplyKeyboardRemove())

        results = get_data(brand=data['brand'],
                           model=data['model'],
                           price_min=data['price_min'],
                           price_max=data['price_max'],
                           year_min=data['year_min'],
                           year_max=data['year_max'],
                           fuel=data['fuel'],
                           km_min=data['km_min'],
                           km_max=data['km_max'],
                           location=data['location'],
                           transmission=data['transmission'])

        await result_message.delete()

        if type(results) == str:
            await message.answer(message.chat.id, results)
        else:
            if results:
                counter = 0
                await message.answer(f"Please, see {min(10, len(results))} newest ads:")
                for result in results:
                    image = result[0]
                    name = result[1]
                    url = result[2]
                    price = result[3]
                    await bot.send_photo(message.chat.id, image,
                                         caption="<b>" + name + "</b>\n" + price + f"\n<a href='{url}'>See details</a>",
                                         parse_mode="html")
                    counter += 1
                    if counter == 10:
                        break

                await message.answer(
                    "Your request has been saves. Next time enter /update to repeat the same searching")

                #  saving search details and the newest result's link
                data_to_save = [data['brand'], data['model'], data['price_min'], data['price_max'], data['year_min'],
                                data['year_max'], data['fuel'], data['km_min'], data['km_max'], data['location'],
                                data['transmission'], results[0][2]
                                ]
                print('data_to save_type = ', type(data_to_save))
                with open(f"request_{message.chat.id}.txt", 'w') as file:
                    for item in data_to_save:
                        file.write(item + ' ')

            else:
                await bot.send_message(message.chat.id, "No ads have been found, please, enter /start for a new search")
    await state.reset_state()


@dp.message_handler(commands='update')
async def update(message: types.Message) -> None:
    if not path.exists(f"request_{message.chat.id}.txt"):
        await bot.send_message(message.chat.id, "You have no data to update, please, enter /start for new search...")
    else:
        result_message = await bot.send_message(message.chat.id, "Receiving data, please wait...")
        with open(f"request_{message.chat.id}.txt", 'r') as file:
            list_from_file = file.read().split()
            print(list_from_file)

            brand = list_from_file[0].strip()
            model = list_from_file[1].strip()
            price_min = list_from_file[2].strip()
            price_max = list_from_file[3].strip()
            year_min = list_from_file[4].strip()
            year_max = list_from_file[5].strip()
            fuel = list_from_file[6].strip()
            km_min = list_from_file[7].strip()
            km_max = list_from_file[8].strip()
            location = list_from_file[9].strip()
            transmission = list_from_file[10].strip()
            previous_newest_url = list_from_file[11].strip()

        results = get_data(brand, model, price_min, price_max, year_min, year_max,
                           fuel, km_min, km_max, location, transmission)
        await result_message.delete()
        counter = 0
        for result in results:
            if result[2] == previous_newest_url:  # if the urls match
                break
            else:
                counter += 1
        if counter:
            await bot.send_message(message.chat.id, f"{counter} new ads have been found:")
            for i in range(counter):
                image = results[i][0]
                name = results[i][1]
                url = results[i][2]
                price = results[i][3]
                await bot.send_photo(message.chat.id, image,
                                     caption="<b>" + name + "</b>\n" + price + f"\n<a href='{url}'>See details</a>",
                                     parse_mode="html")
            data_to_save = [brand, model, price_min, price_max, year_min, year_max, fuel, km_min, km_max, location,
                            transmission, results[0][2]]
            with open(f"request_{message.chat.id}.txt", 'w') as file:
                for item in data_to_save:
                    file.write(item + ' ')
        else:
            await bot.send_message(message.chat.id, "No new ads have been found")


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
