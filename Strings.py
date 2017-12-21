# -*- coding: utf-8 -*-
"""Этот модуль сожержит статус-строки

Args:
    startGreet :obj:`str`: - строка-приветствие
    info :obj:`str`: - Информация о боте
    greeting2 :obj:`str`: - строка при вызове /play
    helpString :obj:`str`: - строка при вызове /help
    answerPhoto :obj:`str`: - ответ на получение ботом
        файла типа "картинка"
    addUsername :obj:`str`: - уведомление об отсутствии username'a
    getPic :obj:`str`: - получение документа без
        использования /decrypt
    lengthMessage :obj:`str`: - уведомление о длине сообщения
    askUser :obj:`str`: - строка о запросе username'a
    addFriendUser :obj:`str`: - уведомление, что пользователь
        получатеть еще не пользовался ботом
    afterEncrypt :obj:`str`: - строка после завершения encrypt'a
    messageUser :obj:`str`: - уведомление о получении сообщения
        от пользователя
    uploadpicture :obj:`str`: - запрос о загрузки документа
    uploadSuccess :obj:`str`: - статус-строка об успешной загрузки
    AnswerStatus :obj:`dict`: - словарь статус-состояний после
        добавления пользователя в базу данных
"""

startGreet = """
Hi! My name is SteganyBot.
Nice to meet you)
I'll help you to hide you owner message
to your friend in picture.

Use methods:
/info - to get more information about me
/play - to start using
/help - some helpful info

If i were you, i would begin with /info
"""

info = """
Okay, this is an information about me:
My ability - hide message in picture and,
of course, get this message from picture. But
this picture should be from me, when you or your
friend hide message.

There are list of methods:
/start - use at the beginning
/play - start conversation with bot
/info - get more info about me
/encrypt - hide message
/decrypt - get message
/help - some more info about methods

To hide message use /encrypt
and follow me)
To get message use /decrypt

"""

greeting2 = """
Choose the next step:
1) Ecrypt message
2) Decrypt message
3) upload own picture
4) send picture to friend
"""

helpString = """Don't worry! To start write \"/start\"
\"Encrypt\" - able you to hide the text in
picture which i provide you
\"Decrypt\" - get the message from picture
it's picture was sent by your friend who got this picture
from this bot"""

answerPhoto = """Sorry, but bot couldn't work with
photo \'cause it compressed before downloading to bot
"""

addUsername = """OOOps, you haven't added username yet.
Please, add username to your profile to have opportunity
to get message from friends across me)
goes settings -> username -> type name -> save
after that? please resend me \'/start\'
it's very simple)
"""

getPic = """good Picture, bro))
maybe you forget select /decrypt"""

askUser = """please, send me
username of your friend in format
\'@username\'
Thanks)"""

addFriendUser = """Sorry but i don't find
user with this username. Maybe your friend
haven't written to me yet. Ask him to write me \'/start\'
"""

afterEncrypt = """to get picture send me
\'/picture\' or if you want send to friend
push method \'/depart\'
"""

messageUser = """Hi, {} send to you
message. To read it, use me and my method
\'/decrypt\'"""

uploadpicture = """Please, upload the picture to decrypt
you should upload as a doc file)"""

uploadSuccess = """Your photo downloaded\n
to hide message in your picture continued
with method \'/encrypt\'"""

lengthMessage = """Your message in English should be
less than {} symbols or {} in Russian"""

AnswerStatus = {
    "add username success": 200,
    "notice user": 365,
    "already exist": 127,
    "successful addUser": 101
}
