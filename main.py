# -*- coding: utf-8 -*-
import logging, nest_asyncio, datetime, asyncio, traceback, ast, random, words
import work_with_bd as ww_bd
from config import TOKEN, STARTMSG
from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from threading import Thread
from deep_translator import GoogleTranslator
from googletrans import Translator
from google_trans_new import google_translator

nest_asyncio.apply()

bot = Bot(token=TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())
translator = GoogleTranslator()
data_text_words = {'en': words.en, 'ru': words.ru}

logging.basicConfig(level=logging.INFO)


async def alarm_algo():
    try:
        bot = Bot(token=TOKEN)
        while True:
            Time_now = datetime.datetime.now()
            if (Time_now.hour == 10 and Time_now.minute == 00) or (Time_now.hour == 15 and Time_now.minute == 00) or (
                    Time_now.hour == 20 and Time_now.minute == 00):
                users_data = ww_bd.SELECTS('user_data', where_status=True, where_column='notifications_time',
                                           where_data=str(Time_now.hour) + ":00", list_words=1, notifications_status=1,
                                           id=1)
                for user_data in users_data:
                    if list(user_data)[1] == 1:
                        random_index, list_words_user = random.randint(0, len(
                            data_text_words['en']) - 1), ast.literal_eval(list(user_data)[0])
                        while random_index == list_words_user:
                            random_index = random.randint(0, len(data_text_words['en']) - 1)
                        list_words_user.append(random_index)
                        ww_bd.UPDATE('user_data', where_status=True, where_column='id', where_data=list(user_data)[2],
                                     list_words=str(list_words_user))
                        await bot.send_message(list(user_data)[2], text="Материал для изучения⏰:\n\n%s - %s" % (
                            data_text_words['en'][random_index], data_text_words['ru'][random_index]))
                        await asyncio.sleep(2)
                await asyncio.sleep(180)
            else:
                await asyncio.sleep(20)

    except Exception:
        print(traceback.format_exc())


def alarm_start():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    loop.run_until_complete(alarm_algo())
    loop.close()


Thread(target=alarm_start, daemon=True).start()

