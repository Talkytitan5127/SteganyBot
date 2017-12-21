# -*- coding: utf-8 -*-
"""
Этот модуль описывает telegram-бота "SteganyBot"
"""

from telegram import KeyboardButton, ReplyKeyboardMarkup
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram import ReplyKeyboardRemove, File
from telegram.ext import Updater, CommandHandler
from telegram.ext import MessageHandler, Filters, Dispatcher
from telegram.ext import CallbackQueryHandler, RegexHandler
from time import sleep
import logging
import Strings
from os import listdir, remove, environ
from random import randint
from algorithm import *
from datawork import *

# Enable logging
logging.basicConfig(format="""%(asctime)s - %(name)s
                     - %(levelname)s - %(message)s""",
                    level=logging.INFO)

logger = logging.getLogger(__name__)

#: флаги пользователей
global UsersFlags


def InitDict():
    """
    Добавление флагов в UsersFlags для пользователей,
    чьи данные есть в базе данных
    """
    temp = {
        "flagEncrypt": False,
        "flagDecrypt": False,
        "getAskUser": False,
        "flagUpload": False,
        "OnlyDepart": False,
        "pathtofile": None,
        "pathUserpic": None,
        "length": 2048
        }
    postredb = DataBase()
    postredb.cur.execute("SELECT * from users;")
    result = postredb.cur.fetchall()
    for i in result:
        UsersFlags[i[-1]] = temp.copy()


def ChangeFlags(num_id, *args):
    """
    Изменение состояния флага

    Args:
        num_id (int): номер чата
        *args: Наименования флагов
    """
    for i in args:
        UsersFlags[num_id][i] = not UsersFlags[num_id][i]


def SetArgs(num_id, path, *args):
    """
    Инициализация флагов данными

    Args:
        num_id (int): номер чата
        path (str): путь до файла
        *args: Наименования флагов
    """
    UsersFlags[num_id][path] = args[0]


