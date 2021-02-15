# coding: utf-8
import codecs
import configparser
import copy
import io
import itertools
import math
import os
import platform
import queue
import socket
import subprocess
import threading
import time
import tkinter.filedialog
import tkinter.font
import tkinter.messagebox
import tkinter.scrolledtext
from operator import itemgetter, attrgetter
from pathlib import Path
from random import *
from tkinter import *
from tkinter.colorchooser import askcolor
from tkinter.ttk import Notebook, Combobox, Progressbar, Style

import csiszaoptions
import manual

try:
    import enchant
    enchantexist = True
    dicthu = enchant.Dict("hu_HU")
except ImportError:
    enchantexist = False

sec = 0
sec1 = 0
c1 = True
turnscore = 0
totalscore = 0
buttonsack = []
board = []
boardoriginal = []
timeractive = False
timesup = False
icon1 = icon2 = None
config = None
tooltipson = False
ruleson1 = 0
notebook = None
tab1 = None
tab2 = None
tab3 = None
tab4 = None
family1 = None
size1 = None
sack = []
sackl = []
players = []
bricks = []
firstmove = True
th_E = None
th_R = None
novalidw = True
fields = []
fieldstemp = []
rackfields = []
frackfields = []
dictionary = []
partsofdictionary = dict()
checkenchant = False
popup1 = None
popup3 = None
popup4 = None
abc = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V',
       'W', 'X', 'Y', 'Z']
abc1 = []
lastword = ''
checktime = False
contiguousletters = []
onthestartfield = False
image11 = None
anchorimage = None
moverack = False
tray = None

class Part:
    """A játéktér területei"""

    def __init__(self, x1, y1, x2, y2):
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2


class Brick:
    """A betűk osztálya"""

    def __init__(self, letterrow):
        self.letter = letterrow.split(',')[0]
        self.count = int(letterrow.split(',')[1])
        self.value = int(letterrow.split(',')[2])
        self.type = letterrow.split(',')[3]
        self.rate = float(letterrow.split(',')[4])
        self.x = -100
        self.y = -100
        self.cx = -100
        self.cy = -100
        self.b1x = -100
        self.b1y = -100
        self.b2x = -100
        self.b2y = -100
        self.objectlist = [None] * 5
        self.changedletter = None
        self.changedvalue = None
        self.multiplier = 1
        self.wordmultiplier = 1
        self.used = False


class Field:
    """A mezők osztálya"""

    def __init__(self, field, value, k, l4):
        self.type = field
        self.value = value
        self.x = l4 * (options.size + options.gap) + 2
        self.y = k * (options.size + options.gap) + 2
        self.cx = self.x + options.size / 2 - 1
        self.cy = self.y + options.size / 2 - 1
        self.changedletter = None
        self.multiplier = 1
        self.wordmultiplier = 1
        self.objectlist = [None] * 5
        self.ignored = False
        self.visible = True
        self.f1x = 0
        self.f1y = 0
        self.f2x = 0
        self.f2y = 0
        self.b1x = 0
        self.b1y = 0
        self.b2x = 0
        self.b2y = 0


class CreateToolTip(object):  # from daniweb.com
    """Leírás megjelenítése"""

    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.widget.bind("<Enter>", self.enter)
        self.widget.bind("<Leave>", self.close)
        self.tw = None

    def enter(self, event=None):
        global tooltipson
        if tooltipson == 0:
            self.tw = False
            return
        x, y, cx, cy = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 15
        y += self.widget.winfo_rooty() + 30
        self.tw = Toplevel(self.widget)
        self.tw.wm_overrideredirect(True)
        self.tw.wm_geometry("+%d+%d" % (x, y))
        label = Label(self.tw, text=self.text, justify='left', highlightthickness=0, background="#00ff00",
                      relief='solid', borderwidth=0, font=("Sans", "10", "normal"))
        label.pack(ipadx=1)

    def close(self, event=None):
        if self.tw:
            self.tw.destroy()


