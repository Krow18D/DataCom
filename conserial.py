from PIL import Image
import matplotlib.pyplot as plt
import numpy as np
import os.path
from random import randint
from itertools import product
import math
import serial 
import time
import os
from subprocess import Popen, PIPE
ser = serial.Serial("COM14", 9600)

position = {
    'l':'',
    'm':'',
    'r':''
}

def getSum(im):
    return int(im[40,40][0])+int(im[40,60][0])+int(im[60,60][0])+int(im[60,40][0])


def getDot(im):
    out=''
    x1= 0 if int(im[60,60][0])<=85 else 1
    x2= 0 if int(im[40,60][0])<=85 else 1
    x3= 0 if int(im[40,40][0])<=85 else 1
    x4= 0 if int(im[60,40][0])<=85 else 1
    return out+str(x1)+str(x2)+str(x3)+str(x4)

def avrCon(val):
    return 0 if val <100 else 1

def bytes_to_String(bytes):
    out =''
    for b in bytes:
        if chr(b)=='0' or chr(b)=='1':out+=chr(b)
    return out

def takepic():
    os.chdir('C:/Program Files (x86)/Java/jdk1.8.0_74/bin')
    process = Popen(['java', 'code.SimpleRead'], stdout=PIPE, stderr=PIPE)
    print("start taking pic")
    #time.sleep(60)
    while process.poll() is None:
        l = process.stdout.readline() 
        print('.',end=' ')
        if str(l).find('image: 10') != -1:
            break
    Popen.kill(process)
    print('end process')

def sendData():
    ser.write(str(input()).encode())
    file = open('D:/Work/2D/Datacom/assign/text/test.txt','r') 
    dataRead = file.read()
    print(len(dataRead))
    i=0
    while(i<len(dataRead)):
        print(dataRead[i])
        ser.write(str(dataRead[i]).encode())
        i+=1
    file.close()


def getData():
    image = Image.open('C:/out/'+'9'+'.bmp')
    box_ul = (0,0,100,100)
    box_ur = (100,0,200,100)
    box_ll = (0,100,100,200)
    box_lr = (100,100,200,200)
    box = (20,60,220,260)
    newimage = image.crop(box)
    upleft = newimage.crop(box_ul)
    upright = newimage.crop(box_ur)
    lowleft = newimage.crop(box_ll)
    lowright = newimage.crop(box_lr)

    upleft = np.array(upleft)
    upright = np.array(upright)
    lowleft = np.array(lowleft)
    lowright = np.array(lowright)
    sumur = getSum(upright)
    sumul = getSum(upleft)
    sumll = getSum(lowleft)
    sumlr = getSum(lowright)
            
    data=''+getDot(lowright)+str((avrCon(math.ceil(sumlr/4))))+''+\
            getDot(lowleft)+str((avrCon(math.ceil(sumll/4))))+''+\
            getDot(upright)+str((avrCon(math.ceil(sumur/4))))+''+\
            getDot(upleft)+str((avrCon(math.ceil(sumul/4))))
    return data

def inittake():
    data=''
    print("start in 5 sec")
    for i in range(5,0,-1):
        print(i)
        time.sleep(1)
    ser.write('l'.encode())
    takepic()
    code = getData()
    position['l']+=code[4]+code[9]+code[14]+code[19]
    data+=position['l']+"1100"

    ser.write('m'.encode())
    takepic()
    code = getData()
    position['m']+=code[4]+code[9]+code[14]+code[19]
    data+=position['m']+"0110"

    ser.write('r'.encode())
    takepic()
    code = getData()
    position['r']+=code[4]+code[9]+code[14]+code[19]
    data+=position['r']+"0011"

    print('yayy')
    print(data)
    #ready to send 
    ser.write('m'.encode())

def singlePic(Getpicturebit):
    print("woohoo",Getpicturebit)
    for pos,val in position.items():
        print(pos,' : ',val)
        if str(Getpicturebit) == val:
            print("hello")
            ser.write(str(pos).encode())
            takepic()
            print(getData())
        





##----------main----------##
inittake()
while(1):
    d = input("picture = ")
    singlePic(str(d))
#     s = ser.readline()
#     print(bytes_to_String(s))






