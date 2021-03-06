#!/usr/bin/python
#
# Created by Alan Aufderheide, February 2013
#
# This provides a menu driven application using the LCD Plates
# from Adafruit Electronics.

import commands
import os
from string import split
from time import sleep, strftime, localtime
from datetime import datetime, timedelta
from xml.dom.minidom import *
from Adafruit_I2C import Adafruit_I2C
from Adafruit_MCP230xx import Adafruit_MCP230XX
from Adafruit_CharLCDPlate import Adafruit_CharLCDPlate
from ListSelector import ListSelector
import picamera

import smbus

configfile = 'lcdmenu.xml'
# set DEBUG=1 for print debug statements
DEBUG = 0
DISPLAY_ROWS = 2
DISPLAY_COLS = 16

# set to 0 if you want the LCD to stay on, 1 to turn off and on auto
AUTO_OFF_LCD = 0

# set busnum param to the correct value for your pi
lcd = Adafruit_CharLCDPlate(busnum = 1)
# in case you add custom logic to lcd to check if it is connected (useful)
#if lcd.connected == 0:
#    quit()

awb_choice = 0
iso_choice = 0
AWB_MODES = ['off', 'auto', 'sunlight', 'cloudy', 'shade', 'tungsten', 'fluorescent', 'incandescent', 'flash', 'horizon']
ISO_MODES = [0, 100, 200, 320, 400, 500, 640, 800]

lcd.begin(DISPLAY_COLS, DISPLAY_ROWS)
lcd.backlight(lcd.OFF)

# commands
def DoQuit():
    lcd.clear()
    lcd.message('Are you sure?\nPress Sel for Y')
    while 1:
        if lcd.buttonPressed(lcd.LEFT):
            break
        if lcd.buttonPressed(lcd.SELECT):
            lcd.clear()
            lcd.backlight(lcd.OFF)
            quit()
        sleep(0.25)

def DoShutdown():
    lcd.clear()
    lcd.message('Are you sure?\nPress Sel for Y')
    while 1:
        if lcd.buttonPressed(lcd.LEFT):
            break
        if lcd.buttonPressed(lcd.SELECT):
            lcd.clear()
            lcd.backlight(lcd.OFF)
            commands.getoutput("sudo shutdown -h now")
            quit()
        sleep(0.25)

def DoReboot():
    lcd.clear()
    lcd.message('Are you sure?\nPress Sel for Y')
    while 1:
        if lcd.buttonPressed(lcd.LEFT):
            break
        if lcd.buttonPressed(lcd.SELECT):
            lcd.clear()
            lcd.backlight(lcd.OFF)
            commands.getoutput("sudo reboot")
            quit()
        sleep(0.25)

def LcdOff():
    global currentLcd
    currentLcd = lcd.OFF
    lcd.backlight(currentLcd)

def LcdOn():
    global currentLcd
    currentLcd = lcd.ON
    lcd.backlight(currentLcd)

def ShowDateTime():
    if DEBUG:
        print('in ShowDateTime')
    lcd.clear()
    while not(lcd.buttonPressed(lcd.LEFT)):
        sleep(0.25)
        lcd.home()
        lcd.message(strftime('%a %b %d %Y\n%I:%M:%S %p', localtime()))
    
def ValidateDateDigit(current, curval):
    # do validation/wrapping
    if current == 0: # Mm
        if curval < 1:
            curval = 12
        elif curval > 12:
            curval = 1
    elif current == 1: #Dd
        if curval < 1:
            curval = 31
        elif curval > 31:
            curval = 1
    elif current == 2: #Yy
        if curval < 1950:
            curval = 2050
        elif curval > 2050:
            curval = 1950
    elif current == 3: #Hh
        if curval < 0:
            curval = 23
        elif curval > 23:
            curval = 0
    elif current == 4: #Mm
        if curval < 0:
            curval = 59
        elif curval > 59:
            curval = 0
    elif current == 5: #Ss
        if curval < 0:
            curval = 59
        elif curval > 59:
            curval = 0
    return curval

