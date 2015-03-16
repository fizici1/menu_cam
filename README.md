Menu_cam
========

Ce programme fourni un menu qui s'affiche sur la platine LCD 16x2 de Adafruit.
Il est basé sur le projet RaspberryPiLcdMenu.

L'arborescence du menu est décrite dans le fichier lcdmenu.xml.

On peut lancer le script python au démarrage à partir de /etc/init.d en utilisant le fichier init fourni.

Suivre le tuto learn.adafruit.com/adafruits-raspberry-pi-lesson-4-gpio-setup/configuration-i2c

Creer un dossier code

Faire git clone https://github.com/fizici1/menu_cam

Faire git clone https://github.com/adafruit/Adafruit-Raspberry-Pi-Python-Code

Copier Adafruit_I2C.py vers le dossier menu_cam

Copier Adafruit_MCP230xx.py vers le dossier menu_cam

Copier Adafruit_CharLCDPlate.py vers le dossier menu_cam

Faire git clone https://github.com/aufder/RaspberryPiLcdMenu

copier ListSelector.py vers le dossier menu_cam

Faire sudo apt-get install python-smbus

Faire sudo apt-get install python-picamera


Pour lancer le script au démarrage : 

sudo cp lcdmenuinit /etc/init.d

sudo update-rc.d lcdmenuinit defaults

Pour tester faire ensuite :

python lcdmenu.py

David Fontaine

Written by Alan Aufderheide

GPL v3 license, kindly include text above in any redistribution.