class SteganyBot:
    """
    Класс реализует telegram-бота "@StegyJpgBot"

    Attributes:
        __token (:obj:`str`): токен бота
        updater (:class:`telegram.ext.Updater`): объект представляет
            входящие обновления
        dispatcher (:class:`telegram.ext.Dispatcher`): объект представляет
            обработчик обновлений
    """
    # initialisation bot
    def __init__(self, Token):
        self.__token = Token
        self.updater = Updater(self.__token)
        self.dispatcher = self.updater.dispatcher

    # /start
    def Start(self, bot, update):
        """
        Метод бота "/start"

         Args:
            bot (:class:`telegram.Bot`): хэндлер бота
            update(:class:`telegram.ext.Updater`): обновления
        """
        logger.info("method start")
        num_id = update.message.chat.id
        update.message.reply_text(text=Strings.startGreet)
        #: загрузка данных о пользователя в базу данных
        userData = self.ParseUpdate(update.message)
        postgredb = DataBase()
        info = postgredb.AddUser(userData)
        logger.info(info)
        if Strings.AnswerStatus[info] == 365:
            update.message.reply_text(Strings.addUsername)
        self.Refresh()
        #: inline клавиатура
        keyboard = [[KeyboardButton("/info ℹ")],
                    [KeyboardButton("/play 🎮")],
                    [KeyboardButton("/help ❓")]
                    ]
        reply_markup = ReplyKeyboardMarkup(
            keyboard,
            one_time_keyboard=True,
            resize_keyboard=True)
        update.message.reply_text('Please choose:', reply_markup=reply_markup)
        return logger.info("Done start")

    def Refresh(self):
        """
        Обновление списка с флагами
        """
        db = DataBase()
        db.cur.execute("SELECT * FROM users;")
        for i in db.cur.fetchall():
            if i[-1] not in UsersFlags:
                UsersFlags[i[-1]] = temp.copy()

    def Restore(self):
        """
        Обнуление флагов для encrypt, decrypt, upload, depart
        """
        for k in UsersFlags:
            UsersFlags[k]['flagEncrypt'] = False
            UsersFlags[k]['flagDecrypt'] = False
            UsersFlags[k]['flagUpload'] = False
            UsersFlags[k]['OnlyDepart'] = False

    # /info
    def Info(self, bot, update):
        """
        Метод бота "/info"

        Args:
            bot (:class:`telegram.Bot`): хэндлер бота
            update(:class:`telegram.ext.Updater`): обновления

        """
        logger.info("Info method")
        update.message.reply_text(text=Strings.info)

    # /play
    def Play(self, bot, update):
        """
        Метод бота "/play"
        Args:
            bot (:class:`telegram.Bot`): хэндлер бота
            update(:class:`telegram.ext.Updater`): обновления

        """
        logger.info("Method play")
        update.message.reply_text(text=Strings.greeting2)
        keyboard = [[KeyboardButton("/encrypt ✉➡🗻"),
                     KeyboardButton("/decrypt 🗻➡✉")],
                    [KeyboardButton("/upload picture"),
                     KeyboardButton("/depart")]]
        reply_markup = ReplyKeyboardMarkup(
            keyboard,
            one_time_keyboard=True,
            resize_keyboard=True
            )
        update.message.reply_text('Please choose:', reply_markup=reply_markup)
        return logger.info("game begins")

    # parsing string
    def ParseUpdate(self, text):
        """
        Разделение строки на отдельные части

        Args:
            text (:obj:`str`): строка обновлений от пользователя

        Returns:
            :obj:`list`: данные о пользователе (username, имя,
                фамилия, номер чата)

        """
        username = text.chat.username
        first = text.chat.first_name
        last = text.chat.last_name
        chat_id = text.chat.id
        return [username, first, last, chat_id]

    #: Обработка /encrypt
    def Encrypt(self, bot, update):
        """
        Метод обработки команды бота /encrypt

        Args:
            bot (:class:`telegram.Bot`): хэндлер бота
            update(:class:`telegram.ext.Updater`): обновления
        """
        num_id = self.GetId(bot, update)
        self.Restore()
        if UsersFlags[num_id]['pathUserpic'] is not None:
                self.GetLength(bot, update)
        ChangeFlags(num_id, 'flagEncrypt')
        self.AskText(bot, update)
        logger.info("choose to encrypt")

    #: обработка /decrypt
    def Decrypt(self, bot, update):
        """
        Метод обработки команды бота /decrypt

        Args:
            bot (:class:`telegram.Bot`): хэндлер бота
            update(:class:`telegram.ext.Updater`): обновления
        """
        num_id = self.GetId(bot, update)
        self.Restore()
        ChangeFlags(num_id, 'flagDecrypt')
        self.AskPicture(bot, update)
        logger.info("choose to decrypt")

    #: обработка /upload
    def Upload(self, bot, update):
        """
        Метод обработки команды бота /upload

        Args:
            bot (:class:`telegram.Bot`): хэндлер бота
            update(:class:`telegram.ext.Updater`): обновления
        """
        num_id = self.GetId(bot, update)
        self.Restore()
        ChangeFlags(num_id, 'flagUpload')
        self.AskPicture(bot, update)

    def Echo(self, bot, update):
        """
        Ответ пользователю им же сообщением

        Args:
            bot (:class:`telegram.Bot`): хэндлер бота
            update(:class:`telegram.ext.Updater`): обновления

        """
        update.message.reply_text(update.message.text)
        logger.info("message was sent")
        return "text replied"

    def SendPicture(self, bot, update, user=None):
        """
        Отправление png-файла:
            + Пользователю, который зашифровал сообщение
            + Пользователю, которую хотят отправить сообщение

        Args:
            bot (:class:`telegram.Bot`): хэндлер бота
            update(:class:`telegram.ext.Updater`): обновления
            user (:obj:`str`, optional): username пользователя-адресата

        """
        chatId = update.message.chat.id
        if UsersFlags[chatId]['pathtofile'] is None:
            update.message.reply_text("No picture to send you")
            return
        if user is None:
            update.message.reply_text("Get the picture")
            update.message.reply_document(
                open(UsersFlags[chatId]['pathtofile'], "rb"))
            update.message.reply_text("Downloaded successful")
        else:
            # get user's id
            postgredb = DataBase()
            num_id = int(postgredb.GetId(user))
            answer = Strings.messageUser.format(update.message.chat.username)
            bot.send_message(text=answer, chat_id=num_id)
            bot.send_document(
                document=open(UsersFlags[chatId]['pathtofile'], "rb"),
                chat_id=num_id)
            update.message.reply_text("Sending was successful")
        SetArgs(chatId, 'pathtofile', None)

    def SendPicToUser(self, bot, update):
        """
        Отправление png-файла пользователю

        Args:
            bot (:class:`telegram.Bot`): хэндлер бота
            update(:class:`telegram.ext.Updater`): обновления

        """
        self.SendPicture(bot, update)

    def AskChooseUser(self, bot, update):
        """
        Попросить пользователя:
            + Загрузить картинку
            + Написать username адресата

        Args:
            bot (:class:`telegram.Bot`): хэндлер бота
            update(:class:`telegram.ext.Updater`): обновления
        """
        num_id = self.GetId(bot, update)
        if UsersFlags[num_id]['pathtofile'] is None:
            self.AskPicture(bot, update)
            ChangeFlags(num_id, "OnlyDepart")

        else:
            bot.send_message(text=Strings.askUser, chat_id=num_id)
            ChangeFlags(num_id, 'getAskUser')

    # user use bot or not
    def CheckUser(self, bot, update, user):
        """
        Оправить пользователь png-файл

        Args:
            bot (:class:`telegram.Bot`): хэндлер бота
            update(:class:`telegram.ext.Updater`): обновления
            user (:obj:`str`): username пользователя

        Note:
            Если пользователя с переданным в базе данных нет, то
            сообщить об этом пользователю и прислать ему png-файл.
        """
        postgredb = DataBase()
        user = user.split()
        user = user[0][1:]
        fl = postgredb.AskUserName(user)
        num_id = update.message.chat.id
        ChangeFlags(num_id, 'getAskUser')
        if fl:
            self.SendPicture(bot, update, user=user)
        else:
            update.message.reply_text("your input username: {}".format(user))
            update.message.reply_text(Strings.addFriendUser)
            self.SendPicture(bot, update)

    def MakePath(self, folder):
        """
        Создание строки-пути

        Args:
            folder (:obj:`str`): папка назначения

        Returns:
            :obj:`str`: Путь до папки назначения
        """
        path = "photos/"
        path += folder + '/'
        return path

    def EncryptMessage(self, bot, update, letter):
        """
        Шифрование сообщение, полученное от пользователя, в png-файл

        Args:
            bot (:class:`telegram.Bot`): хэндлер бота
            update(:class:`telegram.ext.Updater`): обновления
            letter (:obj:`str`): полученное сообщение

        """
        logger.info("\'EncryptMessage\'")
        obj = Container()
        num_id = update.message.chat.id
        #: зашифрование в png-файл по умолчанию
        if UsersFlags[num_id]['pathUserpic'] is None:
            path = self.MakePath("encrypt")
            rang = len(listdir(path))
            photo_id = str(randint(1, rang))
            obj.SetModule(path + "photo" + photo_id + ".png")
            self.ClearDir("photos/decrypt/")
        #: зашифрование в пользовательскую картинку
        else:
            obj.SetModule(UsersFlags[num_id]['pathUserpic'])
        obj.SetUser(update.message.chat.username)
        status = obj.Encrypt(letter)
        if status == 127:
            update.message.reply_text("Something wrong with message's length")
        filepath = obj.Save()
        #: запрос об отправке другому пользователю
        SetArgs(num_id, 'pathtofile', filepath)
        update.message.reply_text("Successful! Picture is ready")
        logger.info("Encryption success")
        ChangeFlags(num_id, 'flagEncrypt')
        SetArgs(num_id, 'pathUserpic', None)
        UsersFlags[num_id]["length"] = 2048
        update.message.reply_text(Strings.afterEncrypt)

    def DecryptMessage(self, bot, update, number):
        """
        Расшифровка сообщения из png-файла

        Args:
            bot (:class:`telegram.Bot`): хэндлер бота
            update(:class:`telegram.ext.Updater`): обновления
            number (:obj:`int`): будущий номер файла в папке

        """
        logger.info("DecryptMessage")
        num_id = self.GetId(bot, update)
        #: обработка случая, когда пользователь отправил картинку
        #:    без первоначального использования "/decrypt"
        if not UsersFlags[num_id]['flagDecrypt']:
            update.message.reply_text(Strings.getPic)
            return "Not yet"
        else:
            obj = Container()
            if UsersFlags[num_id]["pathUserpic"] is None:
                path = self.MakePath("fromUser")
                path += "photo" + str(number) + ".png"
                obj.SetModule(path)
            else:
                obj.SetModule(UsersFlags[num_id]["pathUserpic"])
            text = obj.Decrypt()
            answer = "extracted message => " + text
            bot.send_message(text=answer, chat_id=num_id)
            ChangeFlags(num_id, 'flagDecrypt')
            SetArgs(num_id, 'pathUserpic', None)
            logger.info("decryption success")

    def Help(self, bot, update):
        """
        Метод бота "/help"

        Args:
            bot (:class:`telegram.Bot`): хэндлер бота
            update(:class:`telegram.ext.Updater`): обновления

        """
        logger.info("Help")
        update.message.reply_text(Strings.helpString)

    def GetId(self, bot, update):
        """
        Получение идентификатора чата

        Args:
            bot (:class:`telegram.Bot`): хэндлер бота
            update(:class:`telegram.ext.Updater`): обновления
        Returns:
            :obj:`int`: идентификатор чата с пользователем
        """
        num_id = 0
        try:
            num_id = update.message.chat.id
        except Exception:
            num_id = update.callback_query.message.chat.id
        return num_id

    def Picture(self, bot, update):
        """
        Inline-клавиатура в ответ на загрузку картинки со стороны
        пользователя

        Args:
            bot (:class:`telegram.Bot`): хэндлер бота
            update(:class:`telegram.ext.Updater`): обновления

        """
        keyboard = [[
                    InlineKeyboardButton("encrypt", callback_data=0),
                    InlineKeyboardButton("decrypt", callback_data=1),
                    InlineKeyboardButton("depart", callback_data=2)]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        update.message.reply_text('Please choose:', reply_markup=reply_markup)

    def ProcessButton(self, bot, update):
        """
        Обработка событий от inline-клавиатуры

        Args:
            bot (:class:`telegram.Bot`): хэндлер бота
            update(:class:`telegram.ext.Updater`): обновления
        """
        query = update.callback_query
        data = int(query.data)
        num_id = query.message.chat.id
        if data == 0:
            self.Encrypt(bot, update)
        elif data == 1:
            self.Restore()
            ChangeFlags(num_id, 'flagDecrypt')
            self.DecryptMessage(bot, update, number=2)
        elif data == 2:
            SetArgs(num_id, 'pathtofile', UsersFlags[num_id]["pathUserpic"])
            SetArgs(num_id, 'pathUserpic', None)
            self.AskChooseUser(bot, update)

    def AnswerLog(self, bot, update):
        """
        Отправление сообщение с информацией о пользователе
        разработчику бота

        Args:
            bot (:class:`telegram.Bot`): хэндлер бота
            update(:class:`telegram.ext.Updater`): обновления

        """
        logger.info("Log method")
        ID = update.message.chat.id
        Answer = "Me writing from chat: " + str(ID)
        Answer += "\nUser => " + str(update.message.chat.username)
        Answer += "\nFull Name => " + str(update.message.chat.first_name)
        Answer += " " + str(update.message.chat.last_name)
        num_id = 243247509  #: номер чата разработчика
        bot.send_message(text=Answer, chat_id=num_id)
        return logger.info("log was sent")

    def GetText(self, bot, update):
        """
        Обработка текстовых сообщений от пользователя

        Args:
            bot (:class:`telegram.Bot`): хэндлер бота
            update(:class:`telegram.ext.Updater`): обновления

        """
        logger.info("GetText")
        num_id = update.message.chat.id
        text = update.message.text
        #: обработка для последующего шифрования
        if UsersFlags[num_id]['flagEncrypt']:
            self.EncryptMessage(bot, update, letter=text)
        #: обработка username'a
        elif UsersFlags[num_id]['getAskUser']:
            self.CheckUser(bot, update, user=text)
        #: эхо-ответ
        else:
            self.Echo(bot, update)
        self.AnswerLog(bot, update)
        return logger.info("GetText done")

    def GetLength(self, bot, update):
        """
        Получение информации о возможной длины сообщения
        в переданную картинку

        Args:
            bot (:class:`telegram.Bot`): хэндлер бота
            update(:class:`telegram.ext.Updater`): обновления

        """
        num_id = self.GetId(bot, update)
        obj = Container()
        obj.SetModule(UsersFlags[num_id]['pathUserpic'])
        length = obj.CheckLength()
        UsersFlags[num_id]["length"] = length

    def ClearDir(self, path, num=5):
        """
        Удаление файлов в указанной директории

        Args:
            path (:obj:`str`): директория
            num (:obj:`int`, optional): ограничение на количество файлов
        """
        if (len(listdir(path)) > num):
            for i in listdir(path):
                remove(path + i)

    def GetDoc(self, bot, update):
        """
        Обработка присланных документов пользователем

        Args:
            bot (:class:`telegram.Bot`): хэндлер бота
            update(:class:`telegram.ext.Updater`): обновления

        """
        logger.info("\'getDoc\'")
        user = update.message.chat.username
        num_id = update.message.chat.id
        photo_file = bot.get_file(update.message.document.file_id)
        #: для отправки другому пользователю любой картинки
        if UsersFlags[num_id]['OnlyDepart']:
            path = self.MakePath("UserPicture")
            num = len(listdir(path)) + 1
            self.ClearDir(path, num=20)
            path += str(user) + str(num) + ".png"
            SetArgs(num_id, 'pathtofile', path)
            photo_file.download(path)
            update.message.reply_text(Strings.askUser)
            ChangeFlags(num_id, 'getAskUser', 'OnlyDepart')
        #: для расшифрования сообщения
        elif UsersFlags[num_id]['flagDecrypt']:
            path = self.MakePath("fromUser")
            num = len(listdir(path)) + 1
            self.ClearDir(path)
            path += "photo" + str(num) + ".png"
            photo_file.download(path)
            self.DecryptMessage(bot, update, number=num)
        #: для загрузки пользовательской картинки
        elif UsersFlags[num_id]["flagUpload"]:
            path = self.MakePath("UserPicture")
            num = len(listdir(path)) + 1
            self.ClearDir(path, num=20)
            path += str(user) + str(num) + ".png"
            ChangeFlags(num_id, 'flagUpload')
            SetArgs(num_id, 'pathUserpic', path)
            photo_file.download(path)
            logger.info("Upload success")
            update.message.reply_text(Strings.uploadSuccess)
        else:
            path = self.MakePath("UserPicture")
            num = len(listdir(path)) + 1
            self.ClearDir(path, num=20)
            path += str(user) + str(5127) + ".png"
            SetArgs(num_id, 'pathUserpic', path)
            photo_file.download(path)
            self.Picture(bot, update)
        return logger.info("GetDoc success")

    def ExplicitPhoto(self, bot, update):
        """
        Запрещена обработка фотографий

        Args:
            bot (:class:`telegram.Bot`): хэндлер бота
            update(:class:`telegram.ext.Updater`): обновления

        """
        update.message.reply_text(Strings.answerPhoto)

    def Error(self, bot, update, error):
        """
        Обработка ошибок

        Args:
            bot (:class:`telegram.Bot`): хэндлер бота
            update(:class:`telegram.ext.Updater`): обновления

        """
        logger.warn('Update "%s" caused error "%s"' % (update, error))

    def AskText(self, bot, update):
        """
        Запрос сообщения для шифрования в png-файл

        Args:
            bot (:class:`telegram.Bot`): хэндлер бота
            update(:class:`telegram.ext.Updater`): обновления

        """
        num_id = self.GetId(bot, update)
        string = "Send me a message you want to encrypt\n"
        string += Strings.lengthMessage.format(
            UsersFlags[num_id]["length"],
            UsersFlags[num_id]["length"] // 2)
        bot.send_message(text=string, chat_id=num_id)

    def AskPicture(self, bot, update):
        """
        Запрос оправления фотографии для:
            + Расшифрования
            + Отправления другому пользователю

        Args:
            bot (:class:`telegram.Bot`): хэндлер бота
            update(:class:`telegram.ext.Updater`): обновления

        """
        num_id = self.GetId(bot, update)
        bot.send_message(text=Strings.uploadpicture, chat_id=num_id)

    def AddHandler(self):
        """
        Добавление хэндлеров в Диспатчер
        """
        self.dispatcher.add_handler(CommandHandler(
            "start", self.Start)
            )
        self.dispatcher.add_handler(CommandHandler(
            "play", self.Play)
            )
        self.dispatcher.add_handler(CommandHandler(
            "help", self.Help)
            )
        self.dispatcher.add_handler(CommandHandler(
            "encrypt", self.Encrypt)
            )
        self.dispatcher.add_handler(CommandHandler(
            "decrypt", self.Decrypt)
            )
        self.dispatcher.add_handler(CommandHandler(
            "upload", self.Upload)
            )
        self.dispatcher.add_handler(CommandHandler(
            "info", self.Info)
            )
        self.dispatcher.add_handler(MessageHandler(
            Filters.text, self.GetText)
            )
        self.dispatcher.add_handler(MessageHandler(
            Filters.document, self.GetDoc)
            )
        self.dispatcher.add_handler(MessageHandler(
            Filters.photo, self.ExplicitPhoto)
            )
        self.dispatcher.add_handler(CommandHandler(
            "Log", self.AnswerLog)
            )
        self.dispatcher.add_handler(CommandHandler(
            "picture", self.SendPicToUser)
            )
        self.dispatcher.add_handler(CommandHandler(
            "depart", self.AskChooseUser)
            )
        self.dispatcher.add_handler(CallbackQueryHandler(
            self.ProcessButton)
            )
        self.dispatcher.add_error_handler(self.Error)

    def StartBot(self):
        """
        Запуск telegram-бота
        """
        self.AddHandler()
        self.updater.start_polling()
        self.updater.idle()


if __name__ == '__main__':
    """
    Main
    """
    token = environ["TOKEN"]
    bot = SteganyBot(token)
    UsersFlags = {}
    InitDict()
    bot.StartBot()
