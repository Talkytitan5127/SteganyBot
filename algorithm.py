# -*- coding: utf-8 -*-
"""В этом модуле реализована работа с png-файлом и механизм внедрения
    информации в картинку с помощью алгоритма Куттера-Джордана-Боссена"""

from PIL import Image, ImageDraw
from bitarray import bitarray
import sys


class Picture:
    """Это класс предоставляет работу с файлом изображения

    Note:
        Этот класс недоступен пользователю.

    Attributes:
        image (:class:`Image`): Переданный png-файл для контейнера
        width (:obj:`int`): Ширина картинки
        height (:obj:`int`): Высота картинки
        draw (:class:`ImageDraw`): Перо для работы с png-файлом

    Args:
        path (:obj:`str`): Путь до png-файла

    """

    def __init__(self, path):
        self.image = Image.open(path)
        self.width = self.image.size[0]
        self.height = self.image.size[1]
        self.draw = ImageDraw.Draw(self.image)

    def LengthText(self):
        """Максимальная длина возможного сообщения

        Returns:
        :obj:`int` Длина сообщения
        """
        step = 4
        lenText = ((self.width - step) // step)
        lenText *= ((self.height - step) // step)
        return lenText

    def GetBit(self):
        """
        Расшифрока сообщения из png-файла, внедренного
            алгоритмом Куттера-Джордана-Боссена.
        Проходим по всему png-файлу и достаем биты сообщения.

        Returns:
            :class:`bitarray`: биты сообщения

        """
        pix = self.image.load()
        bText = bitarray()
        lenText = self.GetLen()
        i = 4
        j = 4
        Count = 0  #: количество полученных битов
        t = 0  #: счетчик итераций для получения одного бита
        result = 0  #: прогнозируемое значения яркости синего цвета
        #: количество итерация нужных для получения одного бита
        repeat = 3
        while(Count < lenText):
            bitpix = 0
            for k in range(1, 4):
                bitpix += pix[i, j + k][2]
                bitpix += pix[i, j - k][2]
                bitpix += pix[i + k, j][2]
                bitpix += pix[i - k, j][2]
            value = int(bitpix / (4 * 3))
            result += pix[i, j][2] - value
            t += 1
            #: переходим на следующий пиксель если итерация не завершена
            if t != repeat:
                j += 4
                if (j >= self.height):
                    j = 4
                    i += 4
                continue
            result = int(result / repeat)
            #: обработка случая для уменьшения вероятности ошибки
            if (result == 0 and pix[i, j][2] == 255):
                result = 0.5
            if (result == 0 and pix[i, j][2] == 0):
                result = -0.5
            #: получение бита
            if result > 0:
                bText += '1'
            else:
                bText += '0'
            t = 0
            Count += 1
            result = 0
            j += 4
            #: переход на новую строку
            if (j >= self.height - 3):
                j = 4
                i += 4
            if (i >= self.width - 3):
                raise IndexError
        return bText

    def ChangePix(self, text):
        """Внедрение сообщения в png-файл с помощью алгоритма

        Args:
            (:class:`bitarray`): исходное сообщение в битах

        Returns:
            :obj:`str`: Статус о завершении шифровки

        """
        pix = self.image.load()
        i = 4
        j = 4
        indW = 0  #: текущий бит
        t = 1  #: текущая итерация внедрения indW бита
        repeat = 3  #: количество итераций
        self.SaveLen(len(text))
        while indW < len(text):
            red = pix[i, j][0]
            green = pix[i, j][1]
            blue = pix[i, j][2]
            #: коэффициент энергии встраимаемого бита данных
            lam = 0.3 * red + 0.59 * green + 0.11 * blue
            #: энергия встраимаевого сигнала
            xu = 1.3
            alpha = 3
            if lam == 0:
                lam = alpha / xu
            if text[indW]:
                blue += lam * xu
                blue = int(blue) + 1
                if blue > 255:
                    blue = 255
            else:
                blue -= lam * xu
                if blue < 0:
                    blue = 0
            blue = int(blue)
            self.draw.point((i, j), (red, green, blue))
            j += 4
            if (j >= self.height - 3):
                j = 4
                i += 4
            if (i >= self.width - 3):
                raise IndexError
            if t == repeat:
                indW += 1
                t = 0
            t += 1
        return "Success encryption"

    def Decto256(self, num):
        """
        Перевод десятичного числа в 256-ую систему счистления

        Args:
            num (:obj:`int`): исходное десятичное число

        Returns:
            :obj:`list`: число в 256-ой системе счистления

        """
        res = []
        while num > 0:
            res.append(num % 256)
            num //= 256
        return res

    def Numtodec(self, num):
        """
        Перевод 256-ого числа в десятичную систему счистления

        Args:
            num (:obj:`list`): Исходное число в 256-ой системе счистления

        Returns:
            :obj:`int`: Число в десятиричной системе счистления

        """
        res = 0
        for i in range(len(num)):
            res += num[i] * (256**i)
        return res

    def SaveLen(self, lenT):
        """
        Сохранение длины сообщения в картинке

        Args:
            lenT (:obj:`int`): длина сообщения, внедряемого в png-файл

        """
        pix = self.image.load()
        nums = self.Decto256(lenT)
        self.draw.point((0, 0), (pix[0, 0][0], pix[0, 0][1], len(nums)))
        for i in range(1, len(nums) + 1):
            self.draw.point((0, i), (pix[0, i][0], pix[0, i][1], nums[i-1]))

    def GetLen(self):
        """
        Получение длины сообщения, зашифрованного в png-файле

        Returns:
            :obj:`int`: Длина сообщения, зашифрованного в файле

        """
        pix = self.image.load()
        q = pix[0, 0][2]
        nums = []
        for i in range(1, q + 1):
            nums.append(pix[0, i][2])
        res = self.Numtodec(nums)
        return res

    def WritePix(self, flag):
        """
        Запись всех пикселей в файл

        Args:
            flag (:obj:`str`): составляющая названия файла

        """
        file = flag + "Crypt.txt"
        data = self.image.getdata()
        with open(file, 'w') as f:
            for i in data:
                print(i, file=f)

    def SaveChange(self, path):
        """
        Сохранение результатов шифрования в png-файл

        Args:
            path (:obj:`str`): путь до файла

        Returns:
            str: Путь до файла с зашифрованным сообщением
        """
        newpath = path.replace("jpg", "png")
        newpath = newpath.replace("encrypt", "decrypt")
        self.image.save(newpath, 'png')
        del self.draw
        self.image.close()
        return newpath


class Container:
    """
    Класс предоставляет интерфейс для шифрования/зашифрования
    сообщение в png-файл.

    Note:
        Класс недоступен пользователю

    Attributes:
        MyImage (:class:`Picture`): Объект класса 'Picture'
        Pathfile (:obj:`str`): Путь до png-файла
        UserName (:obj:`str`): Username пользователя

    """
    def __init__(self):
        self.MyImage = None
        self.Pathfile = None
        self.UserName = None

    def SetModule(self, path):
        """
        Установка значений для полей `Pathfile` и `MyImage`

        Args:
            path (:obj:`str`): путь до файла

        """
        self.Pathfile = path
        self.MyImage = Picture(self.Pathfile)

    def SetUser(self, name):
        """
        Установка значения для поля `UserName`

        Args:
            name (:obj:`str`): username пользователя

        """
        self.UserName = name

    def Encrypt(self, text):
        """
        шифрование переданного сообщения в png-файл

        Args:
            text (:obj:`str`): сообщение пользователя
        """
        bText = bitarray()
        bText.frombytes(text.encode('utf-8'))
        self.MyImage.WritePix(flag="Before")
        try:
            print(self.MyImage.ChangePix(text=bText))
        except Exception:
            return 127
        self.MyImage.WritePix(flag="After")

    def Save(self):
        """
        Сохранение в png-файл

        Returns:
            :obj:`str`: Путь до файла с зашифрованным сообщением
        """
        newpath = self.MyImage.SaveChange(self.Pathfile)
        return newpath

    def CheckLength(self):
        """
        Получение возможной длины сообщения

        Returns:
            :obj:`int`: возможная длина сообщения
        """
        lenT = self.MyImage.LengthText()
        return int(lenT // (3*8))

    def Decrypt(self):
        """
        Расшифрование сообщения из png-файла

        Returns:
            :obj:`str`: Статус-строка
            str: {
                "sorry, there are undecoded byte in decrypt message",
                "Ops, are you sure with your choice?)))
                I think, i haven't got this picture before"
            }
        """
        try:
            bText = self.MyImage.GetBit()
        except IndexError:
            return """Ops, are you sure with your choice?)))
                I think, i haven't got this picture before"""
        bText = bText.tobytes()
        try:
            result = bText.decode('utf-8')
            return result
        except Exception:
            result = self.ParseStr(bText)
            return result

    def Decode(self, bits):
        """
        Перевод из байтов в символы utf8

        Args:
            bits (:obj:`int`): byte-строка

        Returns:
            :obj:`str` сообщение
        """
        array = bitarray()
        array.frombytes(bytes(bits))
        result = array.tobytes().decode()
        return result

    def ParseStr(self, text):
        """
        Декодирование байтов в utf8

        Args:
            text (:class:`bitaaray`): byte-строка

        Returns:
            :obj:`str` сообщение
        """
        result = ''
        mas = [text[i:i+2] for i in range(0, len(text), 2)]
        for i in mas:
            try:
                if (type(i) == str):
                    result += i
                else:
                    result += i.decode()
            except Exception:
                if i[0] < 128:
                    sym = i[0]
                else:
                    sym = i[1]
                result += chr(sym)
        return result
