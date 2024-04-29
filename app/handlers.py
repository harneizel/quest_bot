from aiogram import Router, F, Bot, Dispatcher
import config
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from geopy.distance import geodesic
import app.keyboards as kb
import app.database as db
import const_and_texts as ct

bot = Bot(token=config.TOKEN)
dp = Dispatcher()
router = Router()

class b:
    k = 0 # количество геоточек для записи
    l = 0  # счётчик
    cords = [] # при создании маршрута с геоточками
    preview = None # для записи превью
    type = None # тип при удалении


class Form(StatesGroup):        # машина состояний
    caption_rout = State()      # описание оффлайн маршрута
    number_points = State()     # количество геоточек
    lat = State()
    prev = State()              # превью оффлайн маршрута
    prev_onl = State()          # превью онлайн маршрута
    chosen_route_off = State()
    chosen_route_onl = State()
    number_route = State()


async def dont_understand(mess): # функция ответа на непонятные сообщения
    await mess.reply(ct.TEXT1)

async def delete_messages(id):
    bm_id = await db.show_bm_id(id)
    await bot.delete_message(chat_id=id, message_id=bm_id)
    await bot.delete_message(chat_id=id, message_id=bm_id-1)
    await bot.delete_message(chat_id=id, message_id=bm_id-2)

# приветствие
@router.message(F.text == '/start')
async def cmd_start(message: Message):
    await db.cmd_start_db(message.from_user.id)
    if message.from_user.id == config.ADMIN_ID:
        await message.answer(ct.TEXT2, reply_markup=kb.main_admin)
    else:
        await message.answer(ct.TEXT3, reply_markup=kb.main)

# поиск и маршруты
@router.message(F.text == ct.BUTTON2)
async def search(message: Message):
    await message.answer('Маршрут какого типа вы хотите пройти?', reply_markup=kb.menu)

# оффлайн маршруты
@router.callback_query(F.data == 'rout_offline')
async def chosen_offline(callback: CallbackQuery, state: FSMContext):
    a = await db.show_offline()
    await callback.message.answer(f'Доступные маршруты:\n{a}\nПришлите номер того, который выберете', reply_markup=kb.locate)
    await state.set_state(Form.chosen_route_off)
    await db.set_type_ofl(callback.from_user.id)

# онлайн маршруты
@router.callback_query(F.data == 'rout_online')
async def chosen_online(callback: CallbackQuery, state: FSMContext):
    a = await db.show_online()
    await callback.message.answer(f'Доступные маршруты:\n{a}\nПришлите номер того, который выберете', reply_markup=kb.locate)
    await state.set_state(Form.chosen_route_onl)
    await db.set_type_onl(int(callback.from_user.id))

# обработка оффлайн маршрута
@router.message(Form.chosen_route_off)
async def chosen_route_off(message: Message, state: FSMContext):
    number = int(message.text)
    await db.set_number(number, message.from_user.id)
    await state.clear()
    caption = await db.get_caption_off(message.from_user.id)
    await message.answer(f"Описание маршрута: {str(caption)}")

#начало маршрута
@router.message(Form.chosen_route_onl)
async def chosen_route_onl(message: Message, state: FSMContext):
    number = int(message.text)
    await db.set_number(number, message.from_user.id)
    await state.clear()
    photo = FSInputFile('instruction.jpg')/home/sapsan
    await message.answer_photo(photo, caption='Теперь, чтобы начать выбранный маршрут, пришлите трансляцию геопозиции')


