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
send = ''

ar2 = serial.Serial("COM20",115200)

time.sleep(2)

position = {
    'l':'',
    'm':'',
    'r':''
}

def getSum(im):
    return int(im[40,40][0])+int(im[40,60][0])+int(im[60,60][0])+int(im[60,40][0])

def dataforsingle(im):
    return bin(im[40,40][0])[2:].zfill(8) + \
            bin(im[40,60][0])[2:].zfill(8) + \
            bin(im[60,60][0])[2:].zfill(8) + \
            bin(im[60,40][0])[2:].zfill(8) + \
            bin(math.ceil(getSum(im)/4))[2:].zfill(8)


def avrCon(val):
    return 0 if val <=85 else 1

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
        if str(l).find('image: 5') != -1:
            break
    Popen.kill(process)
    print('end camera process')


def getData():
    data = ''
    image = Image.open('C:/out/'+'4'+'.bmp')
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
    data=str((avrCon(math.ceil(sumlr/4))))+\
        str((avrCon(math.ceil(sumll/4))))+\
        str((avrCon(math.ceil(sumur/4))))+\
        str((avrCon(math.ceil(sumul/4))))
    return data

def getDataSin():
    data = ''
    image = Image.open('C:/out/'+'4'+'.bmp')
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
    data =  dataforsingle(lowright)+dataforsingle(lowleft)+dataforsingle(upright)+dataforsingle(upleft)
    return data

def inittake():
    data=''
    print("start in 3 sec")
    for i in range(3,0,-1):
        print(i)
        time.sleep(1)
    ar2.write('l'.encode())
    takepic()
    code = getData()
    position['l']=code[0]+code[1]+code[2]+code[3]
    data+=position['l']+"1100"

    ar2.write('m'.encode())
    takepic()
    code = getData()
    position['m']=code[0]+code[1]+code[2]+code[3]
    data+=position['m']+"0110"

    ar2.write('r'.encode())
    takepic()
    code = getData()
    position['r']=code[0]+code[1]+code[2]+code[3]
    data+=position['r']+"0011"

    send = "00001001"+data
    #ready to send 8bit command + 24bit data
    #ar2.write('m'.encode())
    sendData(send)
    send = ''

def singlePic(Getpicturebit):
    wait = ''
    new = ''
    for pos,val in position.items():
        if str(Getpicturebit) == val:
            ar2.write(str(pos).encode())
            takepic()
            send  = '00001010'+getDataSin()
            new = getData()
            position[str(pos)] = new[0]+new[1]+new[2]+new[3]
            
            sendData(send)
            while wait != b'6\r\n':
                wait = ar2.readline()
                print(wait)
            else :
                print(wait)
                print("send point : ")
                send = ''
                send = '00001011'+'1000100111011100'+'0000000101010100'+'1010101111111110'+'0010001101110110'
                sendData(send)
            print('Done')
            # break
            
        
def sendData(data):
    out = ''
    out += str(chr(int(data[:8],2)))+data[8:]
    print("send : ",out)
    ar2.write(out.encode())
        

#----------main----------##
    
while(1):
    getserial = ar2.readline()
    #print(getserial)
    getcmd = bytes_to_String(getserial)
    print(getcmd)
    if getcmd[:4] == '0000':
        print("Take all picture")
        inittake()
    elif getcmd[:4] == '0101':
        print("Single Shot picture binary : ",getcmd[4:])
        singlePic(str(getcmd[4:]))
