#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
This Bot uses the Updater class to handle the bot.
First, a few handler functions are defined. Then, those functions are passed to
the Dispatcher and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.
Usage:
Basic Echobot example, repeats messages.
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.
"""

from telegram import KeyboardButton, ReplyKeyboardMarkup
from telegram import ReplyKeyboardRemove, File
from telegram.ext import Updater, CommandHandler
from telegram.ext import MessageHandler, Filters, Dispatcher
from telegram.ext import CallbackQueryHandler, RegexHandler
import logging

import Strings
from os import listdir, remove
from random import randint
from algorithm import *

# Enable logging
logging.basicConfig(format="""%(asctime)s - %(name)s -
                        %(levelname)s - %(message)s""",
                    level=logging.INFO)

logger = logging.getLogger(__name__)


class SteganyBot:
    def __init__(self, Token):
        self.__token = Token
        self.updater = Updater(self.__token)
        self.dispatcher = self.updater.dispatcher
        self.flagEncrypt = False
        self.flagDecrypt = False

    def Start(self, bot, update):
        logger.info("Method start")
        update.message.reply_text(text=Strings.greeting)

        keyboard = [[KeyboardButton("EncryptMessage", callback_data='1')],
                    [KeyboardButton("DecryptMessage", callback_data='2')],
                    [KeyboardButton("Option 3", callback_data='3')]
                    ]
        reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
        update.message.reply_text('Please choose:', reply_markup=reply_markup)
        return logger.info("Done start")

    def Choose(self, bot, update):
        logger.info("Method \'Choose\'")

        if "encrypt" in update.message.text.lower():
            self.flagEncrypt = True
            self.AskText(bot, update)
            logger.info("choose to encrypt")
        elif "decrypt" in update.message.text.lower():
            self.flagDecrypt = True
            self.AskPicture(bot, update)
            logger.info("choose to decrypt")

    def EncryptMessage(self, bot, update, letter):
        logger.info("\'EncryptMessage\'")

        if not self.flagEncrypt:
            update.message.reply_text(update.message.text)
            logger.info("message was sent")
            return "Not yet"
        obj = Container()
        rang = len(listdir("photos/encrypt/"))
        photo_id = str(randint(1, rang))

        obj.SetModule("photos/encrypt/photo" + photo_id + ".png")
        obj.SetUser(update.message.chat.username)

        logger.info(obj.Encrypt(letter))
        filepath = obj.Save()
        print("filepath => ", filepath)
        update.message.reply_text("Successful! Get the picture")
        update.message.reply_document(open(filepath, "rb"))
        self.flagEncrypt = False
        return logger.info("success encryption")

    def DecryptMessage(self, bot, update, number):
        logger.info("DecryptMessage")

        obj = Container()
        path = "photos/fromUser/photo"+str(number)+".png"
        print(path)
        obj.SetModule(path)
        text = obj.Decrypt()
        answer = "extracted message => " + text
        update.message.reply_text(answer)
        self.flagDecrypt = False
        return logger.info("decryption method success")

    def Help(self, bot, update):
        logger.info("Help")
        update.message.reply_text(Strings.helpString)

    def AnswerLog(self, bot, update):
        logger.info("Log method")

        ID = update.message.chat.id
        Answer = "Me writing from chat: " + str(ID)
        Answer += "\nUser => " + str(update.message.chat.username)
        Answer += "\nFull Name => " + str(update.message.chat.first_name)
        Answer += " " + str(update.message.chat.last_name)
        bot.send_message(text=Answer, chat_id=243247509)
        return logger.info("log was sent")

    def GetText(self, bot, update):
        logger.info("GetText")
        self.EncryptMessage(bot, update, letter=update.message.text)
        self.AnswerLog(bot, update)
        return logger.info("GetText done")

    def GetDoc(self, bot, update):
        logger.info("\'getPhoto\'")
        user = update.message.chat.username
        photo_file = bot.get_file(update.message.document.file_id)

        num = len(listdir("photos/fromUser/")) + 1
        path = "photos/fromUser/photo" + str(num) + ".png"
        photo_file.download(path)
        if (len(listdir("photos/fromUser/")) > 5):
            for i in listdir("photos/fromUser/"):
                remove("photos/fromUser/" + i)
        print(self.DecryptMessage(bot, update, number=num))
        return logger.info("GetDoc success")

    def GetPhoto(self, bot, update):
        logger.info("\'getPhoto\'")
        user = update.message.chat.username
        photo_file = bot.get_file(update.message.photo[-1].file_id)
        num = len(listdir("photos/fromUser/")) + 1
        path = "photos/fromUser/photo" + str(num) + ".png"
        photo_file.download(path)
        if (len(listdir("photos/fromUser/")) > 5):
            for i in listdir("photos/fromUser/"):
                remove("photos/fromUser/" + i)
        print(self.DecryptMessage(bot, update, number=num))

    def Error(self, bot, update, error):
        logger.warn('Update "%s" caused error "%s"' % (update, error))

    def AskText(self, bot, update):
        update.message.reply_text("Send me a message you want to encrypt")

    def AskPicture(self, bot, update):
        update.message.reply_text("Please, upload the picture to decrypt")

    def AddHandler(self):
        self.dispatcher.add_handler(CommandHandler(
            "start", self.Start)
        )

        self.dispatcher.add_handler(RegexHandler(
            '^((E|e)ncrypt)|((D|d)ecrypt)', self.Choose)
        )

        self.dispatcher.add_handler(CommandHandler(
            "help", self.Help)
        )

        self.dispatcher.add_handler(MessageHandler(
            Filters.text, self.GetText)
        )

        self.dispatcher.add_handler(MessageHandler(
            Filters.document, self.GetDoc)
        )

        self.dispatcher.add_handler(MessageHandler(
            Filters.photo, self.GetPhoto)
        )

        self.dispatcher.add_handler(CommandHandler(
            "Log", self.AnswerLog)
        )

        self.dispatcher.add_error_handler(self.Error)

    def StartBot(self):
        self.AddHandler()
        self.updater.start_polling()
        self.updater.idle()


if __name__ == '__main__':
    token = "TOKEN"
    bot = SteganyBot(token)
    bot.StartBot()

