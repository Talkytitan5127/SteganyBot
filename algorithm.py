from PIL import Image, ImageDraw
from bitarray import bitarray
import sys

class Picture:
    def __init__(self):
        self.image = None
        self.width = 0
        self.height = 0
        self.draw = None
    def __init__(self, path):
        self.image = Image.open(path)
        self.width = self.image.size[0]
        self.height = self.image.size[1]
        self.draw = ImageDraw.Draw(self.image)

    def GetBit(self):
        pix = self.image.load()
        bText = bitarray()
        lenText = pix[0,0][2]
        print("length => ", lenText)
        
        i = 4
        j = 4
        Count = 0
        t = 0
        result = 0
        
        while(Count < lenText):
            
            bitpix = 0
            for k in range(1, 4):
                try:
                    bitpix += pix[i,j + k][2]
                except:
                    pass
                try:
                    bitpix += pix[i,j - k][2]
                except:
                    pass
                try:
                    bitpix += pix[i + k,j][2]
                except:
                    pass
                try:
                    bitpix += pix[i - k,j][2]
                except:
                    pass
            
            value = int(bitpix / (4 * 3))
            
            result += pix[i, j][2] - value
            
            t += 1

            j += 4
            if (j >= self.height):
                j = 0
                i += 4

            if t != 2:
                continue
            
            result = int(result / 2)

            if (result == 0 and pix[i, j][2] == 255):
                result = 0.5
            if (result == 0 and pix[i, j][2] == 0):
                result = -0.5
                                
            if result > 0:
                bText += '1'
            else:
                bText += '0'

            t = 0        
            Count += 1
            result = 0

        return bText


    def ChangePix(self, text):
        pix = self.image.load()
        
        k = 0
        i = 4
        j = 4
        t = 1
        
        self.draw.point((0, 0),(pix[0, 0][0],
            pix[0, 0][1], len(text)))
        
        while k < len(text):
    
            red = pix[i, j][0]
            green = pix[i, j][1]
            blue = pix[i, j][2]
            lam = 0.3*red + 0.59*green + 0.11*blue       
            xu = 0.5
            alpha = 2

            if lam == 0:
                lam = alpha/xu


            if text[k]:
                blue += lam*xu
                blue = int(blue) + 1
                if blue > 255:
                    blue = 255
            else:
                blue -= lam*xu
                if blue < 0:
                    blue = 0
    
            blue = int(blue)
            self.draw.point((i, j), (red, green, blue))
            
            j += 4
            if (j >= self.height):
                j = 4
                i += 4
            
            if t == 2:
                k += 1
                t = 0

            t += 1

        return "Success encryption"

    
    def WritePix(self, flag):
        file = flag + "Crypt.txt"
        data = self.image.getdata()
        with open(file, 'w') as f:
            for i in data:
                print(i, file=f)
    

    def SaveChange(self, path):
        newpath = path.replace("jpg", "png")
        newpath = newpath.replace("encrypt", "decrypt")
        print("path=", newpath)
        self.image.save(newpath, 'png')
        del self.draw
        return newpath



class Container:
    def init(self):
        self.MyImage = Picture()
        self.Pathfile = None
        self.UserName = None
    
    def SetModule(self, path):
        self.Pathfile = path
        self.MyImage = Picture(self.Pathfile)

    def SetUser(self, name):
        self.UserName = name

    def Encrypt(self, text):
        bText = bitarray()
        bText.frombytes(text.encode('utf-8'))
        print(bText, len(bText))
        
        self.MyImage.WritePix(flag="Before")
                
        print(self.MyImage.ChangePix(text=bText))

        self.MyImage.WritePix(flag="After")

    def Save(self):
        newpath = self.MyImage.SaveChange(self.Pathfile)
        return newpath

    def CheckBot(self):
        if not self.MyImage.CheckWrite():
            raise 5127

    def Decrypt(self):
        bText = self.MyImage.GetBit()
        print('btext =>', bText)
        bText = bText.tobytes()
        print('btext =>', bText)
        try:
            result = bText.decode('utf-8')
            print('result => ', result)
            return result
        except:
            return "sorry, there are undecoded byte in decrypt message"


if __name__ == '__main__':
    print(sys.argv)
    value = int(sys.argv[1])
    print(value)
    if (value == 5):
        obj = Container()
        obj.SetModule("photos/encrypt/photo3.png")
        obj.SetUser("Talkytitan5127")
        obj.Encrypt("Nice to meet you")
        obj.Save()
    else:
        obj = Container()
        obj.SetModule("photos/decrypt/photo3.png")
        text = obj.Decrypt()
        print(text)