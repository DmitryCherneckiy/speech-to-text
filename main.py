import telebot
import traceback
import speech_recognition as sr
import subprocess
import os
import logging
from telebot import types

BOT_TOKEN = None

def read_bot_token():
    try:
        from config import BOT_TOKEN
    except:
        pass

    if len(BOT_TOKEN) == 0:
        BOT_TOKEN = os.environ.get('BOT_TOKEN')

    if BOT_TOKEN is None:
        raise ('Token for the bot must be provided (BOT_TOKEN variable)')
    return BOT_TOKEN

BOT_TOKEN = read_bot_token()

r = sr.Recognizer()
bot = telebot.TeleBot(BOT_TOKEN)

LOG_FOLDER = '.logs'
if not os.path.exists(LOG_FOLDER):
    os.makedirs(LOG_FOLDER)

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename = f'{LOG_FOLDER}/app.log'
)

logger = logging.getLogger('telegram-bot')
logging.getLogger('urllib3.connectionpool').setLevel('INFO')

@bot.message_handler(commands=['start'])
def start_message(message):
    bot.send_message(message.chat.id, 'Welcome! This bot can recognize your *voice* in a voice message and translate '
                                      'it into *text*.' + '\n' + 'Two languages supported - Russian and English' +
                     '\n' + 'Send a voice message to start the conversion.', parse_mode='Markdown')


@bot.message_handler(content_types=['voice'])
def voice_handler(message):
    file_id = message.voice.file_id  # file size check. If the file is too big, FFmpeg may not be able to handle it.
    file = bot.get_file(file_id)

    file_size = file.file_size
    if int(file_size) >= 715000:
        bot.send_message(message.chat.id, 'Upload file size is too large.')
    else:
        download_file = bot.download_file(file.file_path)  # download file for processing
        with open('audio.ogg', 'wb') as file:
            file.write(download_file)

        language_buttons(message)  # buttons for selecting the language of the voice message

@bot.callback_query_handler(func=lambda call: True)
def buttons(call):
    if call.data == 'russian':
        text = voice_recognizer('ru_RU')  # call the function with selected language
        bot.send_message(call.from_user.id, text)  # send the heard text to the user
        _clear()
    elif call.data == 'english':
        text = voice_recognizer('en_EN')
        bot.send_message(call.from_user.id, text)
        _clear()

def voice_recognizer(language):
    subprocess.run(['ffmpeg', '-i', 'audio.ogg', 'audio.wav', '-y'])  # formatting ogg file in to wav format
    text = 'Words not recognized.'
    file = sr.AudioFile('audio.wav')
    with file as source:
        try:
            audio = r.record(source)  # listen to file
            text = r.recognize_google(audio, language=language)  # and write the heard text to a text variable
        except:
            logger.error(f"Exception:\n {traceback.format_exc()}")

    return text

def language_buttons(message):
    keyboard = types.InlineKeyboardMarkup()
    button_ru = types.InlineKeyboardButton(text='Russian', callback_data='russian')
    button_eng = types.InlineKeyboardButton(text='English', callback_data='english')
    keyboard.add(button_ru, button_eng)
    bot.send_message(message.chat.id, 'Please select a voice message language.', reply_markup=keyboard)

def _clear():
    """Remove unnecessary files"""
    _files = ['audio.wav', 'audio.ogg']
    for _file in _files:
        if os.path.exists(_file):
            os.remove

if __name__ == '__main__':
    logger.info('start bot')
    bot.polling(True)
    logger.info('stop bot')
