from asyncore import dispatcher
from cgitb import text
import sqlite3
from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.dispatcher import FSMContext
import sqlite_db
from keyboards import *
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram_calendar import simple_cal_callback, SimpleCalendar
from aiogram.types import Message, CallbackQuery


bot = Bot('') #TYPE YOUR TOKEN
storage = MemoryStorage()
dp = Dispatcher(bot, storage = storage)


class TodoStatesGroup(StatesGroup):
    planned_date = State()
    desc = State()


async def on_startup(_):
    await sqlite_db.db_connect()
    bot_commands = [
            types.BotCommand("start", "Start"),
            types.BotCommand("add", "Add new Todo"),
            types.BotCommand("list", "List all todos"),
    ]


    await bot.set_my_commands(bot_commands)


@dp.message_handler(commands=['start']) 
async def start(message : types.Message):
    await message.answer('Welcome to todo bot!',
                         reply_markup = get_start_ikb())
    
@dp.message_handler(commands=['list']) 
async def list(message : types.Message):
    todos = await sqlite_db.get_all_todos()

    if not todos:
        return await message.answer('Your todolist is empty')
    for i,todo in enumerate(todos):
        is_done = "YES" if todo[4] == 1 else "NO"
        await message.answer('\n'.join([str(i+1) + '.Todo description: ' + todo[1], ' Planned date:' + todo[2], ' Done: ' + is_done]),
                                      reply_markup=get_delete_kb(todo[0]))
        
@dp.message_handler(commands=['add']) 
async def add_new(message : types.Message):
    await message.answer("Please select a date: ", reply_markup=await SimpleCalendar().start_calendar())
    await TodoStatesGroup.planned_date.set()

    
@dp.message_handler(commands=['cancel'], state = '*') 
async def cancel(message : types.Message, state = FSMContext):
    if state is not None:
        await state.finish()
        await message.answer('You cancelled action',
                             reply_markup = get_start_ikb())
    

@dp.callback_query_handler(text='get_all')
async def get_all(callback : types.CallbackQuery):
    todos = await sqlite_db.get_all_todos()

    if not todos:
        await callback.message.answer('Your todolist is empty')
        return await callback.answer()
    for i,todo in enumerate(todos):
        is_done = "YES" if todo[4] == 1 else "NO"
        await callback.message.answer('\n'.join([str(i+1) + '.Todo description: ' + todo[1], ' Planned date:' + todo[2], ' Done: ' + is_done]),
                                      reply_markup=get_delete_kb(todo[0]))
        
        
@dp.callback_query_handler(todos_kb.filter(action='delete'))
async def delete(callback : types.CallbackQuery, callback_data : dict):
    await sqlite_db.delete_todo(callback_data['id'])

    await callback.message.reply('Todo has been removed')
    await callback.answer()


@dp.callback_query_handler(todos_kb.filter(action='done'))
async def delete(callback : types.CallbackQuery, callback_data : dict):
    await sqlite_db.update_todo(callback_data['id'])

    await callback.message.reply('Todo is done')
    await callback.answer()

    
@dp.callback_query_handler(text='add')
async def add(callback : types.CallbackQuery):
    await callback.message.answer("Please enter date: ", reply_markup=await SimpleCalendar().start_calendar(),)
    await TodoStatesGroup.planned_date.set()

@dp.callback_query_handler(simple_cal_callback.filter())
async def process_simple_calendar(callback_query: CallbackQuery, callback_data: dict, state: FSMContext):
    selected, date = await SimpleCalendar().process_selection(callback_query, callback_data)
    if selected:
        date=date.strftime("%d.%m.%Y")
        async with state.proxy() as data:
            data['planned_date'] = date
        await callback_query.message.answer(
            '\n'.join(['You selected ' + date,  ' Now please enter description: ']),
        )
        await TodoStatesGroup.desc.set()
       
@dp.message_handler(state = TodoStatesGroup.desc)
async def handle_desc(message : types.Message, state : FSMContext):
    async with state.proxy() as data:
        data['desc'] = message.text
    await sqlite_db.create_todo(state)
    await message.reply("Thank you! Your todo list has been created!",
                        reply_markup = get_start_ikb())
    await state.finish()


dp.register_callback_query_handler(process_simple_calendar,
                              simple_cal_callback.filter(),
                              state=TodoStatesGroup.planned_date)

if __name__ == '__main__':
    executor.start_polling(dispatcher = dp,
                           skip_updates = True,
                           on_startup = on_startup)