class ThreadReception(threading.Thread):
    """üzenetek fogadását kezelő thread objektum"""

    def __init__(self, conn):
        threading.Thread.__init__(self)
        self.connection = conn  # a kapcsolati socket referenciája
        self.messagebuffer = ''
        self.optionsstr = ''

    def manageoptions(self, optionslist):
        global options
        options.racksize = int(optionslist[0].split(',')[1])
        options.randommultiplier = strtobool(optionslist[1].split(',')[1])
        options.connect = strtobool(optionslist[2].split(',')[1])
        options.startfield = strtobool(optionslist[3].split(',')[1])
        options.startfieldx = int(optionslist[3].split(',')[2])
        options.startfieldy = int(optionslist[3].split(',')[3])
        options.lengthbonus = strtobool(optionslist[4].split(',')[1])
        options.twoletterbonus = int(optionslist[4].split(',')[2])
        options.threeletterbonus = int(optionslist[4].split(',')[3])
        options.fourletterbonus = int(optionslist[4].split(',')[4])
        options.fiveletterbonus = int(optionslist[4].split(',')[5])
        options.sixletterbonus = int(optionslist[4].split(',')[6])
        options.sevenletterbonus = int(optionslist[4].split(',')[7])
        options.eightletterbonus = int(optionslist[4].split(',')[8])
        options.nineletterbonus = int(optionslist[4].split(',')[9])
        options.tenletterbonus = int(optionslist[4].split(',')[10])
        options.oldbonusonly = strtobool(optionslist[5].split(',')[1])
        options.useoldbonus = strtobool(optionslist[5].split(',')[2])
        options.useoldbonusvalue = int(optionslist[5].split(',')[3])
        options.wordperturnbonus = strtobool(optionslist[6].split(',')[1])
        options.wordperturnbonusvalue = int(optionslist[6].split(',')[2])
        options.turnlimit = strtobool(optionslist[7].split(',')[1])
        options.turnlimitcount = int(optionslist[7].split(',')[2])
        options.resetsack = strtobool(optionslist[8].split(',')[1])
        options.resetall = strtobool(optionslist[9].split(',')[1])
        options.randomlettervalue = strtobool(optionslist[10].split(',')[1])
        if options.randomlettervalue:
            options.valuemode = 2
        else:
            options.valuemode = 1
        options.checkdictionary = strtobool(optionslist[11].split(',')[1])
        if options.checkdictionary:
            options.checkmode = 1
        else:
            options.checkmode = 2
        options.dontchangejoker = strtobool(optionslist[12].split(',')[1])
        options.onedirection = strtobool(optionslist[13].split(',')[1])
        options.usefletters = strtobool(optionslist[14].split(',')[1])
        options.fletters = []
        fl = optionslist[14].split(',')[2:]
        for i in range(len(fl) // 5):
            options.fletters.append(",".join(fl[i * 5:(i + 1) * 5]))
        #print("fletters", options.fletters)
        options.valueofchangedletter = strtobool(optionslist[15].split(',')[1])
        options.duplicate = strtobool(optionslist[16].split(',')[1])
        options.timelimit = int(optionslist[17].split(',')[1])
        options.aitimelimit[0] = int(optionslist[18].split(',')[1])
        options.bonusforusingall = strtobool(optionslist[19].split(',')[1])
        options.fixpoint = strtobool(optionslist[20].split(',')[1])
        options.pointforfinish = int(optionslist[21].split(',')[1])
        options.valueforeachletter = strtobool(optionslist[22].split(',')[1])
        options.pointforeachletter = int(optionslist[23].split(',')[1])
        options.penaltyforleft = strtobool(optionslist[24].split(',')[1])
        options.pvalueforeachletter = strtobool(optionslist[25].split(',')[1])
        options.ppointforeachletter = int(optionslist[26].split(',')[1])
        options.independentboards = strtobool(optionslist[27].split(',')[1])
        options.changeincreasepasses = strtobool(optionslist[28].split(',')[1])
        self.optionsstr = ";".join(optionslist)
        if options.resetsack and not options.resetall:
            options.lettersetmode = 2
        elif options.resetsack and options.resetall:
            options.lettersetmode = 3
        else:
            options.lettersetmode = 1

    @staticmethod
    def manageplayers(messagelist):
        global players
        global textbox2
        for i in range(len(messagelist)):
            rec = list()
            rec.append(messagelist[i])
            rec.append(0)
            rec.append(0)
            players.append(rec)
        textbox2.configure(state=NORMAL)
        textbox2.insert('1.0', "Játékosok         Pontszámok\n")
        textbox2.insert('2.0', "----------------------------\n")
        for i in range(len(players)):
            player = players[i][0] + " " * (20 - len(players[i][0]))
            loc = str(i + 3) + '.0'
            loc1 = str(i + 3) + '.19'
            textbox2.insert(loc, player)
            textbox2.insert(loc1, "  0    0\n")
        textbox2.configure(state=DISABLED)

    def managebuffer(self, receivedmessage):
        self.messagebuffer += receivedmessage
        allmessages = []
        while 1:
            position = self.messagebuffer.find("|")
            if position == -1:
                break
            allmessages.append(self.messagebuffer[:position])
            self.messagebuffer = self.messagebuffer[position + 1:]
        return allmessages

    def treatmessage(self, rmessage):
        global bricks
        global board
        global notyourgame
        global options
        global firstmove
        global sack
        global sack1
        global lettersonrack
        global requirechange
        global th_E, th_R
        global turnscore
        global turns
        global currentplayer
        global novalidw
        global ok1
        global sec
        global textbox1
        global numberofplayers
        global wanttochange

        def booltostr(boolvar):
            if boolvar:
                return "1"
            else:
                return "0"

        nopponents = 1
        messagelist = rmessage.split(',')
        if messagelist[0] == "NOGAME":
            boardstr = boardtostr()
            sackstr = sacktostr()
            bricksstr = brickstostring()
            optionsstr = "OPTIONS;RACKSIZE," + str(options.racksize) + ";RANDOMMPL," + booltostr(
                options.randommultiplier) + ";CONNECT," + booltostr(options.connect) + ";STARTFIELD," + booltostr(
                options.startfield) + "," + str(options.startfieldx) + "," + str(
                options.startfieldy) + ";LENGTHB," + booltostr(options.lengthbonus) + "," + str(
                options.twoletterbonus) + "," + str(options.threeletterbonus) + "," + str(
                options.fourletterbonus) + "," + str(options.fiveletterbonus) + "," + str(
                options.sixletterbonus) + "," + str(options.sevenletterbonus) + "," + str(
                options.eightletterbonus) + "," + str(options.nineletterbonus) + "," + str(
                options.tenletterbonus) + ";OLDBONUSONLY," + booltostr(options.oldbonusonly) + "," + booltostr(
                options.useoldbonus) + "," + str(options.useoldbonusvalue) + ";WORDPERTURNBONUS," + booltostr(
                options.wordperturnbonus) + "," + str(options.wordperturnbonusvalue) + ";TURNLIMIT," + booltostr(
                options.turnlimit) + "," + str(options.turnlimitcount) + ";RESETSACK," + booltostr(
                options.resetsack) + ";RESETALL," + booltostr(options.resetall) + ";RANDOMLVALUE," + booltostr(
                options.randomlettervalue) + ";CHECKDICT," + booltostr(
                options.checkdictionary) + ";DONTCHANGEJ," + booltostr(
                options.dontchangejoker) + ";ONEDIRECTION," + booltostr(
                options.onedirection) + ";FIXLETTERS," + booltostr(options.usefletters) + "," + ",".join(
                options.fletters) + ";VALUEOFCHANGEDL," + booltostr(
                options.valueofchangedletter) + ";DUPLICATE," + booltostr(options.duplicate) + ";TIMELIMIT," + str(
                options.timelimit) + ";AITIMELIMIT," + str(options.aitimelimit[0]) + ";BONUSFORUSINGALL," + booltostr(
                options.bonusforusingall) + ";FIXPOINT," + booltostr(options.fixpoint) + ";POINTFORFINISH," + str(
                options.pointforfinish) + ";VALUEFOREACHLETTER," + booltostr(
                options.valueforeachletter) + ";POINTFOREACHLETTER," + str(
                options.pointforeachletter) + ";PENALTYFORLEFT," + booltostr(
                options.penaltyforleft) + ";PVALUEFOREACHLETTER," + booltostr(
                options.pvalueforeachletter) + ";PPOINTFOREACHLETTER," + str(
                options.ppointforeachletter) + ";INDEPENDENTBOARDS," + booltostr(
                options.independentboards) + ";CHANGEINCREASEPASSES," + booltostr(
                options.changeincreasepasses) + ";LIMITEDVISIBILITY," + booltostr(
                options.limitedvisibility) + ";OPTIMIZEDDRAW," + booltostr(
                options.optimizeddraw) + ";RESETFRACK," + booltostr(
                options.resetfrack) + ";CHECKATTHEEND," +booltostr(
                options.checkattheend)
            if options.gamemode == 2:
                nopponents = options.aiopponent
            if options.gamemode == 3:
                nopponents = options.networkopponent
            # print("sent: LAUNCH," + options.username + ";" + boardstr + ";" + sackstr + ";" + str(nopponents + 1))
            self.connection.send(("LAUNCH," + options.username + ";" + boardstr + ";" + sackstr + ";" + bricksstr + ";" + str(
                nopponents + 1) + ";" + optionsstr + "|").encode())
            chatboxmessage("Új játékot indítottál\n")
        elif messagelist[0] == "GAMEEXIST":
            notyourgame = True
            self.connection.send(("NAME," + options.username + "|").encode())
        elif messagelist[0] == "NUMOFPLAYERS":
            numberofplayers = int(messagelist[1])
        elif messagelist[0] == "OK":
            chatboxmessage("Csatlakoztál egy játékhoz\n")
        elif messagelist[0] == "INUSE":
            errormessage(options.username + " név már használatban van. Válassz egy másikat!", appwin)
        elif messagelist[0][:7] == "OPTIONS":
            optionslist = rmessage.split(';')
            self.manageoptions(optionslist[1:])
        elif messagelist[0] == "BOARD":
            strtoboard(messagelist)
        elif messagelist[0] == "SACK":
            sack = listtobrick(messagelist[1:])
            sack1 = sack[:]
            for i in range(len(sack)):
                sackl.append([sack[i].letter, sack[i].value, sack[i].wordmultiplier])
        elif messagelist[0] == "ABCLETTERS":
            bricks = listtobrick(messagelist[1:])
        elif messagelist[0] == "LETTERSONRACK":
            lettersonrack = takenewfromsack(messagelist[2:])
        elif messagelist[0] == "START":
            if notyourgame:
                canvas1.delete("all")
                init2()
                drawboard()
            showrack(lettersonrack)
            if options.usefletters:
                loadfrack()
            if not options.duplicate:
                lockon()
        elif messagelist[0] == "PLAYERS":
            self.manageplayers(messagelist[1:])
        elif messagelist[0] == "TURN":
            ok1 = False
            turns = int(messagelist[1])
            counter.config(state="normal", text=str(turns + 1))
            turnscore = 0
            score1.config(text=str(turnscore))
            if options.duplicate:
                starttimer()
            else:
                chatboxmessage("Te következel!\n")
                starttimer()
            self.connection.send("OK|".encode())
            repairboard()
            bind1()
            lockoff()
            printrack()
        elif messagelist[0] == "NEXT":
            starttimer()
            currentplayer = messagelist[1]
            markcurrentplayer()
            chatboxmessage(messagelist[1] + " következik\n")
        elif messagelist[0] == "MOVE":
            self.connection.send("OK|".encode())
            wanttochange = []
            back()
            placeletters(rmessage)
        elif messagelist[0][:5] == "SCORE":
            showscore1(rmessage)
        elif messagelist[0] == "NEWLETTERS":
            if options.resetsack and not options.duplicate:
                time.sleep(2)                                    #összeakadna egyébként az endmove() függvénnyel
            if options.independentboards and novalidw:
                back()
                endmove(lettersonrack)
            newletters = takenewfromsack(messagelist[2:])
            if len(newletters) > 0:
                showrack(newletters)
            if options.duplicate:
                lockoff()
            lettersonrack = ""
            for i in range(len(rack)):
                if rack[i] is not None:
                    lettersonrack += rack[i].letter + " "
            novalidw = True
        elif messagelist[0] == "DUPSWAP":
            back()
            if requirechange:
                finishdupswap()
                requirechange = False
            else:
                ifnovalidmove()
            newletters = takenewfromsack(messagelist[2:])
            newletterss = []
            for i in newletters:
                newletterss.append(i.letter)
            # print("newletterss", newletterss)
            showrack(newletters)
            lockoff()
        elif rmessage == "END":
            endofgame()
        elif rmessage == "TIMEOUT":
            lockon()
            back()
            try:
                popup1.destroy()
            except (NameError, AttributeError):
                pass
        elif messagelist[0] == "CHAT":
            chatboxmessage("".join(messagelist[1:]), "chat")
        else:
            chatboxmessage(rmessage)

    def run(self):
        while 1:
            receivedmessage = self.connection.recv(3064).decode()
            # print("received:", receivedmessage)
            if receivedmessage == "":
                print("Megszakadt a kapcsolat a szerverrel")
                break
            allmessages = self.managebuffer(receivedmessage)
            for rmessage in allmessages:
                self.treatmessage(rmessage)
        print("Leállt a kliens. Kapcsolat megszakítva.")
        self.connection.close()


class ThreadEmission(threading.Thread):
    """üzenetek kibocsátását kezelő thread objektum"""

    def __init__(self, conn, q):
        threading.Thread.__init__(self)
        self.connection = conn
        self.start1 = True
        self.q = q

    def run(self):

        while 1:
            time.sleep(0.1)
            if not self.q.empty():
                qvar = self.q.get()
                if qvar == "TRUE":
                    self.connection.send("GAME|".encode())
                else:
                    try:
                        self.connection.send((qvar + "|").encode())
                    except IOError:
                        print("Nincs kapcsolat")


def strtoboard(messagelist):
    global board
    global fieldrc, fieldcc
    board = []
    fieldrc = int(messagelist[1])
    fieldcc = int(messagelist[2])
    for i in range(fieldrc):
        board.append(messagelist[3 + i * fieldcc:3 + (i + 1) * fieldcc])


def boardtostr():
    #global board
    message1 = "BOARD" + "," + str(len(board)) + "," + str(len(board[0]))
    for i in range(len(board)):
        for j in range(len(board[0])):
            message1 += ","
            message1 += str(board[i][j])
    return message1


def sacktostr():
    #global sack
    global sackl
    letters1 = []
    for brck in sack:
        letters1.append(",".join([brck.letter, str(brck.value), "1",brck.type]))
        sackl.append([brck.letter, brck.value, brck.wordmultiplier])
    message1 = ",".join(["LETTERS", ",".join(letters1)])
    return message1


def brickstostring():
    letters1 = []
    for brck in bricks:
        letters1.append(",".join([brck.letter, str(brck.value), "1", brck.type]))
    message1 = ",".join(["ABCLETTERS", ",".join(letters1)])
    return message1

def strtobool(strg):
    if strg == "1":
        return True
    else:
        return False


def listtobrick(letterlist):
    global sackl

    letterbricks = []
    i = 0
    while i < len(letterlist):
        letterrow = ",".join([letterlist[i], "1", letterlist[i + 1], "", "0"])
        letterbricks.append(Brick(letterrow))
        for j in range(len(sackl)):
            if sackl[j][0] == letterbricks[-1].letter:
                if sackl[j][1] != 0:
                    letterbricks[-1].multiplier = int(letterlist[i + 1]) // sackl[j][1]
                else:
                    letterbricks[-1].multiplier = 1
                break
        letterbricks[-1].wordmultiplier = int(letterlist[i + 2])
        i += 4
    return letterbricks


def new1():
    """Új játék kiválasztása"""
    options.lastopenedcfg = tkinter.filedialog.askopenfilename(initialdir=".", title="Válaszd ki a kívánt fájlt",
                                                               filetypes=(
                                                                   ("Konfigurációs fájlok", "*.cfg"),
                                                                   ("all files", "*.*")))
    if options.lastopenedcfg == "":
        return
    menubar.entryconfig("Beállítások", state="normal")
    button4.configure(state="normal")
    button6.configure(state="disabled")
    canvas1.delete("all")
    init1()
    init2()
    options.createfieldsdict()
    drawboard()


def save1():
    """Játék mentése fájlba (csak egyszemélyes játékban)"""
    global options
    # Jelenlegi konfigurációs beállítások másolása
    cstr = io.StringIO()
    config.write(cstr)
    cstr.seek(0)
    saveg = configparser.ConfigParser()
    saveg.read_file(cstr)
    saveg.set('Rules', 'racksize', str(options.racksize))
    saveg.set('Rules', 'turnlimit', str(options.turnlimit))
    saveg.set('Rules', 'turnlimitcount', str(options.turnlimitcount))
    saveg.set('Rules', 'changeincreasepasses', str(options.changeincreasepasses))
    saveg.set('Rules', 'timelimit', str(options.timelimit))
    saveg.set('Rules', 'duplicate', str(options.duplicate))
    saveg.set('Rules', 'independentboards', str(options.independentboards))
    saveg.set('Rules', 'randommultiplier', str(options.randommultiplier))
    mvaluesstr = ",".join(str(v) for v in options.mvalues)
    saveg.set('Rules', 'mvalues', mvaluesstr)
    saveg.set('Rules', 'connect', str(options.connect))
    saveg.set('Rules', 'startfield', str(options.startfield))
    saveg.set('Rules', 'startfieldx', str(options.startfieldx))
    saveg.set('Rules', 'startfieldy', str(options.startfieldy))
    saveg.set('Rules', 'resetsack', str(options.resetsack))
    saveg.set('Rules', 'resetall', str(options.resetall))
    saveg.set('Rules', 'randomlettervalue', str(options.randomlettervalue))
    valuesstr = ",".join(str(v) for v in options.values)
    saveg.set('Rules', 'values', valuesstr)
    saveg.set('Rules', 'checkdictionary', str(options.checkdictionary))
    saveg.set('Rules', 'dontchangejoker', str(options.dontchangejoker))
    saveg.set('Rules', 'onedirection', str(options.onedirection))
    saveg.set('Rules', 'usefletters', str(options.usefletters))
    flettersstr = "\n" + "\n".join(options.fletters)
    saveg.set('Rules', 'fletters', flettersstr)
    saveg.set('Rules', 'valueofchangedletter', str(options.valueofchangedletter))
    saveg.set('Rules', 'limitedvisibility', str(options.limitedvisibility))
    saveg.set('Rules', 'optimizeddraw', str(options.optimizeddraw))
    saveg.set('Rules', 'resetfrack', str(options.resetfrack))
    saveg.set('Rules', 'checkattheend', str(options.checkattheend))
    saveg.set('Bonuses', 'lengthbonus', str(options.lengthbonus))
    saveg.set('Bonuses', 'twoletterbonus', str(options.twoletterbonus))
    saveg.set('Bonuses', 'threeletterbonus', str(options.threeletterbonus))
    saveg.set('Bonuses', 'fourletterbonus', str(options.fourletterbonus))
    saveg.set('Bonuses', 'fiveletterbonus', str(options.fiveletterbonus))
    saveg.set('Bonuses', 'sixletterbonus', str(options.sixletterbonus))
    saveg.set('Bonuses', 'sevenletterbonus', str(options.sevenletterbonus))
    saveg.set('Bonuses', 'eightletterbonus', str(options.eightletterbonus))
    saveg.set('Bonuses', 'nineletterbonus', str(options.nineletterbonus))
    saveg.set('Bonuses', 'tenletterbonus', str(options.tenletterbonus))
    saveg.set('Bonuses', 'wordlengthbonus', str(options.wordlengthbonus))
    saveg.set('Bonuses', 'wordtwoletterbonus', str(options.wordtwoletterbonus))
    saveg.set('Bonuses', 'wordthreeletterbonus', str(options.wordthreeletterbonus))
    saveg.set('Bonuses', 'wordfourletterbonus', str(options.wordfourletterbonus))
    saveg.set('Bonuses', 'worfiveletterbonus', str(options.wordfiveletterbonus))
    saveg.set('Bonuses', 'wordsixletterbonus', str(options.wordsixletterbonus))
    saveg.set('Bonuses', 'wordsevenletterbonus', str(options.wordsevenletterbonus))
    saveg.set('Bonuses', 'wordeightletterbonus', str(options.wordeightletterbonus))
    saveg.set('Bonuses', 'wordnineletterbonus', str(options.wordnineletterbonus))
    saveg.set('Bonuses', 'wordtenletterbonus', str(options.wordtenletterbonus))
    saveg.set('Bonuses', 'oldbonusonly', str(options.oldbonusonly))
    saveg.set('Bonuses', 'useoldbonus', str(options.useoldbonus))
    saveg.set('Bonuses', 'useoldbonusvalue', str(options.useoldbonusvalue))
    saveg.set('Bonuses', 'wordperturnbonus', str(options.wordperturnbonus))
    saveg.set('Bonuses', 'wordperturnbonusvalue', str(options.wordperturnbonusvalue))
    saveg.set('Bonuses', 'bonusforusingall', str(options.bonusforusingall))
    saveg.set('Bonuses', 'fixpoint', str(options.fixpoint))
    saveg.set('Bonuses', 'pointforfinish', str(options.pointforfinish))
    saveg.set('Bonuses', 'valueforeachletter', str(options.valueforeachletter))
    saveg.set('Bonuses', 'pointforeachletter', str(options.pointforeachletter))
    saveg.set('Bonuses', 'penaltyforleft', str(options.penaltyforleft))
    saveg.set('Bonuses', 'pvalueforeachletter', str(options.pvalueforeachletter))
    saveg.set('Bonuses', 'ppointforeachletter', str(options.ppointforeachletter))
    boardtext = ['.'] * len(board)
    for v in range(len(board)):
        boardtext[v] = " ".join(board[v])
    board10 = "\n"
    board11 = "\n".join(boardtext)
    board10 += board11
    saveg.set('Board', 'board', board10)
    for v in range(len(boardoriginal)):
        boardtext[v] = " ".join(boardoriginal[v])
    board10 = "\n"
    board11 = "\n".join(boardtext)
    board10 += board11
    saveg.set('Board', 'boardoriginal', board10)
    boardsaveletter = []
    boardsavevalue = []
    boardsavemultiplier = []
    boardsavewordmultiplier = []
    for i in range(fieldrc):
        boardsavelline = []
        boardsavevline = []
        boardsavemline = []
        boardsavewmline = []
        for j in range(fieldcc):
            boardsavelline.append(fields[i][j].type)
            boardsavevline.append(str(fields[i][j].value))
            boardsavemline.append(str(fields[i][j].multiplier))
            boardsavewmline.append(str(fields[i][j].wordmultiplier))
        boardsaveletter.append(" ".join(boardsavelline))
        boardsavevalue.append(" ".join(boardsavevline))
        boardsavemultiplier.append(" ".join(boardsavemline))
        boardsavewordmultiplier.append(" ".join(boardsavewmline))
    board10 = "\n"
    board11 = "\n".join(boardsaveletter)
    board10 += board11
    saveg.set('Board', 'savedboardletters', board10)
    board10 = "\n"
    board11 = "\n".join(boardsavevalue)
    board10 += board11
    saveg.set('Board', 'savedboardvalues', board10)
    board10 = "\n"
    board11 = "\n".join(boardsavemultiplier)
    board10 += board11
    saveg.set('Board', 'savedboardmultipliers', board10)
    board10 = "\n"
    board11 = "\n".join(boardsavewordmultiplier)
    board10 += board11
    saveg.set('Board', 'savedboardwordmultipliers', board10)
    lor = []
    for b in rack:
        if b is not None:
            lor.append(",".join(
                [b.letter, '1', str(b.value), str(b.type), str(b.rate), str(b.multiplier), str(b.wordmultiplier)]))
    rackstr = "\n" + "\n".join(lor)
    saveg.set('Board', 'savedrack', rackstr)
    if options.usefletters:
        lor = []
        for b in frack:
            lor.append(",".join(
                [b.letter, '1', str(b.value), str(b.type), str(b.rate), str(b.multiplier), str(b.wordmultiplier)]))
        frackstr = "\n" + "\n".join(lor)
        saveg.set('Board', 'savedfrack', frackstr)
    lor = []
    for b in sack1:
        if b.used:
            used = '1'
        else:
            used = '0'
        lor.append(",".join([b.letter, '1', str(b.value), str(b.type), str(b.rate), used]))
    sackstr = "\n" + "\n".join(lor)
    saveg.set('Board', 'savedsack', sackstr)
    saveg.set('Board', 'turns', str(turns))
    saveg.set('Board', 'passes', str(countofpasses))
    saveg.set('Board', 'turnscore', str(turnscore))
    saveg.set('Board', 'totalscore', str(totalscore))
    saveg.set('Appearance', 'size', str(options.size))
    saveg.set('Appearance', 'bricksize', str(options.size))
    saveg.set('Appearance', 'gap', str(options.gap))
    saveg.set('Appearance', 'colornormal', options.colornormal)
    saveg.set('Appearance', 'colorfix', options.colorfix)
    saveg.set('Appearance', 'colordoublel', options.colordoubleL)
    saveg.set('Appearance', 'colortriplel', options.colortripleL)
    saveg.set('Appearance', 'colordoublew', options.colordoubleW)
    saveg.set('Appearance', 'colortriplew', options.colortripleW)
    saveg.set('Appearance', 'colorwall', options.colorwall)
    saveg.set('Appearance', 'colorborder', options.colorborder)
    saveg.set('Appearance', 'colortext', options.colortext)
    saveg.set('Appearance', 'colornormalbrick', options.colornormalbrick)
    saveg.set('Appearance', 'colordoublebrick', options.colordoublebrick)
    saveg.set('Appearance', 'colortriplebrick', options.colortriplebrick)
    saveg.set('Appearance', 'colordoublewordbrick', options.colordoublewordbrick)
    saveg.set('Appearance', 'colortriplewordbrick', options.colortriplewordbrick)
    saveg.set('Appearance', 'colorborderbrick', options.colorborderbrick)
    saveg.set('Appearance', 'colortextbrick', options.colortextbrick)
    saveg.set('Appearance', 'colorvaluebrick', options.colorvaluebrick)
    saveg.set('Appearance', 'colorchangedbrick', options.colorchangedbrick)
    saveg.set('Appearance', 'fborder', str(options.fborder))
    saveg.set('Appearance', 'bborder', str(options.bborder))
    # Mentés fájlba
    options.lastsavedgame = tkinter.filedialog.asksaveasfilename(initialdir=".", title="Játékállás  mentése fájlba",
                                                                 filetypes=(
                                                                     ("Mentett játékok ", "*.sav"),
                                                                     ("all files", "*.*")))
    with open(options.lastsavedgame, 'w', encoding="utf8") as savegame:
        saveg.write(savegame)


def load1():
    """Mentett játék betöltése fájlból"""
    global rack, frack
    global frackdict
    global turns
    global turnscore
    global totalscore
    global firstmove
    global options
    global sack, sack1
    global countofpasses
    global sec, sec1, c1
    global boardoriginal
    options.lastopenedcfg = tkinter.filedialog.askopenfilename(initialdir=".", title="Válaszd ki a kívánt mentést",
                                                               filetypes=(
                                                                   ("Mentett játékok", "*.sav"), ("all files", "*.*")))
    if options.lastopenedcfg == "":
        return
    menubar.entryconfig("Beállítások", state="disabled")
    button4.configure(state="normal")
    canvas1.delete("all")
    init1()
    init2()
    options.createfieldsdict()
    drawboard()
    # Mentett tábla visszaállítása
    boardos = config.get('Board', 'boardoriginal')
    fields1l = config.get('Board', 'savedboardletters')
    fields1v = config.get('Board', 'savedboardvalues')
    fields1m = config.get('Board', 'savedboardmultipliers')
    fields1wm = config.get('Board', 'savedboardwordmultipliers')
    boardoss = boardos.splitlines()
    fieldrowsl = fields1l.splitlines()
    fieldrowsv = fields1v.splitlines()
    fieldrowsm = fields1m.splitlines()
    fieldrowswm = fields1wm.splitlines()
    r = len(fieldrowsl)
    boardoriginal = []
    saveboardletters = []
    saveboardvalues = []
    saveboardmultipliers = []
    saveboardwordmultipliers = []
    for b in range(1, r):
        boardol = boardoss[b].split(' ')
        boardoriginal.append(boardol)
        fields2 = fieldrowsl[b].split(' ')
        saveboardletters.append(fields2)
        fields2 = fieldrowsv[b].split(' ')
        saveboardvalues.append(fields2)
        fields2 = fieldrowsm[b].split(' ')
        saveboardmultipliers.append(fields2)
        fields2 = fieldrowswm[b].split(' ')
        saveboardwordmultipliers.append(fields2)
    for i in range(fieldrc):
        for j in range(fieldcc):
            if board[i][j] != saveboardletters[i][j]:
                c2 = None
                if fields[i][j].type != '.':
                    c2 = options.fieldsdict[fields[i][j].type][0]
                fields[i][j].type = saveboardletters[i][j]
                fields[i][j].value = int(saveboardvalues[i][j])
                fields[i][j].multiplier = int(saveboardmultipliers[i][j])
                fields[i][j].wordmultiplier = int(saveboardwordmultipliers[i][j])
                c, bc = colors1(fields[i][j])
                canvas1.create_rectangle(fields[i][j].b1x, fields[i][j].b1y, fields[i][j].b2x, fields[i][j].b2y,
                                         width=1, fill=c, outline=bc)
                canvas1.create_text(fields[i][j].cx, fields[i][j].cy + 2,
                                    font=(options.letterfont, options.letterfontsize), text=fields[i][j].type,
                                    fill=options.colortextbrick)
                canvas1.create_text(fields[i][j].b1x + options.wx, fields[i][j].b1y + options.wy,
                                    font=(options.valuefont, options.valuefontsize), text=fields[i][j].value,
                                    fill=options.colorvaluebrick)
                if c2 is not None:
                    canvas1.create_polygon((fields[i][j].b2x - 9, fields[i][j].b1y, fields[i][j].b2x + 1,
                                            fields[i][j].b1y, fields[i][j].b2x, fields[i][j].b1y + 9), fill=c2)
                    canvas1.create_line(fields[i][j].b2x - 9, fields[i][j].b1y, fields[i][j].b2x, fields[i][j].b1y + 9,
                                        fill=bc)
    # Zsák visszaállítása
    sackstr = config.get('Board', 'savedsack')
    letterrows = sackstr.splitlines()
    sack = []
    sack1 = []
    for letterrow in letterrows[1:]:
        letterbrick = Brick(letterrow)
        if letterrow.split(',')[5] == '1':
            letterbrick.used = True
            sack1.append(letterbrick)
        else:
            letterbrick.used = False
            sack1.append(letterbrick)
            sack.append(letterbrick)
    # Tartón levő betűk visszaállítása
    rackstr = config.get('Board', 'savedrack')
    letterrows = rackstr.splitlines()
    rack = []
    for letterrow in letterrows[1:]:
        for letterbrick in sack1:
            if letterbrick.letter == letterrow.split(',')[0] and letterbrick.used and letterbrick not in rack:
                letterbrick.multiplier = int(letterrow[-3])
                letterbrick.wordmultiplier = int(letterrow[-1])
                rack.append(letterbrick)
                break
    for j in range(options.racksize):
        if j == len(rack):
            rack.append(None)
            continue
        rack[j].x = rackfields[j].x
        rack[j].y = rackfields[j].y
        rack[j].cx = rackfields[j].cx
        rack[j].cy = rackfields[j].cy
        rack[j].b1x = rackfields[j].b1x
        rack[j].b1y = rackfields[j].b1y
        rack[j].b2x = rackfields[j].b2x
        rack[j].b2y = rackfields[j].b2y
        c, bc = colors1(rack[j])
        rack[j].objectlist[0] = canvas1.create_rectangle(rackfields[j].b1x, rackfields[j].b1y, rackfields[j].b2x,
                                                         rackfields[j].b2y, width=1, fill=c, outline=bc, tags=str(j))
        rack[j].objectlist[1] = canvas1.create_text(rackfields[j].cx, rackfields[j].cy + 2,
                                                    font=(options.letterfont, options.letterfontsize),
                                                    text=rack[j].letter, fill=options.colortextbrick, tags=str(j))
        rack[j].objectlist[2] = canvas1.create_text(rackfields[j].b1x + options.wx, rackfields[j].b1y + options.wy,
                                                    font=(options.valuefont, options.valuefontsize), text=rack[j].value,
                                                    fill=options.colorvaluebrick, tags=str(j))
        canvas1.addtag_withtag('racks', rack[j].objectlist[0])
        canvas1.addtag_withtag('racks', rack[j].objectlist[1])
        canvas1.addtag_withtag('racks', rack[j].objectlist[2])
        rackfields[j].type = "occupied"
    # Fix betűk visszaállítása
    if options.usefletters:
        frackdict = dict()
        frackstr = config.get('Board', 'savedfrack')
        letterrows = frackstr.splitlines()
        frack = []
        for letterrow in letterrows[1:]:
            letterbrick = Brick(letterrow)
            frack.append(letterbrick)
        for j in range(len(frack)):
            for k in range(len(frackfields)):
                if frack[j].letter == options.fletters[k].split(",")[0]:
                    found = False
                    for jj in range(len(frack)):
                        if frack[jj].x == frackfields[k].x:
                            found = True
                            break
                    if found:
                        continue
                    frackdict[frack[j]] = frackfields[k]
                    frack[j].x = frackfields[k].x
                    frack[j].y = frackfields[k].y
                    frack[j].cx = frackfields[k].cx
                    frack[j].cy = frackfields[k].cy
                    frack[j].b1x = frackfields[k].b1x
                    frack[j].b1y = frackfields[k].b1y
                    frack[j].b2x = frackfields[k].b2x
                    frack[j].b2y = frackfields[k].b2y
                    c = options.colornormalbrick
                    if options.bborder:
                        bc = options.colorborderbrick
                    else:
                        bc = c
                    frack[j].objectlist[0] = canvas1.create_rectangle(frack[j].b1x, frack[j].b1y, frack[j].b2x,
                                                                      frack[j].b2y, width=1, fill=c, outline=bc,
                                                                      tags=str(j))
                    frack[j].objectlist[1] = canvas1.create_text(frack[j].cx, frack[j].cy + 2,
                                                                 font=(options.letterfont, options.letterfontsize),
                                                                 text=frack[j].letter, fill=options.colortextbrick,
                                                                 tags=str(j))
                    frack[j].objectlist[2] = canvas1.create_text(frack[j].b1x + options.wx, frack[j].b1y + options.wy,
                                                                 font=(options.valuefont, options.valuefontsize),
                                                                 text=frack[j].value, fill=options.colorvaluebrick,
                                                                 tags=str(j))
                    canvas1.addtag_withtag('racks', frack[j].objectlist[0])
                    canvas1.addtag_withtag('racks', frack[j].objectlist[1])
                    canvas1.addtag_withtag('racks', frack[j].objectlist[2])
                    break
    # Forduló száma
    turns = int(config.get('Board', 'turns'))
    if turns > 0:
        firstmove = False
    counter.config(text=str(turns))
    # Passzok száma
    countofpasses = int(config.get('Board', 'passes'))
    # Pontszám
    totalscore = int(config.get('Board', 'totalscore'))
    button2.configure(state="normal")
    fb2.configure(state="normal")
    button3.configure(state="normal")
    fb3.configure(state="normal")
    if options.gamemode != 1:
        button4.configure(state="disabled")
    counter.config(state="normal")
    score1.config(state="normal")
    score2.config(state="normal")
    timer.config(state="normal")
    button0.config(state="normal")
    fb0.config(state="normal")
    button1.config(state="normal")
    fb1.config(state="normal")
    checkb1.config(state="normal")
    checkb2.config(state="normal")
    score2.config(text=str(totalscore))
    bind1()
    button6.configure(state="normal", text="Szünet")
    c1 = True
    starttimer()
    chatboxmessage("A mentett játék betöltése kész\n")
    menubar.entryconfig("Beállítások", state="disabled")
    if options.checkattheend:
        options.checkmode = 4


def start():
    """Kiválasztott játék indítása"""
    global button4, button6
    global players
    global textbox2

    def startserver():
        global servproc
        try:
            servproc = subprocess.Popen([interpreter, "csiszaserver.py"])
            # servproc = subprocess.Popen(["./csiszaserver"])
        except IOError:
            pass

    def startaiclient(i):
        global aiclientprocl
        lim = "2"
        if options.aidictionarylimited[i] == "Minden szó":
            lim = "0"
        elif options.aidictionarylimited[i] == "40000 >":
            lim = "1"
        try:
            # aiclientproc = subprocess.Popen("./csiszaaiclient " + str(options.aitimelimit[i]) +
            #                                " " + lim + " " + str(options.aistrength[i]) + " " +
            #                                " ".join(options.wordlengthlist[i]), shell=True)
            aiclientproc = subprocess.Popen(interpreter + " csiszaaiclient.py " + str(options.aitimelimit[i]) +
                                            " " + lim + " " + str(options.aistrength[i]) + " " +
                                            " ".join(options.wordlengthlist[i]), shell = True)
            aiclientprocl.append(aiclientproc)
        except IOError:
            pass


    if options.gamemode == 1:
        if not tkinter.messagebox.askokcancel("Játék újrakezdése",
                                              "Valóban újra akarod kezdeni a játékot a jelenlegi beállításokkal?"):
            return
        filem.entryconfig("Játék mentése", state="normal")
        filem.entryconfig("Játék betöltése", state="normal")
        init2()
    else:
        filem.entryconfig("Játék mentése", state="disabled")
        filem.entryconfig("Játék betöltése", state="disabled")
    canvas1.delete("all")
    drawboard()
    menubar.entryconfig("Beállítások", state="disabled")
    if options.gamemode != 1:
        button4.configure(state="disabled")
    score1.config(state="normal")
    score2.config(state="normal")
    timer.config(state="normal")
    button0.config(state="normal")
    fb0.config(state="normal")
    button1.config(state="normal")
    fb1.config(state="normal")
    if not options.independentboards:
        button2.config(state="normal")
        fb2.config(state="normal")
    button3.config(state="normal")
    fb3.config(state="normal")
    if options.duplicate and options.gamemode != 1:
        button3a.config(state="normal")
        fb3a.config(state="normal")
    checkb1.config(state="normal")
    checkb2.config(state="normal")
    if options.gamemode == 1:
        button6.configure(state="normal")
        counter.config(state="normal", text=str(turns + 1))
        players = []
        textbox2.configure(state=NORMAL)
        textbox2.delete('1.0', END)
        textbox2.configure(state=DISABLED)
        if options.usefletters:
            loadfrack()
        loadrack()
        bind1()
        starttimer()
        chatboxmessage("Új játékot indítottál\n")
        if options.checkattheend:
            options.checkmode = 4
    elif options.gamemode == 2:
        askname()
        ts = threading.Thread(target=startserver)
        ts.daemon = True
        ts.start()
        time.sleep(1)
        players = []
        textbox2.configure(state=NORMAL)
        textbox2.delete('1.0', END)
        textbox2.configure(state=DISABLED)
        connect1()
        time.sleep(0.5)
        for i in range(options.aiopponent):
            ts = threading.Thread(target=startaiclient, args=[i])
            ts.daemon = True
            ts.start()
            time.sleep(0.1)
    elif options.gamemode == 3:
        askname()
        players = []
        textbox2.configure(state=NORMAL)
        textbox2.delete('1.0', END)
        textbox2.configure(state=DISABLED)
        connect1()


def connect1():
    global th_E, th_R
    global queue1
    connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        connection.connect((options.host, options.port))
    except socket.error:
        print("Nem sikerült kapcsolódni")
        tkinter.messagebox.showerror("Hiba", "Nem sikerült kapcsolódni", parent=appwin)
        return
    print("A kapcsolat létrejött a szerverrel.")
    queue1 = queue.Queue()
    th_E = ThreadEmission(connection, queue1)
    th_R = ThreadReception(connection)
    th_E.start()
    th_R.start()
    time.sleep(2)
    queue1.put("TRUE")


def quit1():
    """Kilépés a programból"""
    global queue1
    global th_E
    global servproc
    global aiclientprocl
    if options.gamemode == 1:
        if not tkinter.messagebox.askokcancel("Kilépés", "Valóban el akarod hagyni a programot?"):
            return
        appwin.destroy()
        sys.exit()
    elif options.gamemode == 2:
        if not tkinter.messagebox.askokcancel("Kilépés", "Valóban el akarod hagyni a programot?"):
            return
        queue1.put("END")
        subprocess.Popen.terminate(servproc)
        for aiproc in aiclientprocl:
            try:
                subprocess.Popen.terminate(aiproc)
            except OSError:
                pass
        time.sleep(2)
        appwin.destroy()
        os._exit(1)
    elif options.gamemode == 3:
        if not tkinter.messagebox.askokcancel("Kilépés", "Valóban el akarod hagyni a programot?"):
            return
        queue1.put("END")
        time.sleep(1)
        appwin.destroy()
        os._exit(1)


def askname():
    """Játékos nevének bekérése"""

    def username1(event):
        global options
        options.username = var001.get()
        options.host = var002.get()
        options.port = int(var003.get())
        popup10.destroy()

    popup10 = Toplevel()
    popup10.transient(appwin)
    popup10.title("Név megadása")

    lab1 = Label(popup10, text="Neved a játékban:")
    lab1.grid(row=0, column=0, padx=10, pady=10)

    var001 = StringVar()
    var001.set(options.username)
    var002 = StringVar()
    var002.set(options.host)
    var003 = StringVar()
    var003.set(options.port)

    entry001 = Entry(popup10, width=10, bg="white", relief=SUNKEN, textvariable=var001)
    entry001.grid(row=1, column=0, pady=10)
    entry001.bind('<Return>', username1)
    entry001.bind('<KP_Enter>', username1)

    entry001.focus_set()
    if options.gamemode == 3:
        lab2 = Label(popup10, text="Szerver:")
        lab2.grid(row=2, column=0, padx=10, pady=10)

        entry002 = Entry(popup10, width=10, bg="white", relief=SUNKEN, textvariable=var002)
        entry002.grid(row=3, column=0, pady=10)
        entry002.bind('<Return>', username1)
        entry002.bind('<KP_Enter>', username1)

        lab3 = Label(popup10, text="Port:")
        lab3.grid(row=4, column=0, padx=10, pady=10)

        entry003 = Entry(popup10, width=10, bg="white", relief=SUNKEN, textvariable=var003)
        entry003.grid(row=5, column=0, pady=10)
        entry003.bind('<Return>', username1)
        entry003.bind('<KP_Enter>', username1)
    popup10.grab_set()
    appwin.wait_window(popup10)


def lockon():
    """Funkciók elérésének korlátozása"""
    button2.configure(state="disabled")
    fb2.configure(state="disabled")
    button3.configure(state="disabled")
    fb3.configure(state="disabled")
    if options.duplicate:
        button3a.configure(state="disabled")
        fb3a.configure(state="disabled")


def lockoff():
    """Funkciók elérésének engedése"""
    if not options.independentboards:
        button2.configure(state="normal")
        fb2.configure(state="normal")
    button3.configure(state="normal")
    fb3.configure(state="normal")
    if options.duplicate and options.gamemode != 1:
        button3a.configure(state="normal")
        fb3a.configure(state="normal")


def starttimer():
    """Óra nullázása"""
    global sec
    global timeractive
    sec = 0
    timeractive = True
    canvas10b.create_window(0, 0, window=pb1, anchor=N)
    if currentplayer == options.username or options.gamemode == 1 or options.duplicate:
        pb1.configure(style="green.Vertical.TProgressbar", maximum=options.timelimit - 2, length=frame0.winfo_height())
    else:
        pb1.configure(style="blue.Vertical.TProgressbar", maximum=options.timelimit - 2, length=frame0.winfo_height())


def timelimit():
    """Ha letelik az idő a baloldali gomb felengedését jelzi"""
    global turns
    global timeractive
    global sec
    global timesup
    timesup = True
    canvas1.event_generate("<ButtonRelease-1>")
    try:
        popup1.destroy()
    except (NameError, AttributeError):
        pass
    back()
    unbind1()
    lockon()
    timeractive = False
    sec = 0
    if options.gamemode == 1:
        chatboxmessage("Nincs érvényes szó\n")
        turns += 1
        if options.turnlimit and turns == options.turnlimitcount:
            if options.checkmode == 4:
                checkboard()
                return
            else:
                endofgame()
                return
        counter.configure(text=turns + 1)
        if options.resetall:
            resetsack(rack)
            loadrack()
        starttimer()
        bind1()
        lockoff()


def timerupdate():
    """Óra"""
    global sec
    global options
    global timeractive
    if sec == options.timelimit - 1:
        timelimit()
    else:
        if timeractive:
            sec = sec + 1
            timer.configure(text=options.timelimit - sec - 1)
            varpb1.set(options.timelimit - sec - 1)
            if currentplayer == options.username or options.gamemode == 1 or options.duplicate:
                pb1.configure(style="green.Vertical.TProgressbar")
            else:
                pb1.configure(style="blue.Vertical.TProgressbar")
            if options.timelimit - sec - 1 < 10 and (currentplayer == options.username or options.gamemode == 1
                                                     or options.duplicate):
                pb1.configure(style="red.Vertical.TProgressbar")
        else:
            sec = 0
            varpb1.set(options.timelimit - sec - 1)
            timer.configure(text=options.timelimit - sec - 1)
    appwin.after(1000, timerupdate)


def pause():
    """Megállítja a játékot (csak egyjátékos mód)"""
    global sec, sec1, c1
    if c1:
        button6.config(text="Folytatás")
        unbind1()
        lockon()
        sec1 = sec
        c1 = False
        checkvar()
    else:
        c1 = True


def checkvar():
    global sec, sec1, c1
    if not c1:
        sec = sec1
        appwin.after(100, checkvar)
    else:
        button6.config(text="Szünet")
        bind1()
        lockoff()


def color1(color11):
    """Színválasztó"""
    color2 = askcolor(parent=popup4, color=getattr(options, color11), title="Szín kiválasztása")
    setattr(options, color11, color2[1])
    return color2


def repairboard():
    """A forduló végén foglalt jelzésű mezők visszaállítása (pl: csere közben lejár az idő)"""
    for i in range(fieldrc):
        for j in range(fieldcc):
            if fields[i][j].type == "occupied":
                fields[i][j].type = board[i][j]
                # print("field repaired:", i, ",", j)


def mouseldown(event):
    """Bal oldali gomb lenyomására végrehajtandó művelet"""
    global selectedbrick
    global selectedbricki
    global fields
    global rackfields
    global frackfields
    global whichrack
    global moverack
    appwin.x1, appwin.y1 = canvas1.canvasx(event.x), canvas1.canvasy(event.y)
    if checktime:
        return
    mx, my = canvas1.canvasx(event.x), canvas1.canvasy(event.y)
    x1, y1, x2, y2 = canvas1.bbox(anchorimage)
    if x1 < mx < x2 and y1 < my < y2:
        moverack = True
        return
    else:
        moverack = False
    for i in range(options.racksize):
        if rack[i] is not None and (rack[i].x <= appwin.x1 <= rack[i].x + (options.size - 1) and rack[
                                    i].y <= appwin.y1 <= rack[i].y + (options.size - 1)):
            whichrack = "rack"
            for k in range(len(wanttochange)):
                if rack[i] == wanttochange[k]:
                    # print("Cserére jelölve")
                    return
            canvas1.addtag_withtag('sel', rack[i].objectlist[0])
            canvas1.addtag_withtag('sel', rack[i].objectlist[1])
            canvas1.addtag_withtag('sel', rack[i].objectlist[2])
            canvas1.tag_raise('sel')
            selectedbrick = rack[i]
            selectedbricki = i
            try:
                canvas1.delete(selectedbrick.objectlist[3])
                canvas1.delete(selectedbrick.objectlist[4])
            except (NameError, AttributeError):
                pass
            for jj in range(options.racksize):
                if rackfields[jj].x == selectedbrick.x and rackfields[jj].y == selectedbrick.y:
                    rackfields[jj].type = "."
            for ii in range(fieldrc):
                for j in range(fieldcc):
                    if fields[ii][j].x == selectedbrick.x and fields[ii][j].y == selectedbrick.y:
                        fields[ii][j].type = board[ii][j]
    if options.usefletters:
        for m in range(len(frack)):
            if frack[m] is not None and (frack[m].x <= appwin.x1 <= frack[m].x + (options.size - 1) and frack[
                                         m].y <= appwin.y1 <= frack[m].y + (options.size - 1)):
                whichrack = "frack"
                canvas1.addtag_withtag('sel', frack[m].objectlist[0])
                canvas1.addtag_withtag('sel', frack[m].objectlist[1])
                canvas1.addtag_withtag('sel', frack[m].objectlist[2])
                canvas1.tag_raise('sel')
                selectedbrick = frack[m]
                try:
                    canvas1.delete(selectedbrick.objectlist[3])
                    canvas1.delete(selectedbrick.objectlist[4])
                except (NameError, AttributeError):
                    pass
                for n in range(len(frack)):
                    if frackfields[n].x == selectedbrick.x and frackfields[n].y == selectedbrick.y:
                        frackfields[n].type = "."
                for nn in range(fieldrc):
                    for o in range(fieldcc):
                        if fields[nn][o].x == selectedbrick.x and fields[nn][o].y == selectedbrick.y:
                            fields[nn][o].type = board[nn][o]


def mouselmove(event):
    """Lenyomott bal oldali gombbal, mozgó egérrel végrehajtandó művelet"""
    x2, y2 = canvas1.canvasx(event.x), canvas1.canvasy(event.y)
    dx, dy = x2 - appwin.x1, y2 - appwin.y1
    if event.x < 5 or event.x > canvas1.winfo_width()-5 or event.y < 5 or event.y > canvas1.winfo_height()-5:
        canvas1.event_generate("<ButtonRelease-1>")
    if canvas1.find_withtag('sel'):
        canvas1.move('sel', dx, dy)
        appwin.x1, appwin.y1 = x2, y2
    if moverack:
        canvas1.move('racks', dx, dy)
        appwin.x1, appwin.y1 = x2, y2


def mouselrelease(event):
    """Bal oldali gomb felengedésekor végrehajtandó művelet"""
    global selectedbrick
    global fields
    global rackfields
    global whichrack
    global moverack
    appwin.x, appwin.y = canvas1.canvasx(event.x), canvas1.canvasy(event.y)
    if moverack:
        updatecoords()
        moverack = False
        return
    if options.checkmode == 4 and checktime == True:
        ignoreletter(appwin.x, appwin.y)
        selectedbrick = None
    if selectedbrick is None:
        return
    closest = closesti = closestj = None
    distance = 10000
    x = canvas1.bbox(selectedbrick.objectlist[0])[0]
    y = canvas1.bbox(selectedbrick.objectlist[0])[1]
    if ontheboard(appwin.x, appwin.y) and not onthetray(appwin.x, appwin.y):
        for i in range(fieldrc):
            for j in range(fieldcc):
                if fields[i][j].type in options.fieldsdict:
                    if options.fieldsdict[fields[i][j].type][2] == 1 and fields[i][j].visible:
                        distancenew = math.sqrt((fields[i][j].x - x) ** 2 + (fields[i][j].y - y) ** 2)
                        if distancenew < distance:
                            closesti = i
                            closestj = j
                            distance = distancenew
        selectedbrick.x = fields[closesti][closestj].x
        selectedbrick.y = fields[closesti][closestj].y
        selectedbrick.cx = fields[closesti][closestj].cx
        selectedbrick.cy = fields[closesti][closestj].cy
        selectedbrick.b1x = fields[closesti][closestj].b1x
        selectedbrick.b1y = fields[closesti][closestj].b1y
        selectedbrick.b2x = fields[closesti][closestj].b2x
        selectedbrick.b2y = fields[closesti][closestj].b2y
        canvas1.coords(selectedbrick.objectlist[0], fields[closesti][closestj].b1x, fields[closesti][closestj].b1y,
                       fields[closesti][closestj].b2x, fields[closesti][closestj].b2y)
        canvas1.coords(selectedbrick.objectlist[1], fields[closesti][closestj].cx, fields[closesti][closestj].cy + 2)
        canvas1.coords(selectedbrick.objectlist[2], fields[closesti][closestj].b1x + options.wx,
                       fields[closesti][closestj].b1y + options.wy)
        if fields[closesti][closestj].type != '.':
            c, bc = colors1(selectedbrick)
            selectedbrick.objectlist[3] = canvas1.create_polygon((selectedbrick.b2x - 9, selectedbrick.b1y,
                                                                  selectedbrick.b2x + 1, selectedbrick.b1y,
                                                                  selectedbrick.b2x, selectedbrick.b1y + 9), fill=
                                                                 options.fieldsdict[fields[closesti][closestj].type][0])
            selectedbrick.objectlist[4] = canvas1.create_line(selectedbrick.b2x - 9, selectedbrick.b1y,
                                                              selectedbrick.b2x, selectedbrick.b1y + 9, fill=bc)
        if selectedbrick.letter == '*' and not options.dontchangejoker:
            canvas1.delete(selectedbrick.objectlist[1])
            if options.valueofchangedletter:
                canvas1.delete(selectedbrick.objectlist[2])
            changejoker(selectedbrick)
        if selectedbrick.letter in letterreplacedict:
            canvas1.delete(selectedbrick.objectlist[1])
            changeletter(selectedbrick)
        fields[closesti][closestj].type = "occupied"
        canvas1.dtag(selectedbrick.objectlist[0], 'racks')
        canvas1.dtag(selectedbrick.objectlist[1], 'racks')
        canvas1.dtag(selectedbrick.objectlist[2], 'racks')
        raisetray()
    else:
        if whichrack == "rack":
            for i in range(options.racksize):
                if rackfields[i].type == ".":
                    distancenew = math.sqrt((rackfields[i].x - x) ** 2 + (rackfields[i].y - y) ** 2)
                    if distancenew < distance:
                        closest = i
                        distance = distancenew
            selectedbrick.x = rackfields[closest].x
            selectedbrick.y = rackfields[closest].y
            selectedbrick.cx = rackfields[closest].cx
            selectedbrick.cy = rackfields[closest].cy
            selectedbrick.b1x = rackfields[closest].b1x
            selectedbrick.b1y = rackfields[closest].b1y
            selectedbrick.b2x = rackfields[closest].b2x
            selectedbrick.b2y = rackfields[closest].b2y
            canvas1.coords(selectedbrick.objectlist[0], rackfields[closest].b1x, rackfields[closest].b1y,
                           rackfields[closest].b2x, rackfields[closest].b2y)
            if selectedbrick.letter == '*' and not options.dontchangejoker:
                canvas1.delete(selectedbrick.objectlist[1])
                selectedbrick.objectlist[1] = canvas1.create_text(rackfields[closest].cx, rackfields[closest].cy + 2,
                                                                  font=(options.letterfont, options.letterfontsize),
                                                                  text=selectedbrick.letter)
            canvas1.coords(selectedbrick.objectlist[1], rackfields[closest].cx, rackfields[closest].cy + 2)
            canvas1.coords(selectedbrick.objectlist[2], rackfields[closest].b1x + options.wx,
                           rackfields[closest].b1y + options.wy)
            rackfields[closest].type = "occupied"
            canvas1.addtag_withtag('racks', selectedbrick.objectlist[0])
            canvas1.addtag_withtag('racks', selectedbrick.objectlist[1])
            canvas1.addtag_withtag('racks', selectedbrick.objectlist[2])

            # rack[] lista rackfields[] szerinti sorrendjének helyreállítása:
            for i in range(options.racksize):
                if selectedbrick.x == rackfields[i].x and i != selectedbricki:
                    rack[i], rack[selectedbricki] = rack[selectedbricki], rack[i]
        if whichrack == "frack":
            selectedbrick.x = frackdict[selectedbrick].x
            selectedbrick.y = frackdict[selectedbrick].y
            selectedbrick.cx = frackdict[selectedbrick].cx
            selectedbrick.cy = frackdict[selectedbrick].cy
            selectedbrick.b1x = frackdict[selectedbrick].b1x
            selectedbrick.b1y = frackdict[selectedbrick].b1y
            selectedbrick.b2x = frackdict[selectedbrick].b2x
            selectedbrick.b2y = frackdict[selectedbrick].b2y
            canvas1.coords(selectedbrick.objectlist[0], frackdict[selectedbrick].b1x, frackdict[selectedbrick].b1y,
                           frackdict[selectedbrick].b2x, frackdict[selectedbrick].b2y)
            if selectedbrick.letter == '*' and not options.dontchangejoker:
                canvas1.delete(selectedbrick.objectlist[1])
                selectedbrick.objectlist[1] = canvas1.create_text(frackdict[selectedbrick].cx,
                                                                  frackdict[selectedbrick].cy + 2,
                                                                  font=(options.letterfont, options.letterfontsize),
                                                                  text=selectedbrick.letter)
            canvas1.coords(selectedbrick.objectlist[1], frackdict[selectedbrick].cx, frackdict[selectedbrick].cy + 2)
            canvas1.coords(selectedbrick.objectlist[2], frackdict[selectedbrick].b1x + options.wx,
                           frackdict[selectedbrick].b1y + options.wy)
            canvas1.addtag_withtag('racks', selectedbrick.objectlist[0])
            canvas1.addtag_withtag('racks', selectedbrick.objectlist[1])
            canvas1.addtag_withtag('racks', selectedbrick.objectlist[2])
    selectedbrick = None
    canvas1.dtag(ALL, 'sel')


def ignoreletter(x, y):
    """Ha a táblán lévő szavak érvényességének ellenőrzése a játék végén történik, a fölösleges betűk megjelölése"""
    global fields
    for i in range(fieldrc):
        for j in range(fieldcc):
            if fields[i][j].b1x < x < fields[i][j].b2x and fields[i][j].b1y < y < fields[i][j].b2y:
                if fields[i][j].ignored == False:
                    colofi = options.colornormal
                    colobo = options.colornormal
                    colotx = "#bebebe"
                    colovtx = "#bebebe"
                    fields[i][j].ignored = True
                else:
                    colofi = options.colornormalbrick
                    colobo = options.colorborderbrick
                    colotx = options.colortextbrick
                    colovtx = options.colorvaluebrick
                    fields[i][j].ignored = False
                canvas1.itemconfig( fields[i][j].objectlist[0], fill=colofi, outline=colobo)
                canvas1.itemconfig( fields[i][j].objectlist[1], fill=colotx)
                #if options.valuedisplay:
                canvas1.itemconfig( fields[i][j].objectlist[2], fill=colovtx)


def detectabove(brick1):
    if canvas1.find_above(brick1.objectlist[0]):
        canvas1.tag_raise(brick1.objectlist[0])
        canvas1.tag_raise(brick1.objectlist[1])
        canvas1.tag_raise(brick1.objectlist[2])


def raisetray():
    rackobjects = canvas1.find_withtag("racks")
    for robj in rackobjects:
        canvas1.tag_raise(robj)


def updatecoords():
    """Betűtartó áthelyezése után a mezők új koordinátáinak eltárolása"""
    global rackfields
    global frackfields
    global rack
    #tray_xy = [canvas1.bbox(tray)[0], canvas1.bbox(tray)[1]]
    rackfields[0].x = canvas1.bbox(rackfields[0].objectlist[0])[0]
    rackfields[0].y = canvas1.bbox(rackfields[0].objectlist[0])[1]
    #print("tray",tray_xy)
    for i in range(options.racksize):
        rackfields[i].x = rackfields[0].x + i * (options.size + options.gap)
        rackfields[i].y = rackfields[0].y
        rackfields[i].cx = rackfields[i].x + options.size / 2 - 1
        rackfields[i].cy = rackfields[i].y + options.size / 2 - 1
        rackfields[i].b1x = rackfields[i].x + (options.size - options.bricksize) / 2
        rackfields[i].b1y = rackfields[i].y + (options.size - options.bricksize) / 2
        rackfields[i].b2x = rackfields[i].x + (options.size - options.bricksize) / 2 + options.bricksize - 1
        rackfields[i].b2y = rackfields[i].y + (options.size - options.bricksize) / 2 + options.bricksize - 1
    for i in range(options.racksize):
        if rack[i] is not None and len(canvas1.gettags(rack[i].objectlist[0])) > 1:
            rack[i].x = rackfields[i].x
            rack[i].y = rackfields[i].y
            rack[i].cx = rackfields[i].cx
            rack[i].cy = rackfields[i].cy
            rack[i].b1x = rackfields[i].b1x
            rack[i].b1y = rackfields[i].b1y
            rack[i].b2x = rackfields[i].b2x
            rack[i].b2y = rackfields[i].b2y
    if options.usefletters:
        frackfields[0].x = canvas1.bbox(frackfields[0].objectlist[0])[0]
        frackfields[0].y = canvas1.bbox(frackfields[0].objectlist[0])[1]
        for i in range(len(options.fletters)):
            frackfields[i].x = frackfields[0].x + i * (options.size + options.gap)
            frackfields[i].y = frackfields[0].y
            frackfields[i].cx = frackfields[i].x + options.size / 2 - 1
            frackfields[i].cy = frackfields[i].y + options.size / 2 - 1
            frackfields[i].b1x = frackfields[i].x + (options.size - options.bricksize) / 2
            frackfields[i].b1y = frackfields[i].y + (options.size - options.bricksize) / 2
            frackfields[i].b2x = frackfields[i].x + (options.size - options.bricksize) / 2 + options.bricksize - 1
            frackfields[i].b2y = frackfields[i].y + (options.size - options.bricksize) / 2 + options.bricksize - 1
        for i in range(len(frack)):
            if frack[i] is not None and len(canvas1.gettags(frack[i].objectlist[0])) > 1:
                frack[i].x = frackdict[frack[i]].x
                frack[i].y = frackdict[frack[i]].y
                frack[i].cx = frackdict[frack[i]].cx
                frack[i].cy = frackdict[frack[i]].cy
                frack[i].b1x = frackdict[frack[i]].b1x
                frack[i].b1y = frackdict[frack[i]].b1y
                frack[i].b2x = frackdict[frack[i]].b2x
                frack[i].b2y = frackdict[frack[i]].b2y
    raisetray()


def mouserdown(event):
    """Jobb oldali gomb lenyomására végrehajtandó művelet"""
    appwin.x1, appwin.y1 = canvas1.canvasx(event.x), canvas1.canvasy(event.y)
    global selectedbrick
    global selectedbricki                                                # !!!!!!!!!!!!!!!!!!!!!!!!
    global wanttochange
    global fields
    global rackfields
    closest = None
    distance = 10000
    for i in range(options.racksize):
        if rack[i] is not None and (rack[i].x <= appwin.x1 <= rack[i].x + (options.size - 1) and rack[
                                    i].y <= appwin.y1 <= rack[i].y + (options.size - 1)):
            selectedbrick = rack[i]
            selectedbricki = i
            try:
                canvas1.delete(selectedbrick.objectlist[3])
                canvas1.delete(selectedbrick.objectlist[4])
            except (NameError, AttributeError):
                pass
            x = canvas1.bbox(selectedbrick.objectlist[0])[0]
            y = canvas1.bbox(selectedbrick.objectlist[0])[1]
            if ontheboard(appwin.x1, appwin.y1)  and not onthetray(appwin.x1, appwin.y1):
                for ii in range(options.racksize):
                    if rackfields[ii].type == ".":
                        distancenew = math.sqrt((rackfields[ii].x - x) ** 2 + (rackfields[ii].y - y) ** 2)
                        if distancenew < distance:
                            closest = ii
                            distance = distancenew
                for ii in range(fieldrc):
                    for jj in range(fieldcc):
                        if fields[ii][jj].x == selectedbrick.x and fields[ii][jj].y == selectedbrick.y:
                            fields[ii][jj].type = board[ii][jj]
                selectedbrick.x = rackfields[closest].x
                selectedbrick.y = rackfields[closest].y
                selectedbrick.cx = rackfields[closest].cx
                selectedbrick.cy = rackfields[closest].cy
                selectedbrick.b1x = rackfields[closest].b1x
                selectedbrick.b1y = rackfields[closest].b1y
                selectedbrick.b2x = rackfields[closest].b2x
                selectedbrick.b2y = rackfields[closest].b2y
                canvas1.coords(selectedbrick.objectlist[0], rackfields[closest].b1x, rackfields[closest].b1y,
                               rackfields[closest].b2x, rackfields[closest].b2y)
                if selectedbrick.letter == '*' and not options.dontchangejoker:
                    canvas1.delete(selectedbrick.objectlist[1])
                    selectedbrick.objectlist[1] = canvas1.create_text(rackfields[closest].cx,
                                                                      rackfields[closest].cy + 2,
                                                                      font=(options.letterfont, options.letterfontsize),
                                                                      text=selectedbrick.letter)
                canvas1.coords(selectedbrick.objectlist[1], rackfields[closest].cx, rackfields[closest].cy + 2)
                canvas1.coords(selectedbrick.objectlist[2], rackfields[closest].b1x + options.wx,
                               rackfields[closest].b1y + options.wy)
                rackfields[closest].type = "occupied"
                canvas1.addtag_withtag('racks', selectedbrick.objectlist[0])
                canvas1.addtag_withtag('racks', selectedbrick.objectlist[1])
                canvas1.addtag_withtag('racks', selectedbrick.objectlist[2])
            else:
                if not options.duplicate and not options.resetsack:  # Olyan játékban, amelyben a betűk visszakerülnek
                    # a zsákba, nem lehet egyenként cserélni
                    for j1 in range(len(wanttochange)):
                        if rack[i] == wanttochange[j1]:
                            c, bc = colors1(rack[i])
                            canvas1.itemconfig(rack[i].objectlist[0], fill=c)
                            wanttochange.remove(rack[i])
                            return
                    if len(wanttochange) > len(sack) - numberofplayers * options.racksize:
                        # print("nincs már elég betű")
                        notenoughletter()
                        return
                    canvas1.itemconfig(rack[i].objectlist[0], fill=options.colorchangedbrick)
                    wanttochange.append(rack[i])
            # rack[] lista rackfields[] szerinti sorrendjének helyreállítása:
            for ii in range(options.racksize):
                if selectedbrick.x == rackfields[ii].x and ii != selectedbricki:
                    rack[ii], rack[selectedbricki] = rack[selectedbricki], rack[ii]
    if ontheboard(appwin.x1, appwin.y1) and options.usefletters:
        for i in range(len(frack)):
            if frack[i] is not None and ((frack[i].x <= appwin.x1 <= frack[i].x + (options.size - 1) and frack[
                                         i].y <= appwin.y1 <= frack[i].y + (options.size - 1))):
                selectedbrick = frack[i]
                try:
                    canvas1.delete(selectedbrick.objectlist[3])
                    canvas1.delete(selectedbrick.objectlist[4])
                except (NameError, AttributeError):
                    pass
                for ii in range(fieldrc):
                    for jj in range(fieldcc):
                        if fields[ii][jj].x == selectedbrick.x and fields[ii][jj].y == selectedbrick.y:
                            fields[ii][jj].type = board[ii][jj]
                selectedbrick.x = frackdict[selectedbrick].x
                selectedbrick.y = frackdict[selectedbrick].y
                selectedbrick.cx = frackdict[selectedbrick].cx
                selectedbrick.cy = frackdict[selectedbrick].cy
                selectedbrick.b1x = frackdict[selectedbrick].b1x
                selectedbrick.b1y = frackdict[selectedbrick].b1y
                selectedbrick.b2x = frackdict[selectedbrick].b2x
                selectedbrick.b2y = frackdict[selectedbrick].b2y
                canvas1.coords(selectedbrick.objectlist[0], frackdict[selectedbrick].b1x, frackdict[selectedbrick].b1y,
                               frackdict[selectedbrick].b2x, frackdict[selectedbrick].b2y)
                if selectedbrick.letter == '*' and not options.dontchangejoker:
                    canvas1.delete(selectedbrick.objectlist[1])
                    selectedbrick.objectlist[1] = canvas1.create_text(frackdict[selectedbrick].cx,
                                                                      frackdict[selectedbrick].cy + 2,
                                                                      font=(options.letterfont, options.letterfontsize),
                                                                      text=selectedbrick.letter)
                    if options.valueofchangedletter:
                        canvas1.delete(selectedbrick.objectlist[2])
                        selectedbrick.value = selectedbrick.changedvalue
                        selectedbrick.changedvalue = None
                        selectedbrick.objectlist[2] = canvas1.create_text(frackdict[selectedbrick].b1x,
                                                                          frackdict[selectedbrick].b1y, font=
                                                                          (options.valuefont, options.valuefontsize),
                                                                          text=selectedbrick.value)
                canvas1.coords(selectedbrick.objectlist[1], frackdict[selectedbrick].cx,
                               frackdict[selectedbrick].cy + 2)
                canvas1.coords(selectedbrick.objectlist[2], frackdict[selectedbrick].b1x + options.wx,
                               frackdict[selectedbrick].b1y + options.wy)
                canvas1.addtag_withtag('racks', selectedbrick.objectlist[0])
                canvas1.addtag_withtag('racks', selectedbrick.objectlist[1])
                canvas1.addtag_withtag('racks', selectedbrick.objectlist[2])
                break
    detectabove(selectedbrick)
    selectedbrick = None


def ontheboard(x, y):
    """Adott pont a táblára esik-e"""
    if tabla.x1 <= x <= tabla.x2 and tabla.y1 <= y <= tabla.y2:
        return True

def onthetray(x, y):
    if (canvas1.bbox(tray)[0] < x < canvas1.bbox(tray)[2]) and (canvas1.bbox(tray)[1] < y < canvas1.bbox(tray)[3]):
        return True

def showrack(newletters):
    """Az új betűket elhelyezi a tartón (csak többjátékos módok)"""
    i = 0
    j = 0
    while j < options.racksize:
        if rackfields[j].type == ".":
            rack[j] = newletters[i]
            i += 1
            rack[j].x = rackfields[j].x
            rack[j].y = rackfields[j].y
            rack[j].cx = rackfields[j].cx
            rack[j].cy = rackfields[j].cy
            rack[j].b1x = rackfields[j].b1x
            rack[j].b1y = rackfields[j].b1y
            rack[j].b2x = rackfields[j].b2x
            rack[j].b2y = rackfields[j].b2y
        else:
            j += 1
            continue
        rackfields[j].type = "occupied"
        c, bc = colors1(rack[j])
        rack[j].objectlist[0] = canvas1.create_rectangle(rackfields[j].b1x, rackfields[j].b1y, rackfields[j].b2x,
                                                         rackfields[j].b2y, width=1, fill=c, outline=bc, tags=str(j))
        rack[j].objectlist[1] = canvas1.create_text(rackfields[j].cx, rackfields[j].cy + 2,
                                                    font=(options.letterfont, options.letterfontsize),
                                                    text=rack[j].letter, fill=options.colortextbrick, tags=str(j))
        rack[j].objectlist[2] = canvas1.create_text(rackfields[j].b1x + options.wx, rackfields[j].b1y + options.wy,
                                                    font=(options.valuefont, options.valuefontsize), text=rack[j].value,
                                                    fill=options.colorvaluebrick, tags=str(j))
        canvas1.addtag_withtag("racks", rack[j].objectlist[0])
        canvas1.addtag_withtag("racks", rack[j].objectlist[1])
        canvas1.addtag_withtag("racks", rack[j].objectlist[2])
        j += 1
        if i == len(newletters):
            break
    managesack()


def colors1(brck):
    """Lerakott betű színét adja vissza"""
    c = options.colornormalbrick
    if not options.randomlettervalue:
        if brck.multiplier == 2:
            c = options.colordoublebrick
        if brck.multiplier == 3:
            c = options.colortriplebrick
        if brck.wordmultiplier == 2:
            c = options.colordoublewordbrick
        if brck.wordmultiplier == 3:
            c = options.colortriplewordbrick
    if options.bborder:
        bc = options.colorborderbrick
    else:
        bc = c
    return c, bc


def placeletters(msgclient):
    """Az ellenfél betűit, vagy a legjobb szót alkotó betűket elhelyezi a táblán (csak többjátékos módok)"""
    global fields
    global fieldstemp
    global firstmove
    canvas1.delete("newletter")
    commandlist = msgclient.split(';')
    messagelist0 = commandlist[0].split(',')
    messagelist1 = commandlist[1].split(',')
    i = int(messagelist1[1])
    j = int(messagelist1[2])
    b = 1
    messagelist2 = commandlist[2].split(',')
    direction = messagelist2[1]
    direction1 = ""
    if direction == "across":
        direction1 = "vízsz."
    elif direction == "down":
        direction1 = "függő."
    messagelist3 = commandlist[3].split(',')
    messagelist4 = commandlist[4].split(',')
    messagelist5 = commandlist[5].split(',')
    messagelist6 = list()

    try:
        messagelist6 = commandlist[6].split(',')
    except Exception:
        pass

    if options.duplicate:
        lob1 = takefromrack(messagelist4[1:])
        if not options.independentboards:
            message = (messagelist6[0] + " lépése a legjobb: " + messagelist0[1] + " Pozíció:" +
                       numberstoletters(int(messagelist1[1])) + "," +
                       str(int(messagelist1[2])+1) + "," + direction1 + " " + messagelist3[1] + " pont\n")
            chatboxmessage(message)
    else:
        letterlist = messagelist4[1:]
        lob1 = takemovefromsack(letterlist)
        message = messagelist6[0] + ": " + messagelist0[1] + " Pozíció:" + numberstoletters(int(messagelist1[1]))\
                  + "," + str(int(messagelist1[2])+1) + "," + direction1 + " " + messagelist3[1] + " pont\n"
        chatboxmessage(message)
    k = 0
    if len(lob1) > 0:
        firstmove = False
    fieldstemp = copy.deepcopy(fields)
    if direction == "across":
        while k < len(lob1):
            c2 = None
            if fieldstemp[i][j].type in options.fieldsdict:
                if fieldstemp[i][j].type != '.':
                    c2 = options.fieldsdict[fieldstemp[i][j].type][0]
                if lob1[k].letter == '*' and not options.dontchangejoker:
                    fieldstemp[i][j].type = messagelist5[b]
                else:
                    fieldstemp[i][j].type = lob1[k].letter
                fieldstemp[i][j].value = lob1[k].value
                fieldstemp[i][j].multiplier = lob1[k].multiplier
                fieldstemp[i][j].wordmultiplier = lob1[k].wordmultiplier
                c, bc = colors1(lob1[k])
                canvas1.create_rectangle(fieldstemp[i][j].b1x, fieldstemp[i][j].b1y, fieldstemp[i][j].b2x,
                                         fieldstemp[i][j].b2y, width=1, fill=c, outline=bc)
                if lob1[k].letter == '*' and not options.dontchangejoker:
                    l1 = messagelist5[b]
                else:
                    l1 = lob1[k].letter
                canvas1.create_text(fieldstemp[i][j].cx, fieldstemp[i][j].cy + 2,
                                    font=(options.letterfont, options.letterfontsize), text=l1,
                                    fill=options.colortextbrick)
                valuetext = canvas1.create_text(fieldstemp[i][j].b1x + options.wx, fieldstemp[i][j].b1y + options.wy,
                                    font=(options.valuefont, options.valuefontsize), text=lob1[k].value,
                                    fill=options.colorvaluebrick)
                if not options.valuedisplay:
                    canvas1.itemconfig(valuetext, state="hidden")
                if c2 is not None:
                    canvas1.create_polygon((fieldstemp[i][j].b2x - 9, fieldstemp[i][j].b1y, fieldstemp[i][j].b2x + 1,
                                            fieldstemp[i][j].b1y, fieldstemp[i][j].b2x, fieldstemp[i][j].b1y + 9),
                                           fill=c2)
                    canvas1.create_line(fieldstemp[i][j].b2x - 9, fieldstemp[i][j].b1y, fieldstemp[i][j].b2x,
                                        fieldstemp[i][j].b1y + 9, fill=bc)
                canvas1.create_rectangle(fieldstemp[i][j].b1x, fieldstemp[i][j].b1y, fieldstemp[i][j].b2x,
                                         fieldstemp[i][j].b2y, width=1, outline="yellow", tags="newletter")
                j += 1
                b += 1
                k += 1
            else:
                j += 1
                b += 1
    elif direction == "down":
        while k < len(lob1):
            c2 = None
            if fieldstemp[i][j].type in options.fieldsdict:
                if fieldstemp[i][j].type != '.':
                    c2 = options.fieldsdict[fieldstemp[i][j].type][0]
                if lob1[k].letter == '*' and not options.dontchangejoker:
                    fieldstemp[i][j].type = messagelist5[b]
                else:
                    fieldstemp[i][j].type = lob1[k].letter
                fieldstemp[i][j].value = lob1[k].value
                c, bc = colors1(lob1[k])
                canvas1.create_rectangle(fieldstemp[i][j].b1x, fieldstemp[i][j].b1y, fieldstemp[i][j].b2x,
                                         fieldstemp[i][j].b2y, width=1, fill=c, outline=bc)
                if lob1[k].letter == '*' and not options.dontchangejoker:
                    l1 = messagelist5[b]
                else:
                    l1 = lob1[k].letter
                canvas1.create_text(fieldstemp[i][j].cx, fieldstemp[i][j].cy + 2,
                                    font=(options.letterfont, options.letterfontsize), text=l1,
                                    fill=options.colortextbrick)
                canvas1.create_text(fieldstemp[i][j].b1x + options.wx, fieldstemp[i][j].b1y + options.wy,
                                    font=(options.valuefont, options.valuefontsize), text=lob1[k].value,
                                    fill=options.colorvaluebrick)
                if c2 is not None:
                    canvas1.create_polygon((fieldstemp[i][j].b2x - 9, fieldstemp[i][j].b1y, fieldstemp[i][j].b2x + 1,
                                            fieldstemp[i][j].b1y, fieldstemp[i][j].b2x, fieldstemp[i][j].b1y + 9),
                                           fill=c2)
                    canvas1.create_line(fieldstemp[i][j].b2x - 9, fieldstemp[i][j].b1y, fieldstemp[i][j].b2x,
                                        fieldstemp[i][j].b1y + 9, fill=bc)
                canvas1.create_rectangle(fieldstemp[i][j].b1x, fieldstemp[i][j].b1y, fieldstemp[i][j].b2x,
                                         fieldstemp[i][j].b2y, width=1, outline="yellow", tags="newletter")
                i += 1
                b += 1
                k += 1
            else:
                i += 1
                b += 1
    if options.duplicate:
        endmove(lob1)
    else:
        managesack()
        printboard()
    raisetray()


def numberstoletters(i):
    letter1 = abc1[i]
    return letter1


def showscore1(message):
    """Megjeleníti a pillanatnyi játékállást (csak többjátékos módok)"""
    global players

    pslist = message.split(';')[1:]
    psl1 = []
    for ps in pslist:
        psl = ps.split(',')
        psl1.append(psl)
    textbox2.configure(state=NORMAL)
    for i in range(len(players)):
        for j in range(len(psl1)):
            if players[i][0] == psl1[j][0]:
                players[i][1] = int(psl1[j][1])
                players[i][2] = int(psl1[j][2])
                scstr =  " " * (3 - len(str(players[i][1]))) + str(players[i][1]) + " " * (5 - len(str(players[i][2])))\
                         + str(players[i][2])
                loc1 = str(i + 3) + '.19'
                loc2 = str(i + 3) + '.27'
                textbox2.delete(loc1, loc2)
                textbox2.insert(loc1, scstr)
                break
    textbox2.configure(state=DISABLED)


def markcurrentplayer():
    """Az aktuális játékost jelöli"""
    global players
    global currentplayer
    textbox2.configure(state=NORMAL)
    for i in range(len(players)):
        loc1 = str(i + 3) + '.13'
        textbox2.delete(loc1)
        if players[i][0] == currentplayer:
            textbox2.insert(loc1, '*')
        else:
            textbox2.insert(loc1, ' ')
    textbox2.configure(state=DISABLED)


def swapwithserver():
    """A cserére jelölt betűket elküldi a szervernek (csak többjátékos módok)"""
    global wanttochange
    global rack
    global queue1

    def listtostr(wanttochangel1):
        message11 = "CHANGE," + str(len(wanttochangel1) * 4)
        print("wanttochange", wanttochangel1)
        for ii in range(len(wanttochangel1)):
            message11 += ","
            message11 += str(wanttochangel1[ii][0])
            message11 += ","
            message11 += str(wanttochangel1[ii][1])
            message11 += ","
            message11 += str(wanttochangel1[ii][2])
            message11 += ","
            message11 += str(wanttochangel1[ii][3])
        return message11

    wanttochangel = []
    for i in range(len(wanttochange)):
        for j in range(options.racksize):
            if rack[j] == wanttochange[i]:
                if not options.duplicate:
                    canvas1.delete(rack[j].objectlist[0])
                    canvas1.delete(rack[j].objectlist[1])
                    canvas1.delete(rack[j].objectlist[2])
                    rackfields[j].type = '.'
                wanttochangel.append([rack[j].letter, rack[j].value, rack[j].wordmultiplier, rack[j].type])
    message1 = listtostr(wanttochangel)
    # print("sent: " + message1)
    queue1.put(message1)
    lockon()
    if not options.duplicate:
        backtosack(wanttochange)
        wanttochange = []
        managesack()


def finishdupswap():
    """Szimultán játékban kiüríti a tartót (csak többjátékos módok)"""
    global wanttochange
    global rack
    for i in range(len(wanttochange)):
        for j in range(options.racksize):
            if rack[j] == wanttochange[i]:
                canvas1.delete(rack[j].objectlist[0])
                canvas1.delete(rack[j].objectlist[1])
                canvas1.delete(rack[j].objectlist[2])
                rackfields[j].type = '.'
    backtosack(wanttochange)
    wanttochange = []
    managesack()


def takenewfromsack(letterlist):
    """A szervertől kapott új saját betűket kiveszi a zsákból (csak többjátékos módok)"""
    global sack
    global sackl
    letterbricks = []
    i = 0
    sack = sorted(sack, key=attrgetter('letter'))
    while i < len(letterlist):
        for j in range(len(sack)):
            if sack[j].letter == letterlist[i]:
                if options.randommultiplier:
                    for k in range(len(sackl)):
                        if sackl[k][0] == sack[j].letter:
                            if sackl[k][1] != 0:
                                sack[j].multiplier = int(letterlist[i + 1]) // sackl[k][1]
                            else:
                                sack[j].multiplier = 1
                            break
                sack[j].changedvalue = sack[j].value
                sack[j].value = int(letterlist[i + 1])
                sack[j].wordmultiplier = int(letterlist[i + 2])
                letterbricks.append(sack[j])
                sack[j].used = True
                sack.pop(j)
                break
        i += 4
    return letterbricks


def takemovefromsack(letterlist):
    """Az ellenfél szavához tartozó betűket kiveszi a zsákból (csak többjátékos módok)"""
    global sack
    global sackl
    letterbricks = []
    i = 0
    while i < len(letterlist):
        found = False
        for j in range(len(sack)):
            if sack[j].letter == letterlist[i] and not sack[j].used:
                found = True
                for k in range(len(sackl)):
                    if sackl[k][0] == sack[j].letter:
                        if options.randommultiplier:
                            if sackl[k][1] != 0:
                                sack[j].multiplier = int(letterlist[i + 1]) // sackl[k][1]
                            else:
                                sack[j].multiplier = 1
                        sack[j].changedvalue = sack[j].value
                        sack[j].value = int(letterlist[i + 1])
                        break
                sack[j].wordmultiplier = int(letterlist[i + 2])
                letterbricks.append(sack[j])
                if not options.resetsack:
                    sack[j].used = True
                    sack.pop(j)
                break
        if not found:  # A zsákban nem lévő betűk (az ellenfél közös betűi)
            print("letterlist",letterlist)
            eletter = Brick(",".join([letterlist[i], '1', letterlist[i + 1], letterlist[i + 2], '0']))
            letterbricks.append(eletter)
        i += 4
    return letterbricks


def takefromrack(letterlist):
    """Szimultán játékban a legjobb szó betűit leveszi a tartóról (csak többjátékos módok)"""
    global rack
    global rackfields
    letterbricks = []
    i = 0
    indices = list(range(len(rack)))
    while i < len(letterlist):
        for j in indices:
            if rack[j] is not None:
                if rack[j].letter == letterlist[i] and rack[j].value == int(letterlist[i + 1]) and \
                        rack[j].wordmultiplier == int(letterlist[i + 2]):
                    letterbricks.append(rack[j])
                    for k in range(len(rackfields)):
                        if rack[j].x == rackfields[k].x and rack[j].y == rackfields[j].y:
                            rackfields[k].type = '.'
                            break
                    canvas1.delete(rack[j].objectlist[0])
                    canvas1.delete(rack[j].objectlist[1])
                    canvas1.delete(rack[j].objectlist[2])
                    indices.remove(j)
                    break
        i += 4
    return letterbricks


def ifnovalidmove():
    """Szimultán játékban, ha nincs érvényes szó, a tartón levő betűket visszarakja a zsákba (csak többjátékos módok)"""
    global rack, rackfields
    global wanttochange
    for j in range(options.racksize):
        canvas1.delete(rack[j].objectlist[0])
        canvas1.delete(rack[j].objectlist[1])
        canvas1.delete(rack[j].objectlist[2])
        rackfields[j].type = '.'
        wanttochange.append(rack[j])
    backtosack(wanttochange)
    wanttochange = []
    managesack()


def backtosack(lettersback):
    """Visszarakja a cserére jelölt betűket a zsákba (csak többjátékos módok)"""
    for k in range(len(lettersback)):
        foundonfrack = False
        for f in frack:
            if f.letter == lettersback[k].letter and f.value == lettersback[k].value:
                foundonfrack = True
        if foundonfrack:
            continue
        lettersback[k].used = False
        sack.append(lettersback[k])


def deletefrack():
    global frack
    for fr in frack:
        for frs in frackfields:
            if fr.x == frs.x and fr.y == frs.y:
                canvas1.delete(fr.objectlist[0])
                canvas1.delete(fr.objectlist[1])
                canvas1.delete(fr.objectlist[2])


def loadfrack():
    """A közös betűket helyezi a tartóra"""
    global frack
    global frackfields
    global frackdict

    deletefrack()
    frack = []
    frackdict = dict()
    for i in range(len(options.fletters)):
        frack.append(Brick(options.fletters[i]))
        frack[-1].x = frackfields[i].x
        frack[-1].y = frackfields[i].y
        frack[-1].cx = frackfields[i].cx
        frack[-1].cy = frackfields[i].cy
        frackdict[frack[i]] = frackfields[i]
        if options.bborder:
            bc = options.colorborderbrick
        else:
            bc = options.colornormalbrick
        frack[i].objectlist[0] = canvas1.create_rectangle(frackfields[i].b1x, frackfields[i].b1y, frackfields[i].b2x,
                                                          frackfields[i].b2y, width=1, fill=options.colornormalbrick,
                                                          outline=bc, tags=str(i))
        frack[i].objectlist[1] = canvas1.create_text(frackfields[i].cx, frackfields[i].cy + 2,
                                                     font=(options.letterfont, options.letterfontsize),
                                                     text=frack[i].letter, fill=options.colortextbrick, tags=str(i))
        frack[i].objectlist[2] = canvas1.create_text(frackfields[i].x + options.wx, frackfields[i].y + options.wy,
                                                     font=(options.valuefont, options.valuefontsize),
                                                     text=frack[i].value, fill=options.colorvaluebrick, tags=str(i))
        canvas1.addtag_withtag('racks', frack[i].objectlist[0])
        canvas1.addtag_withtag('racks', frack[i].objectlist[1])
        canvas1.addtag_withtag('racks', frack[i].objectlist[2])


def resetsack(lob):
    """Betűket rak vissza a zsákba"""
    global sack
    if options.resetall:
        for i in rack:
            foundonfrack = False
            for f in frack:
                if f.letter == i.letter and f.value == i.value:
                    foundonfrack = True
            if foundonfrack:
                continue
            sack.append(i)
            i.used = False
            if i.changedvalue is not None:
                i.value = i.changedvalue
                i.changedvalue = None
            i.changedletter = None
            if len(canvas1.gettags(i.objectlist[0])) > 1:
                canvas1.delete(i.objectlist[0])
                canvas1.delete(i.objectlist[1])
                canvas1.delete(i.objectlist[2])
        for j in rackfields:
            j.type = '.'
    else:
        for i in lob:
            foundonfrack = False
            for f in frack:
                if f.letter == i.letter and f.value == i.value:
                    foundonfrack = True
            if foundonfrack:
                continue
            sack.append(i)
            i.used = False
            if i.changedvalue is not None:
                i.value = i.changedvalue
                i.changedvalue = None
            i.changedletter = None


def loadrack():
    """Feltölti betűkkel a tartót (csak egyjátékos módban)"""
    global rackfields
    global sack
    global rack
    global lettersonrack
    j = 0
    lettersonrack = rack
    while j < options.racksize:
        if len(sack) == 0:  # Ha nincs már betű a zsákban
            lettersonrack = []
            for i in range(len(rack)):
                if rack[i] is not None:
                    lettersonrack.append(rack[i])
            if len(lettersonrack) == 0:
                endofgame()
            managesack()
            lockoff()
            starttimer()
            return
        if rackfields[j].type == ".":
            randomnumber = drawletter(j)
            rack[j] = sack[randomnumber]
            rack[j].x = rackfields[j].x
            rack[j].y = rackfields[j].y
            rack[j].cx = rackfields[j].cx
            rack[j].cy = rackfields[j].cy
            rack[j].b1x = rackfields[j].b1x
            rack[j].b1y = rackfields[j].b1y
            rack[j].b2x = rackfields[j].b2x
            rack[j].b2y = rackfields[j].b2y
            if options.randomlettervalue:
                if rack[j].letter != '*' or options.dontchangejoker:
                    values = options.values[:]
                    rn = randrange(len(values))
                    rack[j].value = values[rn]
                    values.pop(rn)
            if options.randommultiplier:
                if rack[j].letter != '*' or options.dontchangejoker:
                    mvalues = options.mvalues[:]
                    rn = randrange(len(mvalues))
                    if mvalues[rn] > 1:
                        typevalues = ["letter", "word", "letter", "letter", "letter", "letter", "letter", "word",
                                      "letter", "letter", "letter"]
                        rntype = randrange(len(typevalues))
                        if typevalues[rntype] == "letter":
                            rack[j].multiplier = mvalues[rn]
                            rack[j].changedvalue = rack[j].value
                            rack[j].value = rack[j].value * mvalues[rn]
                            rack[j].wordmultiplier = 1
                        if typevalues[rntype] == "word":
                            rack[j].multiplier = 1
                            rack[j].changedvalue = rack[j].value
                            rack[j].wordmultiplier = mvalues[rn]
                    else:
                        rack[j].multiplier = mvalues[rn]
                        rack[j].changedvalue = rack[j].value
                        rack[j].value = rack[j].value * mvalues[rn]
            rackfields[j].type = "occupied"
            c, bc = colors1(rack[j])
            rack[j].objectlist[0] = canvas1.create_rectangle(rackfields[j].b1x, rackfields[j].b1y, rackfields[j].b2x,
                                                             rackfields[j].b2y, width=1, fill=c, outline=bc,
                                                             tags=str(j))
            rack[j].objectlist[1] = canvas1.create_text(rackfields[j].cx, rackfields[j].cy + 2,
                                                        font=(options.letterfont, options.letterfontsize),
                                                        text=rack[j].letter, fill=options.colortextbrick, tags=str(j))
            rack[j].objectlist[2] = canvas1.create_text(rackfields[j].b1x + options.wx, rackfields[j].b1y + options.wy,
                                                        font=(options.valuefont, options.valuefontsize),
                                                        text=rack[j].value, fill=options.colorvaluebrick, tags=str(j))
            if not options.valuedisplay:
                canvas1.itemconfig(rack[j].objectlist[2], state="hidden")
            canvas1.addtag_withtag("racks", rack[j].objectlist[0])
            canvas1.addtag_withtag("racks", rack[j].objectlist[1])
            canvas1.addtag_withtag("racks", rack[j].objectlist[2])
            sack[randomnumber].used = True
            sack.pop(randomnumber)
        j += 1
    printrack()
    managesack()
    lockoff()
    starttimer()


def sortsack():
    sackc = []
    sackv = []
    for bck in sack:
        if bck.type == 'C':
            sackc.append(bck)
        if bck.type == 'V' or bck.type == 'N':
            sackv.append(bck)
    return sackc, sackv


def countvowelsonrack():
    """Megállapítja a tartón levő magánhangzók+dzsókerek számát, a tartón levő karaktereket és előfordulásuk számát egy
    dict-ben adja vissza"""
    numberofvowels = 0
    lrack = dict()
    for bck in rack:
        if bck != 0 and bck is not None:
            if bck.letter in lrack:
                lrack[bck.letter] += 1
            else:
                lrack[bck.letter] = 1
            if bck.type == 'V' or bck.type == 'N':
                numberofvowels += 1
    return numberofvowels, lrack


def drawletter(j):
    """Alapesetben kihúz egy véletlen betűt, ha az options.optimizeddraw = True, akkor amíg a szükséges számú betűt
     tartalmazza a zsák, addig a magánhangzók+dzsókerek számát 40-60%-os arányban  tartja, illetve maximum 2
     egyforma betű lehet egyidejűleg a tartón, ha van még elég betű a zsákban"""
    while 1:
        randomnumber = randrange(len(sack))
        if options.optimizeddraw:
            sackc, sackv = sortsack()
            numberofvowels, lrack = countvowelsonrack()

            #print("mhg", "msg","arány", numberofvowels, lrack, numberofvowels / options.racksize )
            if (j+1) / options.racksize > 0.6:
                if sack[randomnumber].type == 'C' and numberofvowels / options.racksize < 0.4 and len(sackv) > 0:
                    #print("magánhangzót inkább")
                    continue
                if sack[randomnumber].type == 'V' and numberofvowels / options.racksize > 0.6 and len(sackc) > 0:
                    #print("mássalhangzót inkább")
                    continue
            if sack[randomnumber].letter in lrack and lrack[sack[randomnumber].letter] == 2:
                #print("van már belőle kettő a tartón", sack[randomnumber].letter)
                cou = 0
                for bck in sack:
                    if bck.type == sack[randomnumber].type:
                        cou += 1
                if cou > 2:
                    continue
        break
    return randomnumber


def changejoker(sbrick):
    """Dzsóker becserélésére szolgáló ablakot jeleníti meg"""
    global popup1
    popup1 = Toplevel()
    popup1.transient(appwin)
    popup1.title("Válassz egy betűt")
    popup1.protocol("WM_DELETE_WINDOW", close2)
    i = 0
    j = 0
    button = []
    while 1:
        if j == len(bricks):
            break
        letter = bricks[j].letter
        if letter == '*':
            j += 1
        else:
            button.append('*')
            button[i] = Button(popup1, width=buttonwidth + 2, height=1, padx=1, pady=1, text=letter, font=("Sans", 15),
                               bg="#cecece", command=lambda letter=letter: changej(letter, sbrick))
            button[i].grid(row=i // 7, column=i % 7)
            i += 1
            j += 1
    popup1.grab_set()
    appwin.wait_window(popup1)


def close2():
    pass


def changej(letter, sbrick):
    """Lerakott dzsókert a megfelelő betűre cseréli a táblán"""
    sbrick.changedletter = letter
    # print("changed:", sbrick.changedletter)
    if options.valueofchangedletter:
        for i in sack1:
            if i.letter == letter:
                v = i.value
                sbrick.objectlist[2] = canvas1.create_text(sbrick.b1x + options.wx, sbrick.b1y + options.wy,
                                                           font=(options.valuefont, options.valuefontsize), text=v,
                                                           fill=options.colorvaluebrick)
                sbrick.changedvalue = sbrick.value
                sbrick.value = i.value
                break
    sbrick.objectlist[1] = canvas1.create_text(sbrick.cx, sbrick.cy + 2,
                                               font=(options.letterfont, options.letterfontsize),
                                               text=sbrick.changedletter)
    popup1.destroy()


def changeletter(sbrick):
    """Betű kicserélésére szolgáló ablakot jeleníti meg"""
    global popup1
    popup1 = Toplevel()
    popup1.transient(appwin)
    popup1.title("Válaszd ki a megfelelő betűt")
    popup1.protocol("WM_DELETE_WINDOW", close2)
    x1, y1, x2, y2 = canvas1.bbox(sbrick.objectlist[0])
    x = x2 + canvas1.winfo_rootx()
    y = y2 + canvas1.winfo_rooty()
    popup1.wm_geometry("%dx%d+%d+%d" % (3*options.size, options.size, x, y))
    button = ['.'] * len(letterreplacedict[sbrick.letter])
    for i in range(len(letterreplacedict[sbrick.letter])):
        letter = letterreplacedict[sbrick.letter][i]
        button[i] = Button(popup1, width=buttonwidth + 2, height=1, padx=1, pady=1, text=letter, font=("Sans", 15),
                           bg="#cecece", command=lambda letter=letter: changel(letter, sbrick))
        button[i].grid(row=i // 7, column=i % 7)
        i += 1
    popup1.grab_set()
    appwin.wait_window(popup1)


def changel(letter, sbrick):
    """Lerakott karaktert a megfelelő betűre cseréli a táblán"""
    sbrick.changedletter = letter
    # print("changed:", sbrick.changedletter)
    sbrick.objectlist[1] = canvas1.create_text(sbrick.cx, sbrick.cy + 2,
                                               font=(options.letterfont, options.letterfontsize),
                                               text=sbrick.changedletter)
    popup1.destroy()


def lettersontheboard():
    """A játékos által a táblára rakott betűket vizsgálja (van-e lerakott betű, egyvonalba esnek-e, vízszintesen vagy
    függőlegesen )"""
    global rack
    global frack
    urack = []
    urack.extend(rack)
    if options.usefletters:
        urack.extend(frack)
    k = []
    across = down = True
    for i in range(len(urack)):
        if urack[i] is not None and ontheboard(urack[i].x, urack[i].y) and not onthetray(urack[i].x, urack[i].y):
            k.append(urack[i])
    if options.checkmode != 4:
        if options.onedirection and len(k) < 2:
           short()
           return
        if len(k) > 0:
            for i in range(len(k)):
                if k[i].y != k[0].y:
                    across = False
                    break
            for i in range(len(k)):
                if k[i].x != k[0].x:
                    down = False
                    break
            if across:
                direction = "across"
                lob = sorted(k, key=attrgetter('x'))
            elif down:
                direction = "down"
                lob = sorted(k, key=attrgetter('y'))
            else:
                # Ha nem esnek egyvonalba:
                notline()
                return
            validmove(lob, direction)
        # Passz?
        else:
            pass1()
            return
    else:
        manageboard(k)


def manageboard(lob):
    """Ha a szavak érvényességének ellenőrzése csak a játék végén történik, akkor tábla aktualizálása
    itt történik"""
    global fieldrc
    global fieldcc
    global fields
    for k in range(len(lob)):
        for i in range(fieldrc):
            for j in range(fieldcc):
                if lob[k].x == fields[i][j].x and lob[k].y == fields[i][j].y:
                    if lob[k].letter != '*' or options.dontchangejoker:
                        if lob[k].letter != '*' and lob[k].letter in letterreplacedict:
                            fields[i][j].type = lob[k].changedletter
                        else:
                            fields[i][j].type = lob[k].letter
                    else:
                        fields[i][j].type = lob[k].changedletter
                    fields[i][j].value = lob[k].value
                    fields[i][j].changedletter = lob[k].changedletter
                    fields[i][j].multiplier = lob[k].multiplier
                    fields[i][j].wordmultiplier = lob[k].wordmultiplier
                    fields[i][j].objectlist[0] = lob[k].objectlist[0]
                    fields[i][j].objectlist[1] = lob[k].objectlist[1]
                    fields[i][j].objectlist[2] = lob[k].objectlist[2]
                    fields[i][j].objectlist[3] = lob[k].objectlist[3]
                    fields[i][j].objectlist[4] = lob[k].objectlist[4]
    endmove(lob)


def checkboard():
    """A játék végén elindítja a tábla ellenőrzését"""
    global checktime
    global timeractive
    contiguous = checkcontiguity()
    print("contiguous",contiguous)
    if not contiguous:
        errormessage("A lerakott betűk között vannak, amelyek nem kapcsolódnak, vagy a szólánc nem halad át a "
                     "kezdőmezőn (ha ez be van állítva).\nKattints az OK gombra, majd jelöld ki a felesleges betűket.\n"
                     "Ha kész, kattints a Rendben gombra", appwin)
        chatboxmessage("Jelöld ki azokat a betűket a táblán, amelyek eltávolítása után csak kapcsolódó betűk maradnak "
                       "a táblán, és a szólánc áthalad a kezdőmezőn (ha az be van állítva), majd kattints a Rendben "
                       "gombra.\n")
        timeractive = False
        checktime = True
        bind1()
        return
    notvalid = validboard()
    if notvalid:
        timeractive = False
        checktime = True
        bind1()
        errormessage(",".join(notvalid) + " nincs a szótárban.\nKattints az OK gombra, majd jelöld ki a felesleges "
                                          "betűket.\nHa kész, kattints a Rendben gombra", appwin)
        chatboxmessage(",".join(notvalid) + " nincs a szótárban\nJelöld ki azokat a betűket a táblán, amelyek "
                                            "eltávolítása után a táblán csak érvényes szavak maradnak."
                                            " Ha kész, kattints a Rendben gombra\n")
    else:
        checktime = False
        endofgame()


def checkcontiguity():
    global boardtemp1
    global boardoriginal
    global onthestartfield
    global contiguousletters
    onthestartfield = False
    boardtemp1 = copy.deepcopy(board)
    print("boardoriginal",boardoriginal)
    found = False
    for i in range(fieldrc):
        for j in range(fieldcc):
            if not fields[i][j].ignored and fields[i][j].type != board[i][j] and boardoriginal[i][j] != '?':
                contiguousletters = [[i, j]]
                findneighbours()
                found = True
                break
        if found:
            break
    for i in range(fieldrc):
        for j in range(fieldcc):
            if not fields[i][j].ignored and fields[i][j].type != board[i][j] and boardtemp1[i][j] != "checked" and boardoriginal[i][j] != '?':
                print("ii,jj",i,j,fields[i][j].type,board[i][j],boardtemp1[i][j])
                if len(contiguousletters) > 0:
                    findneighbours()
                    for sor in boardtemp1:
                        print(sor)
                return False
    if options.startfield and not onthestartfield:
        return False
    return True


def validboard():
    """Ha a szavak érvényességének ellenőrzése csak a játék végén történik, akkor a táblára került szavak
    ellenőrzése itt történik"""
    global fieldrc
    global fieldcc
    global fields
    wordsfields = []
    words = []
    # Vízszintesen:
    for i in range(fieldrc):
        word = ''
        wordfields = []
        for j in range(fieldcc):
            if fields[i][j].type not in options.fieldsdict and not fields[i][j].ignored:
                word += fields[i][j].type
                if board[i][j] in options.fieldsdict:
                    l1 = board[i][j]
                else:
                    l1 = "old"
                wordfields.append([fields[i][j], l1, i, j])
            if fields[i][j].type in options.fieldsdict or j == fieldcc-1 or fields[i][j].ignored:
                if len(wordfields) > 1:
                    words.append(word)
                    print("szó",word)
                    wordsfields.append(wordfields)
                wordfields = []
                word = ''
    # Függőlegesen:
    for j in range(fieldcc):
        word = ''
        wordfields = []
        for i in range(fieldrc):
            if fields[i][j].type not in options.fieldsdict and not fields[i][j].ignored:
                word += fields[i][j].type
                if board[i][j] in options.fieldsdict:
                    l1 = board[i][j]
                else:
                    l1 = "old"
                wordfields.append([fields[i][j], l1, i, j])
            if fields[i][j].type in options.fieldsdict or i == fieldrc - 1 or fields[i][j].ignored:
                if len(wordfields) > 1:
                    words.append(word)
                    print("szó",word)
                    wordsfields.append(wordfields)
                wordfields = []
                word = ''
    notvalid = findindictionary(wordsfields)
    if notvalid:
        return notvalid
    boardscore(wordsfields)
    return notvalid


def findneighbours():
    global boardtemp1
    global boardoriginal
    global onthestartfield
    global contiguousletters
    #print(contiguousletters)
    i = contiguousletters[0][0]
    j = contiguousletters[0][1]
    #print("i,j",i,j)
    if options.startfield:
        if i == options.startfieldx and j == options.startfieldy:
            onthestartfield = True
    if i < fieldrc-1:
        if not fields[i + 1][j].ignored and (fields[i + 1][j].type != board[i + 1][j] or boardoriginal[i + 1][j] == '?')\
                and boardtemp1[i + 1][j] != "checked":
            contiguousletters.append([i + 1, j])
    if i > 0:
        if not fields[i - 1][j].ignored and (fields[i - 1][j].type != board[i - 1][j] or boardoriginal[i - 1][j] == '?')\
                and boardtemp1[i - 1][j] != "checked":
            contiguousletters.append([i - 1, j])
    if j < fieldcc-1:
        if not fields[i][j + 1].ignored and (fields[i][j + 1].type != board[i][j + 1] or boardoriginal[i][j + 1] == '?')\
                and boardtemp1[i][j + 1] != "checked":
            contiguousletters.append([i, j + 1])
    if j > 0:
        if not fields[i][j - 1].ignored and (fields[i][j - 1].type != board[i][j - 1] or boardoriginal[i][j - 1] == '?')\
                and boardtemp1[i][j - 1] != "checked":
            contiguousletters.append([i, j - 1])
    boardtemp1[i][j] = "checked"
    contiguousletters.pop(0)
    #print("szomszédok", contiguousletters)
    if len(contiguousletters) > 0:
        findneighbours()
    else:
        pass
        #print("boardtemp1",boardtemp1)

def validmove(lob, direction):
    """Tovább vizsgálja a lépés érvényességét (folyamatosan vannak-e a betűk, minden irányban érvényes szót alkotnak-e,
    többjátékos módban, ha érvényes a lépés, elküldi a szervernek)"""
    global textbox1
    global sec
    global fieldrc
    global fieldcc
    global fields, fieldstemp
    global firstmove
    global turnscore
    global novalidw
    global lastword
    rec = []
    fob = []
    word = ''
    wordrec = []
    wordfields = []
    words = []
    wordsfields = []
    wordsfields1 = []
    onthestartfield = False
    fieldstemp = copy.deepcopy(fields)
    lobch = []
    ii = None
    jj = None
    # Az újonnan lerakott betűk és a tábla előző állapota egy ideiglenes táblára kerül
    for k in range(len(lob)):
        for i in range(fieldrc):
            for j in range(fieldcc):
                if lob[k].x == fieldstemp[i][j].x and lob[k].y == fieldstemp[i][j].y:
                    if lob[k].letter != '*' or options.dontchangejoker:
                        if lob[k].letter != '*' and lob[k].letter in letterreplacedict:
                            fieldstemp[i][j].type = lob[k].changedletter
                        else:
                            fieldstemp[i][j].type = lob[k].letter
                    else:
                        fieldstemp[i][j].type = lob[k].changedletter
                    fieldstemp[i][j].value = lob[k].value
                    fieldstemp[i][j].changedletter = lob[k].changedletter
                    fieldstemp[i][j].multiplier = lob[k].multiplier
                    fieldstemp[i][j].wordmultiplier = lob[k].wordmultiplier
                    rec.append(lob[k].letter)
                    rec.append(lob[k].value)
                    rec.append(i)
                    rec.append(j)
                    fob.append(rec)
                    rec = []
                    if options.startfield and firstmove:
                        if i == options.startfieldx and j == options.startfieldy:
                            onthestartfield = True
    if firstmove:
        if options.startfield and not onthestartfield:
            notstartfield()
            return

    if len(lob) == 1:    # Ha csak 1 új betű kerül a táblára, akkor itt dől el a szó iránya
        directionset = False
        try:
            if fieldstemp[fob[0][2]][fob[0][3]-1].type not in options.fieldsdict:
                direction = "across"
                directionset = True
        except IndexError:
            pass
        try:
            if fieldstemp[fob[0][2]][fob[0][3]+1].type not in options.fieldsdict:
                direction = "across"
                directionset = True
        except IndexError:
            pass
        if not directionset:
            direction = "down"

    row = fieldrc
    col = fieldcc
    # Az új betűkkel összefüggő összes string felépítése
    # ------------------------------------------------------------------------------------------------------------------
    # Vízszintesen:
    if direction == "across":
        ii = fob[k][2]
    for k in range(len(fob)):
        inside = True
        i = fob[k][2]
        j = fob[k][3]
        if j < col:  # A lerakott betűk bal felső tagját keressük
            col = j
        while inside:
            if fieldstemp[i][j - 1].type not in options.fieldsdict and j > 0:
                j -= 1
            else:
                inside = False
        inside = True
        copl = 0
        while inside:
            word += fieldstemp[i][j].type
            wordrec.append(fieldstemp[i][j])
            if direction == "across":
                lobch.append(fieldstemp[i][j].type)
                if jj is None:
                    jj = j
            if fieldstemp[i][j].type != fields[i][j].type:
                copl = 0
                wordrec.append(board[i][j])
            else:
                copl += 1
                if options.onedirection and copl > 1:
                    appended()
                    return
                wordrec.append("old")
            wordfields.append(wordrec)
            wordrec = []
            if j + 1 < fieldcc:
                if fieldstemp[i][j + 1].type not in options.fieldsdict:
                    j += 1
                else:
                    inside = False
            else:
                inside = False
        # Ha a szó hosszabb mint egy betű:
        if len(wordfields) > 1:
            words.append(word)
            wordsfields.append(wordfields)
        if direction == "across":
            wordsfields1.append(wordfields)
        word = ''
        wf = wordfields
        wordfields = []
        # A szó tartalmazza-e az összes lerakott betűt? Ha nem, akkor hibaüzenet:
        if direction == "across":
            for m in range(len(lob)):
                find = False
                for n in range(len(wf)):
                    if lob[m].x == wf[n][0].x:
                        find = True
                        break
                if not find:
                    notcontinuous()
                    return
            break
    # ------------------------------------------------------------------------------------------------------------------
            # Függőlegesen:
    if direction == "down":
        jj = fob[k][3]
    for k in range(len(fob)):
        inside = True
        i = fob[k][2]
        j = fob[k][3]
        if i < row:  # A lerakott betűk bal felső tagját keressük
            row = i
        while inside:
            if fieldstemp[i - 1][j].type not in options.fieldsdict and i > 0:
                i -= 1
            else:
                inside = False
        inside = True
        copl = 0
        while inside:
            word += fieldstemp[i][j].type
            wordrec.append(fieldstemp[i][j])
            if direction == "down":
                lobch.append(fieldstemp[i][j].type)
                if ii is None:
                    ii = i
            if fieldstemp[i][j].type != fields[i][j].type:
                wordrec.append(board[i][j])
                copl = 0
            else:
                copl += 1
                if options.onedirection and copl > 1:
                    appended()
                    return
                wordrec.append("old")
            wordfields.append(wordrec)
            wordrec = []
            if i + 1 < fieldrc:
                if fieldstemp[i + 1][j].type not in options.fieldsdict:
                    i += 1
                else:
                    inside = False
            else:
                inside = False
        # Ha a szó hosszabb mint egy betű:
        if len(wordfields) > 1:
            words.append(word)
            wordsfields.append(wordfields)
        if direction == "down":
            wordsfields1.append(wordfields)
        word = ''
        wf = wordfields
        wordfields = []
        # A szó tartalmazza-e az összes lerakott betűt? Ha nem, akkor hibaüzenet:
        if direction == "down":
            for m in range(len(lob)):
                find = False
                for n in range(len(wf)):
                    if lob[m].y == wf[n][0].y:
                        find = True
                        break
                if not find:
                    notcontinuous()
                    return
            break
    # ------------------------------------------------------------------------------------------------------------------
    if len(wordsfields) == 0:
        return
    allletter = 0
    for z in range(len(words)):
        allletter += len(wordsfields[z])
    if len(lob) == allletter and not firstmove and options.connect:
        notcontinuous()
        return
    notvalid = findindictionary(wordsfields)
    #print("wordsfields",wordsfields)
    if notvalid is None:
        return
    # Ha minden szó érvényes, vagy nem kell vizsgálni az érvényességet:
    if len(notvalid) == 0:
        # Pontérték számítása:
        if options.onedirection:
            wordsfields = wordsfields1
        score(wordsfields)
        lobl = []
        for l5 in range(len(lob)):
            lobl.append(lob[l5].letter)
            lobl.append(str(lob[l5].value))
            lobl.append(str(lob[l5].wordmultiplier))
            lobl.append(lob[l5].type)
        wordsfieldss = []
        for n in range(len(wordsfields)):
            ww = []
            for l6 in range(len(wordsfields[n])):
                ww.append(wordsfields[n][l6][0].type)
            wordsfieldss.append("".join(ww))
        if direction == "down":
            wordsfieldss[0], wordsfieldss[-1] = wordsfieldss[-1], wordsfieldss[0]
        wordsinmove = "+".join(wordsfieldss)
        direction1 = ""
        if direction == "across":
            direction1 = "vízsz."
        elif direction == "down":
            direction1 = "függő."

        chatboxmessage(options.username + ": " + wordsinmove + " Pozíció:" + numberstoletters(ii) + "," +
                       str(jj+1) + "," + direction1 + " " + str(turnscore) + " pont\n")
        lastword = "*Név:" + str(turns+1) + "," + wordsfieldss[0] + "," + str(turnscore) + ",(" + numberstoletters(ii)\
                   + "," + str(jj+1) + "," + direction1[0].upper() + ")*"
        novalidw = False
        # Hálózati játékban lépés küldése a szervernek:
        if options.gamemode != 1:
            moveofhuman = "MOVE" + "," + wordsinmove + ";POS," + str(ii) + "," + str(
                          jj) + ";DIR," + direction + ";SCORE," + str(turnscore) + ";LOB," + ",".join(lobl)+";LOBCH," +\
                          ",".join(lobch)
            # print("sent:", moveofhuman)
            queue1.put(moveofhuman)
            if not options.duplicate:
                lockon()
                time.sleep(2)
                if options.gamemode != 1:
                    unbind1()
        if not options.duplicate or options.gamemode == 1:
            endmove(lob)
        if not options.duplicate:
            turnscore = 0
        firstmove = False
    else:                                # Ha érvénytelen valamelyik szó, hibaüzenet:
        errormessage(",".join(notvalid) + " nincs a szótárban", appwin)


def endmove(lob):
    """Befejezi a lépést (szimultán módban a szerver által kiválasztott legjobb szó visszakapása után, egyébként
    azonnal)"""
    global firstmove
    global turns
    global turnscore
    global countofpasses
    if not (firstmove and options.independentboards):
        printboard()
    if not options.independentboards:
        firstmove = False
    repairboard()
    # Körök számának ellenőrzése:
    if options.gamemode == 1:
        turns += 1
        if options.turnlimit and turns == options.turnlimitcount:
            if options.checkmode == 4:
                checkboard()
                return
            else:
                endofgame()
                return
        counter.configure(text=turns + 1)
    # Kirakott betűk törlése a rack[] listából vagy az összes/felhasznált visszamegy a sack[] listába:
    if options.resetsack:
        resetsack(lob)
    else:
        for i in range(len(lob)):
            for j in range(len(rack)):
                if rack[j] == lob[i]:
                    rack[j] = None
    # A rack[] lista megüresedett helyeinek feltöltése:
    if options.gamemode == 1:
        loadrack()
        if options.usefletters and options.resetfrack:
            loadfrack()
        bind1()
    countofpasses = 0
    # Kirakott betűk törlése a frack[] listából:
    for i in range(len(lob)):
        for j in reversed(range(len(frack))):
            if frack[j] == lob[i]:
                frack.pop(j)
    # Ha a korlátozott láthatóság be van állítva, a láthatóvá váló mezők kezelése
    if options.limitedvisibility:
        for k in range(len(lob)):
            for i in range(fieldrc):
                for j in range(fieldcc):
                   if lob[k].x == fieldstemp[i][j].x and lob[k].y == fieldstemp[i][j].y:
                       #print("i,j",i,j)
                       assignvisiblefields(i,j)
    if options.duplicate:
        turnscore = 0


def printrack():
    rack1 = ""
    for i in range(len(rack)):
        if rack[i] is not None:
            rack1 += rack[i].letter + " "
        else:
            rack1 = rack1 + "_"
    # print("\n"+rack1+"\n")


def printboard():
    print("")
    sor = ""
    if not options.duplicate or options.gamemode == 1:
        canvas1.delete("newletter")
    for i in range(fieldrc):
        for j in range(fieldcc):
            if options.checkmode != 4:
                if fields[i][j].type != fieldstemp[i][j].type:
                   canvas1.create_rectangle(fields[i][j].b1x, fields[i][j].b1y, fields[i][j].b2x, fields[i][j].b2y,
                                            width=1, outline="yellow", tags="newletter")
                fields[i][j] = fieldstemp[i][j]
            if len(fields[i][j].type) == 1:
                sor += fields[i][j].type + " "
            else:
                sor += fields[i][j].type
        #print("client",sor)
        sor = ""


def findindictionary(wordsfields):
    """Létrejött szavak érvényességének vizsgálata szótár alapján"""
    global timesup
    notvalid = []
    word1l = []
    numofjokers = 0
    for i in range(len(wordsfields)):
        for j in range(len(wordsfields[i])):
            if wordsfields[i][j][0].type != '*' or options.dontchangejoker:
                if wordsfields[i][j][0].type == '*':
                    numofjokers += 1
                word1l.append(wordsfields[i][j][0].type)
            else:
                word1l.append(wordsfields[i][j][0].changedletter)
        word = "".join(word1l)
        if options.dontchangejoker and numofjokers > 0:
            found = False
            for perm in itertools.permutations(notjokerbricks, numofjokers):
                l1 = 0
                word2l = word1l[:]
                for m in range(len(word1l)):
                    if word1l[m] == "*":
                        word2l[m] = perm[l1].letter
                        l1 += 1
                if checkenchant:
                    word2s = "".join(word2l)
                    found = spellcheck(word2s)
                else:
                    found = findinapartofdictionary(word2l)
                if found:
                    break
            if not found:
                notvalid.append(word)
            word1l = []
        else:
            if checkenchant:
                found = spellcheck(word)
            else:
                #print("word1l",word1l)
                found = findinapartofdictionary(word1l)
            if not found:
                notvalid.append(word)
            word1l = []
    if not options.checkdictionary:
        if len(notvalid) != 0 and options.checkmode != 4:
            timesup = False
            if not tkinter.messagebox.askokcancel("Érvényes?", ",".join(
                    notvalid) + " nincs a szótárban. Maradjon a táblán ennek ellenére?"):
                return
            if timesup:
                return
            notvalid = []
    return notvalid


def findinapartofdictionary(word1l):
    """Lista formátumban megadott szó keresése a kezdőbetű+hossz által meghatározott részszótárban"""
    # print("word1l", word1l)
    for w in partsofdictionary[word1l[0]+str(len(word1l))]:
        if w == tuple(word1l):
            return True


def spellcheck(word):
    if dicthu.check(word):
        return True


def score(wordsfields):
    """Pontérték meghatározása (ha lépésenként történik)"""
    global totalscore
    global turnscore
    if turnscore != 0:
        totalscore -= turnscore
        score2.config(text=str(totalscore))
        turnscore = 0
        score1.config(text=str(turnscore))
    for i in range(len(wordsfields)):
        wordvaluemulti = 1
        wordscore = 0
        ul = 0
        for j in range(len(wordsfields[i])):
            if wordsfields[i][j][1] == "2W":
                wordvaluemulti = 2 * wordvaluemulti
            elif wordsfields[i][j][1] == "3W":
                wordvaluemulti = 3 * wordvaluemulti
            if wordsfields[i][j][1] == "2L":
                wordscore += wordsfields[i][j][0].value * 2
            elif wordsfields[i][j][1] == "3L":
                wordscore += wordsfields[i][j][0].value * 3
            else:
                if options.useoldbonus and wordsfields[i][j][1] == "old":
                    if options.oldbonusonly:
                        wordscore += options.useoldbonusvalue
                    else:
                        wordscore += options.useoldbonusvalue
                        wordscore += wordsfields[i][j][0].value
                else:
                    wordscore += wordsfields[i][j][0].value
            if wordsfields[i][j][1] != "old":
                ul += 1
                if len(wordsfields[i][j][1]) == 1 and wordsfields[i][j][1].isdigit():
                    wordscore += int(wordsfields[i][j][1])
                if wordsfields[i][j][0].wordmultiplier == 2:
                    wordvaluemulti = 2 * wordvaluemulti
                elif wordsfields[i][j][0].wordmultiplier == 3:
                    wordvaluemulti = 3 * wordvaluemulti
        turnscore = turnscore + wordscore * wordvaluemulti
        if options.lengthbonus:
            if ul == 2:
                turnscore += options.twoletterbonus
            elif ul == 3:
                turnscore += options.threeletterbonus
            elif ul == 4:
                turnscore += options.fourletterbonus
            elif ul == 5:
                turnscore += options.fiveletterbonus
            elif ul == 6:
                turnscore += options.sixletterbonus
            elif ul == 7:
                turnscore += options.sevenletterbonus
            elif ul == 8:
                turnscore += options.eightletterbonus
            elif ul == 9:
                turnscore += options.nineletterbonus
            elif ul == 10:
                turnscore += options.tenletterbonus
    if options.wordperturnbonus:
        turnscore += options.wordperturnbonusvalue * (len(wordsfields) - 1)
    score1.config(text=str(turnscore))
    totalscore += turnscore
    score2.config(text=str(totalscore))


def boardscore(wordsfields):
    """Pontérték meghatározása (ha a játék végén történik)"""
    global totalscore
    global board
    boardtemp2 = copy.deepcopy(board)
    for i in range(len(wordsfields)):
        wordscore = 0
        for j in range(len(wordsfields[i])):
            if boardtemp2[wordsfields[i][j][2]][wordsfields[i][j][3]] == "used":
                continue
            if wordsfields[i][j][1] == "2L":
                wordscore += wordsfields[i][j][0].value * 2
            elif wordsfields[i][j][1] == "3L":
                wordscore += wordsfields[i][j][0].value * 3
            else:
                if len(wordsfields[i][j][1]) == 1 and wordsfields[i][j][1].isdigit():
                    wordscore += int(wordsfields[i][j][1])
                if options.useoldbonus and wordsfields[i][j][1] == "old":
                    wordscore += options.useoldbonusvalue
                else:
                    wordscore += wordsfields[i][j][0].value
            boardtemp2[wordsfields[i][j][2]][wordsfields[i][j][3]] = "used"
        if options.wordlengthbonus:
            if len(wordsfields[i]) == 2:
                wordscore += options.wordtwoletterbonus
            elif len(wordsfields[i]) == 3:
                wordscore += options.wordthreeletterbonus
            elif len(wordsfields[i]) == 4:
                wordscore += options.wordfourletterbonus
            elif len(wordsfields[i]) == 5:
                wordscore += options.wordfiveletterbonus
            elif len(wordsfields[i]) == 6:
                wordscore += options.wordsixletterbonus
            elif len(wordsfields[i]) == 7:
                wordscore += options.wordsevenletterbonus
            elif len(wordsfields[i]) == 8:
                wordscore += options.wordeightletterbonus
            elif len(wordsfields[i]) == 9:
                wordscore += options.wordnineletterbonus
            elif len(wordsfields[i]) >= 10:
                wordscore += options.wordtenletterbonus
        totalscore += wordscore
    score2.config(text=str(totalscore))


def chatboxmessage(message, source="game"):
    """Szöveg megjelenítése"""
    textbox1.configure(state=NORMAL)
    if source == "chat":
        textbox1.insert(END, message, "Blue")
    else:
        textbox1.insert(END, message)
    textbox1.yview(END)
    textbox1.configure(state=DISABLED)


def selectfont():
    """Betűtípus választása"""
    global family1, size1

    def selectitem(event):
        global family1, size1

        widget = event.widget
        sel = listbox1.curselection()
        family1 = widget.get(sel[0])
        lbl0.configure(font=(family1, size1))

    def com1000(event):
        global size1
        size1 = int(v1000.get())
        lbl0.configure(font=(family1, size1))

    def com1001():
        popup5.destroy()

    popup5 = Toplevel()
    popup5.transient(popup4)
    popup5.title("Betűtípus választás")

    frame1000 = Frame(popup5, bg='#d6d6d6')
    frame1000.pack(side=LEFT)
    frame1001 = Frame(frame1000, bg='#d6d6d6')
    frame1001.pack(side=TOP)

    fonts = list(tkinter.font.families())
    fonts.sort()
    listbox1 = Listbox(frame1001)
    listbox1.pack(fill=BOTH, expand=YES, side=LEFT)
    scrollbar = Scrollbar(frame1001)
    scrollbar.pack(side=RIGHT, fill=Y, expand=NO)
    scrollbar.configure(command=listbox1.yview)
    listbox1.configure(yscrollcommand=scrollbar.set)
    listbox1.bind("<Double-Button-1>", selectitem)
    listbox1.bind("Return", selectitem)
    listbox1.bind('<KP_Enter>', selectitem)
    for f in fonts:
        listbox1.insert(END, f)

    v1000 = StringVar()
    v1000.set(size1)
    cb1000 = Combobox(frame1000, textvariable=v1000, width=10, justify="right")
    cb1000['values'] = 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30
    cb1000.bind('<<ComboboxSelected>>', com1000)
    cb1000.pack(side=BOTTOM)

    lbl0 = Label(popup5, text="0123456789\nAÁBCDEÉFGH\nIÍJKLMNOÓÖ\nŐPQRSTUÚÜŰ\nVWXYZ", font=(family1, size1))
    lbl0.pack(side=TOP)
    Button(popup5, text="Vissza", command=com1001).pack(side=BOTTOM)

    popup5.grab_set()
    popup4.wait_window(popup5)


def close1():
    global popup4
    global var200
    global ruleson1
    ruleson1 = 0
    var200.set(ruleson1)
    popup4.destroy()


def setup1(sow):
    """Beállítások kérdőív"""
    global popup4
    global options
    global icon1, icon2
    global notebook
    global tab1, tab2, tab3, tab4

    def com1(event):
        options.size = scale1.get()
        if options.fieldsize > options.size:
            options.fieldsize = options.size
        scale1a.configure(to=options.size)
        scale1a.set(options.fieldsize)
        drawfield(canvas3, options.fieldsize, options.gap)
        if options.bricksize > options.size:
            options.bricksize = options.size
        scale3.configure(to=options.size)
        scale3.set(options.bricksize)

    def com1a(event):
        options.fieldsize = scale1a.get()
        drawfield(canvas3, options.fieldsize, options.gap)

    def com2(event):
        options.gap = scale2.get()

    def com3(event):
        options.bricksize = scale3.get()
        drawbrick(canvas4, options.bricksize)

    def drawfield(canvas30, size, gap):
        canvas30.delete("all")
        canvas30.create_rectangle(1, 1, size, size, width=1, outline=options.colorborder, fill=options.colorfix)
        canvas30.create_text(size / 2 - 1, size / 2 - 1, font=(options.fixletterfont, options.fixletterfontsize),
                             text="SZ")

    def drawbrick(canvas40, bricksize):
        canvas40.delete("all")
        canvas40.create_rectangle(1, 1, bricksize, bricksize, width=1, outline=options.colorborderbrick,
                                  fill=options.colornormalbrick)
        canvas40.create_text(bricksize / 2 - 1, bricksize / 2 - 1, font=(options.letterfont, options.letterfontsize),
                             text="SZ")
        canvas40.create_text(options.wx, options.wy, font=(options.valuefont, options.valuefontsize), text='3',
                             fill=options.colorvaluebrick)

    def changecolor1(button, color11):
        c11 = color1(color11)
        button.configure(bg=c11[1], activebackground=c11[1])

    popup4 = Toplevel(appwin)
    popup4.transient(appwin)
    popup4.title("Beállítások")

    canvas2 = Canvas(popup4, bg="#bebebe", height=530, width=530)
    canvas2.pack(side=LEFT)

    notebook = Notebook(canvas2)
    tab1 = Frame(notebook)
    tab2 = Frame(notebook)
    tab3 = Frame(notebook)
    tab4 = Frame(notebook)

    if sow:
        sow1 = "normal"
        sow2 = "readonly"
    else:
        sow1 = sow2 = "disabled"
    # ---------------------------Tábla----------------------------
    canvas3 = Canvas(tab1, height=50, width=50)
    canvas3.grid(row=1, column=1)

    drawfield(canvas3, options.size, options.gap)

    label0 = Label(tab1, state=sow1, disabledforeground="gray50", text="Méret")
    label0.grid(row=1, column=2, sticky=E)

    CreateToolTip(label0, "Mező mérete")

    scale1 = Scale(tab1, length=110, orient=HORIZONTAL, troughcolor="#a9a9a9",
                   sliderlength=20, showvalue=1, from_=15, to=75, tickinterval=20, command=com1)
    scale1.set(options.size)
    scale1.grid(row=1, column=3)
    scale1.config(state=sow1)

    CreateToolTip(scale1, "Mező mérete")

    label0a = Label(tab1, state=sow1, disabledforeground="gray50", text="Méret")
    label0a.grid(row=1, column=4, sticky=E)

    CreateToolTip(label0a, "Jelölőnégyzet mérete")

    scale1a = Scale(tab1, length=110, orient=HORIZONTAL, troughcolor="#a9a9a9",
                    sliderlength=20, showvalue=1, from_=0, to=options.size, tickinterval=20, command=com1a)
    scale1a.set(options.fieldsize)
    scale1a.grid(row=1, column=5)
    scale1a.config(state=sow1)

    CreateToolTip(scale1a, "Jelölőnégyzet mérete")

    label1a = Label(tab1, state=sow1, disabledforeground="gray50", text="     Térköz")
    label1a.grid(row=1, column=6, sticky=E)

    CreateToolTip(label1a, "Mezők közötti térköz mérete")

    scale2 = Scale(tab1, length=110, orient=HORIZONTAL, troughcolor="#a9a9a9", sliderlength=20,
                   showvalue=1, from_=-1, to=10, tickinterval=5, command=com2)
    scale2.set(options.gap)
    scale2.grid(row=1, column=7)
    scale2.config(state=sow1)

    CreateToolTip(scale2, "Mezők közötti térköz mérete")

    label1 = Label(tab1, state=sow1, disabledforeground="gray50", text="Normál mező")
    label1.grid(row=2, column=1)

    button01 = Button(tab1, state=sow1, width=buttonwidth, bg=options.colornormal, activebackground=options.colornormal)
    button01.grid(row=2, column=2)
    button01.configure(command=lambda button=button01, color="colornormal": changecolor1(button, color))

    CreateToolTip(button01, "Szín módosítása")

    label2 = Label(tab1, state=sow1, disabledforeground="gray50", text="Előre beírt betű")
    label2.grid(row=3, column=1)

    button002 = Button(tab1, state=sow1, width=buttonwidth, bg=options.colorfix, activebackground=options.colorfix)
    button002.grid(row=3, column=2)
    button002.configure(command=lambda button=button002, color="colorfix": changecolor1(button, color))

    CreateToolTip(button002, "Szín módosítása")

    label3 = Label(tab1, state=sow1, disabledforeground="gray50", text="Betű értékét duplázó mező")
    label3.grid(row=4, column=1)

    button03 = Button(tab1, state=sow1, width=buttonwidth, bg=options.colordoubleL,
                      activebackground=options.colordoubleL)
    button03.configure(command=lambda button=button03, color="colordoubleL": changecolor1(button, color))
    button03.grid(row=4, column=2)

    CreateToolTip(button03, "Szín módosítása")

    label4 = Label(tab1, state=sow1, disabledforeground="gray50", text="Betű értékét triplázó mező")
    label4.grid(row=5, column=1)

    button04 = Button(tab1, state=sow1, width=buttonwidth, bg=options.colortripleL,
                      activebackground=options.colortripleL)
    button04.configure(command=lambda button=button04, color="colortripleL": changecolor1(button, color))
    button04.grid(row=5, column=2)

    CreateToolTip(button04, "Szín módosítása")

    label5 = Label(tab1, state=sow1, disabledforeground="gray50", text="Szó értékét duplázó mező")
    label5.grid(row=6, column=1)

    button05 = Button(tab1, state=sow1, width=buttonwidth, bg=options.colordoubleW, activebackground=options.colordoubleW)
    button05.configure(command=lambda button=button05, color="colordoubleW": changecolor1(button, color))
    button05.grid(row=6, column=2)

    CreateToolTip(button05, "Szín módosítása")

    label6 = Label(tab1, state=sow1, disabledforeground="gray50", text="Szó értékét triplázó mező")
    label6.grid(row=7, column=1)

    button06 = Button(tab1, state=sow1, width=buttonwidth, bg=options.colortripleW,
                      activebackground=options.colortripleW)
    button06.configure(command=lambda button=button06, color="colortripleW": changecolor1(button, color))
    button06.grid(row=7, column=2)

    CreateToolTip(button06, "Szín módosítása")

    label6a = Label(tab1, state=sow1, disabledforeground="gray50", text="Fal")
    label6a.grid(row=8, column=1)

    button6a = Button(tab1, state=sow1, width=buttonwidth, bg=options.colorwall,
                      activebackground=options.colorwall)
    button6a.configure(command=lambda button=button6a, color="colorwall": changecolor1(button, color))
    button6a.grid(row=8, column=2)

    CreateToolTip(button6a, "Szín módosítása")

    label7 = Label(tab1, state=sow1, disabledforeground="gray50", text="Keret")
    label7.grid(row=9, column=1)

    button7 = Button(tab1, state=sow1, width=buttonwidth, bg=options.colorborder,
                     activebackground=options.colorborder)
    button7.configure(command=lambda button=button7, color="colorborder": changecolor1(button, color))
    button7.grid(row=9, column=2)

    CreateToolTip(button7, "Szín módosítása")

    def com1a():
        options.fborder = var1a.get()

    var1a = BooleanVar()
    var1a.set(options.fborder)
    checkb1a = Checkbutton(tab1, state=sow1, disabledforeground="gray50", variable=var1a, command=com1a)
    checkb1a.grid(row=9, column=3, sticky=W)

    CreateToolTip(checkb1a, "Legyen-e keret?")

    label8 = Label(tab1, state=sow1, disabledforeground="gray50", text="Felirat")
    label8.grid(row=10, column=1)

    button8 = Button(tab1, state=sow1, width=buttonwidth, bg=options.colortext, activebackground=options.colortext)
    button8.configure(command=lambda button=button8, color="colortext": changecolor1(button, color))
    button8.grid(row=10, column=2)

    CreateToolTip(button8, "Szín módosítása")

    def com90a():
        global family1, size1

        family1 = options.fixletterfont
        size1 = options.fixletterfontsize
        selectfont()
        options.fixletterfont = family1
        options.fixletterfontsize = size1
        drawfield(canvas3, options.size, options.gap)

    button9 = Button(tab1, state=sow1, width=11, text="Betűtípus", command=com90a)
    button9.grid(row=10, column=3)

    CreateToolTip(button9, "Betűtípus kiválasztása")

    def com1x():
        options.numbering = var1x.get()

    var1x = BooleanVar()
    var1x.set(options.numbering)
    checkb1x = Checkbutton(tab1, state=sow1, disabledforeground="gray50", highlightthickness=0, borderwidth=0, pady=0,
                           text="Sorszámozás", variable=var1x, command=com1x)
    checkb1x.grid(row=11, column=1, sticky=W)

    CreateToolTip(checkb1x, "Legyenek-e a tábla sorai és oszlopai megszámozva.")

    icon1 = tkinter.PhotoImage(file="edit.gif")
    if len(board) > 0:
        button9a = Button(tab1, state=sow1, text="Szerkesztés", image=icon1, compound="top",
                          command=lambda: createoreditboard(board))
        button9a.grid(row=12, column=4)

        CreateToolTip(button9a, "A betöltött tábla módosítása")

    def com91():

        def com58(popup):

            if not validate1():
                return
            v1a = int(var430.get())
            v2a = int(var431.get())
            if v2a < options.rowmin or v1a < options.columnmin or v2a > options.rowmax or v1a > options.columnmax:
                tkinter.messagebox.showerror("Hibás érték", "1 és 99 között kell legyen", parent=popup4)
                return
            board1 = []
            options.width = int(var430.get())
            options.height = int(var431.get())
            for i in range(options.height):
                board1.append(['.'] * options.width)
            popup.destroy()
            createoreditboard(board1)

        def validate1():
            try:
                int(var430.get())
                int(var431.get())
                return 1
            except ValueError:
                tkinter.messagebox.showerror("Hibás érték", "1 és 99 között kell legyen", parent=popup4)
                return 0

        popup9 = Toplevel()
        popup9.title("Új tábla mérete")
        popup9.transient(popup4)
        label113 = Label(popup9, text="Szélesség:")
        label113.grid(row=0, column=0)
        label113.focus_set()

        var430 = StringVar()
        var430.set(options.width)

        entry8 = Entry(popup9, width=2, bg="white", relief=SUNKEN, textvariable=var430, justify="right")
        entry8.grid(row=0, column=1)

        label114 = Label(popup9, text="Magasság:")
        label114.grid(row=1, column=0)
        var431 = StringVar()
        var431.set(options.height)
        entry9 = Entry(popup9, width=2, bg="white", relief=SUNKEN, textvariable=var431, justify="right")
        entry9.grid(row=1, column=1)

        button222 = Button(popup9, state=sow1, text='Rendben', command=lambda popup=popup9: com58(popup))
        button222.grid(row=2, column=1, sticky=E + W)

        popup9.grab_set()
        popup4.wait_window(popup9)

    icon2 = tkinter.PhotoImage(file="new.gif")

    button9b = Button(tab1, state=sow1, text="Új tábla", image=icon2, compound="top", command=com91)
    button9b.grid(row=12, column=5)

    CreateToolTip(button9b, "Új tábla készítése")

    button01 = Button(tab1, width=11, text="Vissza", command=close1)
    button01.grid(row=15, column=5)

    CreateToolTip(button01, "Kilépés a beállításokból")

    # -----------------------Betűk-----------------------

    canvas4 = Canvas(tab2, height=50, width=50)
    canvas4.grid(row=1, column=1)

    drawbrick(canvas4, options.bricksize)

    label10 = Label(tab2, state=sow1, disabledforeground="gray50", text="Méret")
    label10.grid(row=1, column=2, sticky=E)

    CreateToolTip(label10, "Betű mérete")

    scale3 = Scale(tab2, length=110, orient=HORIZONTAL, troughcolor="#a9a9a9", sliderlength=20,
                   showvalue=1, from_=0, to=options.size, tickinterval=20, command=com3)
    scale3.set(options.bricksize)
    scale3.grid(row=1, column=3)
    scale3.config(state=sow1)

    CreateToolTip(scale3, "Betű mérete")

    label11 = Label(tab2, state=sow1, disabledforeground="gray50", text="Normál betű")
    label11.grid(row=2, column=1)

    button11 = Button(tab2, state=sow1, width=buttonwidth, bg=options.colornormalbrick,
                      activebackground=options.colornormalbrick)
    button11.configure(command=lambda button=button11, color="colornormalbrick": changecolor1(button, color))
    button11.grid(row=2, column=2)

    CreateToolTip(button11, "Szín módosítása")

    label12 = Label(tab2, state=sow1, disabledforeground="gray50", text="Dupla értékű betű")
    label12.grid(row=3, column=1)

    button12 = Button(tab2, state=sow1, width=buttonwidth, bg=options.colordoublebrick,
                      activebackground=options.colordoublebrick)
    button12.configure(command=lambda button=button12, color="colordoublebrick": changecolor1(button, color))
    button12.grid(row=3, column=2)

    CreateToolTip(button12, "Szín módosítása")

    label13 = Label(tab2, state=sow1, disabledforeground="gray50", text="Tripla értékű betű")
    label13.grid(row=4, column=1)

    button13 = Button(tab2, state=sow1, width=buttonwidth, bg=options.colortriplebrick,
                      activebackground=options.colortriplebrick)
    button13.configure(command=lambda button=button13, color="colortriplebrick": changecolor1(button, color))
    button13.grid(row=4, column=2)

    CreateToolTip(button13, "Szín módosítása")

    label14a = Label(tab2, state=sow1, disabledforeground="gray50", text="Szó értékét duplázó betű")
    label14a.grid(row=5, column=1)

    button14a = Button(tab2, state=sow1, width=buttonwidth, bg=options.colordoublewordbrick,
                       activebackground=options.colordoublewordbrick)
    button14a.configure(command=lambda button=button14a, color="colordoublewordbrick": changecolor1(button, color))
    button14a.grid(row=5, column=2)

    CreateToolTip(button14a, "Szín módosítása")

    label14b = Label(tab2, state=sow1, disabledforeground="gray50", text="Szó értékét triplázó betű")
    label14b.grid(row=6, column=1)

    button14b = Button(tab2, state=sow1, width=buttonwidth, bg=options.colortriplewordbrick,
                       activebackground=options.colortriplewordbrick)
    button14b.configure(command=lambda button=button14b, color="colortriplewordbrick": changecolor1(button, color))
    button14b.grid(row=6, column=2)

    CreateToolTip(button14b, "Szín módosítása")

    label14 = Label(tab2, state=sow1, disabledforeground="gray50", text="Felirat")
    label14.grid(row=7, column=1)

    button14 = Button(tab2, state=sow1, width=buttonwidth, bg=options.colortextbrick,
                      activebackground=options.colortextbrick)
    button14.configure(command=lambda button=button14, color="colortextbrick": changecolor1(button, color))
    button14.grid(row=7, column=2)

    CreateToolTip(button14, "Szín módosítása")

    def com91a():
        global family1, size1

        family1 = options.letterfont
        size1 = options.letterfontsize
        selectfont()
        options.letterfont = family1
        options.letterfontsize = size1
        drawbrick(canvas4, options.bricksize)

    button14a = Button(tab2, state=sow1, width=11, text="Betűtípus", command=com91a)
    button14a.grid(row=7, column=3)

    CreateToolTip(button14a, "Betűtípus kiválasztása")

    label15 = Label(tab2, state=sow1, disabledforeground="gray50", text="Érték")
    label15.grid(row=8, column=1)

    def com2b():
        options.valuedisplay = var2b.get()
        if not options.valuedisplay:
            options.colorvaluebrick = options.colornormalbrick

    var2b = BooleanVar()
    var2b.set(options.valuedisplay)
    checkb2b = Checkbutton(tab2, state=sow1, disabledforeground="gray50", variable=var2b, command=com2b)
    checkb2b.grid(row=8, column=4, sticky=W)

    CreateToolTip(checkb2b, "Legyenek-e megjelenítve a pontértékek?")


    button15 = Button(tab2, state=sow1, width=buttonwidth, bg=options.colorvaluebrick,
                      activebackground=options.colorvaluebrick)
    button15.configure(command=lambda button=button15, color="colorvaluebrick": changecolor1(button, color))
    button15.grid(row=8, column=2)

    CreateToolTip(button15, "Szín módosítása")

    def com92a():
        global family1, size1

        family1 = options.valuefont
        size1 = options.valuefontsize
        selectfont()
        options.valuefont = family1
        options.valuefontsize = size1
        drawbrick(canvas4, options.bricksize)

    button15a = Button(tab2, state=sow1, width=11, text="Betűtípus", command=com92a)
    button15a.grid(row=8, column=3)

    CreateToolTip(button15a, "Betűtípus kiválasztása")

    label16 = Label(tab2, state=sow1, disabledforeground="gray50", text="Keret")
    label16.grid(row=9, column=1)

    button16 = Button(tab2, state=sow1, width=buttonwidth, bg=options.colorborderbrick,
                      activebackground=options.colorborderbrick)
    button16.configure(command=lambda button=button16, color="colorborderbrick": changecolor1(button, color))
    button16.grid(row=9, column=2)

    CreateToolTip(button16, "Szín módosítása")

    def com2a():
        options.bborder = var2a.get()

    var2a = BooleanVar()
    var2a.set(options.bborder)
    checkb2a = Checkbutton(tab2, state=sow1, disabledforeground="gray50", variable=var2a, command=com2a)
    checkb2a.grid(row=9, column=3, sticky=W)

    CreateToolTip(checkb2a, "Legyen-e keret?")

    label17 = Label(tab2, state=sow1, disabledforeground="gray50", text="Cserére jelölt")
    label17.grid(row=10, column=1)

    button17 = Button(tab2, state=sow1, width=buttonwidth, bg=options.colorchangedbrick,
                      activebackground=options.colorchangedbrick)
    button17.configure(command=lambda button=button17, color="colorchangedbrick": changecolor1(button, color))
    button17.grid(row=10, column=2)

    CreateToolTip(button17, "Szín módosítása")

    button00 = Button(tab2, width=11, text="Vissza", command=close1)
    button00.grid(row=11, column=5)

    CreateToolTip(button00, "Kilépés a beállításokból")

    # ----------------------------Játék------------------------
    f0 = LabelFrame(tab3, text="Játék", padx=5, pady=5)
    f0.grid(row=0, column=0, columnspan=5, sticky=E + W)

    def com21():
        options.gamemode = v1.get()
        if v1.get() == 2:
            var8.set(False)
            options.valueofchangedletter = False
        if v1.get() == 2 or v1.get() == 3:
            options.checkmode = 1
            v6.set(options.checkmode)
            var4c.set(False)
            options.limitedvisibility = False
            var7a.set(False)
            options.checkattheend = False

    v1 = IntVar()
    v1.set(options.gamemode)
    rb1 = Radiobutton(f0, state=sow1, disabledforeground="gray50", highlightthickness=0, borderwidth=0, pady=0,
                      text="Egyedül játszom.", variable=v1, value=1, command=com21)
    rb1.grid(row=0, column=0, sticky=W)

    CreateToolTip(rb1, "Egyszemélyes gyakorló játék beállítása")

    rb2 = Radiobutton(f0, state=sow1, disabledforeground="gray50", highlightthickness=0, borderwidth=0, pady=0,
                      text="Gép ellen játszom,", variable=v1, value=2, command=com21)
    rb2.grid(row=1, column=0, sticky=W)

    CreateToolTip(rb2,
                  "Egy vagy több gépi játékos elleni játék beállítása.")

    def com51(event):
        options.aiopponent = int(v2.get())
        managetabs()

    v2 = StringVar()
    v2.set(options.aiopponent)
    cb1 = Combobox(f0, textvariable=v2, width=2, state=sow2, justify="right")
    cb1['values'] = (0, 1, 2, 3)
    cb1.bind('<<ComboboxSelected>>', com51)
    cb1.grid(row=1, column=1, sticky=W)

    CreateToolTip(cb1, "Gépi játékosok száma")

    lb2 = Label(f0, state=sow1, disabledforeground="gray50", highlightthickness=0, borderwidth=0, pady=0,
                text=" ellenféllel szemben,")
    lb2.grid(row=1, column=2, rowspan=2)

    rb3 = Radiobutton(f0, state=sow1, disabledforeground="gray50", highlightthickness=0, borderwidth=0, pady=0,
                      text="Hálózaton játszom,", variable=v1, value=3, command=com21)
    rb3.grid(row=2, column=0, sticky=W)
    # rb3.configure(state="disabled")

    CreateToolTip(rb3, "Más játékosok elleni hálózatos játék beállítása")

    def com114():
        options.duplicate = var114.get()
        if not var114.get():
            var115.set(False)
            options.independentboards = False
        if var114.get():
            var5.set(False)
            options.usefletters = False
            var14.set(False)
            options.bonusforusingall = False
            var15.set(False)
            options.fixpoint = False
            var16.set(False)
            options.valueforeachletter = False
            var17.set(False)
            options.penaltyforleft = False
            var18.set(False)
            options.pvalueforeachletter = False

    var114 = BooleanVar()
    var114.set(options.duplicate)
    checkb114 = Checkbutton(f0, state=sow1, disabledforeground="gray50", highlightthickness=0, borderwidth=0, pady=0,
                            text=" szimultán,", variable=var114, command=com114)
    checkb114.grid(row=1, column=3, rowspan=2, sticky=W)

    CreateToolTip(checkb114,
                  "A játékosok akciója lehet egymás utáni vagy egyidejű (duplicate mód)\n" +
                  "Közös betűk megadása ilyenkor nem lehetséges, és\na játék végi jutalmak," +
                  " levonások sem állíthatók be")

    def com115():
        options.independentboards = var115.get()
        if var115.get():
            var114.set(True)
            com114()
            options.lettersetmode = 3
            options.resetsack = True
            options.resetall = True
            v4.set(options.lettersetmode)

    var115 = BooleanVar()
    var115.set(options.independentboards)
    checkb115 = Checkbutton(f0, state=sow1, disabledforeground="gray50", highlightthickness=0, borderwidth=0, pady=0,
                            text=" külön táblán.", variable=var115, command=com115)
    checkb115.grid(row=1, column=4, rowspan=2, sticky=W)

    CreateToolTip(checkb115,
                  "A játék történhet közös táblán vagy egymástól\nfüggetlen, csak az adott játékos által láthatón.\n" +
                  "Független táblán csak szimultán módban lehet játszani.")

    def com52(event):
        options.networkopponent = int(v3.get())

    v3 = StringVar()
    v3.set(options.networkopponent)
    cb2 = Combobox(f0, textvariable=v3, width=2, state=sow2, justify="right")
    cb2['values'] = (0, 1, 2, 3, 4, 5, 6, 7, 8, 9)
    cb2.bind('<<ComboboxSelected>>', com52)
    cb2.grid(row=2, column=1, sticky=W)

    CreateToolTip(cb2, "Ellenfelek száma hálózati játékban")

    label70a = Label(f0, state=sow1, disabledforeground="gray50", highlightthickness=0, borderwidth=0, pady=0,
                     text="Gondolkodási idő:")
    label70a.grid(row=3, column=0, sticky=W)

    def com59(event):

        def validate2():
            try:
                int(var70a.get())
                int(var42.get())
                int(var43.get())
                int(var44.get())
                int(var45.get())
                int(var46.get())
                int(var47.get())
                int(var48.get())
                int(var70.get())
                return 1
            except ValueError:
                tkinter.messagebox.showerror("Hibás érték", "Csak számjegyeket fogadnak a beviteli mezők",
                                             parent=popup4)
                return 0

        if not validate2():
            return
        int(var70a.get())
        v11 = var41.get()
        v12 = int(var42.get())
        v13 = int(var43.get())
        int(var44.get())
        int(var45.get())
        int(var46.get())
        int(var47.get())
        int(var48.get())
        int(var70.get())
        if not v11.isalpha():
            tkinter.messagebox.showerror("Hibás kezdő mező pozíció",
                                         "Csak nagybetűket fogad a beviteli mező",
                                         parent=popup4)
            return
        try:
            rowl = abc.index(v11)
        except Exception:
            tkinter.messagebox.showerror("Hibás kezdő mező pozíció",
                                         "Csak nagybetűket fogad a beviteli mező",
                                         parent=popup4)
            return
        if rowl > options.height:
            tkinter.messagebox.showerror("Hibás kezdő mező pozíció",
                                         "Csak A és " + rowl + " közé eshet",
                                         parent=popup4)
            return
        if v12 < 1 or v12 > options.width:
            tkinter.messagebox.showerror("Hibás kezdő mező pozíció",
                                         "Nem lehet kisebb, mint 1, és nem lehet nagyobb,mint a tábla szélessége",
                                         parent=popup4)
            return
        if v13 < 1:
            tkinter.messagebox.showerror("Hibás érték", "A körök száma nem lehet kisebb, mint 1", parent=popup4)
            return
        options.timelimit = int(var70a.get())
        options.startfieldx = abc.index(var41.get().upper().strip())
        options.startfieldy = int(var42.get())-1
        options.turnlimitcount = int(var43.get())
        options.useoldbonusvalue = int(var44.get())
        options.wordperturnbonusvalue = int(var45.get())
        options.pointforfinish = int(var46.get())
        options.pointforeachletter = int(var47.get())
        options.ppointforeachletter = int(var48.get())
        options.aitimelimit[notebook1.index("current")] = int(var70.get())

    var70a = StringVar()
    var70a.set(options.timelimit)
    entry70a = Entry(f0, state=sow1, disabledforeground="gray50", width=4, bg="white", relief=SUNKEN, borderwidth=2,
                     textvariable=var70a, justify="right")
    entry70a.grid(row=3, column=1, sticky=E)
    entry70a.bind("<KeyRelease>", com59)

    CreateToolTip(entry70a, "Fordulónkénti gondolkodási idő")

    f1 = LabelFrame(tab3, text="Szabályok megadása", padx=5, pady=5)
    f1.grid(row=4, column=0, columnspan=3, sticky=E + W)

    lb23 = Label(f1, state=sow1, disabledforeground="gray50", padx=1, pady=1, text="Kapott betűk száma")
    lb23.grid(row=3, column=0, sticky=W)

    def com510(event):
        global rack, rackfields
        options.racksize = int(v20.get())
        rackfields = [0] * options.racksize
        rack = [0] * options.racksize
        for i in range(len(options.wordlengthlist[0])):
            if i + 1 > options.racksize:
                options.wordlengthlist[0][i] = 'False'

    v20 = StringVar()
    v20.set(options.racksize)
    cb10 = Combobox(f1, textvariable=v20, width=2, state=sow2, justify="right")
    cb10['values'] = (3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20)
    cb10.bind('<<ComboboxSelected>>', com510)
    cb10.grid(row=3, column=3, sticky=E)

    CreateToolTip(cb10, "A kisorsolt betűk száma")

    def com11():
        options.connect = var2.get()

    var2 = BooleanVar()
    var2.set(options.connect)
    checkb2a = Checkbutton(f1, state=sow1, disabledforeground="gray50", highlightthickness=0, borderwidth=0, pady=0,
                          text="Az új szónak kapcsolódni kell a már táblán lévőkkel", variable=var2, command=com11)
    checkb2a.grid(row=4, column=0, sticky=W)

    CreateToolTip(checkb2a, "A már táblán levő betűket kötelező-e felhasználni új szó alkotásakor")

    def com12():
        options.startfield = var3.get()

    var3 = BooleanVar()
    var3.set(options.startfield)
    checkb3a = Checkbutton(f1, state=sow1, disabledforeground="gray50", highlightthickness=0, borderwidth=0, pady=0,
                          text="Meghatározott kezdő mezőre kell kerülnie az első szónak", variable=var3, command=com12)
    checkb3a.grid(row=6, column=0, sticky=W)

    CreateToolTip(checkb3a, "Ha a táblán vannak előre beírt betűk, akkor ne legyen bejelölve")

    ffs = Frame(f1)
    ffs.grid(row=6, column=3, sticky=E)

    var41 = StringVar()
    var41.set(abc[options.startfieldx])
    entry1 = Entry(ffs, state=sow1, disabledforeground="gray50", width=2, bg="white", relief=SUNKEN, borderwidth=2,
                   textvariable=var41, justify="right")
    entry1.grid(row=0, column=0, sticky=E)
    entry1.bind("<KeyRelease>", com59)

    CreateToolTip(entry1, "Sor")

    var42 = StringVar()
    var42.set(options.startfieldy+1)
    entry2 = Entry(ffs, state=sow1, disabledforeground="gray50", width=2, bg="white", relief=SUNKEN, borderwidth=2,
                   textvariable=var42, justify="right")
    entry2.grid(row=0, column=1, sticky=E)
    entry2.bind("<KeyRelease>", com59)

    CreateToolTip(entry2, "Oszlop")

    def com13():
        options.turnlimit = var4.get()

    var4 = BooleanVar()
    var4.set(options.turnlimit)
    checkb4 = Checkbutton(f1, state=sow1, disabledforeground="gray50", highlightthickness=0, borderwidth=0, pady=0,
                          text="Körök száma előre meghatározott", variable=var4, command=com13)
    checkb4.grid(row=7, column=0, sticky=W)

    CreateToolTip(checkb4, "A játék adott számú kör után befejeződik")

    var43 = StringVar()
    var43.set(options.turnlimitcount)
    entry3 = Entry(f1, state=sow1, disabledforeground="gray50", width=2, bg="white", relief=SUNKEN, borderwidth=2,
                   textvariable=var43, justify="right")
    entry3.grid(row=7, column=3, sticky=E)
    entry3.bind("<KeyRelease>", com59)

    CreateToolTip(entry3, "Fordulók száma")

    def com13b():
        options.changeincreasepasses = var4b.get()

    var4b = BooleanVar()
    var4b.set(options.changeincreasepasses)
    checkb4b = Checkbutton(f1, state=sow1, disabledforeground="gray50", highlightthickness=0, borderwidth=0, pady=0,
                           text="A cserék száma számítson bele a passzok számába", variable=var4b, command=com13b)
    checkb4b.grid(row=8, column=0, sticky=W)

    CreateToolTip(checkb4b,
                  "A cserék száma beleszámít-e a passzok számába.\nAkkor érdemes bekapcsolni, ha a " +
                  "betűkészlet végtelenítve van\nés nincs beállítva a fordulók száma sem.")

    def com13c():
        options.limitedvisibility = var4c.get()
        if options.gamemode == 2 or options.gamemode == 3:
            v1.set(1)
            options.gamemode = 1

    var4c = BooleanVar()
    var4c.set(options.limitedvisibility)
    checkb4c = Checkbutton(f1, state=sow1, disabledforeground="gray50", highlightthickness=0, borderwidth=0, pady=0,
                           text="Tábla látható területének korlátozása", variable=var4c, command=com13c)
    checkb4c.grid(row=9, column=0, sticky=W)

    CreateToolTip(checkb4c,
                  "Ha be van kapcsolva, a tartó méretére korlátozza a\n láthatóságot. Akkor érdemes bekapcsolni, ha "
                  "a\ntábla felfedezése célja a játéknak.\n(Csak egyjátékos módban)")



    label18 = Label(f1, state=sow1, disabledforeground="gray50", highlightthickness=0, borderwidth=0, pady=0,
                    text="Betűk kezelése")
    label18.grid(row=10, column=0, sticky=W)

    def com22():
        options.lettersetmode = v4.get()
        if options.lettersetmode == 1:
            options.resetsack = False
            options.resetall = False
            options.duplicate = False
            options.independentboards = False
            var114.set(False)
            var115.set(False)
        elif options.lettersetmode == 2:
            options.resetsack = True
            options.resetall = False
            options.independentboards = False
            var115.set(False)
        elif options.lettersetmode == 3:
            var5.set(False)
            options.usefletters = False
            options.resetsack = True
            options.resetall = True

    v4 = IntVar()
    v4.set(options.lettersetmode)
    rb4 = Radiobutton(f1, state=sow1, disabledforeground="gray50", highlightthickness=0, borderwidth=0, pady=0,
                      text="Adott betűkészletből, melyből a kihúzottak eltűnnek", variable=v4, value=1, command=com22)
    rb4.grid(row=11, column=0, sticky=W)

    CreateToolTip(rb4,
                  "A betűk húzása egy előre meghatározott betűkészletből történik,\n" +
                  "amely a kisorsolt betűkkel csökken.")

    def com80():
        global data
        data = []
        for bck in bricks:
            rec = list()
            rec.append(bck.letter)
            rec.append(bck.count)
            rec.append(bck.value)
            rec.append(bck.type)
            rec.append(bck.rate)
            if bck.letter in letterreplacedict:
                rec.append((',').join(letterreplacedict[bck.letter]))
            else:
                rec.append("")
            data.append(rec)
        letterset("letterset")

    button18 = Button(f1, state=sow1, text='Készlet', width=7, command=com80)
    button18.grid(row=11, column=3)

    CreateToolTip(button18, "A betűkészlet")

    rb5 = Radiobutton(f1, state=sow1, disabledforeground="gray50", highlightthickness=0, borderwidth=0, pady=0,
                      text="Adott betűkészletből, melyben a felhasználtak pótlódnak", variable=v4, value=2, command=com22)
    rb5.grid(row=12, column=0, sticky=W)

    CreateToolTip(rb5,
                  "A betűk húzása egy előre meghatározott betűkészletből történik,\n" +
                  "minden forduló után pótlódnak a zsákban a táblára került betűk")

    rb6 = Radiobutton(f1, state=sow1, disabledforeground="gray50", highlightthickness=0, borderwidth=0, pady=0,
                      text="Adott készlet, mely nem csökken, a teljes tartó cserélődik", variable=v4, value=3, command=com22)
    rb6.grid(row=13, column=0, sticky=W)

    CreateToolTip(rb6,
                  "A betűk húzása egy előre meghatározott betűkészletből történik,\n" +
                  "minden forduló után a játékos összes betűje cserélődik")

    def com13a():
        options.optimizeddraw = var4b.get()

    var4b = BooleanVar()
    var4b.set(options.optimizeddraw)
    checkb4b = Checkbutton(f1, state=sow1, disabledforeground="gray50", highlightthickness=0, borderwidth=0, pady=0,
                          text="A magánhangzók és mássalhangzók arányának befolyásolása         ", variable=var4b, command=com13a)
    checkb4b.grid(row=14, column=0, sticky=W)

    CreateToolTip(checkb4b, "A sorsolt magánhangzók+dzsókerek arányát 40-60% körül tartja")

    def com14():
        options.usefletters = var5.get()
        if var5.get():
            var114.set(False)
            options.duplicate = False
            var115.set(False)
            options.independentboards = False
            if options.lettersetmode == 3:
                options.lettersetmode = 1
                options.resetsack = False
                options.resetall = False
                v4.set(options.lettersetmode)

    var5 = IntVar()
    var5.set(options.usefletters)
    checkb5 = Checkbutton(f1, state=sow1, disabledforeground="gray50", highlightthickness=0, borderwidth=0, pady=0,
                          text="Közös betűk", variable=var5, command=com14)
    checkb5.grid(row=15, column=0, sticky=W)

    CreateToolTip(checkb5, "A játék folyamán minden játékos számára\nrendelkezésre álló betűk adhatók meg")

    def com81():
        global data
        data = []
        for lts in options.fletters:
            rec = list()
            rec.append(lts.split(",")[0])
            rec.append(int(lts.split(",")[1]))
            rec.append(int(lts.split(",")[2]))
            rec.append(lts.split(",")[3])
            rec.append(float(lts.split(",")[4]))
            data.append(rec)
        letterset("fletterset")

    button19 = Button(f1, state=sow1, text='Készlet', width=7, command=com81)
    button19.grid(row=15, column=3)

    CreateToolTip(button19, "A közös betűk készlete")

    def com14a():
        options.resetfrack = var5a.get()

    var5a = BooleanVar()
    var5a.set(options.resetfrack)
    checkb4b = Checkbutton(f1, state=sow1, disabledforeground="gray50", highlightthickness=0, borderwidth=0, pady=0,
                          text="A közös betűk nem fogynak", variable=var5a, command=com14a)
    checkb4b.grid(row=16, column=0, sticky=W)

    CreateToolTip(checkb4b, "A kirakott betű helyén egy új jelenik meg a tartón")

    label19 = Label(f1, state=sow1, disabledforeground="gray50", highlightthickness=0, borderwidth=0, pady=0,
                    text="Betűk pontértéke")
    label19.grid(row=17, column=0, sticky=W)

    def com23():
        options.valuemode = v5.get()
        if options.valuemode == 1:
            options.randomlettervalue = False
        else:
            options.randomlettervalue = True
            var6.set(False)
            options.randommultiplier = False
            var8.set(False)
            options.valueofchangedletter = False

    v5 = IntVar()
    v5.set(options.valuemode)
    rb7 = Radiobutton(f1, state=sow1, disabledforeground="gray50", highlightthickness=0, borderwidth=0, pady=0,
                      text="Adott pontszámok", variable=v5, value=1, command=com23)
    rb7.grid(row=18, column=0, sticky=W)

    CreateToolTip(rb7, "A betűkészletnél meghatározott állandó pontértékek")

    rb8 = Radiobutton(f1, state=sow1, disabledforeground="gray50", highlightthickness=0, borderwidth=0, pady=0,
                      text="Véletlen pontszámok", variable=v5, value=2, command=com23)
    rb8.grid(row=19, column=0, sticky=W)

    CreateToolTip(rb8, "A jobbra levő készletből sorsolt\nvéletlenszerű pontértékek")

    def showvalues():

        def ok111():
            t2 = t1.get("1.0", "end-1c")
            v1a = []
            for r in range(len(t2)):
                try:
                    v0 = int(t2[r])
                    v1a.append(v0)
                except ValueError:
                    tkinter.messagebox.showerror("Hibás érték", "Csak számjegyeket tartalmazhat", parent=popup4)
                    return
            options.values = v1a
            popup8.destroy()

        popup8 = Toplevel()
        popup8.title("Készlet")
        popup8.transient(popup4)
        t1 = Text(popup8, background="white")
        t1.pack()
        tvalues = ""
        for q in options.values:
            tvalues += str(q)
        t1.insert(END, tvalues)

        button201 = Button(popup8, text='Rendben', command=ok111)
        button201.pack()

        popup8.grab_set()
        popup4.wait_window(popup8)

    button20 = Button(f1, state=sow1, text='Készlet', width=7, command=showvalues)
    button20.grid(row=19, column=3)

    CreateToolTip(button20, "A lehetséges pontértékek készlete")

    def com15():
        options.randommultiplier = var6.get()
        if var6.get():
            v5.set(1)
            options.randomlettervalue = False

    var6 = BooleanVar()
    var6.set(options.randommultiplier)
    checkb6 = Checkbutton(f1, state=sow1, disabledforeground="gray50", highlightthickness=0, borderwidth=0, pady=0,
                          text="Véletlen szorzó", variable=var6, command=com15)
    checkb6.grid(row=20, column=0, sticky=W)

    CreateToolTip(checkb6, "A jobbra levő készletből sorsolt\nvéletlenszerű szorzók")

    def showmvalues():

        def ok2():
            t2 = t1.get("1.0", "end-1c")
            v1a = []
            for r in range(len(t2)):
                if t2[r] not in ["1", "2", "3"]:
                    tkinter.messagebox.showerror("Hibás érték", "Csak 1-3 számjegyeket tartalmazhat", parent=popup4)
                    return
                else:
                    v1a.append(int(t2[r]))
            options.mvalues = v1
            popup8.destroy()

        popup8 = Toplevel()
        popup8.title("Készlet")
        popup8.transient(popup4)
        t1 = Text(popup8, background="white")
        t1.pack()
        tmvalues = ""
        for q in options.mvalues:
            tmvalues += str(q)
        t1.insert(END, tmvalues)

        button201 = Button(popup8, text='Rendben', command=ok2)
        button201.pack()

        popup8.grab_set()
        popup4.wait_window(popup8)

    button21 = Button(f1, state=sow1, text='Készlet', width=7, command=showmvalues)
    button21.grid(row=20, column=3)

    CreateToolTip(button21, "A lehetséges szorzók készlete")

    label20 = Label(f1, state=sow1, disabledforeground="gray50", highlightthickness=0, borderwidth=0, pady=0,
                    text="Szavak érvényessége")
    label20.grid(row=21, column=0, sticky=W)

    def com24():
        global checkenchant
        options.checkmode = v6.get()
        if options.checkmode == 1:
            options.checkdictionary = True
        else:
            options.checkdictionary = False
            if options.checkmode == 3:
                if options.gamemode == 1:
                    checkenchant = True
                else:
                    options.checkmode = 1
                    v6.set(options.checkmode)

    v6 = IntVar()
    v6.set(options.checkmode)
    rb9 = Radiobutton(f1, state=sow1, disabledforeground="gray50", highlightthickness=0, borderwidth=0, pady=0,
                      text="Csak ha benne van a szótárban", variable=v6, value=1, command=com24)
    rb9.grid(row=22, column=0, sticky=W)

    CreateToolTip(rb9, "Az összes újonnan létrejött szó érvényességének\nellenőrzése a lépés továbbítása előtt")

    rb10 = Radiobutton(f1, state=sow1, disabledforeground="gray50", highlightthickness=0, borderwidth=0, pady=0,
                       text="Ha nincs benne a szótárban, figyelmeztetés", variable=v6, value=2, command=com24)
    rb10.grid(row=23, column=0, sticky=W)

    CreateToolTip(rb10,
                  "Ha be van jelölve,\n minden kirakott szó érvényesnek számít." +
                  " A játékost\n a program figyelmezteti, hogy a szó nincs a szótárban.)")

    rb11 = Radiobutton(f1, state=sow1, disabledforeground="gray50", highlightthickness=0, borderwidth=0, pady=0,
                       text="Helyesírás-ellenőrző program", variable=v6, value=3, command=com24)
    rb11.grid(row=24, column=0, sticky=W)

    CreateToolTip(rb11, "Az összes újonnan létrejött szó érvényességének\nellenőrzése a telepített "
                        "helyesírás-ellenőrző programmal\n(Csak egyjátékos módban állítható be.)")

    if not enchantexist:
        rb11.configure(state="disabled", disabledforeground="grey")

    def com16a():
        options.checkattheend = var7a.get()
        if var7a.get():
            options.checkmode = 4
            if options.gamemode == 2 or options.gamemode == 3:
                v1.set(1)
                options.gamemode = 1

    var7a = BooleanVar()
    var7a.set(options.checkattheend)
    checkb7a = Checkbutton(f1, state=sow1, disabledforeground="gray50", highlightthickness=0, borderwidth=0, pady=0,
                       text="Csak a játék végén", variable=var7a, command=com16a)
    checkb7a.grid(row=25, column=0, sticky=W)

    CreateToolTip(checkb7a, "A kirakott szavak érvényességét csak a játék végén ellenőrzi"
                        "\n(Csak egyjátékos módban állítható be.)")

    label21 = Label(f1, state=sow1, disabledforeground="gray50", highlightthickness=0, borderwidth=0, pady=0,
                    text="Dzsóker kezelése")
    label21.grid(row=26, column=0, sticky=W)

    def com16():
        options.dontchangejoker = var7.get()
        if var7.get():
            var8.set(False)
            options.valueofchangedletter = False

    var7 = BooleanVar()
    var7.set(options.dontchangejoker)
    checkb7 = Checkbutton(f1, state=sow1, disabledforeground="gray50", highlightthickness=0, borderwidth=0, pady=0,
                          text="Dzsóker bármilyen betűt helyettesíthet a táblán ", variable=var7, command=com16)
    checkb7.grid(row=27, column=0, sticky=W)

    CreateToolTip(checkb7,
                  "A lerakott dzsóker a táblán is dzsóker marad,\nés bármilyen betűként felhasználható a" +
                  " keresztező szóban.")

    def com17():
        options.valueofchangedletter = var8.get()
        if var8.get():
            var7.set(False)
            options.dontchangejoker = False
            if options.gamemode == 2:
                v1.set(1)
                options.gamemode = 1
            v5.set(1)
            options.randomlettervalue = False

    var8 = IntVar()
    var8.set(options.valueofchangedletter)
    checkb8 = Checkbutton(f1, state=sow1, disabledforeground="gray50", highlightthickness=0, borderwidth=0, pady=0,
                          text="Dzsóker pontértéke is változik", variable=var8, command=com17)
    checkb8.grid(row=28, column=0, sticky=W)

    CreateToolTip(checkb8,
                  "A lerakott dzsóker a helyettesített betű\npontértékét is megkapja.\n" +
                  "Gép elleni játékban jelenleg nem állítható be.")

    label22 = Label(f1, state=sow1, disabledforeground="gray50", highlightthickness=0, borderwidth=0, pady=0,
                    text="Pontszámítás")
    label22.grid(row=29, column=0, sticky=W)

    def com18():
        options.onedirection = var9.get()

    var9 = BooleanVar()
    var9.set(options.onedirection)
    checkb9 = Checkbutton(f1, state=sow1, disabledforeground="gray50", highlightthickness=0, borderwidth=0, pady=0,
                          text="Csak az utoljára lerakott betűk irányába eső szóra jár pont.     ", variable=var9,
                          command=com18)
    checkb9.grid(row=30, column=0, sticky=W)

    CreateToolTip(checkb9,
                  "A keresztező szavaknak érvényesnek kell lenniük, de pont nem jár értük.\n" +
                  "Minden fordulóban legalább két új betűt fel kell használni")

    f2 = LabelFrame(tab3, text="Jutalmak, levonások", padx=5, pady=5)
    f2.grid(row=0, column=5, rowspan=15, columnspan=3, sticky=E + N + W)

    def com19():
        options.lengthbonus = var10.get()

    var10 = BooleanVar()
    var10.set(options.lengthbonus)
    checkb10 = Checkbutton(f2, state=sow1, disabledforeground="gray50", highlightthickness=0, borderwidth=0, pady=0,
                           text="A lerakott betűk száma alapján", variable=var10, command=com19)
    checkb10.grid(row=25, column=0, sticky=W)

    CreateToolTip(checkb10, "A mutat gombra kattintva megváltoztathatóak a jutalmak.")

    button22 = Button(f2, state=sow1, text='Mutat', width=7, command = lambda caller="numberofplacedletters": bonuses(caller))
    button22.grid(row=25, column=3)

    CreateToolTip(button22, "A beállított jutalmak.")

    def com20():
        options.useoldbonus = var11.get()

    var11 = BooleanVar()
    var11.set(options.useoldbonus)
    checkb11 = Checkbutton(f2, state=sow1, disabledforeground="gray50", highlightthickness=0, borderwidth=0, pady=0,
                           text="A már táblán lévőkért", variable=var11, command=com20)
    checkb11.grid(row=26, column=0, sticky=W)

    CreateToolTip(checkb11, "A táblán levő betűk felhasználásáért járó\njutalom a jobbra levő mezőben adható meg.")

    var44 = StringVar()
    var44.set(options.useoldbonusvalue)
    entry4 = Entry(f2, state=sow1, disabledforeground="gray50", width=2, bg="white", relief=SUNKEN, borderwidth=2,
                   textvariable=var44, justify="right")
    entry4.grid(row=26, column=3, sticky=E)
    entry4.bind("<KeyRelease>", com59)

    CreateToolTip(entry4, "A táblán levő betűk\nfelhasználásáért járó jutalom.")

    def com31():
        options.oldbonusonly = var12.get()

    var12 = BooleanVar()
    var12.set(options.oldbonusonly)
    checkb12 = Checkbutton(f2, state=sow1, disabledforeground="gray50", highlightthickness=0, borderwidth=0, padx=15,
                           pady=0, text="A már táblán lévőkért nem jár a rajtuk lévő pontszám", variable=var12,
                           command=com31)
    checkb12.grid(row=27, column=0, sticky=W)

    CreateToolTip(checkb12, "A táblán levő betűkért csak a jutalom jár,\na rajtuk levő pontszám már nem.")

    def com32():
        options.wordperturnbonus = var13.get()

    var13 = BooleanVar()
    var13.set(options.wordperturnbonus)
    checkb13 = Checkbutton(f2, state=sow1, disabledforeground="gray50", highlightthickness=0, borderwidth=0, pady=0,
                           text="Egy körben létrejött szavak száma alapján", variable=var13, command=com32)
    checkb13.grid(row=28, column=0, sticky=W)

    CreateToolTip(checkb13, "A fordulóban létrejött szavak száma után járó\njutalom a jobbra levő mezőben adható meg.")

    var45 = StringVar()
    var45.set(options.wordperturnbonusvalue)
    entry5 = Entry(f2, state=sow1, disabledforeground="gray50", width=2, bg="white", relief=SUNKEN, borderwidth=2,
                   textvariable=var45, justify="right")
    entry5.grid(row=28, column=3, sticky=E)
    entry5.bind("<KeyRelease>", com59)

    CreateToolTip(entry5, "A létrejött szavak száma alapján járó jutalom")

    def com33():
        options.bonusforusingall = var14.get()
        if var14.get():
            var114.set(False)
            options.duplicate = False
            var115.set(False)
            options.independentboards = False

    var14 = BooleanVar()
    var14.set(options.bonusforusingall)
    checkb14 = Checkbutton(f2, state=sow1, disabledforeground="gray50", highlightthickness=0, borderwidth=0, pady=0,
                           text="A játékot befejező játékosnak:", variable=var14, command=com33)
    checkb14.grid(row=29, column=0, sticky=W)

    CreateToolTip(checkb14, "Szimultán játékban nem állítható be.")

    def com34():
        options.fixpoint = var15.get()
        if var15.get():
            var114.set(False)
            options.duplicate = False
            var115.set(False)
            options.independentboards = False

    var15 = BooleanVar()
    var15.set(options.fixpoint)
    checkb15 = Checkbutton(f2, state=sow1, disabledforeground="gray50", highlightthickness=0, borderwidth=0, padx=15,
                           pady=0, text="Adott pontszám", variable=var15, command=com34)
    checkb15.grid(row=30, column=0, sticky=W)

    CreateToolTip(checkb15, "Állandó érték, ami a\njobbra levő mezőben adható meg.")

    var46 = StringVar()
    var46.set(options.pointforfinish)
    entry6 = Entry(f2, state=sow1, disabledforeground="gray50", width=2, bg="white", relief=SUNKEN, borderwidth=2,
                   textvariable=var46, justify="right")
    entry6.grid(row=30, column=3, sticky=E)
    entry6.bind("<KeyRelease>", com59)

    CreateToolTip(entry6, "A beállított jutalom.")

    def com35():
        options.valueforeachletter = var16.get()
        if var16.get():
            var114.set(False)
            options.duplicate = False
            var115.set(False)
            options.independentboards = False

    var16 = BooleanVar()
    var16.set(options.valueforeachletter)
    checkb16 = Checkbutton(f2, state=sow1, disabledforeground="gray50", highlightthickness=0, borderwidth=0, padx=15,
                           pady=0, text="A megmaradt betűk értéke, egyébként betűnként", variable=var16, command=com35)
    checkb16.grid(row=31, column=0, sticky=W)

    CreateToolTip(checkb16,
                  "A többi játékosnál megmaradt betűk összértéke,\nvagy betűnként egy adott pontszám, ami a\n" +
                  "jobbra levő mezőben adható meg.")

    var47 = StringVar()
    var47.set(options.pointforeachletter)
    entry7 = Entry(f2, state=sow1, disabledforeground="gray50", width=2, bg="white", relief=SUNKEN, borderwidth=2,
                   textvariable=var47, justify="right")
    entry7.grid(row=31, column=3, sticky=E)
    entry7.bind("<KeyRelease>", com59)

    CreateToolTip(entry7, "A betűnkénti állandó pontszám.")

    def com36():
        options.penaltyforleft = var17.get()
        if var17.get():
            var114.set(False)
            options.duplicate = False
            var115.set(False)
            options.independentboards = False

    var17 = BooleanVar()
    var17.set(options.penaltyforleft)
    checkb17 = Checkbutton(f2, state=sow1, disabledforeground="gray50", highlightthickness=0, borderwidth=0, pady=0,
                           text="Pontlevonás a megmaradt betűkért", variable=var17, command=com36)
    checkb17.grid(row=32, column=0, sticky=W)

    CreateToolTip(checkb17, "Pontlevonás a játék során szerzett összpontszámból\na játékos megmaradt betűi alapján.")

    def com37():
        options.pvalueforeachletter = var18.get()
        if var18.get():
            var114.set(False)
            options.duplicate = False
            var115.set(False)
            options.independentboards = False

    var18 = BooleanVar()
    var18.set(options.pvalueforeachletter)
    checkb18 = Checkbutton(f2, state=sow1, disabledforeground="gray50", highlightthickness=0, borderwidth=0, padx=15,
                           pady=0, text="A megmaradt betűk értéke, egyébként betűnként", variable=var18, command=com37)
    checkb18.grid(row=33, column=0, sticky=W)

    CreateToolTip(checkb18,
                  "A játékosnál maradt betűk összértéke,\nvagy betűnként egy adott pontszám, ami a\n" +
                  "jobbra levő mezőben adható meg.")

    var48 = StringVar()
    var48.set(options.ppointforeachletter)
    entry7a = Entry(f2, state=sow1, disabledforeground="gray50", width=2, bg="white", relief=SUNKEN, borderwidth=2,
                    textvariable=var48, justify="right")
    entry7a.grid(row=33, column=3, sticky=E)
    entry7a.bind("<KeyRelease>", com59)

    CreateToolTip(entry7a, "A betűnkénti állandó pontszám.")

    def com19a():
        options.wordlengthbonus = var10a.get()
        if var10a.get():
            options.checkattheend = True
            var7a.set(True)
            options.checkmode = 4
            if options.gamemode == 2 or options.gamemode == 3:
                v1.set(1)
                options.gamemode = 1

    var10a = BooleanVar()
    var10a.set(options.wordlengthbonus)
    checkb10a = Checkbutton(f2, state=sow1, disabledforeground="gray50", highlightthickness=0, borderwidth=0, pady=0,
                           text="A szavak hossza alapján", variable=var10a, command=com19a)
    checkb10a.grid(row=34, column=0, sticky=W)

    CreateToolTip(checkb10a, "Csak akkor állítható be, ha a szavak\nérvényességének ellenőrzése csak\na játék végén történik\nA mutat gombra kattintva megváltoztathatóak a jutalmak.")

    button22a = Button(f2, state=sow1, text='Mutat', width=7, command = lambda caller="lengthofwords": bonuses(caller))
    button22a.grid(row=34, column=3)

    CreateToolTip(button22a, "A beállított jutalmak.")


    button000 = Button(tab3, width=11, text="Vissza", command=close1)
    button000.grid(row=35, column=6)

    CreateToolTip(button000, "Kilépés a beállításokból.")

    # -------------------- Gépi játékosok beállításai --------------------

    global tabs

    notebook1 = Notebook(tab4, style="sidetab.TNotebook")

    tabs = []

    def currenttab(event):
        try:
            i = notebook1.index("current")
            notebooktab(i)
        except Exception:
            pass

    def notebooktab(tabi):
        global tabs
        label60 = Label(tabs[tabi], state=sow1, disabledforeground="gray50", text="Gépi játékos beállításai")
        label60.grid(row=0, column=0, sticky=W)

        variables = [None, None, None, None, None, None, None, None, None, None]
        checkboxes = [None, None, None, None, None, None, None, None, None, None]

        def com60(tabi, i, var):
            global options
            global tabs
            wll = var.get()
            if wll:
                options.wordlengthlist[tabi][i] = 'True'
            else:
                options.wordlengthlist[tabi][i] = 'False'


        for i in range(len(checkboxes)):
            variables[i] = BooleanVar()
            if options.wordlengthlist[tabi][i] == 'True':
                variables[i].set(True)
            checkboxes[i] = Checkbutton(tabs[tabi], state=sow1, disabledforeground="gray50", text="   "+str(i+1), variable=variables[i],
                                        command=lambda tabi=tabi, i=i, var=variables[i]: com60(tabi, i, var) )
            if options.racksize < i+1:
                checkboxes[i].config(state=DISABLED)
            checkboxes[i].grid(row=i+1, column=0, sticky=W)

            CreateToolTip(checkboxes[i], "Gépi játékos által felhasználható\nbetűk számának beállítása.")


        label61 = Label(tabs[tabi], state=sow1, disabledforeground="gray50", text="betűt felhasználva")
        label61.grid(row=5, column=1, sticky=W)

        label70 = Label(tabs[tabi], state=sow1, disabledforeground="gray50", text="Gép max. ideje")
        label70.grid(row=11, column=0, sticky=W)

        global var70
        var70 = StringVar()
        var70.set(options.aitimelimit[tabi])
        entry70 = Entry(tabs[tabi], state=sow1, disabledforeground="gray50", width=4, bg="white", relief=SUNKEN,
                        borderwidth=2, textvariable=var70,
                        justify="right")
        entry70.grid(row=11, column=1, sticky=E)
        entry70.bind("<KeyRelease>", com59)

        CreateToolTip(entry70, "Gépi játékos által maximálisan\nfelhasználható idő fordulónként.")

        Label(tabs[tabi], state=sow1, disabledforeground="gray50", highlightthickness=0, borderwidth=0, pady=0,
              text="Szókészlet:").grid(row=21, column=0, sticky=W)

        def com510(event):
            global options
            options.aidictionarylimited[tabi] = v200.get()

        v200 = StringVar()
        v200.set(options.aidictionarylimited[tabi])
        cb100 = Combobox(tabs[tabi], textvariable=v200, width=11, state=sow2, justify="right")
        cb100['values'] = ("Minden szó", "40000 >", "20000 >")
        cb100.bind('<<ComboboxSelected>>', com510)
        cb100.grid(row=21, column=1, sticky=W)

        CreateToolTip(cb100, "Gépi játékos szókészlete. Teljes, kevesebb mint 40000 szó, kevesebb mint 20000 szó")

        label00 = Label(tabs[tabi], state=sow1, disabledforeground="gray50", text="Erösség")
        label00.grid(row=22, column=0, sticky=W)

        CreateToolTip(label00, "Gépi játékos erőssége százalékban")

        def com_1(event):
            options.aistrength[notebook1.index("current")] = scale11.get()

        scale11 = Scale(tabs[tabi], length=110, orient=HORIZONTAL, troughcolor="#a9a9a9", sliderlength=20,
                       showvalue=50, from_=0, to=100, tickinterval=50, command=com_1)
        scale11.set(options.aistrength[tabi])
        scale11.grid(row=22, column=1)
        scale11.config(state=sow1)

        CreateToolTip(scale11, "Gépi játékos erőssége százalékban")

        button0000 = Button(tabs[tabi], width=11, text="Vissza", command=close1)
        button0000.grid(row=23, column=3)

        CreateToolTip(button0000, "Kilépés a beállításokból.")

    def managetabs():
        global tabs
        for i in range(3):
            tabs.append(Frame(notebook1))
            notebook1.add(tabs[i], text="Gép" + str(i + 1))
            if i >= options.aiopponent:
                notebook1.tab(tabs[i], state="disabled")
            else:
                notebook1.tab(tabs[i], state="normal")
        notebook1.pack(fill=BOTH, expand=ON)
        if options.aiopponent > 0:
            notebooktab(0)

    managetabs()
    notebook1.bind("<<NotebookTabChanged>>", currenttab)

    notebook.add(tab1, text="Tábla")
    notebook.add(tab2, text="Betűk")
    notebook.add(tab3, text="Játék")
    notebook.add(tab4, text="Gépi ellenfelek")
    notebook.pack()

    popup4.protocol("WM_DELETE_WINDOW", close1)
    if sow == 1:
        popup4.grab_set()
    appwin.wait_window(popup4)


def notimplemented():
    pass


def letterset(caller):
    """Betűkészlet beállítása"""
    global data, entries

    def validateentry():
        global data
        abc2 = ('A', 'Á', 'B', 'C', 'CS', 'D', 'E', 'É', 'F', 'G', 'GY', 'H', 'I', 'Í', 'J', 'K', 'L', 'LY', 'M', 'N',
                'NY','O', 'Ó', 'Ö', 'Ő', 'P', 'Q', 'R', 'S', 'SZ', 'T', 'TY', 'U', 'Ú', 'Ü', 'Ű', 'V', 'W', 'X', 'Y',
                'Z', 'ZS')

        for k in range(len(data)):
            for l7 in range(len(data[k])):
                if l7 == 0 or l7 == 3:
                    data[k][l7] = entries[k][l7].get().upper().strip()
                    if not (data[k][l7]).isalpha() and data[k][l7] != '*':
                        tkinter.messagebox.showerror("Hibás érték", "Csak betűket fogad a beviteli mező",
                                                     parent=popup7)
                        entries[k][l7].focus()
                        return 0
                    if l7 == 0 and data[k][l7] not in abc2 and data[k][l7] != '*':
                        tkinter.messagebox.showerror("Hibás érték", "A betűt nem tartalmazza a program ábécéje",
                                                     parent=popup7)
                        entries[k][l7].focus()
                        return 0
                    if l7 == 3 and data[k][l7] not in ['C', 'N', 'V']:
                        tkinter.messagebox.showerror("Hibás érték", "A mező értéke csak C, N vagy V lehet",
                                                     parent=popup7)
                        entries[k][l7].focus()
                        return 0
                elif l7 == 1 or l7 == 2:
                    data[k][l7] = entries[k][l7].get().strip()
                    try:
                        int(data[k][l7])
                    except ValueError:
                        tkinter.messagebox.showerror("Hibás érték", "Csak egész számot fogad a beviteli mező",
                                                     parent=popup7)
                        entries[k][l7].focus()
                        return 0
                elif l7 == 4:
                    data[k][l7] = entries[k][l7].get().strip()
                    try:
                        float(data[k][l7])
                    except ValueError:
                        tkinter.messagebox.showerror("Hibás érték", "Csak tizedes törtet fogad a beviteli mező",
                                                     parent=popup7)
                        entries[k][l7].focus()
                        return 0
                elif l7 == 5:
                    data[k][l7] = entries[k][l7].get().strip()
                    content = ('').join((data[k][l7]).split(','))
                    if not content.isalpha() and content != '':
                        tkinter.messagebox.showerror("Hibás érték", "Csak betűket fogad a beviteli mező",
                                                     parent=popup7)
                        entries[k][l7].focus()
                        return 0
        return 1

    def com1():
        global data
        global bricks
        global options
        letterstrl = []
        if not validateentry():
            return
        popup7.destroy()
        if caller == "letterset":
            bricks = []
        else:
            options.fletters = []
        for line1 in range(len(data)):
            data5 = data[line1][5]  if data[line1][5] == '' else '['+data[line1][5]+']'
            letterstrl.append(data[line1][0]+','+str(data[line1][1])+','+str(data[line1][2])+','+data[line1][3]+','
                              +str(data[line1][4])+','+data5)
            if caller == "letterset":
                bricks.append(Brick(data[line1][0]+','+str(data[line1][1])+','+str(data[line1][2])+','+
                                    data[line1][3]+','+str(data[line1][4])))
            else:
                options.fletters.append(",".join(data[line1]))
        letterstr = "\n" + "\n".join(letterstrl)
        if caller == "letterset":
            config.set('Letters', 'letters', letterstr)
        else:
            config.set('Rules', 'fletters', letterstr)


    def createentries():
        global data, entries
        global recordpointerindex
        entries = copy.deepcopy(data)
        for i in range(len(data)):
            for j in range(len(data[i])):
                entries[i][j] = Entry(frame500, width=11, bg="white", justify=RIGHT, relief=FLAT)
                entries[i][j].grid(row=i + 1, column=j)
                entries[i][j].insert(END, data[i][j])
                entries[i][j].bind("<ButtonRelease-1>", getrecordpointerindex)
                frame500.grid_columnconfigure(j, pad=pad1)
                if i == recordpointerindex and j ==0:
                    entries[i][j].focus()
            frame500.grid_rowconfigure(i + 1, pad=pad1)
        entry500.update()
        canvas5.config(yscrollcommand=scrollbar.set, width=len(data[0]) * (entry500.winfo_width() + 1))


    def insertrecord():
        global recordpointerindex
        global data, entries
        data1 = data[:recordpointerindex]
        data2 = data[recordpointerindex:]
        data = []
        data.extend(data1)
        if len(data[0]) == 6:
            data.append(['', 0, 0, 'C', 0.0, ''])
        else:
            data.append(['', 0, 0, 'C', 0.0])
        data.extend(data2)
        createentries()
        drawrecordpointer()

    def newrecord():
        global recordpointerindex
        global data, entries
        if len(data[0]) == 6:
            data.append(['', 0, 0, 'C', 0.0, ''])
            record = [None, None, None, None, None, None]
        else:
            data.append(['', 0, 0, 'C', 0.0])
            record = [None, None, None, None, None]
        for jj in range(len(record)):
            record[jj] = Entry(frame500, width=11, bg="white", justify=RIGHT, relief=FLAT)
            record[jj].grid(row= 100, column=jj)
            record[jj].insert(END, data[-1][jj])
            record[jj].bind("<ButtonRelease-1>", getrecordpointerindex)
            if jj == 0:
                record[jj].focus()
            frame500.grid_columnconfigure(jj, pad=pad1)
        entries.append(record)
        recordpointerindex = len(data)-1
        drawrecordpointer()

    def deleterecord():
        global recordpointerindex
        global data, entries
        try:
            data.pop(recordpointerindex)
        except IndexError:
            return
        for jj in range(len(entries[recordpointerindex])):
            entries[recordpointerindex][jj].destroy()
        entries.pop(recordpointerindex)
        drawrecordpointer()

    def getrecordpointerindex(event):
        global recordpointerindex
        global data, entries
        widget1 = str(event.widget).split('.')[-1]
        for ii in range(len(data)):
            for jj in range(len(data[ii])):
                if widget1 == entries[ii][jj].winfo_name():
                    recordpointerindex = ii
                    drawrecordpointer()
                    return

    def drawrecordpointer():
        global recordpointerindex
        global data, entries
        for ii in range(len(data)):
            for jj in range(len(data[ii])):
                if ii == recordpointerindex:
                    entries[ii][jj].config(bg="lightyellow")
                else:
                    entries[ii][jj].config(bg="white")

    def conf(event):
        canvas5.configure(scrollregion=canvas5.bbox("all"))

    header = ["Betű", "Darab", "Pontszám", "Típus", "Előfordulás", "Csere"]
    recordpointerindex = 0
    popup7 = Toplevel()
    popup7.title("Betűkészlet")
    popup7.transient(popup4)

    # Fejléc
    frame399 = Frame(popup7, bg='#d6d6d6')
    frame399.grid(row=0, column=0, sticky=W, columnspan=4)
    entry500 = None
    for w in range(len(data[0])):
        var500 = StringVar()
        var500.set(header[w])
        entry500 = Entry(frame399, width=11, bg="#bebebe", justify=CENTER, textvariable=var500, relief=FLAT,
                         state="readonly")
        entry500.grid(row=0, column=w)
        frame399.grid_columnconfigure(w, pad=pad1)
    frame399.grid_rowconfigure(1, pad=pad1)
    # Adatbeviteli mezők
    frame400 = Frame(popup7, bg='#d6d6d6')
    frame400.grid(row=1, column=0, columnspan=4)

    canvas5 = Canvas(frame400, width=500)
    frame500 = Frame(canvas5, bg='#d6d6d6')

    scrollbar = Scrollbar(frame400, orient="vertical", command=canvas5.yview)
    canvas5.configure(yscrollcommand=scrollbar.set)
    scrollbar.pack(side="right", fill="y")
    canvas5.pack()
    canvas5.create_window((0, 0), window=frame500, anchor='nw')
    frame500.bind("<Configure>", conf)

    createentries()

    button111a = Button(popup7, text='Beszúrás', command=insertrecord)
    button111a.grid(row=2, column=0)

    button111a = Button(popup7, text='Új', command=newrecord)
    button111a.grid(row=2, column=1)

    button111b = Button(popup7, text='Törlés', command=deleterecord)
    button111b.grid(row=2, column=2)

    button111c = Button(popup7, text='Rendben', command=com1)
    button111c.grid(row=2, column=3)

    drawrecordpointer()

    popup7.grab_set()
    popup4.wait_window(popup7)


def bonuses(caller):
    # Lerakott betűk száma utáni jutalom beállítása
    def com1():
        entries = [entry30, entry31, entry32, entry33, entry34, entry35, entry36, entry37, entry38]
        com2(entries)

    def com2(entries1):

        def validate3(entries2):
            try:
                int(entries2[0].get())
                int(entries2[1].get())
                int(entries2[2].get())
                int(entries2[3].get())
                int(entries2[4].get())
                int(entries2[5].get())
                int(entries2[6].get())
                int(entries2[7].get())
                int(entries2[8].get())
                return 1
            except ValueError:
                tkinter.messagebox.showerror("Hibás érték", "Csak számjegyeket fogadnak a beviteli mezők",
                                             parent=popup4)
                return 0

        if not validate3(entries1):
            return
        if caller == "numberofplacedletters":
            options.twoletterbonus = int(entries1[0].get())
            options.threeletterbonus = int(entries1[1].get())
            options.fourletterbonus = int(entries1[2].get())
            options.fiveletterbonus = int(entries1[3].get())
            options.sixletterbonus = int(entries1[4].get())
            options.sevenletterbonus = int(entries1[5].get())
            options.eightletterbonus = int(entries1[6].get())
            options.nineletterbonus = int(entries1[7].get())
            options.tenletterbonus = int(entries1[8].get())
        else:
            options.wordtwoletterbonus = int(entries1[0].get())
            options.wordthreeletterbonus = int(entries1[1].get())
            options.wordfourletterbonus = int(entries1[2].get())
            options.wordfiveletterbonus = int(entries1[3].get())
            options.wordsixletterbonus = int(entries1[4].get())
            options.wordsevenletterbonus = int(entries1[5].get())
            options.wordeightletterbonus = int(entries1[6].get())
            options.wordnineletterbonus = int(entries1[7].get())
            options.wordtenletterbonus = int(entries1[8].get())
        popup7.destroy()

    popup7 = Toplevel()
    popup7.transient(popup4)
    popup7.title("Jutalmak")

    Label(popup7, text="Felhasznált betűk").grid(row=0, column=0)
    Label(popup7, text="Jutalom").grid(row=0, column=1)

    i = 1
    for w in ["2", "3", "4", "5", "6", "7", "8", "9", "10"]:
        Label(popup7, text=w).grid(row=i, column=0)
        i += 1
    entry30 = Entry(popup7, width=3, bg="white", justify=RIGHT, relief=FLAT)
    entry30.grid(row=1, column=1)
    entry30.insert(END, str(options.twoletterbonus) if  caller == "numberofplacedletters" else str(options.wordtwoletterbonus))
    entry30.focus_set()
    entry31 = Entry(popup7, width=3, bg="white", justify=RIGHT, relief=FLAT)
    entry31.grid(row=2, column=1)
    entry31.insert(END, str(options.threeletterbonus if  caller == "numberofplacedletters" else str(options.wordthreeletterbonus)))
    entry32 = Entry(popup7, width=3, bg="white", justify=RIGHT, relief=FLAT)
    entry32.grid(row=3, column=1)
    entry32.insert(END, str(options.fourletterbonus if  caller == "numberofplacedletters" else str(options.wordfourletterbonus)))
    entry33 = Entry(popup7, width=3, bg="white", justify=RIGHT, relief=FLAT)
    entry33.grid(row=4, column=1)
    entry33.insert(END, str(options.fiveletterbonus if  caller == "numberofplacedletters" else str(options.wordfiveletterbonus)))
    entry34 = Entry(popup7, width=3, bg="white", justify=RIGHT, relief=FLAT)
    entry34.grid(row=5, column=1)
    entry34.insert(END, str(options.sixletterbonus if  caller == "numberofplacedletters" else str(options.wordsixletterbonus)))
    entry35 = Entry(popup7, width=3, bg="white", justify=RIGHT, relief=FLAT)
    entry35.grid(row=6, column=1)
    entry35.insert(END, str(options.sevenletterbonus if  caller == "numberofplacedletters" else str(options.wordsevenletterbonus)))
    entry36 = Entry(popup7, width=3, bg="white", justify=RIGHT, relief=FLAT)
    entry36.grid(row=7, column=1)
    entry36.insert(END, str(options.eightletterbonus if  caller == "numberofplacedletters" else str(options.wordeightletterbonus)))
    entry37 = Entry(popup7, width=3, bg="white", justify=RIGHT, relief=FLAT)
    entry37.grid(row=8, column=1)
    entry37.insert(END, str(options.nineletterbonus if  caller == "numberofplacedletters" else str(options.wordnineletterbonus)))
    entry38 = Entry(popup7, width=3, bg="white", justify=RIGHT, relief=FLAT)
    entry38.grid(row=9, column=1)
    entry38.insert(END, str(options.tenletterbonus if  caller == "numberofplacedletters" else str(options.wordtenletterbonus)))
    button111 = Button(popup7, text='Rendben', command=com1)
    button111.grid(row=10, column=1)

    popup7.grab_set()
    popup4.wait_window(popup7)


def createoreditboard(board1):
    # Új tábla készítése, vagy meglevő szerkesztése
    buttons = copy.deepcopy(board1)

    def selectletter(button, v11, w11):
        """Betű kiválasztása"""
        popup11 = Toplevel()
        popup11.transient(popup7)
        popup11.title("Válassz egy betűt")
        i = 0
        j = 0
        button125 = []
        b1 = []
        for br in bricks:
            b1.append(br.letter)
        b1.extend(['?', '1', '2', '3', '4', '5', '6', '7', '8', '9'])
        while 1:
            if j == len(b1):
                break
            letter = b1[j]
            if letter == '*':
                j += 1
            else:
                button125.append('*')
                button125[i] = Button(popup11, width=buttonwidth+2, height=1, padx=1, pady=1, text=letter,
                                      command=lambda letter=letter: writeletter(letter, button, popup11, v11, w11))
                button125[i].grid(row=i // 7, column=i % 7)
                i += 1
                j += 1

        popup11.grab_set()
        popup7.wait_window(popup11)

    def writeletter(letter, button, popup11, v11, w11):
        popup11.destroy()
        button.configure(text=letter)
        board1[v11][w11] = letter

    def writecfg():
        """Tábla változásainak fájlba mentése"""
        options.lastopenedcfg = tkinter.filedialog.asksaveasfilename(
                                                                     initialdir=".", initialfile=options.lastopenedcfg,
                                                                     title="Tábla mentése fájlba",
                                                                     filetypes=(
                                                                                ("Konfigurációs fájlok ", "*.cfg"),
                                                                                ("all files", "*.*")))
        config.set('Rules', 'racksize', str(options.racksize))
        config.set('Rules', 'turnlimit', str(options.turnlimit))
        config.set('Rules', 'turnlimitcount', str(options.turnlimitcount))
        config.set('Rules', 'changeincreasepasses', str(options.changeincreasepasses))
        config.set('Rules', 'timelimit', str(options.timelimit))
        config.set('Rules', 'duplicate', str(options.duplicate))
        config.set('Rules', 'independentboards', str(options.independentboards))
        config.set('Rules', 'randommultiplier', str(options.randommultiplier))
        mvaluesstr = ",".join(str(v11) for v11 in options.mvalues)
        config.set('Rules', 'mvalues', mvaluesstr)
        config.set('Rules', 'connect', str(options.connect))
        config.set('Rules', 'startfield', str(options.startfield))
        config.set('Rules', 'startfieldx', str(options.startfieldx))
        config.set('Rules', 'startfieldy', str(options.startfieldy))
        config.set('Rules', 'resetsack', str(options.resetsack))
        config.set('Rules', 'resetall', str(options.resetall))
        config.set('Rules', 'randomlettervalue', str(options.randomlettervalue))
        valuesstr = ",".join(str(v11) for v11 in options.values)
        config.set('Rules', 'values', valuesstr)
        config.set('Rules', 'checkdictionary', str(options.checkdictionary))
        config.set('Rules', 'dontchangejoker', str(options.dontchangejoker))
        config.set('Rules', 'onedirection', str(options.onedirection))
        config.set('Rules', 'usefletters', str(options.usefletters))
        flettersstr = "\n" + "\n".join(options.fletters)
        config.set('Rules', 'fletters', flettersstr)
        config.set('Rules', 'valueofchangedletter', str(options.valueofchangedletter))
        config.set('Rules', 'limitedvisibility', str(options.limitedvisibility))
        config.set('Rules', 'optimizeddraw', str(options.optimizeddraw))
        config.set('Rules', 'resetfrack', str(options.resetfrack))
        config.set('Rules', 'checkattheend', str(options.checkattheend))
        config.set('Bonuses', 'lengthbonus', str(options.lengthbonus))
        config.set('Bonuses', 'twoletterbonus', str(options.twoletterbonus))
        config.set('Bonuses', 'threeletterbonus', str(options.threeletterbonus))
        config.set('Bonuses', 'fourletterbonus', str(options.fourletterbonus))
        config.set('Bonuses', 'fiveletterbonus', str(options.fiveletterbonus))
        config.set('Bonuses', 'sixletterbonus', str(options.sixletterbonus))
        config.set('Bonuses', 'sevenletterbonus', str(options.sevenletterbonus))
        config.set('Bonuses', 'eightletterbonus', str(options.eightletterbonus))
        config.set('Bonuses', 'nineletterbonus', str(options.nineletterbonus))
        config.set('Bonuses', 'tenletterbonus', str(options.tenletterbonus))
        config.set('Bonuses', 'wordlengthbonus', str(options.wordlengthbonus))
        config.set('Bonuses', 'wordtwoletterbonus', str(options.wordtwoletterbonus))
        config.set('Bonuses', 'wordthreeletterbonus', str(options.wordthreeletterbonus))
        config.set('Bonuses', 'wordfourletterbonus', str(options.wordfourletterbonus))
        config.set('Bonuses', 'worfiveletterbonus', str(options.wordfiveletterbonus))
        config.set('Bonuses', 'wordsixletterbonus', str(options.wordsixletterbonus))
        config.set('Bonuses', 'wordsevenletterbonus', str(options.wordsevenletterbonus))
        config.set('Bonuses', 'wordeightletterbonus', str(options.wordeightletterbonus))
        config.set('Bonuses', 'wordnineletterbonus', str(options.wordnineletterbonus))
        config.set('Bonuses', 'wordtenletterbonus', str(options.wordtenletterbonus))
        config.set('Bonuses', 'oldbonusonly', str(options.oldbonusonly))
        config.set('Bonuses', 'useoldbonus', str(options.useoldbonus))
        config.set('Bonuses', 'useoldbonusvalue', str(options.useoldbonusvalue))
        config.set('Bonuses', 'wordperturnbonus', str(options.wordperturnbonus))
        config.set('Bonuses', 'wordperturnbonusvalue', str(options.wordperturnbonusvalue))
        config.set('Bonuses', 'bonusforusingall', str(options.bonusforusingall))
        config.set('Bonuses', 'fixpoint', str(options.fixpoint))
        config.set('Bonuses', 'pointforfinish', str(options.pointforfinish))
        config.set('Bonuses', 'valueforeachletter', str(options.valueforeachletter))
        config.set('Bonuses', 'pointforeachletter', str(options.pointforeachletter))
        config.set('Bonuses', 'penaltyforleft', str(options.penaltyforleft))
        config.set('Bonuses', 'pvalueforeachletter', str(options.pvalueforeachletter))
        config.set('Bonuses', 'ppointforeachletter', str(options.ppointforeachletter))

        board1text = ['.'] * len(board1)
        for line11 in range(len(board1)):
            board1text[line11] = " ".join(board1[line11])
        board10 = "\n"
        board11 = "\n".join(board1text)
        board10 += board11
        config.set('Board', 'board', board10)

        config.set('Appearance', 'size', str(options.size))
        config.set('Appearance', 'bricksize', str(options.size))
        config.set('Appearance', 'gap', str(options.gap))
        config.set('Appearance', 'colornormal', options.colornormal)
        config.set('Appearance', 'colorfix', options.colorfix)
        config.set('Appearance', 'colordoublel', options.colordoubleL)
        config.set('Appearance', 'colortriplel', options.colortripleL)
        config.set('Appearance', 'colordoublew', options.colordoubleW)
        config.set('Appearance', 'colortriplew', options.colortripleW)
        config.set('Appearance', 'colorwall', options.colorwall)
        config.set('Appearance', 'colorborder', options.colorborder)

        config.set('Appearance', 'colortext', options.colortext)

        config.set('Appearance', 'colornormalbrick', options.colornormalbrick)
        config.set('Appearance', 'colordoublebrick', options.colordoublebrick)
        config.set('Appearance', 'colortriplebrick', options.colortriplebrick)
        config.set('Appearance', 'colordoublewordbrick', options.colordoublewordbrick)
        config.set('Appearance', 'colortriplewordbrick', options.colortriplewordbrick)
        config.set('Appearance', 'colorborderbrick', options.colorborderbrick)
        config.set('Appearance', 'colortextbrick', options.colortextbrick)
        config.set('Appearance', 'colorvaluebrick', options.colorvaluebrick)
        config.set('Appearance', 'colorchangedbrick', options.colorchangedbrick)

        config.set('Appearance', 'fborder', str(options.fborder))
        config.set('Appearance', 'bborder', str(options.bborder))
        with open(options.lastopenedcfg, 'w', encoding="utf8") as configfile:
            config.write(configfile)
        popup7.destroy()

    def changefield(v12, w12, button):
        """Tábla mezőjének megváltoztatása"""
        if options.fieldtype == '.':
            col11 = options.colornormal
            button.configure(bg=col11, activebackground=col11, text="")
            board1[v12][w12] = '.'
        elif options.fieldtype == '2L':
            col11 = options.colordoubleL
            button.configure(bg=col11, activebackground=col11, text="")
            board1[v12][w12] = '2L'
        elif options.fieldtype == '2W':
            col11 = options.colordoubleW
            button.configure(bg=col11, activebackground=col11, text="")
            board1[v12][w12] = '2W'
        elif options.fieldtype == '3L':
            col11 = options.colortripleL
            button.configure(bg=col11, activebackground=col11, text="")
            board1[v12][w12] = '3L'
        elif options.fieldtype == '3W':
            col11 = options.colortripleW
            button.configure(bg=col11, activebackground=col11, text="")
            board1[v12][w12] = '3W'
        elif options.fieldtype == '!':
            col11 = options.colorwall
            button.configure(bg=col11, activebackground=col11, text="")
            board1[v12][w12] = '!'
        else:
            col11 = options.colorfix
            selectletter(button, v12, w12)
            button.configure(bg=col11, activebackground=col11)

    def conf(event):
        canvas5.configure(scrollregion=canvas5.bbox("all"))

    popup7 = Toplevel()
    popup7.title("Tábla szerkesztése")

    def changefieldtype(menu1):
        if menu1 == 0:
            options.fieldtype = '.'
        elif menu1 == 1:
            options.fieldtype = None
        elif menu1 == 2:
            options.fieldtype = '2L'
        elif menu1 == 3:
            options.fieldtype = '3L'
        elif menu1 == 4:
            options.fieldtype = '2W'
        elif menu1 == 5:
            options.fieldtype = '3W'
        elif menu1 == 6:
            options.fieldtype = '!'

    def popupmenu(event):
        """Menü megjelenítése a kattintás helyén"""
        menu.post(event.x_root, event.y_root)

    button111 = Button(popup7, text='Rendben', command=writecfg)
    button111.pack(expand=1, fill=BOTH, side=BOTTOM)
    frame400 = Frame(popup7, bg='#d6d6d6')
    frame400.pack()
    canvas5 = Canvas(frame400)
    frame500 = Frame(canvas5, bg='#d6d6d6')

    menu = Menu(canvas5, tearoff=0)
    menu.add_command(label="Normál", command=lambda menu1=0: changefieldtype(menu1))
    menu.add_command(label="Előre beírt", command=lambda menu1=1: changefieldtype(menu1))
    menu.add_command(label="Betűduplázó", command=lambda menu1=2: changefieldtype(menu1))
    menu.add_command(label="Betűtriplázó", command=lambda menu1=3: changefieldtype(menu1))
    menu.add_command(label="Szóduplázó", command=lambda menu1=4: changefieldtype(menu1))
    menu.add_command(label="Szótriplázó", command=lambda menu1=5: changefieldtype(menu1))
    menu.add_command(label="Fal", command=lambda menu1=6: changefieldtype(menu1))

    scrollbarv = Scrollbar(frame400, orient="vertical", command=canvas5.yview)
    scrollbarh = Scrollbar(frame400, orient="horizontal", command=canvas5.xview)

    scrollbarv.pack(side="right", fill="y")
    scrollbarh.pack(side="bottom", fill="x")
    canvas5.pack()
    canvas5.create_window((0, 0), window=frame500, anchor='nw')
    canvas5.configure(yscrollcommand=scrollbarv.set, xscrollcommand=scrollbarh.set)
    frame500.bind("<Configure>", conf)
    for v12 in range(len(board1)):
        for w12 in range(len(board1[0])):
            if board1[v12][w12] == ".":
                color11 = options.colornormal
            elif board1[v12][w12] == "2L":
                color11 = options.colordoubleL
            elif board1[v12][w12] == "3L":
                color11 = options.colortripleL
            elif board1[v12][w12] == "2W":
                color11 = options.colordoubleW
            elif board1[v12][w12] == "3W":
                color11 = options.colortripleW
            elif board1[v12][w12] == "!":
                color11 = options.colorwall
            else:
                color11 = options.colorfix
            if board1[v12][w12] not in options.fieldsdict:
                text1 = board1[v12][w12]
            else:
                text1 = ""
            buttons[v12][w12] = Button(frame500, bg=color11, relief=FLAT, text=text1, font=("Sans", 10),
                                       width=buttonwidth+2, height=1, padx=1, pady=1, activebackground=color11)
            buttons[v12][w12].configure(command=lambda v12=v12, w12=w12, button=buttons[v12][w12]:
                                        changefield(v12, w12, button))
            buttons[v12][w12].grid(row=v12, column=w12)
            buttons[v12][w12].bind("<Button-3>", popupmenu)
            frame500.grid_columnconfigure(w12, pad=pad1)
        frame500.grid_rowconfigure(v12, pad=pad1)
    buttons[0][0].update()
    canvas5.configure(yscrollcommand=scrollbarv.set, xscrollcommand=scrollbarh.set,
                      width=len(board1[0]) * (buttons[0][0].winfo_width()+1),
                      height=len(board1) * (buttons[0][0].winfo_height()+1))
    canvas5.config(scrollregion=canvas5.bbox("all"))
    popup7.grab_set()
    popup4.wait_window(popup7)


def errormessage(error, parent1):
    """Hibaüzenetek megjelenítése"""
    tkinter.messagebox.showerror("Szabálytalan", error, parent=parent1)


def pass1():
    """Forduló kihagyása"""
    global countofpasses
    global turns

    decision = tkinter.messagebox.askquestion("Passz", "Valóban ki akarsz maradni a fordulóból?")
    if decision == "yes":
        countofpasses += 1
        if options.gamemode == 1:
            chatboxmessage("Passz\n")
            if countofpasses == 2:
                chatboxmessage("A játéknak vége\n")
                endofgame()
            else:
                chatboxmessage(str(2 - countofpasses) + " passz és a játéknak vége\n")
            turns += 1
            if options.turnlimit and turns == options.turnlimitcount:
                endofgame()
                return
            counter.config(state="normal", text=str(turns + 1))
            starttimer()
        if options.gamemode != 1:
            # print("sent: PASS")
            queue1.put("PASS")
            unbind1()
            lockon()


def endofgame():
    """Eredmény kijelzése a játék végén"""
    global servproc
    global aiclientprocl
    global timeractive
    unbind1()
    lockon()
    popup11 = Toplevel(bg="lightblue")
    popup11.transient(appwin)
    popup11.title("Vége a játéknak")

    pb1.configure(style="green.Vertical.TProgressbar", maximum=options.timelimit - 2, length=frame0.winfo_height())
    timeractive = False
    if options.gamemode == 1:
        la1 = Label(popup11, text="A játéknak vége",
                    font=(tkinter.font.nametofont("TkFixedFont").actual()["family"], 25), bg="lightblue")
        la1.grid(row=0, column=0, padx=10, pady=10)
        la2 = Label(popup11, text=str(totalscore) + " pontot értél el",
                    font=(tkinter.font.nametofont("TkFixedFont").actual()["family"], 25), bg="lightblue")
        la2.grid(row=1, column=0, padx=10, pady=10)
        chatboxmessage("A játéknak vége\n")
        chatboxmessage(str(totalscore) + " pontot értél el\n")
    else:
        draw = False
        winner = ""
        result = sorted(players, key=itemgetter(2), reverse=True)
        if (options.gamemode == 2 and options.aiopponent > 0) or (
                options.gamemode == 3 and options.networkopponent > 0):
            if result[0][2] == result[1][2]:
                draw = True
            else:
                winner = result[0]
            if draw:
                text00 = 'Döntetlen\n\n\n'
            else:
                text00 = winner[0] + ' nyerte a játékot\n\n\n'
            for i in range(len(players)):
                text00 = text00 + players[i][0] + " " * (20 - len(players[i][0]) + 5 - len(str(players[i][2]))) + str(
                    players[i][2]) + "\n"
            la1 = Label(popup11, text=text00, font=(tkinter.font.nametofont("TkFixedFont").actual()["family"], 25),
                        bg="lightblue", justify=LEFT)
            la1.grid(row=0, column=0, padx=10, pady=10)
            chatboxmessage(text00 + "\n")
        else:
            la1 = Label(popup11, text="A játéknak vége",
                        font=(tkinter.font.nametofont("TkFixedFont").actual()["family"], 25), bg="lightblue")
            la1.grid(row=0, column=0, padx=10, pady=10)
            la2 = Label(popup11, text=str(totalscore) + " pontot értél el",
                        font=(tkinter.font.nametofont("TkFixedFont").actual()["family"], 25), bg="lightblue")
            la2.grid(row=1, column=0, padx=10, pady=10)
            chatboxmessage("A játéknak vége\n")
            chatboxmessage(str(totalscore) + " pontot értél el\n")
    try:
        hindsack()
    except (NameError, AttributeError):
        pass
    var100.set(0)
    if options.gamemode == 2:
        subprocess.Popen.terminate(servproc)
        for aiproc in aiclientprocl:
            try:
                subprocess.Popen.terminate(aiproc)
            except OSError:
                pass

def drawsack():
    """Zsák rajzolása"""
    global popup3
    global sack1
    global buttonsack

    def closewin():
        hindsack()
        var100.set(0)

    popup3 = Toplevel(bg="#cecece")
    popup3.title("Készlet")
    popup3.transient(appwin)
    i = 0
    j = 0
    while 1:
        if j == len(sack1):
            break
        rec = []
        b0001 = (Button(popup3, bg="#cecece", width=2, padx=1, pady=1, height=1, text=sack1[j].letter))
        b0001.grid(row=i // 7, column=i % 7)
        popup3.rowconfigure(i//7, pad=pad1)
        popup3.columnconfigure(i%7, pad=pad1)
        rec.append(b0001)
        rec.append(sack1[j])
        buttonsack.append(rec)
        i += 1
        j += 1
    managesack()
    popup3.protocol("WM_DELETE_WINDOW", closewin)


def hindsack():
    """Zsák elrejtése"""
    global buttonsack
    global popup3
    popup3.destroy()
    popup3 = None
    buttonsack = []


def managesack():
    """Zsák kezelése"""
    global buttonsack
    for i in range(len(buttonsack)):
        if buttonsack[i][1].used:
            buttonsack[i][0].configure(relief=FLAT, disabledforeground="#a3a3a3", bg="#cecece", state="disabled")
        else:
            buttonsack[i][0].configure(relief=RAISED, foreground="black", bg="#cecece", state="normal")


def notstartfield():
    errormessage("Nem a kezdő mezőre esik", appwin)


def notline():
    errormessage("A lerakott betűk nem esnek egyvonalba", appwin)


def notcontinuous():
    errormessage("A lerakott és a táblán lévő betűk nem kapcsolódnak", appwin)


def short():
    errormessage("A beállított szabályok alapján legalább két új betűt le kell rakni", appwin)


def appended():
    errormessage("A beállított szabályok alapján nem lehet a táblán levő szót megtoldani", appwin)


def notenoughletter():
    errormessage("Nincs már elég betű hátra a cseréhez", appwin)


def back():
    """Kirakott de nem véglegesített betűk visszavétele a tábláról"""
    global fields
    global rackfields
    global frack
    global frackfields
    global rack
    for i in range(options.racksize):
        if rack[i] is not None:
            if ontheboard(rack[i].x, rack[i].y) and len(canvas1.gettags(rack[i].objectlist[0])) == 1:
                try:
                    canvas1.delete(rack[i].objectlist[3])
                    canvas1.delete(rack[i].objectlist[4])
                except (NameError, AttributeError):
                    pass
                for z in range(options.racksize):
                    if rackfields[z].type == ".":
                        if rack[i].letter == '*':
                            canvas1.delete(rack[i].objectlist[1])
                            rack[i].objectlist[1] = canvas1.create_text(rackfields[z].cx, rackfields[z].cy + 2, font=(
                                options.letterfont, options.letterfontsize), text=rack[i].letter)
                            if options.valueofchangedletter:
                                canvas1.delete(rack[i].objectlist[2])
                                rack[i].value = rack[i].changedvalue
                                rack[i].changedvalue = None
                                rack[i].objectlist[2] = canvas1.create_text(rackfields[z].b1x, rackfields[z].b1y,
                                                                            font=(
                                                                                options.valuefont,
                                                                                options.valuefontsize),
                                                                            text=rack[i].value)
                        canvas1.coords(rack[i].objectlist[0], rackfields[z].b1x, rackfields[z].b1y, rackfields[z].b2x,
                                       rackfields[z].b2y)
                        canvas1.coords(rack[i].objectlist[1], rackfields[z].cx, rackfields[z].cy + 2)
                        canvas1.coords(rack[i].objectlist[2], rackfields[z].b1x + options.wx,
                                       rackfields[z].b1y + options.wy)
                        rackfields[z].type = "occupied"
                        for m in range(fieldrc):
                            for n in range(fieldcc):
                                if fields[m][n].x == rack[i].x and fields[m][n].y == rack[i].y:
                                    fields[m][n].type = board[m][n]
                        rack[i].x = rackfields[z].x
                        rack[i].y = rackfields[z].y
                        rack[i].cx = rackfields[z].cx
                        rack[i].cy = rackfields[z].cy
                        rack[i].b1x = rackfields[z].b1x
                        rack[i].b1y = rackfields[z].b1y
                        rack[i].b2x = rackfields[z].b2x
                        rack[i].b2y = rackfields[z].b2y
                        canvas1.addtag_withtag('racks', rack[i].objectlist[0])
                        canvas1.addtag_withtag('racks', rack[i].objectlist[1])
                        canvas1.addtag_withtag('racks', rack[i].objectlist[2])
                        detectabove(rack[i])
                        break
    if options.usefletters:
        for z in range(len(frack)):
            if ontheboard(frack[z].x, frack[z].y) and len(canvas1.gettags(frack[z].objectlist[0])) == 1:
                try:
                    canvas1.delete(frack[z].objectlist[3])
                    canvas1.delete(frack[z].objectlist[4])
                except (NameError, AttributeError):
                    pass
                for m in range(fieldrc):
                    for n in range(fieldcc):
                        if fields[m][n].x == frack[z].x and fields[m][n].y == frack[z].y:
                            fields[m][n].type = board[m][n]
                frack[z].x = frackdict[frack[z]].x
                frack[z].y = frackdict[frack[z]].y
                frack[z].cx = frackdict[frack[z]].cx
                frack[z].cy = frackdict[frack[z]].cy
                frack[z].b1x = frackdict[frack[z]].b1x
                frack[z].b1y = frackdict[frack[z]].b1y
                frack[z].b2x = frackdict[frack[z]].b2x
                frack[z].b2y = frackdict[frack[z]].b2y
                canvas1.coords(frack[z].objectlist[0], frack[z].b1x, frack[z].b1y, frack[z].b2x, frack[z].b2y)
                if frack[z].letter == '*' and not options.dontchangejoker:
                    canvas1.delete(frack[z].objectlist[1])
                    frack[z].objectlist[1] = canvas1.create_text(frack[z].cx, frack[z].cy + 2,
                                                                 font=(options.letterfont, options.letterfontsize),
                                                                 text=frack[z].letter)
                    if options.valueofchangedletter:
                        canvas1.delete(frack[z].objectlist[2])
                        frack[z].value = frack[z].changedvalue
                        frack[z].changedvalue = None
                        frack[z].objectlist[2] = canvas1.create_text(frack[z].b1x, frack[z].b1y,
                                                                     font=(options.valuefont, options.valuefontsize),
                                                                     text=frack[z].value)
                canvas1.coords(frack[z].objectlist[1], frack[z].cx, frack[z].cy + 2)
                canvas1.coords(frack[z].objectlist[2], frack[z].b1x + options.wx, frack[z].b1y + options.wy)
                canvas1.addtag_withtag('racks', frack[z].objectlist[0])
                canvas1.addtag_withtag('racks', frack[z].objectlist[1])
                canvas1.addtag_withtag('racks', frack[z].objectlist[2])
                detectabove(frack[z])
    repairboard()


def shuffle1():
    """Tartón levő betűk keverése"""
    global rack
    back()
    shuffle(rack)
    for i in range(options.racksize):
        if rack[i] is not None:
            canvas1.coords(rack[i].objectlist[0], rackfields[i].b1x, rackfields[i].b1y, rackfields[i].b2x,
                           rackfields[i].b2y)
            canvas1.coords(rack[i].objectlist[1], rackfields[i].cx, rackfields[i].cy + 2)
            canvas1.coords(rack[i].objectlist[2], rackfields[i].b1x + options.wx, rackfields[i].b1y + options.wy)
            rack[i].x = rackfields[i].x
            rack[i].y = rackfields[i].y
            rack[i].cx = rackfields[i].cx
            rack[i].cy = rackfields[i].cy
            rack[i].b1x = rackfields[i].b1x
            rack[i].b1y = rackfields[i].b1y
            rack[i].b2x = rackfields[i].b2x
            rack[i].b2y = rackfields[i].b2y


def swap():
    """Kijelölt betűk cseréje"""
    global wanttochange
    global sack
    global requirechange
    global turns
    global rack
    if options.gamemode == 1:
        if not options.resetsack:
            if len(wanttochange) == 0:
                errormessage("Nincs cserére jelölt betű", appwin)
                return
        else:
            wanttochange = rack[:]
            back()
        chatboxmessage(str(len(wanttochange)) + " betű cserélve\n")
        turns += 1
        if options.turnlimit and turns == options.turnlimitcount:
            endofgame()
            return
        counter.config(state="normal", text=str(turns + 1))
    if options.gamemode != 1:
        if options.duplicate or options.resetsack:
            wanttochange = []
            for i in range(len(rack)):
                if rack[i] is not None:
                    wanttochange.append(rack[i])
                else:
                    # print("Nincs már lehetőség cserélni")
                    return
        elif len(wanttochange) == 0:
            errormessage("Nincs cserére jelölt betű", appwin)
            return
        requirechange = True
        unbind1()
        lockon()
        swapwithserver()
        return
    jokeronrack = False
    try:
        for i in range(len(rack)):
            if rack[i].letter == '*':
                jokeronrack = True
                break
    except Exception:
        pass
    for i in range(len(wanttochange)):
        randomnumber = drawletter(i)
        for j in range(options.racksize):
            if rack[j] == wanttochange[i]:
                canvas1.delete(rack[j].objectlist[0])
                canvas1.delete(rack[j].objectlist[1])
                canvas1.delete(rack[j].objectlist[2])
                rack[j] = sack[randomnumber]
                rack[j].x = wanttochange[i].x
                rack[j].y = wanttochange[i].y
                rack[j].cx = wanttochange[i].cx
                rack[j].cy = wanttochange[i].cy
                rack[j].b1x = wanttochange[i].b1x
                rack[j].b1y = wanttochange[i].b1y
                rack[j].b2x = wanttochange[i].b2x
                rack[j].b2y = wanttochange[i].b2y
                if options.randomlettervalue:
                    values = options.values[:]
                    rn = randrange(len(values))
                    rack[j].value = values[rn]
                    values.pop(rn)
                if options.randommultiplier:
                    mvalues = options.mvalues[:]
                    rn = randrange(len(mvalues))
                    rack[j].multiplier = mvalues[rn]
                    rack[j].changedvalue = rack[j].value
                    rack[j].value = rack[j].value * mvalues[rn]
                c, bc = colors1(rack[j])
                rack[j].objectlist[0] = canvas1.create_rectangle(rack[j].b1x, rack[j].b1y, rack[j].b2x, rack[j].b2y,
                                                                 width=1, fill=c, outline=bc, tags=str(j))
                rack[j].objectlist[1] = canvas1.create_text(rack[j].cx, rack[j].cy + 2,
                                                            font=(options.letterfont, options.letterfontsize),
                                                            text=rack[j].letter, fill=options.colortextbrick, tags=str(j))
                rack[j].objectlist[2] = canvas1.create_text(rack[j].b1x + options.wx, rack[j].b1y + options.wy,
                                                            font=(options.valuefont, options.valuefontsize),
                                                            text=rack[j].value, fill=options.colorvaluebrick,
                                                            tags=str(j))
                if not options.valuedisplay:
                    canvas1.itemconfig(rack[j].objectlist[2], state="hidden")
                sack[randomnumber].used = True
                sack.pop(randomnumber)
                canvas1.addtag_withtag('racks', rack[j].objectlist[0])
                canvas1.addtag_withtag('racks', rack[j].objectlist[1])
                canvas1.addtag_withtag('racks', rack[j].objectlist[2])
    for k in range(len(wanttochange)):
        wanttochange[k].used = False
        sack.append(wanttochange[k])
    wanttochange = []
    managesack()
    starttimer()


def next1():
    """Lépés véglegesítése"""
    global ok1
    global turns
    ok1 = True
    if checktime:
        turns-=1
    lettersontheboard()


def loaddictionary():
    """Szótár betöltése"""
    global dictionary
    global partsofdictionary
    file = "szotar22a_kat.dic"
    abc2 = ('A', 'Á', 'B', 'C', 'CS', 'D', 'E', 'É', 'F', 'G', 'GY', 'H', 'I', 'Í', 'J', 'K', 'L', 'LY', 'M', 'N', 'NY',
           'O', 'Ó', 'Ö', 'Ő', 'P', 'Q', 'R', 'S', 'SZ', 'T', 'TY', 'U', 'Ú', 'Ü', 'Ű', 'V', 'W', 'X', 'Y', 'Z', 'ZS')
    for letter1 in abc2:
        for length1 in range(2, 35):
            partsofdictionary[letter1+str(length1)] = set()
    f = codecs.open(file, 'r', encoding='utf-8')
    while 1:
        line = f.readline()
        if line == '':
            break
        w = line.strip().split(" ")[0]
        dictionary.append(w)
    f.close()
    for word1 in dictionary:
        wordl1 = wordtotuples(word1)
        for w in wordl1:
            if '_' in w:
                w1 = list()
                for le in w:
                    if le != '_':
                        w1.append(le)
                w = tuple(w1)
            key1 = "".join([w[0], str(len(w))])
            try:
                partsofdictionary[key1].add(w)
            except KeyError:
                # print("except", w)
                pass
    return partsofdictionary


def wordtotuples(word1):
    """A szótár szavait listákká alakítja a kétjegyű mássalhangzókra tekintettel"""
    wordl1 = []
    digraph = ['CS', 'GY', 'LY', 'NY', 'SZ', 'TY', 'ZS']
    position = []
    i = 0
    while i < len(word1) - 1:
        if word1[i:i + 2] in digraph:
            position.append(i)
            i += 1
        i += 1
    if not position:
        wordl1.append(tuple(word1))
        return wordl1
    words1 = list()
    words1.append(word1)
    for j in position:
        for k in range(len(words1)):
            if words1[k][j:j + 2] == 'CS':
                newword = "".join([words1[k][:j], '01', words1[k][j + 2:]])
                words1.append(newword)
            elif words1[k][j:j + 2] == 'GY':
                newword = "".join([words1[k][:j], '02', words1[k][j + 2:]])
                words1.append(newword)
            elif words1[k][j:j + 2] == 'LY':
                newword = "".join([words1[k][:j], '03', words1[k][j + 2:]])
                words1.append(newword)
            elif words1[k][j:j + 2] == 'NY':
                newword = "".join([words1[k][:j], '04', words1[k][j + 2:]])
                words1.append(newword)
            elif words1[k][j:j + 2] == 'SZ':
                newword = "".join([words1[k][:j], '05', words1[k][j + 2:]])
                words1.append(newword)
            elif words1[k][j:j + 2] == 'TY':
                newword = "".join([words1[k][:j], '06', words1[k][j + 2:]])
                words1.append(newword)
            elif words1[k][j:j + 2] == 'ZS':
                newword = "".join([words1[k][:j], '07', words1[k][j + 2:]])
                words1.append(newword)
    for ws in words1:
        wordl = list(ws)
        wordlnew = []
        for i in range(len(wordl)):
            if wordl[i] == '0' or wordl[i] == '_':
                continue
            if wordl[i] in ['1', '2', '3', '4', '5', '6', '7']:
                if wordl[i] == '1':
                    wordlnew.append('CS')
                if wordl[i] == '2':
                    wordlnew.append('GY')
                if wordl[i] == '3':
                    wordlnew.append('LY')
                if wordl[i] == '4':
                    wordlnew.append('NY')
                if wordl[i] == '5':
                    wordlnew.append('SZ')
                if wordl[i] == '6':
                    wordlnew.append('TY')
                if wordl[i] == '7':
                    wordlnew.append('ZS')
            else:
                wordlnew.append(wordl[i])
        wordl1.append(tuple(wordlnew))
    return wordl1


def createabc1():
    global abc1

    if len(abc) < fieldrc:
        q = fieldrc // len(abc) + 1
        abc1 = []
        for n in range(1, q+1):
            for l2 in abc:
                abc1.append(l2 * n)
    else:
        abc1 = abc[:]


def assignvisiblefields(i,j):
    racksize=options.racksize
    for ii in range(0, racksize+1):
        for jj in range(0, racksize-ii+1):
            if -1 < i+ii < fieldrc and -1 < j+jj < fieldcc and  fields[i + ii][j + jj].visible == False:
                fields[i + ii][j + jj].visible = True
                canvas1.delete(fields[i + ii][j + jj].objectlist[0])
            if -1 < i-ii < fieldrc and -1 < j-jj < fieldcc and  fields[i - ii][j - jj].visible == False:
                fields[i - ii][j - jj].visible = True
                canvas1.delete(fields[i - ii][j - jj].objectlist[0])
            if -1 < i+ii < fieldrc and -1 < j-jj < fieldcc and  fields[i + ii][j - jj].visible == False:
                fields[i + ii][j - jj].visible = True
                canvas1.delete(fields[i + ii][j - jj].objectlist[0])
            if -1 < i-ii < fieldrc and -1 < j+jj < fieldcc and  fields[i - ii][j + jj].visible == False:
                fields[i - ii][j + jj].visible = True
                canvas1.delete(fields[i - ii][j + jj].objectlist[0])


def drawboard():
    """Tábla rajzolása"""
    global tabla
    global fields
    global rackfields
    global frackfields
    global firstmove
    global image11, image12, image13, image14, image15, image16
    global anchorimage
    global tray
    global fb0, fb1, fb2, fb3, fb3a
    createabc1()
    if options.limitedvisibility:
        for i in range(fieldrc):
            for j in range(fieldcc):
                fields[i][j].visible = False
        assignvisiblefields(options.startfieldx,options.startfieldy)
    else:
        for i in range(fieldrc):
            for j in range(fieldcc):
                fields[i][j].visible = True
                assignvisiblefields(i,j)
    if options.numbering:
        offset = 15
    else:
        offset = 15
    for j in range(fieldcc):
        for i in range(fieldrc):
            fields[i][j].x = j * (options.size + options.gap) + offset
            fields[i][j].y = i * (options.size + options.gap) + offset
            fields[i][j].cx = fields[i][j].x + options.size / 2 - 1
            fields[i][j].cy = fields[i][j].y + options.size / 2 - 1
            if fields[i][j].type in options.fieldsdict:
                if len(fields[i][j].type) == 1 and fields[i][j].type.isdigit():
                    lettertext = fields[i][j].type
                    fsize = options.valuefontsize
                else:
                    lettertext = ""
                    fsize= options.fixletterfontsize
                lettertextcolor = options.colortext
                bground = options.fieldsdict[fields[i][j].type][0]
            else:
                lettertext = fields[i][j].type
                fsize = options.fixletterfontsize
                lettertextcolor = options.colortext
                bground = options.colorfix
            if options.fborder:
                fc = options.colorborder
            else:
                fc = bground
            fields[i][j].f1x = fields[i][j].x + (options.size - options.fieldsize) / 2
            fields[i][j].f1y = fields[i][j].y + (options.size - options.fieldsize) / 2
            fields[i][j].f2x = fields[i][j].x + (options.size - options.fieldsize) / 2 + options.fieldsize - 1
            fields[i][j].f2y = fields[i][j].y + (options.size - options.fieldsize) / 2 + options.fieldsize - 1
            fields[i][j].b1x = fields[i][j].x + (options.size - options.bricksize) / 2
            fields[i][j].b1y = fields[i][j].y + (options.size - options.bricksize) / 2
            fields[i][j].b2x = fields[i][j].x + (options.size - options.bricksize) / 2 + options.bricksize - 1
            fields[i][j].b2y = fields[i][j].y + (options.size - options.bricksize) / 2 + options.bricksize - 1
            o1 = canvas1.create_rectangle(fields[i][j].f1x, fields[i][j].f1y, fields[i][j].f2x, fields[i][j].f2y,
                                     width=1, fill=bground, outline=fc)
            if len(lettertext) == 1 and lettertext.isdigit():
                o1a = canvas1.create_oval(fields[i][j].f1x+options.size/4, fields[i][j].f1y+options.size/4,
                                    fields[i][j].f2x-options.size/4, fields[i][j].f2y-options.size/4,
                                    width=1, fill="white", outline=fc)
            o2 = canvas1.create_text(fields[i][j].cx, fields[i][j].cy + 2,
                                font=(options.fixletterfont, fsize), text=lettertext, fill=lettertextcolor)
            if options.limitedvisibility and not fields[i][j].visible:
                fields[i][j].objectlist[0] = canvas1.create_rectangle(fields[i][j].f1x, fields[i][j].f1y,
                                                                       fields[i][j].f2x, fields[i][j].f2y,
                                                                       width=1, fill="gray", outline="gray")
            if options.numbering:
                if i == 0:
                    o3 = canvas1.create_text(fields[i][j].cx, 3, font=(options.fixletterfont, 8), text=str(j + 1),
                                        fill=lettertextcolor)
                if j == 0:
                    o4 = canvas1.create_text(3, fields[i][j].cy, font=(options.fixletterfont, 8), text=abc1[i],
                                        fill=lettertextcolor)
                if i == fieldrc - 1:
                    o5 = canvas1.create_text(fields[i][j].cx, fields[i][j].y + options.size + 5,
                                        font=(options.fixletterfont, 8), text=str(j + 1), fill=lettertextcolor)
                if j == fieldcc - 1:
                    o6 = canvas1.create_text(fields[i][j].x + options.size + 7, fields[i][j].cy,
                                        font=(options.fixletterfont, 8), text=abc1[i], fill=lettertextcolor)
    tabla = Part(0, 0, fields[i][j].x + (options.size - 1), fields[i][j].y + (options.size - 1))
    found = False
    for i in range(fieldrc):  # Ha az első lépés előtt már vannak betűk a táblán, és kötelező a kapcsolódás
        for j in range(fieldcc):
            if fields[i][j].type not in options.fieldsdict:
                found = True
                firstmove = False
                break
        if found:
            break
    # Kezdő mező kijelölése, ha van
    if options.startfield:
        canvas1.create_line(fields[options.startfieldx][options.startfieldy].x + 1,
                            fields[options.startfieldx][options.startfieldy].y + 1,
                            fields[options.startfieldx][options.startfieldy].x + (options.size - 1),
                            fields[options.startfieldx][options.startfieldy].y + (options.size - 1), fill="black")
        canvas1.create_line(fields[options.startfieldx][options.startfieldy].x + (options.size - 1),
                            fields[options.startfieldx][options.startfieldy].y + 1,
                            fields[options.startfieldx][options.startfieldy].x + 1,
                            fields[options.startfieldx][options.startfieldy].y + (options.size - 1), fill="black")
    z = fieldrc + 0.5
    if options.racksize > len(options.fletters):
        w = options.racksize
    else:
        if options.usefletters:
            w = len(options.fletters)
        else:
            w = options.racksize
    if options.usefletters:
        hm = 1.5
    else:
        hm = 0.5
    while 1:
        if appwin.winfo_height() < (z + hm) * (options.size + options.gap) + offset +70:
            z-=1
        else:
            break
    tray = canvas1.create_rectangle(offset - 5, z * (options.size + options.gap) + offset - 5,
                                    w * (options.size + options.gap) + 35,
                                    (z + hm) * (options.size + options.gap) + offset +70 , width=1, fill="#bebebe",
                                    outline="yellow")
    dashboardframe = Frame(canvas1)
    dashboardwindow = canvas1.create_window(canvas1.bbox(tray)[0]+5, canvas1.bbox(tray)[3]-35, anchor=NW, window=dashboardframe)
    image12 = tkinter.PhotoImage(file="back_icon.gif")
    fb0 = Button(dashboardframe, state="disabled", image=image12, command=back)
    fb0.grid(row=0, column=0, sticky=E + W)

    CreateToolTip(fb0, "Vissza\nAz összes táblára került, de\nmég nem véglegesített betű visszavétele.")

    image13 = tkinter.PhotoImage(file="shuffle_icon.gif")
    fb1 = Button(dashboardframe, state="disabled", image=image13, command=shuffle1)
    fb1.grid(row=0, column=1, sticky=E + W)

    CreateToolTip(fb1, "Keverés\nA betűk véletlenszerű átrendezése.")

    image14 = tkinter.PhotoImage(file="swap_icon.gif")
    fb2 = Button(dashboardframe, state="disabled", image=image14, command=swap)
    fb2.grid(row=0, column=2, sticky=E + W)

    CreateToolTip(fb2, "Csere\nAz egér jobb gombjával kijelölt betűk, vagy a teljes tartó cseréje.")

    image15 = tkinter.PhotoImage(file="ok_icon.gif")
    fb3 = Button(dashboardframe, state="disabled", image=image15, command=next1)
    fb3.grid(row=0, column=3, sticky=E + W)

    CreateToolTip(fb3,
                  "Rendben\nA fordulóban táblára került betűk véglegesítése. Szimultán játékban\nelküldi a szervernek," +
                  " de az idő lejártáig újabbak rakhatók ki.")

    image16 = tkinter.PhotoImage(file="next_icon.gif")
    fb3a = Button(dashboardframe, state="disabled", image=image16, command=complete)
    fb3a.grid(row=0, column=4, sticky=E + W)

    CreateToolTip(fb3a, "Végleges\nSzimultán játékban a lépés idő előtti\nvéglegesítésére szolgál.")

    canvas1.addtag_withtag('racks', dashboardwindow)
    canvas1.addtag_withtag('racks', tray)
    # Rack rajzolása:
    bground = options.colornormal
    if options.fborder:
        fc = options.colorborder
    else:
        fc = bground
    for i in range(options.racksize):
        rackfields[i] = Field(".", 0, z, i)
        rackfields[i].x = i * (options.size + options.gap) + offset
        rackfields[i].y = z * (options.size + options.gap) + offset
        rackfields[i].cx = rackfields[i].x + options.size / 2 - 1
        rackfields[i].cy = rackfields[i].y + options.size / 2 - 1
        rackfields[i].b1x = rackfields[i].x + (options.size - options.bricksize) / 2
        rackfields[i].b1y = rackfields[i].y + (options.size - options.bricksize) / 2
        rackfields[i].b2x = rackfields[i].x + (options.size - options.bricksize) / 2 + options.bricksize - 1
        rackfields[i].b2y = rackfields[i].y + (options.size - options.bricksize) / 2 + options.bricksize - 1
        rackfields[i].objectlist[0]= canvas1.create_rectangle(rackfields[i].b1x, rackfields[i].b1y, rackfields[i].b2x,
                                                              rackfields[i].b2y, width=1, fill=bground, outline=fc)
        canvas1.addtag_withtag('racks', rackfields[i].objectlist[0])
    image11 = tkinter.PhotoImage(file="anchor.gif")
    anchorimage = canvas1.create_image(rackfields[i].b2x+5 , rackfields[i].b1y, anchor=NW, image=image11)
    canvas1.addtag_withtag('racks', anchorimage)
    # Rack1 rajzolása:
    if options.usefletters:
        frackfields = [0] * len(options.fletters)
        for i in range(len(options.fletters)):
            frackfields[i] = Field(".", 0, z + 2, i)
            frackfields[i].x = i * (options.size + options.gap) + offset
            frackfields[i].y = (z+hm) * (options.size + options.gap) + offset
            frackfields[i].cx = frackfields[i].x + options.size / 2 - 1
            frackfields[i].cy = frackfields[i].y + options.size / 2 - 1
            frackfields[i].b1x = frackfields[i].x + (options.size - options.bricksize) / 2
            frackfields[i].b1y = frackfields[i].y + (options.size - options.bricksize) / 2
            frackfields[i].b2x = frackfields[i].x + (options.size - options.bricksize) / 2 + options.bricksize - 1
            frackfields[i].b2y = frackfields[i].y + (options.size - options.bricksize) / 2 + options.bricksize - 1
            frackfields[i].objectlist[0] = canvas1.create_rectangle(frackfields[i].b1x, frackfields[i].b1y,
                                                                   frackfields[i].b2x, frackfields[i].b2y,
                                                                   width=1, fill=bground, outline=fc)
            frackfields[i].objectlist[1] = canvas1.create_text(frackfields[i].cx, frackfields[i].cy + 2,
                                                               font=(options.letterfont, options.letterfontsize),
                                                               text=options.fletters[i].split(',')[0], fill="#bebebe")
            canvas1.addtag_withtag('racks', frackfields[i].objectlist[0])
            canvas1.addtag_withtag('racks', frackfields[i].objectlist[1])
    canvas1.config(width=canvas1.bbox(ALL)[2]+5, height=canvas1.bbox(ALL)[3]+5)
    canvas1.config(xscrollcommand=scrollbarh1.set)
    canvas1.config(yscrollcommand=scrollbarv1.set)
    canvas1.config(scrollregion=canvas1.bbox("all"))
    frame0.unbind("<Configure>")
    frame0.bind("<Configure>", conf0)


def chat1(event):
    """Szöveg küldése a szervernek"""
    v50 = "CHAT," + " " * 10 + options.username + " írja: " + var700.get() + "\n"
    if v50 != "":
        queue1.put(v50)
    var700.set("")


def init1():
    """Kiinduló beállítások"""
    global frack
    global fieldrc
    global fieldcc
    global board
    global boardoriginal
    global sack, sack1, sackl
    global bricks
    global fields, fieldstemp
    global rackfields
    global frackfields
    global rack
    global sec
    global turnscore
    global totalscore
    global whichrack
    global frackdict
    global config
    global notjokerbricks
    global ok1
    global selectedbrick
    global selectedbricki
    global wanttochange
    global dictionary
    global turnscore
    global totalscore
    global buttonsack
    global tabla
    global countofpasses
    global firstmove
    global lettersonrack
    global turns
    global popup1
    global popup3
    global popup4
    global players
    global currentplayer
    global timeractive
    global requirechange
    global notyourgame
    global th_E, th_R
    global servproc
    global aiclientprocl
    global numberofplayers
    global options
    global recordpointerindex
    global data
    global entries
    global letterreplacedict
    recordpointerindex = 0
    data = []
    entries= []
    numberofplayers = 1
    selectedbrick = None
    selectedbricki = None
    wanttochange = []
    dictionary = []
    sec = 0
    turnscore = 0
    totalscore = 0
    popup1 = None
    popup3 = None
    popup4 = None
    buttonsack = []
    tabla = None
    bricks = []
    sack = []
    sackl = []
    sack1 = []
    board = []
    boardoriginal = []
    fields = []
    fieldstemp = []
    rackfields = []
    frackfields = []
    score1.config(text=str(turnscore))
    score2.config(text=str(totalscore))
    countofpasses = 0
    lettersonrack = []
    firstmove = True
    notjokerbricks = []
    ok1 = False
    players = []
    currentplayer = ""
    timeractive = False
    requirechange = False
    notyourgame = False
    turns = 0
    th_E = None
    th_R = None
    servproc = None
    aiclientprocl = []
    letterreplacedict = dict()
    config = configparser.ConfigParser()
    config.read_file(open(options.lastopenedcfg, encoding="utf8"))
    options.racksize = int(config.get('Rules', 'racksize'))
    options.turnlimit = config.getboolean('Rules', 'turnlimit')
    options.turnlimitcount = int(config.get('Rules', 'turnlimitcount'))
    options.changeincreasepasses = config.getboolean('Rules', 'changeincreasepasses')
    options.timelimit = int(config.get('Rules', 'timelimit'))
    options.duplicate = config.getboolean('Rules', 'duplicate')
    options.independentboards = config.getboolean('Rules', 'independentboards')
    options.randommultiplier = config.getboolean('Rules', 'randommultiplier')
    charlist = config.get('Rules', 'mvalues').split(',')
    for i in range(len(charlist)):
        charlist[i] = int(charlist[i])
    options.mvalues = charlist
    options.connect = config.getboolean('Rules', 'connect')
    options.startfield = config.getboolean('Rules', 'startfield')
    options.startfieldx = int(config.get('Rules', 'startfieldx'))
    options.startfieldy = int(config.get('Rules', 'startfieldy'))
    options.resetsack = config.getboolean('Rules', 'resetsack')
    options.resetall = config.getboolean('Rules', 'resetall')
    options.randomlettervalue = config.getboolean('Rules', 'randomlettervalue')
    if options.randomlettervalue:
        options.valuemode = 2
    else:
        options.valuemode = 1
    charlist = config.get('Rules', 'values').split(',')
    for i in range(len(charlist)):
        charlist[i] = int(charlist[i])
    options.values = charlist
    options.checkdictionary = config.getboolean('Rules', 'checkdictionary')
    if options.checkdictionary:
        options.checkmode = 1
    else:
        options.checkmode = 2
    options.dontchangejoker = config.getboolean('Rules', 'dontchangejoker')
    options.onedirection = config.getboolean('Rules', 'onedirection')
    options.usefletters = config.getboolean('Rules', 'usefletters')
    fletters = config.get('Rules', 'fletters')
    options.fletters = fletters.splitlines()[1:]
    options.valueofchangedletter = config.getboolean('Rules', 'valueofchangedletter')
    options.limitedvisibility = config.getboolean('Rules', 'limitedvisibility')
    options.optimizeddraw = config.getboolean('Rules', 'optimizeddraw')
    options.resetfrack = config.getboolean('Rules', 'resetfrack')
    options.checkattheend = config.getboolean('Rules', 'checkattheend')
    options.lengthbonus = config.getboolean('Bonuses', 'lengthbonus')
    options.twoletterbonus = int(config.get('Bonuses', 'twoletterbonus'))
    options.threeletterbonus = int(config.get('Bonuses', 'threeletterbonus'))
    options.fourletterbonus = int(config.get('Bonuses', 'fourletterbonus'))
    options.fiveletterbonus = int(config.get('Bonuses', 'fiveletterbonus'))
    options.sixletterbonus = int(config.get('Bonuses', 'sixletterbonus'))
    options.sevenletterbonus = int(config.get('Bonuses', 'sevenletterbonus'))
    options.eightletterbonus = int(config.get('Bonuses', 'eightletterbonus'))
    options.nineletterbonus = int(config.get('Bonuses', 'nineletterbonus'))
    options.tenletterbonus = int(config.get('Bonuses', 'tenletterbonus'))
    options.wordlengthbonus = config.getboolean('Bonuses', 'wordlengthbonus')
    options.wordtwoletterbonus = int(config.get('Bonuses', 'wordtwoletterbonus'))
    options.wordthreeletterbonus = int(config.get('Bonuses', 'wordthreeletterbonus'))
    options.wordfourletterbonus = int(config.get('Bonuses', 'wordfourletterbonus'))
    options.wordfiveletterbonus = int(config.get('Bonuses', 'wordfiveletterbonus'))
    options.wordsixletterbonus = int(config.get('Bonuses', 'wordsixletterbonus'))
    options.wordsevenletterbonus = int(config.get('Bonuses', 'wordsevenletterbonus'))
    options.wordeightletterbonus = int(config.get('Bonuses', 'wordeightletterbonus'))
    options.wordnineletterbonus = int(config.get('Bonuses', 'wordnineletterbonus'))
    options.wordtenletterbonus = int(config.get('Bonuses', 'wordtenletterbonus'))
    options.oldbonusonly = config.getboolean('Bonuses', 'oldbonusonly')
    options.useoldbonus = config.getboolean('Bonuses', 'useoldbonus')
    options.useoldbonusvalue = int(config.get('Bonuses', 'useoldbonusvalue'))
    options.wordperturnbonus = config.getboolean('Bonuses', 'wordperturnbonus')
    options.wordperturnbonusvalue = int(config.get('Bonuses', 'wordperturnbonusvalue'))
    options.bonusforusingall = config.getboolean('Bonuses', 'bonusforusingall')
    options.fixpoint = config.getboolean('Bonuses', 'fixpoint')
    options.pointforfinish = int(config.get('Bonuses', 'pointforfinish'))
    options.valueforeachletter = config.getboolean('Bonuses', 'valueforeachletter')
    options.pointforeachletter = int(config.get('Bonuses', 'pointforeachletter'))
    options.penaltyforleft = config.getboolean('Bonuses', 'penaltyforleft')
    options.pvalueforeachletter = config.getboolean('Bonuses', 'pvalueforeachletter')
    options.ppointforeachletter = int(config.get('Bonuses', 'ppointforeachletter'))
    options.size = int(config.get('Appearance', 'size'))
    options.fieldsize = options.size
    options.bricksize = int(config.get('Appearance', 'bricksize'))
    options.gap = int(config.get('Appearance', 'gap'))
    options.colornormal = config.get('Appearance', 'colornormal')
    options.colorfix = config.get('Appearance', 'colorfix')
    options.colordoubleL = config.get('Appearance', 'colordoubleL')
    options.colortripleL = config.get('Appearance', 'colortripleL')
    options.colordoubleW = config.get('Appearance', 'colordoubleW')
    options.colortripleW = config.get('Appearance', 'colortripleW')
    options.colorwall = config.get('Appearance', 'colorwall')
    options.colorborder = config.get('Appearance', 'colorborder')
    options.colortext = config.get('Appearance', 'colortext')
    options.colornormalbrick = config.get('Appearance', 'colornormalbrick')
    options.colordoublebrick = config.get('Appearance', 'colordoublebrick')
    options.colortriplebrick = config.get('Appearance', 'colortriplebrick')
    options.colordoublewordbrick = config.get('Appearance', 'colordoublewordbrick')
    options.colortriplewordbrick = config.get('Appearance', 'colortriplewordbrick')
    options.colorborderbrick = config.get('Appearance', 'colorborderbrick')
    options.colortextbrick = config.get('Appearance', 'colortextbrick')
    options.colorvaluebrick = config.get('Appearance', 'colorvaluebrick')
    options.colorchangedbrick = config.get('Appearance', 'colorchangedbrick')
    options.fborder = config.getboolean('Appearance', 'fborder')
    options.bborder = config.getboolean('Appearance', 'bborder')
    if options.resetsack and not options.resetall:
        options.lettersetmode = 2
    elif options.resetsack and options.resetall:
        options.lettersetmode = 3
    else:
        options.lettersetmode = 1
    letters = config.get('Letters', 'letters')
    letterrows = letters.splitlines()
    for letterrow in letterrows:
        if letterrow == "":
            continue
        bricks.append(Brick(letterrow))
        for i in range(bricks[-1].count):
            sack.append(Brick(letterrow))
        try:
            letterreplacedict[bricks[-1].letter] = letterrow.split('[')[1].strip(']').split(',')
        except IndexError:
            pass
    sack1 = sack[:]
    for brck in bricks:
        if brck.letter != '*':
            notjokerbricks.append(brck)
    fields1 = config.get('Board', 'board')
    fieldrows = fields1.splitlines()
    fieldrc = len(fieldrows) - 1
    for fieldrow in fieldrows:
        if fieldrow == "":
            continue
        fieldrowl = fieldrow.split(' ')
        boardoriginal.append(fieldrowl[:])
        for i in range(len(fieldrowl)):
            if fieldrowl[i] == '?':
                 fieldrowl[i] = sack[randrange(len(sack))].letter
        board.append(fieldrowl)
    fieldcc = len(fieldrow.split(' '))
    fields = []
    for i in range(fieldrc):
        fields.append(["."] * fieldcc)
    for i in range(fieldrc):
        for j in range(fieldcc):
            fields[i][j] = Field(board[i][j], 0, i, j)
    rackfields = [0] * options.racksize
    frackfields = [0] * len(options.fletters)
    rack = [0] * options.racksize
    frack = []
    for i in range(len(options.wordlengthlist[0])):
        if i + 1 <= options.racksize:
            options.wordlengthlist[0][i] = 'True'
        else:
            options.wordlengthlist[0][i] = 'False'


def init2():
    """Végleges beállítások"""
    global frack
    global fieldrc
    global fieldcc
    global board
    global sack, sack1
    global bricks
    global fields, fieldstemp
    global rackfields
    global frackfields
    global rack
    global sec
    global turnscore
    global totalscore
    global whichrack
    global frackdict
    global config
    global notjokerbricks
    global ok1
    global numberofplayers
    global countofpasses
    global wanttochange
    global dictionary
    global buttonsack
    global tabla
    global lettersonrack
    global firstmove
    global turns
    numberofplayers = 1
    wanttochange = []
    dictionary = []
    sec = 0
    turnscore = 0
    totalscore = 0
    buttonsack = []
    tabla = None
    fields = []
    fieldstemp = []
    rackfields = []
    frackfields = []
    score1.config(text=str(turnscore))
    score2.config(text=str(totalscore))
    countofpasses = 0
    firstmove = True
    notjokerbricks = []
    turns = 0
    ok1 = False
    if options.gamemode == 1:
        sack = []
        for brck in bricks:
            for i in range(brck.count):
               sack.append(Brick(brck.letter+","+str(brck.count)+","+str(brck.value)+","+brck.type+","+str(brck.rate)))
            if brck.letter != '*':
               notjokerbricks.append(brck)
        sack1 = sack[:]
    for i in range(fieldrc):
        fields.append(["."] * fieldcc)
    for i in range(fieldrc):
        for j in range(fieldcc):
            fields[i][j] = Field(board[i][j], 0, i, j)
    rackfields = [0] * options.racksize
    frackfields = [0] * len(options.fletters)
    rack = [0] * options.racksize
    frack = []
    for i in range(len(options.wordlengthlist[0])):
        if i + 1 <= options.racksize:
            options.wordlengthlist[0][i] = 'True'
        else:
            options.wordlengthlist[0][i] = 'False'


def bind1():
    canvas1.bind("<Button-1>", mouseldown)
    canvas1.bind("<Button1-Motion>", mouselmove)
    canvas1.bind("<ButtonRelease-1>", mouselrelease)
    canvas1.bind("<Button-3>", mouserdown)


def unbind1():
    canvas1.unbind("<Button-1>")
    canvas1.unbind("<Button1-Motion>")
    canvas1.unbind("<ButtonRelease-1>")
    canvas1.unbind("<Button-3>")


def mouse_wheel_canvas(event):
    # Görgő Linux vagy Windows alatt
    direction = None
    if event.num == 5 or event.delta == -120:
        direction = 1
    if event.num == 4 or event.delta == 120:
        direction = -1
    canvas1.yview_scroll(direction, "units")


def mouse_wheelh_canvas(event):
    # Shift+görgő Linux vagy Windows alatt
    direction = None
    if event.num == 5 or event.delta == -120:
        direction = 1
    if event.num == 4 or event.delta == 120:
        direction = -1
    canvas1.xview_scroll(direction, "units")


def bind2():
    # Windows
    canvas1.bind("<MouseWheel>", mouse_wheel_canvas)
    canvas1.bind("<Shift-MouseWheel>", mouse_wheelh_canvas)
    # Linux
    canvas1.bind("<Button-4>", mouse_wheel_canvas)
    canvas1.bind("<Button-5>", mouse_wheel_canvas)
    canvas1.bind("<Shift-Button-4>", mouse_wheelh_canvas)
    canvas1.bind("<Shift-Button-5>", mouse_wheelh_canvas)


def about1():
    aboutpopup = Toplevel(appwin)
    sct = tkinter.scrolledtext.ScrolledText(master=aboutpopup, font=(options.letterfont, 19), background="white")
    sct.pack()
    sct.insert("1.0", "\n                                              CsiSza v0.3\n\n\n"
                      
                      "   Saját szórakoztatásomra készítettem ezt a programot, de úgy\n"
                      "   gondolom, hogy mások számára is hasznos lehet. A GPLv3 licensz\n"
                      "   alapján használható, semmiféle garancia nincs a rendeltetésszerű\n"
                      "   működésére, és a készítője semmilyen felelősséget nem vállal\n"
                      "   a program használatából eredő esetleges károkért.\n\n"
                      "   This program is free software: you can redistribute it and/or modify\n"
                      "   it under the terms of the GNU General Public License as published by\n"
                      "   the Free Software Foundation, either version 3 of the License, or\n"
                      "   (at your option) any later version.\n\n"
                      "   This program is distributed in the hope that it will be useful,\n"
                      "   but WITHOUT ANY WARRANTY; without even the implied warranty of\n"
                      "   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the\n"
                      "   GNU General Public License for more details.\n\n"
                      "   You should have received a copy of the GNU General Public License\n"
                      "   along with this program.  If not, see <http://www.gnu.org/licenses/>.")
    sct.configure(state=DISABLED)


options = csiszaoptions.Options()
queue1 = queue.Queue()
ld = threading.Thread(target=loaddictionary)
ld.start()
appwin = Tk()
appwin.title("Csináld szavad")
options.letterfont = tkinter.font.nametofont("TkDefaultFont").actual()
options.valuefont = tkinter.font.nametofont("TkDefaultFont").actual()
options.fixletterfont = tkinter.font.nametofont("TkDefaultFont").actual()
# print(platform.platform())
defaultfont = tkinter.font.nametofont("TkDefaultFont")
textfont = tkinter.font.nametofont("TkTextFont")
fixedfont = tkinter.font.nametofont("TkFixedFont")
platform1 = platform.system()
if platform1 == "Windows":
    buttonwidth = 1
    defaultfont.configure(size=10)
    pad1 = 1
    interpreter = "python"
else:
    buttonwidth = 0
    pad1 = 0
    interpreter = "python3"

frame1 = Frame(appwin, bg='#d6d6d6')
frame1.pack(side=RIGHT, fill=BOTH,)

frame0 = Frame(appwin, bg='#d6d6d6')
frame0.pack(side=LEFT, anchor=W, fill=BOTH, expand=1)

menubar = Menu(appwin, activebackground="#9acd32")
filem = Menu(menubar, tearoff=0)
filem.add_command(label="Új játék", activebackground="#9acd32", command=new1)
filem.add_command(label="Játék mentése", activebackground="#9acd32", command=save1)
filem.add_command(label="Játék betöltése", activebackground="#9acd32", command=load1)
filem.add_separator()
filem.add_command(label="Kilépés", activebackground="#9acd32", command=quit1)
menubar.add_cascade(label="Fájl", menu=filem)
configm = Menu(menubar, tearoff=0)
configm.add_command(label="Beállítások", activebackground="#9acd32", command=lambda sow=1: setup1(sow))
menubar.add_cascade(label="Beállítások", menu=configm)

helpm = Menu(menubar, tearoff=0)
helpm.add_command(label="Kezelés", activebackground="#9acd32", command=lambda : manual.help1(appwin, options))
helpm.add_command(label="Program", activebackground="#9acd32", command=about1)
menubar.add_cascade(label="Segítség", menu=helpm)

appwin.config(menu=menubar)


def conf0(event):
    canvas1.configure(scrollregion=canvas1.bbox("all"))


frame0.grid_rowconfigure(1, weight=1)
frame0.grid_columnconfigure(0, weight=1)
canvas1 = Canvas(frame0, width=700, height=640, bg="#bebebe")
scrollbarh1 = Scrollbar(frame0, bg='#d6d6d6', orient="horizontal", command=canvas1.xview)
scrollbarv1 = Scrollbar(frame0, bg='#d6d6d6', orient="vertical", command=canvas1.yview)
canvas1.configure(yscrollcommand=scrollbarv1.set, xscrollcommand=scrollbarh1.set)
scrollbarh1.grid(row=0, column=0, sticky='ew')
scrollbarv1.grid(row=1, column=1, sticky='ns')
canvas1.grid(row=1, column=0)
frame0.bind("<Configure>", conf0)

bind2()

def conf10a(event):
    canvas10b.configure(height=frame0.winfo_height())  #frame0
    pb1.configure(length=frame0.winfo_height())        #frame0


frame10b = Frame(frame1, borderwidth=1, bg='#d6d6d6')
frame10b.grid(row=2, column=0, sticky=N + S)
canvas10b = Canvas(frame10b, width=5, bg='#d6d6d6')
canvas10b.pack(side="left", fill=BOTH, expand=1)
scrollbarv1.bind("<Configure>", conf10a)

frame10c = Frame(frame1, borderwidth=1, bg='#d6d6d6')
frame10c.grid(row=2, column=1, sticky=N)

frame10 = Frame(frame10c, bg='#d6d6d6')
frame10.grid(row=1, column=0, sticky=NS + EW, padx=5, pady=10)
frame99 = Frame(frame10, bg='#d6d6d6')
frame99.pack(side=LEFT)

frame100a = Frame(frame10c, borderwidth=1, relief=RAISED)
frame100a.grid(row=0, column=0, sticky=EW)

button4 = Button(frame99, width=10, bg='#d6d6d6', text='Indítás', command=start)
button4.grid(row=0, column=1, sticky=E + W)
button4.configure(state="disabled")

CreateToolTip(button4,
              "Egyjátékos módban és gépi játékban elindítja\na beállított játékot, többjátékos módban indít egy új\n" +
              "játékot a szerveren, majd vár a többi\njátékosra.")

frame100 = Frame(frame10, bg='#d6d6d6')
frame100.pack(side=RIGHT)

textbox2 = Text(frame100, width=28, height=15, borderwidth=2, relief=SUNKEN)
scrollbar2 = Scrollbar(frame100, bg='#d6d6d6', command=textbox2.yview)
textbox2.configure(yscrollcommand=scrollbar2.set, bg="white")
textbox2.grid(row=0, column=2, pady=0, sticky=E)
textbox2.configure(state=DISABLED)
scrollbar2.grid(row=0, column=3, sticky=N + S, pady=0)

button5 = Button(frame99, width=10, bg='#d6d6d6', text='Kilépés', command=quit1)
button5.grid(row=1, column=1, sticky=E + W)

CreateToolTip(button5, "Program elhagyása")

button6 = Button(frame99, width=10, bg='#d6d6d6', text='Szünet', command=pause)
button6.grid(row=2, column=1, sticky=E + W)
button6.configure(state="disabled")

CreateToolTip(button6, "Szünet/Folytatás")

frame99.grid_columnconfigure(1, pad=pad1)
for rown in range(4):
    frame99.grid_rowconfigure(rown, pad=pad1)

Frame(frame99, width=110, height=30, bg='#d6d6d6').grid(row=8, column=1)

countertext = Label(frame99, anchor=W, bg='#d6d6d6', text="Kör:", font=("Sans", 10))
countertext.grid(row=0, column=0, sticky=W)

CreateToolTip(countertext, "Fordulók száma")

counter = Label(frame99, state="disabled", background="white", width=4, borderwidth=2, pady=1, relief=SUNKEN, anchor=E,
                text="0", font=("Sans", 10))
counter.grid(row=1, column=0, sticky=W)

CreateToolTip(counter, "Fordulók száma")

timertext = Label(frame99, anchor=W, bg='#d6d6d6', text="Idő:", font=("Sans", 10))
timertext.grid(row=2, column=0, sticky=W)

CreateToolTip(timertext, "Hátralevő idő")

timer = Label(frame99, state="disabled", background="white", width=4, borderwidth=2, pady=1, relief=SUNKEN, anchor=E,
              text="0", font=("Sans", 10))
timer.grid(row=3, column=0, sticky=W)

CreateToolTip(timer, "Hátralevő idő")

score1text = Label(frame99, anchor=W, bg='#d6d6d6', text="Utolsó lépés:", font=("Sans", 10))
score1text.grid(row=4, column=0, sticky=W)

CreateToolTip(score1text, "A fordulóban szerzett pontszám.")

score1 = Label(frame99, state="disabled", background="white", width=4, borderwidth=2, pady=1, relief=SUNKEN, anchor=E,
               text=str(totalscore), font=("Sans", 10))
score1.grid(row=5, column=0, sticky=W)

CreateToolTip(score1, "A fordulóban szerzett pontszám.")

score2text = Label(frame99, anchor=W, bg='#d6d6d6', text="Összpontszám:", font=("Sans", 10))
score2text.grid(row=6, column=0, sticky=W)

CreateToolTip(score2text, "A játékban szerzett összes pont.")

score2 = Label(frame99, state="disabled", background="white", width=5, borderwidth=2, pady=1, relief=SUNKEN, anchor=E,
               text=str(turnscore), font=("Sans", 10))
score2.grid(row=7, column=0, sticky=W)

CreateToolTip(score2, "A játékban szerzett összes pont.")

Frame(frame99, width=110, height=10, bg='#d6d6d6').grid(row=8, column=0)

frame11 = Frame(frame10c, bg='#d6d6d6')
frame11.grid(row=2, column=0, sticky=W, padx=5, pady=10)
textbox1 = Text(frame11, height=11, width=60, borderwidth=2, relief=SUNKEN, wrap=WORD)
scrollbar1 = Scrollbar(frame11, bg='#d6d6d6', command=textbox1.yview)
textbox1.configure(yscrollcommand=scrollbar1.set, bg="white")
textbox1.grid(row=0, column=0, pady=0, sticky=E)
textbox1.configure(state=DISABLED)
scrollbar1.grid(row=0, column=1, sticky=N + S, pady=0)
textbox1.tag_config("Blue", foreground="blue")

var700 = StringVar()
var700.set("")
entry700 = Entry(frame11, bg="white", relief=SUNKEN, borderwidth=2, textvariable=var700)
entry700.grid(row=1, column=0, sticky=E + W)
entry700.bind('<Return>', chat1)
entry700.bind('<KP_Enter>', chat1)

frame12 = Frame(frame10c, bg='#d6d6d6')
frame12.grid(row=3, column=0, sticky=NS + EW, padx=5)


def switchsack():
    if var100.get() == 1:
        drawsack()
    else:
        hindsack()


var100 = IntVar()
var100.set(0)
checkb1 = Checkbutton(frame12, state="disabled", bg='#d6d6d6', text="Készlet", variable=var100, command=switchsack)
checkb1.grid(row=1, column=1, sticky=W)

CreateToolTip(checkb1, "A hátralevő betűk\n vagy a teljes betűkészlet.")


def ruleson():
    global tab3
    global notebook
    setup1(0)
    notebook.select(tab_id=tab3)


def switchrules():
    global ruleson1
    ruleson1 = var200.get()
    if var200.get() == 1:
        ruleson()
    else:
        close1()


var200 = IntVar()
var200.set(ruleson1)
checkb2 = Checkbutton(frame12, state="disabled", bg='#d6d6d6', text="Szabályok", variable=var200, command=switchrules)
checkb2.grid(row=2, column=1, sticky=W)

CreateToolTip(checkb2, "A beállított szabályok\nmegtekintése.")


def switchballoon():
    global tooltipson
    if var300.get() == 1:
        tooltipson = 1
    else:
        tooltipson = 0


var300 = IntVar()
var300.set(tooltipson)
checkb3 = Checkbutton(frame12, text="Információ", bg='#d6d6d6', variable=var300, command=switchballoon)
checkb3.grid(row=3, column=1, sticky=W)

CreateToolTip(checkb3, "Rövid információ\naz egyes funkciókhoz.")


def complete():
    global ok1
    global timeractive
    unbind1()
    lockon()
    pb1.configure(style="green.Vertical.TProgressbar", maximum=options.timelimit - 2, length=frame0.winfo_height())
    timeractive = False
    if not ok1:      # Ha nincs még elküldött szó
        next1()
    # print("sent: COMPLETED")
    queue1.put("COMPLETED")


button3a = Button(frame12, state="disabled", width=10, bg='#d6d6d6', text="Végleges", command=complete)
button3a.grid(row=4, column=1, sticky=E + W)

CreateToolTip(button3a, "Szimultán játékban a lépés idő előtti\nvéglegesítésére szolgál.")

button0 = Button(frame12, state="disabled", width=10, bg='#d6d6d6', text="Vissza", command=back)
button0.grid(row=1, column=0, sticky=E + W)

CreateToolTip(button0, "Az összes táblára került, de\nmég nem véglegesített betű visszavétele.")

button1 = Button(frame12, state="disabled", width=10, bg='#d6d6d6', text="Keverés", command=shuffle1)
button1.grid(row=2, column=0, sticky=E + W)

CreateToolTip(button1, "A betűk véletlenszerű átrendezése.")

button2 = Button(frame12, state="disabled", width=10, bg='#d6d6d6', text="Csere", command=swap)
button2.grid(row=3, column=0, sticky=E + W)

CreateToolTip(button2, "Az egér jobb gombjával kijelölt betűk, vagy a teljes tartó cseréje.")

button3 = Button(frame12, state="disabled", width=10, bg='#d6d6d6', text="Rendben", command=next1)
button3.grid(row=4, column=0, sticky=E + W)

CreateToolTip(button3,
              "A fordulóban táblára került betűk véglegesítése. Szimultán játékban\nelküldi a szervernek," +
              " de az idő lejártáig újabbak rakhatók ki.")

frame12.grid_columnconfigure(0, pad=pad1)
for rown in range(4):
    frame12.grid_rowconfigure(rown, pad=pad1)

Frame(frame12, width=30, bg='#d6d6d6').grid(row=1, column=2)


def csiszabutton():
    appwin.clipboard_clear()
    appwin.clipboard_append(lastword)
    chatboxmessage(lastword + " a vágólapra másolva.\n")


image1 = tkinter.PhotoImage(file="csisza.gif")
but1 = Button(frame12, anchor=W, bg='#d6d6d6', activebackground='#d6d6d6', image=image1, relief=FLAT,
              command=csiszabutton)
but1.grid(row=2, column=3, rowspan=4)

Frame(frame12, width=110, height=15, bg='#d6d6d6').grid(row=5, column=0)
Frame(frame12, width=110, height=15, bg='#d6d6d6').grid(row=5, column=1)

varpb1 = IntVar()
varpb1.set(100)
s = Style()
s.theme_use('clam')
s.configure("green.Vertical.TProgressbar", foreground="#00ff00", background="#00ff00")
s.configure("red.Vertical.TProgressbar", foreground="#ff0000", background="#ff0000")
s.configure("blue.Vertical.TProgressbar", foreground="#0000ff", background="#0000ff")
pb1 = Progressbar(canvas10b, style="green.Vertical.TProgressbar", orient="vertical", length=frame0.winfo_height(),
                  maximum=100, mode="determinate", variable=varpb1)
s.configure("sidetab.TNotebook", tabposition="w")

timerupdate()
appwin.protocol("WM_DELETE_WINDOW", quit1)
appwin.mainloop()

