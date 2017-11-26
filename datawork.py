# -*- coding: utf-8 -*-
"""Этот модуль сожержит класс DataBase, реализующий работу
    с базой данных"""

import os
from urllib import parse
import psycopg2

parse.uses_netloc.append("postgres")
url = parse.urlparse(os.environ["DATABASE_URL"])


class DataBase:
    """Реализует интерфейс работы с базой данных
    
    Note:
        У пользователя прямого доступа к классу нет
    
    Attributes:
        conn (:class: `connection`): Дескриптор подключения к базе данных
        cur (:class: `cursor`): Перо для выполнения PostgreSQL команд.
    Args:
        conn (:class: `connection`): Дескриптор подключения к базе данных.
            Создается подключение между программой и базой данных, созданная
            в приложении в сервисе Heroku.
        cur (:class: `cursor`): Перо для выполнения PostgreSQL команд.
            Создается и связывается с текущим соединением к базе данных.

    """
    def __init__(self):
        self.conn = psycopg2.connect(
            database=url.path[1:],
            user=url.username,
            password=url.password,
            host=url.hostname,
            port=url.port
        )
        self.cur = self.conn.cursor()

    def __del__(self):
        self.conn.close()
        self.cur.close()

    # add user to database
    def AddUser(self, user):
        """Добавление пользователя в базу данных

        Args:
            user (list): Данные о пользователе:
                + Username
                + Имя
                + Фамилия
                + Номер чата

        Returns:
            str: Возвращает строку статуса:
                {
                    "add username success": успешное добавление username'a
                        пользователя в базу данных
                    "notice user": у пользователя нет username'a
                    "already exist": данные пользователя в базе данных
                    "successful addUser": успешное добавление данных
                        пользователя в базу данных
                }

        """
        f = self.CheckUser(user[3])
        if f:
            # if in db not username but user have it will be added
            if not self.CheckFullUser(user) and user[0] is not None:
                self.AddUserName(user)
                return "add username success"
            # or user will be noticed about username
            elif user[0] is None:
                return "notice user"
            return "already exist"
        self.cur.execute(
            """INSERT INTO users (username, first_name,
            last_name, chat_id)
            VALUES (%s, %s, %s, %s);""",
            (user[0], user[1], user[2], user[3])
        )
        self.conn.commit()
        if len(user[0]) == 0:
                return "notice user"
        return "successful addUser"

    # if user in db or not
    def CheckUser(self, id):
        """Проверка наличия данных о пользователе в базе данных

        Agrs:
            id (int): номер чата

        Returns:
            bool: True если есть, False в противном случае

        """
        self.cur.execute(
            "SELECT * FROM users WHERE chat_id={}".format(id)
        )
        res = self.cur.fetchall()
        if len(res) != 0:
            return True
        else:
            return False

    def CheckFullUser(self, user):
        """Проверка наличия username'a пользователя

        Args:
            user (list): данные о пользователе

        Returns:
            bool: True если есть username, False в противном случае

        """
        self.cur.execute(
            """SELECT * FROM users WHERE username=\'{}\'
                OR first_name=\'{}\' OR last_name=\'{}\' OR
                chat_id={}
            """.format(user[0], user[1], user[2], user[3])
        )
        res = self.cur.fetchall()
        if res[0][0] is None:
            return False
        else:
            return True

    def AddUserName(self, user):
        """Обновление поля username у пользователя

        Args:
            user (list): данные о пользователе

        """
        self.cur.execute(
            """UPDATE users SET username=\'{}\'
            WHERE chat_id=\'{}\'
            """.format(user[0], user[3])
        )
        self.conn.commit()
        return "successful changed username"

    def GetId(self, user):
        """Возвращает номер чата переданного пользователя

        Args:
            user (list): данные о пользователе

        Returns:
            :obj:`int`: Номер чата с данным пользователем
        """
        self.cur.execute("""SELECT chat_id FROM users
            WHERE username=\'{}\'""".format(user))
        res = self.cur.fetchall()
        print(res)
        id = int(res[0][0])
        return id

    def AskUserName(self, username):
        """Проверка наличия пользователя с переданным username'ом
        
        Args:
            username (str): Username пользователя

        Returns:
            bool: True если есть, False иначе.
        """
        self.cur.execute(
            """SELECT * FROM users WHERE
            username=\'{}\'""".format(username)
        )
        res = self.cur.fetchall()
        if len(res) == 0:
            return False
        else:
            return True