try:
    @dp.message_handler(commands="start")
    async def start(message: types.Message):
        await registration_user(message, (message.from_user.id,))
        await message.answer_sticker("CAACAgIAAxkBAAEEP1ViOyyYFQmUy2PxxTtv27vXAz-GiQACYBYAApktAAFJOBKCKGA3rbgjBA")

    async def registration_user(message, user_id):
        id_data = list(ww_bd.SELECT("id", "user_data"))
        """if user_id not in id_data:"""
        ww_bd.INSERT("user_data", id=list(user_id)[0], list_words=[], notifications_status=1, notifications_time='10:00')
        await message.answer(STARTMSG,
                                 reply_markup=types.ReplyKeyboardMarkup(one_time_keyboard=False, resize_keyboard=True,
                                                                        row_width=2).add(*["Играть🕹", "Уведомления⏰"]))
        """else:
            await message.answer("Здравствуйте, выберите команду:",
                                 reply_markup=types.ReplyKeyboardMarkup(one_time_keyboard=False, resize_keyboard=True,
                                                                        row_width=2).add(*["Играть🕹", "Уведомления⏰"]))"""


    @dp.message_handler(lambda message: message.text == "Уведомления⏰")
    async def notifications(message: types.Message):
        await notifications_message(message.from_user.id, message.message_id, message=message)


    async def notifications_message(user_id, id_message, message=None, call=None):
        noti_status, noti_time = list(list(
            ww_bd.SELECTS("user_data", where_status=True, where_column='id', where_data=user_id, notifications_status=1,
                          notifications_time=1))[0])
        keyboard = types.InlineKeyboardMarkup(row_width=3).add(
            *[types.InlineKeyboardButton("10:00", callback_data="changeNotiTime_10:00_" + str(id_message)),
              types.InlineKeyboardButton("15:00", callback_data="changeNotiTime_15:00_" + str(id_message)),
              types.InlineKeyboardButton("20:00", callback_data="changeNotiTime_20:00_" + str(id_message))])
        keyboard.add(
            *[types.InlineKeyboardButton("Вкл. уведомления✅", callback_data="changeNotiStatus_1_" + str(id_message)),
              types.InlineKeyboardButton("Выкл. уведомления❌", callback_data="changeNotiStatus_0_" + str(id_message))])
        if message != None:
            await message.answer(
                "---Уведомления⏰---\n\nСтатус уведомления: %(status)s\nВремя отправки уведомлений: %(time)s" % {
                    'status': {1: "Вкл.✅", 0: "Выкл.❌"}[noti_status], 'time': noti_time},
                reply_markup=keyboard.add(
                    types.InlineKeyboardButton("Закрыть окно", callback_data="delete_" + str(id_message))))
        else:
            try:
                await call.message.edit_text(
                    "---Уведомления⏰---\n\nСтатус уведомления: %(status)s\nВремя отправки уведомлений: %(time)s" % {
                        'status': {1: "Вкл.✅", 0: "Выкл.❌"}[noti_status], 'time': noti_time},
                    reply_markup=keyboard.add(
                        types.InlineKeyboardButton("Закрыть окно", callback_data="delete_" + str(id_message))))
            except:
                None


    @dp.callback_query_handler(Text(startswith="changeNotiTime_"))
    async def change_notifications_time(call: types.CallbackQuery):
        ww_bd.UPDATE("user_data", where_status=True, where_column='id', where_data=call.from_user.id,
                     notifications_time=call.data.split("_")[1])
        await notifications_message(call.from_user.id, call.data.split("_")[2], call=call)


    @dp.callback_query_handler(Text(startswith="changeNotiStatus_"))
    async def change_notifications_status(call: types.CallbackQuery):
        ww_bd.UPDATE("user_data", where_status=True, where_column='id', where_data=call.from_user.id,
                     notifications_status=call.data.split("_")[1])
        await notifications_message(call.from_user.id, call.data.split("_")[2], call=call)


    @dp.callback_query_handler(Text(startswith="delete_"), state='*')
    async def delete_message(call: types.CallbackQuery, state: FSMContext):
        try:
            await state.finish()
        except:
            None
        try:
            await call.message.delete()
            await bot.delete_message(chat_id=call.from_user.id, message_id=int(call.data.split("_")[1]))
        except:
            None


    @dp.message_handler(lambda message: message.text == "Играть🕹")
    async def play(message: types.Message):
        buttons = buttons_play(message.message_id)
        await message.answer_sticker("CAACAgIAAxkBAAEElG5iamweEp4d2cGpsYkfu7X_Btkx2gACuhoAAhBJIUmyiDlP9ryorSQE")
        await message.answer("Выберите количество слов для игры:",
                             reply_markup=types.InlineKeyboardMarkup(row_width=2).add(*buttons))


    @dp.callback_query_handler(Text(startswith="pLen_"), state='*')
    async def play_len(call: types.CallbackQuery, state: FSMContext):
        list_words_data, dict_buttons = ast.literal_eval(list(list(list(
            ww_bd.SELECT("list_words", "user_data", where_status=True, where_column="id",
                         where_data=call.from_user.id)))[0])[0]), {}
        if len(list_words_data) < int(call.data.split("_")[1]) and len(call.data.split("_")) != 4:
            buttons = buttons_play(call.data.split("_")[2])
            buttons.insert(4, types.InlineKeyboardButton("Рандомная игра",
                                                         callback_data="pLen_" + call.data.split("_")[1] + "_" +
                                                                       call.data.split("_")[2] + "_rand"))
            try:
                await call.message.edit_text("Вы изучили меньше, чем выбрали\nКоличество изученного: " + str(
                    len(list_words_data)) + "\n\nВыберите число поменьше или играйте с рандомными фразами:",
                                             reply_markup=types.InlineKeyboardMarkup(row_width=2).add(*buttons))
            except:
                None
        else:
            count_for_dict, words_for_play = 0, []
            if len(call.data.split("_")) == 4:
                for count in range(0, int(call.data.split("_")[1])):
                    random_index = random.randint(0, len(data_text_words['en']) - 1)
                    while random_index in words_for_play:
                        random_index = random.randint(0, len(data_text_words['en']) - 1)
                    words_for_play.append(random_index)
                list_words_data = words_for_play
            else:
                list_words_data = list_words_data[0:int(call.data.split("_")[1])]
                random.shuffle(list_words_data)
            for key_word in list_words_data:
                words_for_play, count_for_dict = [data_text_words['en'][key_word]], count_for_dict + 1
                for count in range(0, 5):
                    random_index = random.randint(0, len(data_text_words['en']) - 1)
                    while random_index == key_word:
                        random_index = random.randint(0, len(data_text_words['en']) - 1)
                    words_for_play.append(data_text_words['en'][random_index])
                dict_buttons[str(count_for_dict)] = {data_text_words['ru'][key_word]: words_for_play,
                                                     'answer_status': 0, 'answer': None,
                                                     'answer_true': words_for_play[0]}
            await state.update_data(dict_buttons_state=dict_buttons)
            await keyboard_play(1, call.data.split("_")[2], state, call)


    async def keyboard_play(id_question, id_message, state, call):
        form_data_values = await state.get_data()
        keyboard, buttons_answer, text_answer, dict_buttons = types.InlineKeyboardMarkup(
            row_width=3), [], "Вы не ответили", form_data_values['dict_buttons_state']
        if dict_buttons[str(id_question)]['answer'] is not None: text_answer = dict_buttons[str(id_question)]['answer']
        for word in dict_buttons[str(id_question)][list(dict_buttons[str(id_question)].keys())[0]]:
            buttons_answer.append(types.InlineKeyboardButton(str(word),
                                                             callback_data="pAnswer_" + str(word) + "_" + str(
                                                                 id_question) + "_" + str(id_message)))
        random.shuffle(buttons_answer)
        keyboard.add(*buttons_answer)
        keyboard.add(*[types.InlineKeyboardButton("⬅️",
                                                  callback_data="pChangeQuestion_0_" + str(id_question) + "_" + str(
                                                      id_message)),
                       types.InlineKeyboardButton(str(id_question) + "/" + str(list(dict_buttons.keys())[-1]),
                                                  callback_data="pChangeQuestion_2_" + str(id_question) + "_" + str(
                                                      id_message)), types.InlineKeyboardButton("➡️",
                                                                                               callback_data="pChangeQuestion_1_" + str(
                                                                                                   id_question) + "_" + str(
                                                                                                   id_message))])
        keyboard.add(types.InlineKeyboardButton("Завершить попытку", callback_data="pFinish_" + str(id_message)))
        keyboard.add(types.InlineKeyboardButton("Закрыть окно", callback_data="delete_" + str(id_message)))
        await call.message.edit_text(
            "Какой перевод - %s\n\nОтвет: %s" % (list(dict_buttons[str(id_question)].keys())[0], text_answer),
            reply_markup=keyboard)


    def check_word(word, list_words_data, data_text_words):
        if word not in list_words_data:
            return data_text_words['en'][word]
        else:
            check_word(random.randint(0, len(data_text_words['en']) - 1), list_words_data, data_text_words)


    def buttons_play(id_message):
        return [types.InlineKeyboardButton("5", callback_data="pLen_5_" + str(id_message)),
                types.InlineKeyboardButton("10", callback_data="pLen_10_" + str(id_message)),
                types.InlineKeyboardButton("15", callback_data="pLen_15_" + str(id_message)),
                types.InlineKeyboardButton("20", callback_data="pLen_20_" + str(id_message)),
                types.InlineKeyboardButton("Закрыть окно", callback_data="delete_" + str(id_message))]


    @dp.callback_query_handler(Text(startswith="pAnswer_"), state='*')
    async def play_answer(call: types.CallbackQuery, state: FSMContext):
        form_data_values = await state.get_data()
        form_data_values['dict_buttons_state'][call.data.split("_")[2]]['answer'] = call.data.split("_")[1]
        form_data_values['dict_buttons_state'][call.data.split("_")[2]]['answer_status'] = 1
        await state.update_data(dict_buttons_state=form_data_values['dict_buttons_state'])
        if int(call.data.split("_")[2]) + 1 <= int(list(form_data_values['dict_buttons_state'].keys())[-1]):
            await keyboard_play(int(call.data.split("_")[2]) + 1, call.data.split("_")[3], state, call)
        else:
            await keyboard_play(int(call.data.split("_")[2]), call.data.split("_")[3], state, call)


    @dp.callback_query_handler(Text(startswith="pChangeQuestion_"), state='*')
    async def play_change_question(call: types.CallbackQuery, state: FSMContext):
        form_data_values, keyboard, buttons = await state.get_data(), types.InlineKeyboardMarkup(row_width=5), []
        if (call.data.split("_")[1] == '0' and int(call.data.split("_")[2]) - 1 >= 1) or (
                call.data.split("_")[1] == '1' and int(call.data.split("_")[2]) + 1 <= int(
            list(form_data_values['dict_buttons_state'].keys())[-1])):
            await keyboard_play(int(call.data.split("_")[2]) + {'1': 1, '0': -1}[call.data.split("_")[1]],
                                call.data.split("_")[3], state, call)
        elif call.data.split("_")[1] == '2':
            for number_question in range(1, int(list(form_data_values['dict_buttons_state'].keys())[-1]) + 1):
                buttons.append(types.InlineKeyboardButton({1: "📝", 0: "✏"}[form_data_values['dict_buttons_state'][
                    str(number_question)]['answer_status']] + " " + str(number_question),
                                                          callback_data="pChangeQuestionNumber_" + str(
                                                              number_question) + "_" + call.data.split("_")[3]))
            keyboard.add(*buttons)
            keyboard.add(types.InlineKeyboardButton("Назад", callback_data="pBack_" + call.data.split("_")[2] + "_" +
                                                                           call.data.split("_")[3]))
            await call.message.edit_text("Выберите № вопроса:", reply_markup=keyboard)


    @dp.callback_query_handler(Text(startswith="pChangeQuestionNumber_"), state='*')
    async def play_change_question_number(call: types.CallbackQuery, state: FSMContext):
        await keyboard_play(int(call.data.split("_")[1]), call.data.split("_")[2], state, call)


    @dp.callback_query_handler(Text(startswith="pBack_"), state='*')
    async def play_back(call: types.CallbackQuery, state: FSMContext):
        await keyboard_play(int(call.data.split("_")[1]), call.data.split("_")[2], state, call)


    @dp.callback_query_handler(Text(startswith="pFinish_"), state='*')
    async def play_finish(call: types.CallbackQuery, state: FSMContext):
        form_data_values, text = await state.get_data(), "Результаты:"
        for question in form_data_values['dict_buttons_state']:
            if form_data_values['dict_buttons_state'][question]['answer_true'] == \
                    form_data_values['dict_buttons_state'][question]['answer']:
                text += "\n✅ "
            else:
                text += "\n❌ "
            text += "%(question)s = %(answer_true)s Ответ: %(answer)s" % {
                'question': list(form_data_values['dict_buttons_state'][question].keys())[0],
                'answer_true': form_data_values['dict_buttons_state'][question]['answer_true'],
                'answer': form_data_values['dict_buttons_state'][question]['answer']}
        await call.message.edit_text(text)
        await state.finish()


    class form_data(StatesGroup):
        text_for_translate = State()
        dict_buttons_state = State()


    @dp.message_handler(content_types=['text'], state='*')
    async def text_for_translate(message: types.Message, state: FSMContext):
        if message.text not in ["Играть🕹", "Уведомления⏰"]:
            await state.update_data(text_for_translate=message.text)
            await message.answer_sticker("CAACAgIAAxkBAAEEP1liOzBgmZTT1GPWW0Qx8lRSasPKeQACehkAArJEIEncS7Ny7JI95CME")
            await message.answer("Выберите язык на который хотите перевести:",
                                 reply_markup=types.InlineKeyboardMarkup(row_width=2).add(
                                     *[types.InlineKeyboardButton("Английский", callback_data="translate_ru"),
                                       types.InlineKeyboardButton("Русский", callback_data="translate_en")]))


    @dp.callback_query_handler(Text(startswith="translate_"), state='*')
    async def translate(call: types.CallbackQuery, state: FSMContext):
        form_data_values = await state.get_data()
        await call.message.edit_text("%(translate_message)s" % {
            'translate_message': translator.translate(form_data_values['text_for_translate'],
                                                      lang_src=call.data.split("_")[1],
                                                      lang_tgt={'en': 'ru', 'ru': 'en'}[call.data.split("_")[1]])})
        await state.update_data(text_for_translate="")

except Exception:
    # print(error)
    pass

if __name__ == "__main__":
    dp.register_message_handler(start, commands="start")
    executor.start_polling(dp, skip_updates=True)
