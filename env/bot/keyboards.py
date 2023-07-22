from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.callback_data import CallbackData

todos_kb = CallbackData('todo', 'id', 'action')

def get_start_ikb():
    ikb = InlineKeyboardMarkup(inline_keyboard = [
        [InlineKeyboardButton("All todo lists", callback_data = 'get_all')],
        [InlineKeyboardButton("Create new", callback_data = 'add')],
    ], resize_keyboard = True)
    return ikb
    
def get_cancel_ikb():
    ikb = ReplyKeyboardMarkup(keyboard = [
        [KeyboardButton("/cancel")],
    ], resize_keyboard = True, one_time_keyboard=True)
    return ikb

def get_delete_kb(todo_id : int):
     return InlineKeyboardMarkup(inline_keyboard = [
        [InlineKeyboardButton("Delete todo", callback_data = todos_kb.new(todo_id, 'delete'))],
        [InlineKeyboardButton("Done", callback_data = todos_kb.new(todo_id, 'done'))],
    ], resize_keyboard = True)

