# -*- coding: utf-8 -*-
"""В этом модуле прописаны unit-тесты для проверки работоспособности
шифрования/дешифрования сообщения стеганографическим алгоритмом
Куттера-Джордана-Боссена"""

import unittest
from algorithm import *
from random import randint

pathPhoto1 = "./photos/encrypt/photo1.png"
pathPhoto3 = "./photos/encrypt/photo3.png"
pathPhoto5 = "./photos/encrypt/photo5.png"


def GenerateMes(length):
    res = ''
    for i in range(length):
        num = randint(65, 122)
        res += chr(num)
    return res


def Encrypt(mes, photo):
    enc = Container()
    enc.SetModule(pathPhoto1)
    enc.Encrypt(mes)
    path = enc.Save()
    return path


def Decrypt(path):
    dec = Container()
    dec.SetModule(path)
    result = dec.Decrypt()
    return result


def CheckStr(mes, result):
    if len(mes) != len(result):
        raise "length not equal"

    errors = 0
    for i in range(len(mes)):
        if (mes[i] != result[i]):
            errors += 1
    print("errors ==> ", errors)
    return errors


class Length150(unittest.TestCase):
    def testphoto1(self):
        length = 150
        mes = GenerateMes(length)
        print("message ==> ", mes)

        path = Encrypt(mes, pathPhoto1)

        result = Decrypt(path)

        self.assertEqual(mes, result)

    def testphoto3(self):
        length = 150
        mes = GenerateMes(length)
        print("message ==> ", mes)

        path = Encrypt(mes, pathPhoto3)

        result = Decrypt(path)

        self.assertEqual(mes, result)

    def testphoto5(self):
        length = 150
        mes = GenerateMes(length)
        print("message ==> ", mes)

        path = Encrypt(mes, pathPhoto5)

        result = Decrypt(path)

        self.assertEqual(mes, result)


class Length1500(unittest.TestCase):
    def testphoto1(self):
        length = 1500
        mes = GenerateMes(length)
        print("message ==> ", mes)

        path = Encrypt(mes, pathPhoto1)

        result = Decrypt(path)

        errors = CheckStr(mes, result)
        self.assertLessEqual(errors, 3)

    def testphoto3(self):
        length = 1500
        mes = GenerateMes(length)
        print("message ==> ", mes)

        path = Encrypt(mes, pathPhoto3)

        result = Decrypt(path)

        errors = CheckStr(mes, result)
        self.assertLessEqual(errors, 3)

    def testphoto5(self):
        length = 1500
        mes = GenerateMes(length)
        print("message ==> ", mes)

        path = Encrypt(mes, pathPhoto5)

        result = Decrypt(path)

        errors = CheckStr(mes, result)

        self.assertLessEqual(errors, 3)


if __name__ == "__main__":
    unittest.main()