def SetDateTime():
    if DEBUG:
        print('in SetDateTime')
    # M D Y H:M:S AM/PM
    curtime = localtime()
    month = curtime.tm_mon
    day = curtime.tm_mday
    year = curtime.tm_year
    hour = curtime.tm_hour
    minute = curtime.tm_min
    second = curtime.tm_sec
    ampm = 0
    if hour > 11:
        hour -= 12
        ampm = 1
    curr = [0,0,0,1,1,1]
    curc = [2,5,11,1,4,7]
    curvalues = [month, day, year, hour, minute, second]
    current = 0 # start with month, 0..14

    lcd.clear()
    lcd.message(strftime("%b %d, %Y  \n%I:%M:%S %p  ", curtime))
    lcd.blink()
    lcd.setCursor(curc[current], curr[current])
    sleep(0.5)
    while 1:
        curval = curvalues[current]
        if lcd.buttonPressed(lcd.UP):
            curval += 1
            curvalues[current] = ValidateDateDigit(current, curval)
            curtime = (curvalues[2], curvalues[0], curvalues[1], curvalues[3], curvalues[4], curvalues[5], 0, 0, 0)
            lcd.home()
            lcd.message(strftime("%b %d, %Y  \n%I:%M:%S %p  ", curtime))
            lcd.setCursor(curc[current], curr[current])
        if lcd.buttonPressed(lcd.DOWN):
            curval -= 1
            curvalues[current] = ValidateDateDigit(current, curval)
            curtime = (curvalues[2], curvalues[0], curvalues[1], curvalues[3], curvalues[4], curvalues[5], 0, 0, 0)
            lcd.home()
            lcd.message(strftime("%b %d, %Y  \n%I:%M:%S %p  ", curtime))
            lcd.setCursor(curc[current], curr[current])
        if lcd.buttonPressed(lcd.RIGHT):
            current += 1
            if current > 5:
                current = 5
            lcd.setCursor(curc[current], curr[current])
        if lcd.buttonPressed(lcd.LEFT):
            current -= 1
            if current < 0:
                lcd.noBlink()
                return
            lcd.setCursor(curc[current], curr[current])
        if lcd.buttonPressed(lcd.SELECT):
            # set the date time in the system
            lcd.noBlink()
            os.system(strftime('sudo date --set="%d %b %Y %H:%M:%S"', curtime))
            break
        sleep(0.25)

    lcd.noBlink()

def ShowIPAddress():
    if DEBUG:
        print('in ShowIPAddress')
    lcd.clear()
    lcd.message(commands.getoutput("/sbin/ifconfig").split("\n")[1].split()[1][5:])
    while 1:
        if lcd.buttonPressed(lcd.LEFT):
            break
        sleep(0.25)
        
def CameraTakePicture():
    if DEBUG:
        print('in CameraTakePicture')
    lcd.clear()
    lcd.message("Select to take")
    while not lcd.buttonPressed(lcd.LEFT):
        if lcd.buttonPressed(lcd.SELECT):
            with picamera.PiCamera() as camera:
                camera.awb_mode = AWB_MODES[awb_choice]
                camera.iso = ISO_MODES[iso_choice]
                camera.capture('image.jpg')
            lcd.setCursor(0,1)
            lcd.message("Taken")
            sleep(0.5)
            lcd.clear()
            lcd.message("Select to take")


def CameraTimeLapse():
    if DEBUG:
        print('in CameraTimeLapse')

def Awb_select():
    global awb_choice
    lcd.clear()
    lcd.message("Select AWB:")
    while not lcd.buttonPressed(lcd.LEFT):
        lcd.setCursor(0,1)
        lcd.message(AWB_MODES[awb_choice])
        lcd.message("          ")
        if lcd.buttonPressed(lcd.UP):
            if awb_choice > 0:
                awb_choice -=1
            else:
                awb_choice = 9
            sleep(0.5)
        if lcd.buttonPressed(lcd.DOWN):
            if awb_choice < 9:
                awb_choice += 1
            else:
                awb_choice = 0
            sleep(0.5)

def Iso_select():
    global iso_choice
    lcd.clear()
    lcd.message("Select ISO:")
    while not lcd.buttonPressed(lcd.LEFT):
        lcd.setCursor(0,1)
        lcd.message(ISO_MODES[iso_choice])
        lcd.message("          ")
        if lcd.buttonPressed(lcd.UP):
            if iso_choice > 0:
                iso_choice -=1
            else:
                iso_choice = 7
            sleep(0.5)
        if lcd.buttonPressed(lcd.DOWN):
            if iso_choice < 7:
                iso_choice += 1
            else:
                iso_choice = 0
            sleep(0.5)

        

