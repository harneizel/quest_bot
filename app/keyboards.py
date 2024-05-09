from aiogram.types import (ReplyKeyboardMarkup, KeyboardButton,
                           InlineKeyboardMarkup, InlineKeyboardButton)
import app.const_and_texts as ct
#главное меню
main_kb = [
    [KeyboardButton(text=ct.BUTTON1),
     KeyboardButton(text=ct.BUTTON2)],
    [KeyboardButton(text=ct.BUTTON3),
     KeyboardButton(text=ct.BUTTON4)]
]
main = ReplyKeyboardMarkup(keyboard=main_kb,
                           resize_keyboard=True,
                           input_field_placeholder='Выберите пункт ниже')

#главное меню админ
main_admin_kb = [
    [KeyboardButton(text=ct.BUTTON1),
     KeyboardButton(text=ct.BUTTON2)],
    [KeyboardButton(text=ct.BUTTON3),
     KeyboardButton(text=ct.BUTTON4)],
    [KeyboardButton(text=ct.BUTTON5)]
]
main_admin = ReplyKeyboardMarkup(keyboard=main_admin_kb,
                           resize_keyboard=True,
                           input_field_placeholder='Выберите пункт ниже')

#админ панель
admin_panel = [
    [KeyboardButton(text=ct.BUTTON8),
     KeyboardButton(text=ct.BUTTON9)],
    [KeyboardButton(text=ct.BUTTON10),
     KeyboardButton(text=ct.BUTTON6)]
]
panel = ReplyKeyboardMarkup(keyboard=admin_panel,
                           resize_keyboard=True,
                           input_field_placeholder='Выберите пункт ниже')

#админ выбор типа маршрута
choose_type = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text=ct.CB_BUTTON1, callback_data='caption')],
    [InlineKeyboardButton(text=ct.CB_BUTTON2, callback_data='live')],

])

#при прохождении маршрута
locate_kb = [
    [KeyboardButton(text=ct.BUTTON6)],
    [KeyboardButton(text=ct.BUTTON7)]
]

locate = ReplyKeyboardMarkup(keyboard=locate_kb,
                           resize_keyboard=True,
                           input_field_placeholder='Выберите пункт ниже')



#inline выбор типа маршрута
menu = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text=ct.CB_BUTTON1, callback_data='rout_offline')],
    [InlineKeyboardButton(text=ct.CB_BUTTON2, callback_data='rout_online')],

])

#inline проверка локации
check_loc = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text=ct.CB_BUTTON5, callback_data='send_location')],
])

progress = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text=ct.CB_BUTTON3, callback_data='yes'),
    InlineKeyboardButton(text=ct.CB_BUTTON4, callback_data='no')],
])

delete_route = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text=ct.CB_BUTTON1, callback_data='offline'),
    InlineKeyboardButton(text=ct.CB_BUTTON2, callback_data='online')],
])