# создание онлайн маршрута с геоточками
@router.message(Form.lat)
async def cords_point(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    b.cords.append(message.location.latitude)
    b.cords.append(message.location.longitude)
    b.l += 1
    if b.l >= b.k:
        for i in range((10 - b.k)*2): # 10 - максимальное число точек, цикл заполняет пустые точки нулями
            b.cords.append(0)
        await db.add_online_rout(b.cords)
        await state.clear()
        b.cords = []
        await message.answer('Маршрут создан и записан в базу данных')
    else:
        await message.answer(f'Хорошо, теперь геоточку номер {b.l+1}')

# обработка трансялции
@router.message(F.location)
async def location_o(message: Message):
    flag = await db.show_flag(message.from_user.id)
    if flag == 0:
        a = await db.get_cords(message.from_user.id)
        await message.answer('Вы должны прийти в точку №1:')
        await bot.send_location(chat_id=message.from_user.id, latitude=a[0], longitude=a[1])
        cords = (message.location.latitude, message.location.longitude)
        dist = int(geodesic((a[0], a[1]), cords).meters)
        msg = await message.answer(f"Оставшееся расстояние до точки в метрах: {dist}", reply_markup=kb.check_loc)
        await db.set_bm_id(message.from_user.id, msg.message_id)
    else:
        await message.reply('Вы уже отправили локацию, чтобы начать заново нажмите "Сбросить прогресс"')

# проверить моё местоположение
@router.callback_query(F.data == 'send_location')
async def check_locate(callback: CallbackQuery):
    await db.flag1(callback.from_user.id)

# изменение сообщения с расстоянием до точки и обработка нахождения точки
@router.edited_message(F.location)
async def edited_message_handler(edited_message: Message):
    flag1 = await db.flag1_view(edited_message.from_user.id)
    if flag1 == 1:
        await db.flag1_set0(edited_message.from_user.id)
        a = await db.get_cords(edited_message.from_user.id)
        cords = (edited_message.location.latitude, edited_message.location.longitude)
        dist = int(geodesic((a[0], a[1]), cords).meters)
        if dist>ct.RADIUS:                         #если юзер не дошёл до точки
            bm_id = await db.show_bm_id(edited_message.from_user.id)
            await edited_message.bot.edit_message_text(text=f"Оставшееся расстояние до точки в метрах: {dist}",
                                                        chat_id=edited_message.from_user.id,
                                                        reply_markup=kb.check_loc, message_id=bm_id)
        elif dist<=ct.RADIUS and a[2]==a[3]:       # если юзер закончил маршрут
            await delete_messages(edited_message.from_user.id)
            await edited_message.answer('🎉 Поздравляем, вы прошли маршрут!')
            await db.delete_prog(edited_message.from_user.id)
        else:                               #если юзер собрал точку
            await delete_messages(edited_message.from_user.id)
            point = await db.plus_get_point(edited_message.from_user.id)
            await edited_message.answer(f"Вы достигли точки №{point+1}, следующая точка №{point+2}")
            a = await db.get_cords(edited_message.from_user.id)
            await bot.send_location(chat_id=edited_message.from_user.id, latitude=a[0], longitude=a[1])
            dist = int(geodesic((a[0], a[1]), cords).meters)
            msg = await edited_message.answer(f"Оставшееся расстояние до точки в метрах: {dist}", reply_markup=kb.check_loc)
            await db.set_bm_id(edited_message.from_user.id, msg.message_id)

# сбросить прогресс
@router.message(F.text== ct.BUTTON7)
async def reset_progress(message: Message):
    await message.answer("Уверены что хотите сбросить выбор маршрута и весь прогресс по нему?", reply_markup=kb.progress)

#сбрасывание прогресса
@router.callback_query(F.data == 'yes')
async def reset_prog_yes(callback: CallbackQuery):
    await db.delete_prog(callback.from_user.id)
    await callback.message.answer('Сбросил в исходное состояние')

@router.callback_query(F.data == 'no')
async def reset_prog_no(callback: CallbackQuery):
    await callback.message.answer("Не сбрасываю прогресс")


# возвращение в меню
@router.message(F.text == '🔙 Вернуться в меню')
async def back_menu(message: Message):
    if message.from_user.id == config.ADMIN_ID:
        await message.answer(text='Возвращаюсь в меню', reply_markup=kb.main_admin)
    else:
        await message.answer(text='Возвращаюсь в меню', reply_markup=kb.main)

# профиль юзера
@router.message(F.text == '👤 Профиль')
async def cmd_my_id(message: Message):
    await message.answer(f'Ваш ID: {message.from_user.id}\nВаше имя: {message.from_user.first_name}')

# обработка кнопки информация
@router.message(F.text == '🌲 Информация')
async def contacts(message: Message):
    await message.answer_photo(photo='https://proza.ru/pics/2015/06/21/1155.jpg',
                               caption = 'С помощью этого бота вы можете искать физические и виртуальные клады. Присутствует два режима: с описанием и со сбором геоточек.\n\nВ первом вам выдаётся описание маршрута. Во втором вы должны прийти в геоточку, отправленную ботом, и нажать на кнопку "проверить мою геопозицию". Если вы находитесь в правильном месте, вам выдастся следующая геоточка.')

# оплата
@router.message(F.text == '💵 Оплата')
async def cmd_payments(message: Message):
    await message.answer('Пока что бот работает бесплатно, пользуйтесь :)')

                            ########################
                            # админ взаимодействия #
                            ########################
# панелька
@router.message(F.text == '💻 Админ панель')
async def panel(message: Message):
    if message.from_user.id == config.ADMIN_ID:
        await message.answer('Что вы хотите сделать?', reply_markup=kb.panel)
    else:
        await dont_understand(message)

# админ выбор типа маршрута
@router.message(F.text == 'Создать маршрут')
async def create_route(message: Message):
    if message.from_user.id == config.ADMIN_ID:
        await message.answer('Маршрут какого типа вы хотите создать?', reply_markup=kb.choose_type)
    else:
        await dont_understand(message)

@router.message(F.text == "Удалить маршрут")
async def delete_route(message: Message):
    if message.from_user.id == config.ADMIN_ID:
        await message.answer("Маршрут какого типа хотите удалить?", reply_markup=kb.delete_route)

#удаление маршрута
@router.callback_query(F.data=="offline")
async def get_type_offline(callback: CallbackQuery, state: FSMContext):
    b.type = 'offline'
    await callback.message.answer('Введите номер маршрута который хотите удалить')
    await state.set_state(Form.number_route)

# удаление маршрута
@router.callback_query(F.data == "online")
async def get_type_online(callback: CallbackQuery, state: FSMContext):
    b.type = 'online'
    await callback.message.answer('Введите номер маршрута который хотите удалить')
    await state.set_state(Form.number_route)

@router.message(Form.number_route)
async def get_number_delete_route(message: Message, state:FSMContext):
    if b.type == "online":
        id = int(message.text)
        await db.delete_route_onl(id)
    elif b.type == "offline":
        id = int(message.text)
        await db.delete_route_ofl(id)
    await message.answer("Маршрут успешно удалён")
    await state.clear()

# начало создания оффлайн маршрута
@router.callback_query(F.data == 'caption')
async def offline_route(callback: CallbackQuery, state: FSMContext):
    await state.set_state(Form.prev)
    await callback.message.answer('Отлично, введите превью маршрута')

# превью оффлайн маршрута
@router.message(Form.prev)
async def preview_offline(message: Message, state: FSMContext):
    b.preview = message.text
    await state.update_data(name=message.text)
    await state.set_state(Form.caption_rout)
    await message.answer('Теперь введите описание маршрута')


# записывание в бд оффлайн маршрута
@router.message(Form.caption_rout)
async def add_offline(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await db.add_offline_rout(b.preview, message.text)
    await message.answer("Маршрут записан в базу данных")
    await state.clear()

# начало создания онлайн маршрута
@router.callback_query(F.data == 'live')
async def online_route(callback: CallbackQuery, state: FSMContext):
    await state.set_state(Form.prev_onl)
    await callback.message.answer('Приступаем к созданию, введите превью маршрута')

# превью онлайн маршрута
@router.message(Form.prev_onl)
async def preview_online(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(Form.number_points)
    b.cords.append(message.text)
    await message.answer('Введите количество геоточек')

# улавливание количества геоточек
@router.message(Form.number_points)
async def process_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    b.k = int(message.text)
    if b.k<=10:
        b.l = 0
        b.cords.append(int(message.text))
        await message.answer('Теперь пришлите первую геоточку')
        await state.set_state(Form.lat)
    else:
        await state.clear()

# непонятные сообщения
@router.message()
async def echo(message: Message):
    await dont_understand(message)