# Get a word from the UI, a character at a time.
# Click select to complete input, or back out to the left to quit.
# Return the entered word, or None if they back out.
def GetWord():
    lcd.clear()
    lcd.blink()
    sleep(0.75)
    curword = list("A")
    curposition = 0
    while 1:
        if lcd.buttonPressed(lcd.UP):
            if (ord(curword[curposition]) < 127):
                curword[curposition] = chr(ord(curword[curposition])+1)
            else:
                curword[curposition] = chr(32)
        if lcd.buttonPressed(lcd.DOWN):
            if (ord(curword[curposition]) > 32):
                curword[curposition] = chr(ord(curword[curposition])-1)
            else:
                curword[curposition] = chr(127)
        if lcd.buttonPressed(lcd.RIGHT):
            if curposition < DISPLAY_COLS - 1:
                curword.append('A')
                curposition += 1
                lcd.setCursor(curposition, 0)
            sleep(0.75)
        if lcd.buttonPressed(lcd.LEFT):
            curposition -= 1
            if curposition <  0:
                lcd.noBlink()
                return
            lcd.setCursor(curposition, 0)
        if lcd.buttonPressed(lcd.SELECT):
            # return the word
            sleep(0.75)
            return ''.join(curword)
        lcd.home()
        lcd.message(''.join(curword))
        lcd.setCursor(curposition, 0)
        sleep(0.25)

    lcd.noBlink()

# An example of how to get a word input from the UI, and then
# do something with it
def EnterWord():
    if DEBUG:
        print('in EnterWord')
    word = GetWord()
    lcd.clear()
    lcd.home()
    if word is not None:
        lcd.message('>'+word+'<')
        sleep(5)

class CommandToRun:
    def __init__(self, myName, theCommand):
        self.text = myName
        self.commandToRun = theCommand
    def Run(self):
        self.clist = split(commands.getoutput(self.commandToRun), '\n')
        if len(self.clist) > 0:
            lcd.clear()
            lcd.message(self.clist[0])
            for i in range(1, len(self.clist)):
                while 1:
                    if lcd.buttonPressed(lcd.DOWN):
                        break
                    sleep(0.25)
                lcd.clear()
                lcd.message(self.clist[i-1]+'\n'+self.clist[i])          
                sleep(0.5)
        while 1:
            if lcd.buttonPressed(lcd.LEFT):
                break

class Widget:
    def __init__(self, myName, myFunction):
        self.text = myName
        self.function = myFunction
        
class Folder:
    def __init__(self, myName, myParent):
        self.text = myName
        self.items = []
        self.parent = myParent

def HandleSettings(node):
    global lcd
    if node.getAttribute('lcdColor').lower() == 'red':
        LcdRed()
    elif node.getAttribute('lcdColor').lower() == 'green':
        LcdGreen()
    elif node.getAttribute('lcdColor').lower() == 'blue':
        LcdBlue()
    elif node.getAttribute('lcdColor').lower() == 'yellow':
        LcdYellow()
    elif node.getAttribute('lcdColor').lower() == 'teal':
        LcdTeal()
    elif node.getAttribute('lcdColor').lower() == 'violet':
        LcdViolet()
    elif node.getAttribute('lcdColor').lower() == 'white':
        LcdOn()
    if node.getAttribute('lcdBacklight').lower() == 'on':
        LcdOn()
    elif node.getAttribute('lcdBacklight').lower() == 'off':
        LcdOff()

def ProcessNode(currentNode, currentItem):
    children = currentNode.childNodes

    for child in children:
        if isinstance(child, xml.dom.minidom.Element):
            if child.tagName == 'settings':
                HandleSettings(child)
            elif child.tagName == 'folder':
                thisFolder = Folder(child.getAttribute('text'), currentItem)
                currentItem.items.append(thisFolder)
                ProcessNode(child, thisFolder)
            elif child.tagName == 'widget':
                thisWidget = Widget(child.getAttribute('text'), child.getAttribute('function'))
                currentItem.items.append(thisWidget)
            elif child.tagName == 'run':
                thisCommand = CommandToRun(child.getAttribute('text'), child.firstChild.data)
                currentItem.items.append(thisCommand)

class Display:
    def __init__(self, folder):
        self.curFolder = folder
        self.curTopItem = 0
        self.curSelectedItem = 0
    def display(self):
        if self.curTopItem > len(self.curFolder.items) - DISPLAY_ROWS:
            self.curTopItem = len(self.curFolder.items) - DISPLAY_ROWS
        if self.curTopItem < 0:
            self.curTopItem = 0
        if DEBUG:
            print('------------------')
        str = ''
        for row in range(self.curTopItem, self.curTopItem+DISPLAY_ROWS):
            if row > self.curTopItem:
                str += '\n'
            if row < len(self.curFolder.items):
                if row == self.curSelectedItem:
                    cmd = '-'+self.curFolder.items[row].text
                    if len(cmd) < 16:
                        for row in range(len(cmd), 16):
                            cmd += ' '
                    if DEBUG:
                        print('|'+cmd+'|')
                    str += cmd
                else:
                    cmd = ' '+self.curFolder.items[row].text
                    if len(cmd) < 16:
                        for row in range(len(cmd), 16):
                            cmd += ' '
                    if DEBUG:
                        print('|'+cmd+'|')
                    str += cmd
        if DEBUG:
            print('------------------')
        lcd.home()
        lcd.message(str)

    def update(self, command):
        global currentLcd
        global lcdstart
        lcd.backlight(currentLcd)
        lcdstart = datetime.now()
        if DEBUG:
            print('do',command)
        if command == 'u':
            self.up()
        elif command == 'd':
            self.down()
        elif command == 'r':
            self.right()
        elif command == 'l':
            self.left()
        elif command == 's':
            self.select()
    def up(self):
        if self.curSelectedItem == 0:
            return
        elif self.curSelectedItem > self.curTopItem:
            self.curSelectedItem -= 1
        else:
            self.curTopItem -= 1
            self.curSelectedItem -= 1
    def down(self):
        if self.curSelectedItem+1 == len(self.curFolder.items):
            return
        elif self.curSelectedItem < self.curTopItem+DISPLAY_ROWS-1:
            self.curSelectedItem += 1
        else:
            self.curTopItem += 1
            self.curSelectedItem += 1
    def left(self):
        if isinstance(self.curFolder.parent, Folder):
            # find the current in the parent
            itemno = 0
            index = 0
            for item in self.curFolder.parent.items:
                if self.curFolder == item:
                    if DEBUG:
                        print('foundit')
                    index = itemno
                else:
                    itemno += 1
            if index < len(self.curFolder.parent.items):
                self.curFolder = self.curFolder.parent
                self.curTopItem = index
                self.curSelectedItem = index
            else:
                self.curFolder = self.curFolder.parent
                self.curTopItem = 0
                self.curSelectedItem = 0
    def right(self):
        if isinstance(self.curFolder.items[self.curSelectedItem], Folder):
            self.curFolder = self.curFolder.items[self.curSelectedItem]
            self.curTopItem = 0
            self.curSelectedItem = 0
        elif isinstance(self.curFolder.items[self.curSelectedItem], Widget):
            if DEBUG:
                print('eval', self.curFolder.items[self.curSelectedItem].function)
            eval(self.curFolder.items[self.curSelectedItem].function+'()')
        elif isinstance(self.curFolder.items[self.curSelectedItem], CommandToRun):
            self.curFolder.items[self.curSelectedItem].Run()

    def select(self):
        if DEBUG:
            print('check widget')
        if isinstance(self.curFolder.items[self.curSelectedItem], Widget):
            if DEBUG:
                print('eval', self.curFolder.items[self.curSelectedItem].function)
            eval(self.curFolder.items[self.curSelectedItem].function+'()')

# now start things up
uiItems = Folder('root','')

dom = parse(configfile) # parse an XML file by name

top = dom.documentElement

currentLcd = lcd.OFF
LcdOff()
ProcessNode(top, uiItems)

display = Display(uiItems)
display.display()

if DEBUG:
    print('start while')

lcdstart = datetime.now()
while 1:
    if (lcd.buttonPressed(lcd.LEFT)):
       	display.update('l')
        display.display()
        sleep(0.25)

    if (lcd.buttonPressed(lcd.UP)):
        display.update('u')
        display.display()
        sleep(0.25)

    if (lcd.buttonPressed(lcd.DOWN)):
        display.update('d')
        display.display()
        sleep(0.25)

    if (lcd.buttonPressed(lcd.RIGHT)):
        display.update('r')
        display.display()
        sleep(0.25)

    if (lcd.buttonPressed(lcd.SELECT)):
        display.update('s')
        display.display()
        sleep(0.25)

    if AUTO_OFF_LCD:
        lcdtmp = lcdstart + timedelta(seconds=5)
        if (datetime.now() > lcdtmp):
            lcd.backlight(lcd.OFF)

