# coding: utf-8
import codecs
import itertools
import os
import queue
import socket
import sys
import threading
import time
from operator import itemgetter
from random import *

import csiszaoptions

board = []
fields = []
fieldrc = 1
fieldcc = 1
options = None
aitimelimit = 30
ailettersonrackl = []
ailettersonfrackl = []
ainotjokerletters = []
ainotjokerlettersl = []
moveofai = ""
ready = False
sack = []
sack1 = []
firstmove = True
wanttochange = []
countofchanges = 0
timeractive = False
starttime = 0
aimove = ""
turns = 0
timesup = False


class Field:
    """A mezők osztálya"""

    def __init__(self, field, value, k, l):
        self.type1 = field
        self.value = value
        self.x = l * (options.size + options.gap) + 2
        self.y = k * (options.size + options.gap) + 2
        self.cx = self.x + options.size / 2 - 1
        self.cy = self.y + options.size / 2 - 1
        self.changedletter = None
        self.multiplier = 1
        self.wordmultiplier = 1


host = 'localhost'
port = 40000


class ThreadReception(threading.Thread):
    """üzenetek fogadását kezelő thread objektum"""

    def __init__(self, conn):
        threading.Thread.__init__(self)
        self.connection = conn
        self.messagebuffer = ''
        self.partsofdictionary = None

    def treatmessage(self, rmessage):
        global board
        global options
        global ailettersonrackl
        global ailettersonfrackl
        global ainotjokerletters
        global firstmove
        global starttime
        global sack
        global th_E, th_R
        global sack1
        global turns
        global numberofplayers
        messagelist = rmessage.split(',')
        if messagelist[0] == "OK":
            pass
        elif messagelist[0] == "NUMOFPLAYERS":
            numberofplayers = int(messagelist[1])
        elif messagelist[0][:7] == "OPTIONS":
            options = csiszaoptions.Options()
            optionslist = rmessage.split(';')
            manageoptions(optionslist[1:])
            if options.usefletters:
                for fl in options.fletters:
                    fl1 = fl.split(',')[:3]
                    ailettersonfrackl.append([fl1[0], fl1[2], '1'])
                # print("frack", ailettersonfrackl)
            else:
                ailettersonfrackl = []
        elif messagelist[0] == "BOARD":
            strtoboard(messagelist)
            self.partsofdictionary = init1()
        elif messagelist[0] == "SACK":
            sack = strtoletterlist(messagelist[1:])
            sack1 = sack[:]
        elif messagelist[0] == "LETTERSONRACK":
            i = 0
            ailettersonrackl = []
            while i < (int(messagelist[1]) // 3):
                ailettersonrackl.append(messagelist[2 + i * 3:5 + i * 3])
                i += 1
            lob = strtoletterlist(messagelist[2:])
            removefromsack(lob)
        elif messagelist[0] == "START":
            for brick in sack:
                if brick[0] != '*' and brick[0] not in ainotjokerletters:
                    ainotjokerletters.append(brick[0])
                    ainotjokerlettersl.append(brick)
        elif messagelist[0] == "TURN":
            turns = int(messagelist[1])
            ailettersonrackls = ""
            for i in reversed(range(len(ailettersonrackl))):
                if ailettersonrackl[i] is None:
                    ailettersonrackl.pop(i)
            for j in ailettersonrackl:
                ailettersonrackls += j[0] + " "
            # print("\n"+ailettersonrackls+"\n")
            self.connection.send("OK|".encode())
            starttime = time.time()
            aimove1(self.partsofdictionary)
        elif messagelist[0] == "MOVE":
            self.connection.send("OK|".encode())
            commandlist = rmessage.split(';')
            messagelist1 = commandlist[1].split(',')
            i = int(messagelist1[1])
            j = int(messagelist1[2])
            messagelist2 = commandlist[2].split(',')
            direction = messagelist2[1]
            messagelist3 = commandlist[4].split(',')
            lob = strtoletterlist(messagelist3[1:])
            messagelist5 = commandlist[5].split(',')
            lobch = messagelist5[1:]
            move = ["", [], i, j, direction, lob, lobch]
            manageboard(move, 1)
        elif messagelist[0] == "NEWLETTERS":
            i = 0
            while i < (int(messagelist[1]) // 3):
                found = False
                for n in range(len(ailettersonrackl)):
                    if ailettersonrackl[n] is None:
                        ailettersonrackl[n] = messagelist[2 + i * 3:5 + i * 3]
                        found = True
                        break
                if not found:
                    pass
                i += 1
            lob = strtoletterlist(messagelist[2:])
            removefromsack(lob)
        elif messagelist[0] == "DUPSWAP":
            ailettersonrackl = []
            i = 0
            while i < (int(messagelist[1]) // 3):
                ailettersonrackl.append(messagelist[2 + i * 3:5 + i * 3])
                i += 1
            lob = strtoletterlist(messagelist[2:])
            removefromsack(lob)
        elif rmessage == "END":
            self.connection.send("END|".encode())
            return "break"

    def run(self):
        returnvalue = None
        while 1:
            receivedmessage = self.connection.recv(3064).decode()
            # print("received:", receivedmessage)
            if receivedmessage == "":
                self.connection.send("END|".encode())
                break
            allmessages = self.managebuffer(receivedmessage)
            for rmessage in allmessages:
                returnvalue = self.treatmessage(rmessage)
            if returnvalue == "break":
                break
        print("Leállt a kliens. Kapcsolat megszakítva.")
        self.connection.close()
        os._exit(1)

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


class ThreadEmission(threading.Thread):
    """üzenetek kibocsátását kezelő thread objektum"""

    def __init__(self, conn, q):
        threading.Thread.__init__(self)
        self.connection = conn
        self.start1 = True
        self.q = q

    def run(self):
        while 1:
            time.sleep(1)
            if self.start1:
                rn = randrange(100000)
                self.connection.send(("NAME,Gép" + str(rn) + "|").encode())
                self.start1 = False
            elif not self.q.empty():
                moveofai1 = self.q.get()
                self.connection.send((moveofai1 + "|").encode())
                time.sleep(0.5)
                if options.duplicate and moveofai1.split(',')[0] == "MOVE":
                    self.connection.send("COMPLETED|".encode())


def strtoboard(messagelist):
    global board
    global fieldrc, fieldcc
    fieldrc = int(messagelist[1])
    fieldcc = int(messagelist[2])
    for i in range(fieldrc):
        board.append(messagelist[3 + i * fieldcc:3 + (i + 1) * fieldcc])


def strtoletterlist(messagelist):
    letterlist = []
    for i in range(len(messagelist) // 3):
        letterlist.append(messagelist[i * 3:(i + 1) * 3])
    return letterlist


def strtobool(strg):
    if strg == "1":
        return True
    else:
        return False


def manageoptions(optionslist):
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
    options.checkdictionary = strtobool(optionslist[11].split(',')[1])
    options.dontchangejoker = strtobool(optionslist[12].split(',')[1])
    options.onedirection = strtobool(optionslist[13].split(',')[1])
    options.usefletters = strtobool(optionslist[14].split(',')[1])
    options.fletters = []
    fl = optionslist[14].split(',')[2:]
    for i in range(len(fl) // 5):
        options.fletters.append(",".join(fl[i * 5:(i + 1) * 5]))
    options.valueofchangedletter = strtobool(optionslist[15].split(',')[1])
    options.duplicate = strtobool(optionslist[16].split(',')[1])
    options.timelimit = int(optionslist[17].split(',')[1])
    options.aitimelimit = int(optionslist[18].split(',')[1])
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


def removefromrack(lob):
    """Felhasznált betűk eltávolítása a tartóról"""
    global ailettersonrackl
    for brick in lob:
        found = False
        for j in range(len(ailettersonrackl)):
            if ailettersonrackl[j] is not None:
                if brick[0] == ailettersonrackl[j][0] and brick[1] == ailettersonrackl[j][1] and brick[2] == \
                        ailettersonrackl[j][2]:
                    ailettersonrackl[j] = None
                    found = True
                    break
        if options.usefletters and not found:
            for j in range(len(ailettersonfrackl)):
                if brick[0] == ailettersonfrackl[j][0] and brick[1] == ailettersonfrackl[j][1] and brick[2] == \
                        ailettersonfrackl[j][2]:
                    ailettersonfrackl.pop(j)
                    break


def removefromsack(lob):
    """A tartóra került, vagy az ellenfél által kirakott betűk kivétele a zsákból"""
    global sack
    for brick in lob:
        for j in range(len(sack)):
            if brick[0] == sack[j][0]:
                sack.pop(j)
                break


def manageboard(move, caller):
    """A gépi játékos vagy az ellenfél által kirakott betűk megjelenítése a táblán"""
    global board
    global fields
    global ailettersonrackl
    global firstmove
    direction = move[4]
    lob = move[5]
    if len(lob) > 0:
        firstmove = False
    if options.duplicate:            # közös betűk, legjobb lépés
        if options.resetsack:
            if options.resetall:
                lob1 = ailettersonrackl[:]
            else:
                lob1 = lob[:]
            removefromrack(lob1)
            backtosack(lob1)
        else:
            removefromrack(lob)
    else:
        if caller == 1:              # ellenfél lépése
            if not options.resetsack:
                removefromsack(lob)
        if caller == 0:              # saját lépés
            if options.resetsack:
                if options.resetall:
                    lob1 = ailettersonrackl[:]
                else:
                    lob1 = lob[:]
                backtosack(lob1)
                removefromrack(lob1)
            else:
                removefromrack(lob)
    i = move[2]
    j = move[3]
    k = 0
    b = 0
    if direction == "across":
        while k < len(lob):
            # print("i,j", i, j)
            if board[i][j] in options.fieldsdict:
                if lob[k][0] == '*' and not options.dontchangejoker:
                    board[i][j] = move[6][b]
                    fields[i][j] = Field(move[6][b], int(lob[k][1]), i, j)
                else:
                    board[i][j] = lob[k][0]
                    fields[i][j] = Field(lob[k][0], int(lob[k][1]), i, j)
                j += 1
                b += 1
                k += 1
            else:
                j += 1
                b += 1
    elif direction == "down":
        while k < len(lob):
            if board[i][j] in options.fieldsdict:
                if lob[k][0] == '*' and not options.dontchangejoker:
                    # print("move[6][b]", move[6][b])
                    board[i][j] = move[6][b]
                    fields[i][j] = Field(move[6][b], int(lob[k][1]), i, j)
                else:
                    board[i][j] = lob[k][0]
                    fields[i][j] = Field(lob[k][0], int(lob[k][1]), i, j)
                i += 1
                b += 1
                k += 1
            else:
                i += 1
                b += 1
    sor = ""
    for i in range(fieldrc):
        for j in range(fieldcc):
            if len(fields[i][j].type1) == 1:
                sor += fields[i][j].type1 + " "
            else:
                sor += fields[i][j].type1
        # print(sor)
        sor = ""


def init1():
    """Kezdeti beállítások"""
    global fields
    global aitimelimit
    global ailettersonfrackl
    global firstmove
    global numberofplayers
    if len(sys.argv) > 1:
        options.aitimelimit = int(sys.argv[1])
    fields = []
    for i in range(fieldrc):
        fields.append(["0"] * fieldcc)
    for i in range(fieldrc):
        for j in range(fieldcc):
            fields[i][j] = Field(board[i][j], 0, i, j)
    partsofdictionary = loaddictionary("szotar20c_.dic")
    found = False
    for i in range(fieldrc):          # Ha az első lépés előtt már vannak betűk a táblán, és kötelező a kapcsolódás
        for j in range(fieldcc):
            if fields[i][j].type1 not in options.fieldsdict:
                firstmove = False
                found = True
                break
        if found:
            break
    return partsofdictionary


def loaddictionary(file):
    """Szótár betöltése"""
    dictionary = list()
    partsofdictionary = dict()
    abc = ('A', 'Á', 'B', 'C', 'CS', 'D', 'E', 'É', 'F', 'G', 'GY', 'H', 'I', 'Í', 'J', 'K', 'L', 'LY', 'M', 'N', 'NY',
           'O', 'Ó', 'Ö', 'Ő', 'P', 'Q', 'R', 'S', 'SZ', 'T', 'TY', 'U', 'Ú', 'Ü', 'Ű', 'V', 'W', 'X', 'Y', 'Z', 'ZS')
    for letter1 in abc:
        for length1 in range(2, 35):
            partsofdictionary[letter1+str(length1)] = set()
    f = codecs.open(file, 'r', encoding='utf-8')
    while 1:
        line = f.readline()
        if line == '':
            break
        dictionary.append(line.strip())
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
            except Exception:
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
            if wordl[i] == '0':
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


def aimove1(partsofdictionary):
    """A gép lépésének számítása itt indul. Az aifindplace() függvény által visszaadott
    érvényes szavak pontozásához az aiscore() függvényt hívja
    """
    global board
    global fields
    global timesup
    timesup = False
    ailettersonbothrackl = []
    ailettersonbothrackl.extend(ailettersonrackl)
    if options.usefletters:
        found = False
        fromfrack = 0
        for brick in ailettersonfrackl:
            if brick[0] != '*' or not found:            # Egy fordulóban csak egy dzsókert használhat a gép
                ailettersonbothrackl.append(brick)
                fromfrack += 1
                if brick[0] == '*':
                    found = True
            if fromfrack == 3:                          # Egy fordulóban csak legfeljebb 3 fix betűt használhat fel
                break
    ailettersonbothrack = []
    for l in ailettersonbothrackl:
        ailettersonbothrack.append(l[0])
    allvalidword = []
    aifields = [*board]
    for i in range(fieldrc):
        for j in range(fieldcc):
            if fields[i][j].type1 != '*':
                aifields[i][j] = fields[i][j].type1
            else:
                if options.dontchangejoker:
                    aifields[i][j] = fields[i][j].type1
                else:
                    aifields[i][j] = fields[i][j].changedletter
    usedletters = []
    if len(sys.argv) == 12:
        for wl in range(2, 12):
            if sys.argv[wl] == 'True':
                if options.onedirection and wl == 2:  # Legalább két új betűt fel kell használni
                    continue
                if wl - 1 <= len(ailettersonbothrackl):
                    usedletters.append(wl - 1)
    else:
        for wl in range(len(options.wordlengthlist)):
            if options.wordlengthlist[wl] == 'True':
                if options.onedirection and wl == 0:  # Legalább két új betűt fel kell használni
                    continue
                if wl + 1 <= len(ailettersonbothrackl):
                    usedletters.append(wl + 1)
    # Milyen sorrendben menjen végig a usedletters[] listán (ha esetleg nem jut idő az összesre)
    # ha lengthbonus=True, akkor 1, 2, 3, 4, a legkisebb ezektől különböző jutalmazott, majd max.-tól visszafelé a többi
    # ha lengthbonus=False, akkor 1, 2, 3, 4, majd max.-tól visszafelé a többi
    usedletters1=[]
    usedletters2=[]
    found = False
    for i in usedletters:
        if i < 5:
            usedletters1.append(i)
        else:
            if options.lengthbonus and not found:
                if i == 5 and options.fiveletterbonus > 0:
                    found = True
                    usedletters1.append(i)
                elif i == 6 and options.sixletterbonus > 0:
                    found = True
                    usedletters1.append(i)
                elif i == 7 and options.sevenletterbonus > 0:
                    found = True
                    usedletters1.append(i)
                elif i == 8 and options.eightletterbonus > 0:
                    found = True
                    usedletters1.append(i)
                elif i == 9 and  options.nineletterbonus > 0:
                    found = True
                    usedletters1.append(i)
                elif i == 10 and options.tenletterbonus > 0:
                    found = True
                    usedletters1.append(i)
                if not found:
                    usedletters2.append(i)
            else:
                usedletters2.append(i)
    usedletters = usedletters1[:]
    usedletters.extend(sorted(usedletters2, reverse=True))
    for numofletters in usedletters:
        validwords = aifindplace(partsofdictionary, numofletters, aifields, ailettersonbothrackl)
        if len(validwords) > 0:
            allvalidword.extend(validwords)
        if int(time.time() - starttime) > options.aitimelimit - 10:
            # print("Time1", numofletters, "betű")
            break
    if len(allvalidword) > 0:
        allvalidwordscores = aiscore(allvalidword)
        selectbestmove(allvalidwordscores)
    else:
        # print("nincs érvényes szó")
        if int(time.time() - starttime) < 10:
            time.sleep(10 - int(time.time() - starttime))
        novalidword()


def novalidword():
    """Ha nincs érvényes lépés, csere vagy passz a zsákban lévő betűk számától függően"""
    global sack
    global ailettersonrackl
    global wanttochange
    if len(sack) >= numberofplayers * options.racksize:
        wanttochange = ailettersonrackl[:]
        swapwithserver()
        return
    else:
        # print("sent: PASS")
        queue1.put("PASS")


def swapwithserver():
    """A cserére jelölt betűket elküldi a szervernek"""
    global wanttochange
    message1 = "CHANGE," + str(len(wanttochange) * 3)
    for brick in wanttochange:
        message1 += ","
        message1 += str(brick[0])
        message1 += ","
        message1 += str(brick[1])
        message1 += ","
        message1 += str(brick[2])
    queue1.put(message1)
    backtosack(wanttochange)
    removefromrack(wanttochange)
    wanttochange = []


def backtosack(lettersback):
    """Betűket rak vissza a zsákba, ha a beállítások igénylik"""
    global sack1
    lettersback1 = lettersback[:]
    for brick in lettersback1:
        foundonfrack = False
        for f in ailettersonfrackl:
            if f[0] == brick[0] and f[1] == brick[1]:
                foundonfrack = True
        if foundonfrack:
            continue
        for brick1 in sack1:
            if brick[0] == brick1[0]:
                brick[1] = brick1[1]
                break
        sack.append(brick)


def aifindplace(partsofdictionary, numofletters, aifields, ailettersonbothrackl):
    """A betűk kirakására alkalmas helyeket gyűjti össze listába, majd a checkwords() függvénnyel az egyes mintákra
    illeszkedő összes szót megkeresi, allpossiblescoring() vagy scoring() függvényekkel előállítja az egyes szavakhoz
    tartozó összes lehetséges pontozást, aztán az aivalidmove() függvénnyel érvényesség szempontjából megvizsgáltatja
    az összes kirakott szót.
    """
    validwords = []
    aifieldrc = fieldrc
    aifieldcc = fieldcc
    patterns1 = [[[" "], [" "]]]
    aifieldstransposed = []
    for i in range(aifieldcc):
        newline = []
        for j in range(aifieldrc):
            newline.append(aifields[j][i])
        aifieldstransposed.append(newline)
    jokersonracks = 0
    for le in ailettersonbothrackl:
        if le[0] == '*':
            jokersonracks += 1
    for direction in ["across", "down"]:
        if direction == "down":
            aifields = aifieldstransposed
            aifieldrc, aifieldcc = aifieldcc, aifieldrc
        for i in range(aifieldrc):
            endofline = False
            for j in range(aifieldcc):
                if aifields[i][j] != '!':
                    if j > 0 and (aifields[i][j - 1] not in options.fieldsdict):   # Az előző mezőn még ne legyen betű:
                        continue
                    pattern1 = []
                    conn = False
                    startfield = False
                    listitem = 0
                    newletter = 0
                    wall = False
                    copl = 0
                    while True:
                        if aifields[i][j + listitem] in options.fieldsdict:
                            copl = 0
                            pattern1.append(".")
                            if firstmove:                                          # A kezdő mezőre esik a minta?
                                if i == options.startfieldy and j + listitem == options.startfieldx:
                                    startfield = True
                                    # Ha kötelező a kapcsolódás, akkor ez a minta kapcsolódik-e:
                            if options.connect:
                                if not conn:
                                    if i > 0:
                                        if aifields[i - 1][j + listitem] not in options.fieldsdict:
                                            conn = True
                                    if i < fieldrc - 1:
                                        if aifields[i + 1][j + listitem] not in options.fieldsdict:
                                            conn = True
                            listitem += 1
                            newletter += 1
                        else:
                            copl += 1
                            if options.onedirection and copl > 1:
                                pattern1 = []
                                break
                            pattern1.append(aifields[i][j + listitem])
                            conn = True
                            listitem += 1
                        if j + listitem == aifieldcc:
                            endofline = True
                            break
                        if aifields[i][j + listitem] == "!":
                            wall = True
                            break
                        if newletter == numofletters and aifields[i][j + listitem] in options.fieldsdict:
                            break

                    if newletter < numofletters:
                        # Ha nem használtuk fel az összes betűt, de elértük a sor végét vagy egy határoló mezőt:
                        if endofline or wall:
                            continue
                    if options.connect:
                        # Az első lépés kivételével csak a kapcsolódó mintákat vizsgálja, ha be van állítva a kötelező
                        # kapcsolódás:
                        if not conn and not firstmove:
                            continue
                    if options.startfield:
                        # Az első lépésnél csak a kezdő mezőre eső mintákat vizsgálja, ha van kezdő mező beállítva:
                        if firstmove and not startfield:
                            continue

                    found2 = None
                    for p in range(len(patterns1)):
                        if patterns1[p][0] == pattern1:
                            found2 = p
                            break
                    if found2:
                        words = patterns1[found2][1]
                    else:
                        words = checkwords(partsofdictionary, pattern1, ailettersonbothrackl)
                        rec = list()
                        rec.append(pattern1)
                        rec.append(words)
                        patterns1.append(rec)
                        if int(time.time() - starttime) > options.aitimelimit - 10:
                            # print("Time2")
                            return validwords
                    if len(words) > 0:
                        for pword in words:
                            if not options.randomlettervalue and not options.randommultiplier and not jokersonracks:
                                pword1 = scoring(pword, pattern1, ailettersonbothrackl)
                            else:
                                pword1 = allpossiblescoring(pword, pattern1, ailettersonbothrackl)
                                if timesup:
                                    return validwords
                            for pw in pword1:
                                validword = aivalidmove(partsofdictionary, aifields, pw, i, j, direction, aifieldrc)
                                if len(validword) > 0:
                                    validwords.append(validword)
    return validwords


def scoring(pword, pattern1, ailettersonbothrackl):
    """A szó pontozását adja vissza (ha nincs dzsóker a tartón és nincsenek véletlen pontértékek)"""
    lob1 = []
    pword1 = []
    for i in range(len(pattern1)):
        if pattern1[i] == '.':
            for le in ailettersonbothrackl:
                if pword[i] == le[0]:
                    lob1.append(le)
                    break
        else:
            lob1.append('.')
    rec = list()
    rec.append(pword)
    rec.append(lob1)
    pword1.append(rec)
    return pword1


def allpossiblescoring(pword, pattern1, ailettersonbothrackl):
    """A kirakható szó minden lehetséges pontozását adja vissza (ha van dzsóker a tartón vagy véletlen
     pontértékek vannak)"""
    global timesup
    pword1 = []
    lob = []
    letterdict = dict()
    for i in range(len(pattern1)):
        if pattern1[i] == '.':
            lob.append(pword[i])
        else:
            lob.append('.')
    for i in range(len(lob)):
        if lob[i] != '.':
            try:
                letterdict[pword[i]].append(i)
            except Exception:
                letterdict[pword[i]] = []
                letterdict[pword[i]].append(i)
    jl = []                                                     # tartókon levő dzsókerek listája
    for le in ailettersonbothrackl:
        if le[0] == '*':
            jl.append(le)
    lobl = [lob[:]]
    for key1 in letterdict:
        ll = []
        for le in ailettersonbothrackl:
            if key1 == le[0]:
                ll.append(le)
        if len(ll) < len(letterdict[key1]):
            for n in range(len(letterdict[key1]) - len(ll)):
                ll.append('*')
        lobltemp = []
        for perm in itertools.permutations(ll, len(letterdict[key1])):
            for lob1 in lobl:
                p = 0
                for i in letterdict[key1]:
                    lob1[i] = perm[p]
                    p += 1
            loblcopy = [l1[:] for l1 in lobl]
            lobltemp.extend(loblcopy)
            if not options.randomlettervalue and not options.randommultiplier and not len(jl):
                break
        lobl = lobltemp[:]
    # '*' helyettesítése
    if len(jl):                                                     # ha van dzsóker a tartókon
        loblnew = []
        for lob2 in lobl:
            jokerlist = list()
            njokerlist = list()
            for i in range(len(lob2)):
                if lob2[i] == '*':
                    jokerlist.append(i)
                else:
                    if lob2[i][0] != '.':
                        njokerlist.append(i)
            if len(jokerlist) == 0:                                 # ha nincs szükség dzsókerre
                lob2copy = [l1[:] for l1 in lob2]
                loblnew.append(lob2copy)
            for perm in itertools.permutations(jl, len(jl)):
                for i in jokerlist:
                    p = 0
                    lob2[i] = perm[p]
                    if options.valueofchangedletter:
                        for let1 in ainotjokerlettersl:
                            if pword[i] == let1[0]:
                                lob2[i][1] = let1[2]
                                break
                    p += 1
                if len(jokerlist) > 0:
                    lob2copy = [l1[:] for l1 in lob2]              # ha csak annyi dzsókert használunk amennyi szükséges
                    loblnew.append(lob2copy)
                if not options.valueofchangedletter:
                    for j in range(len(jl)-len(jokerlist)):        # ennyivel több dzsóker van a tartókon a szükségesnél
                        for perm1 in itertools.permutations(njokerlist, j+1):
                            lob2copy = [l1[:] for l1 in lob2]      # ha 1-max. több dzsókert használunk mint szükséges
                            pp = len(jokerlist)
                            for p1 in perm1:
                                lob2copy[p1] = perm[pp]
                                pp += 1
                            loblnew.append(lob2copy)
        lobl = loblnew
        if int(time.time() - starttime) > options.aitimelimit - 10:
            # print("Time4")
            timesup = True
            return []
    for lob1 in lobl:
        rec = list()
        rec.append(pword)
        rec.append(lob1)
        pword1.append(rec)
    pword1temp = []
    for i in range(len(pword1)):
        found = False
        for j in range(i+1, len(pword1)):
            if pword1[i][1]== pword1[j][1]:
                found = True
                break
        if not found:
            pword1temp.append(pword1[i])
    pword1 = pword1temp
    return pword1


def checkwords(partsofdictionary, pattern1, ailettersonbothrackl):
    """Megvizsgálja, hogy a minta első eleme szabad mező, vagy korábban a táblára került betű"""
    words = []
    if pattern1 == ['.'] or pattern1 == []:
        return words
    ailettersonbothrack = []
    for l in ailettersonbothrackl:
        ailettersonbothrack.append(l[0])
    if pattern1[0] != '.':
        firstletter = True
        words = compare1(partsofdictionary, firstletter, pattern1, ailettersonbothrack)
    else:
        firstletter = False
        words = compare1(partsofdictionary, firstletter, pattern1, ailettersonbothrack)
    return words


def compare1(partsofdictionary, firstletter, pattern1, ailettersonbothrack):
    """A pattern1[] hosszának megfelelő szavak kirakhatóságát ellenőrzi, és az illeszkedőket adja vissza"""
    words = []
    if firstletter:
        if pattern1[0] == '*':
            letterstobegin = ainotjokerletters[:]
        else:
            letterstobegin = [pattern1[0]]
    else:
        if '*' in ailettersonbothrack:
            letterstobegin = ainotjokerletters[:]
        else:
            letterstobegin = ailettersonbothrack[:]
    usedbletter = []
    for l in letterstobegin:
        if l not in usedbletter:
            usedbletter.append(l)
            for word1 in partsofdictionary[l+str(len(pattern1))]:
                suit = True
                for k in range(len(pattern1)):
                    if pattern1[k] != word1[k] and pattern1[k] != '.' and pattern1[k] != '*':
                        suit = False
                        break
                if not suit:
                    continue
                ailettersonbothrackcopy = [*ailettersonbothrack]
                if not firstletter:
                    try:
                        ailettersonbothrackcopy.remove(l)
                    except ValueError:
                        ailettersonbothrackcopy.remove('*')
                #suit = True
                for pidx in range(1, len(pattern1)):
                    if pattern1[pidx] != '.':
                        if pattern1[pidx] == '*':
                            continue
                        elif word1[pidx] != pattern1[pidx]:
                            suit = False
                            break
                    else:
                        try:
                            ailettersonbothrackcopy.remove(word1[pidx])
                        except ValueError:
                            try:
                                ailettersonbothrackcopy.remove('*')
                            except ValueError:
                                suit = False
                                break
                if not suit:
                    continue
                words.append(list(word1))
                if int(time.time() - starttime) > options.aitimelimit - 10:
                    # print("Time3")
                    return words
    return words


def aivalidmove(partsofdictionary, aifields, pword, ii, jj, direction, aifieldrc):
    """Az aifillpattern() függvény által megtalált szavak érvényességét vizsgálja tovább úgy,
    hogy a keresztező összes karaktersorozat érvényességét is ellenőrzi a szótár alapján
    """
    validword = []
    swords = []
    lob = pword[1]
    # Az új betűkkel összefüggő összes string ellenőrzése:
    for x in range(len(lob)):
        if lob[x][0] != '.':
            inside = True
            i = ii
            wordl = []
            lobs = []
            while inside:
                if (aifields[i - 1][jj + x] not in options.fieldsdict) and i > 0:
                    i -= 1
                else:
                    inside = False
            si = i
            sj = jj + x
            inside = True
            while inside:
                if i == ii:
                    wordl.append(pword[0][x])
                    lobs.append(lob[x])
                else:
                    wordl.append(aifields[i][jj + x])
                    lobs.append('.')
                if i + 1 < aifieldrc:
                    if (aifields[i + 1][jj + x] not in options.fieldsdict) or i + 1 == ii:
                        i += 1
                    else:
                        inside = False
                else:
                    inside = False
            if len(wordl) > 1:
                if options.onedirection:
                    return validword
                wordl1 = tuple(wordl)
                if '*' not in wordl1:
                    if wordl1 not in partsofdictionary[wordl1[0] + str(len(wordl1))]:
                        return validword
                    else:
                        rec = list()
                        rec.append(wordl)
                        if direction == "across":
                            rec.append(si)
                            rec.append(sj)
                            rec.append("down")
                        else:
                            rec.append(sj)
                            rec.append(si)
                            rec.append("across")
                        rec.append(lobs)
                        swords.append(rec)
                else:
                    patt = []
                    for le in wordl1:
                        if le != '*':
                            patt.append(le)
                        else:
                            patt.append('.')
                    if not checkwords(partsofdictionary, patt, ainotjokerletters):
                        return validword
                    else:
                        rec = list()
                        rec.append(wordl)
                        if direction == "across":
                            rec.append(si)
                            rec.append(sj)
                            rec.append("down")
                        else:
                            rec.append(sj)
                            rec.append(si)
                            rec.append("across")
                        rec.append(lobs)
                        swords.append(rec)
    validword.append(pword[0])
    validword.append(swords)
    if direction == "across":
        validword.append(ii)
        validword.append(jj)
    else:
        validword.append(jj)
        validword.append(ii)
    validword.append(direction)
    validword.append(pword[1])
    return validword


def aiscore(allvalidword):
    """Az érvényes szavak pontozásához a wordscore() függvényt hívja"""
    for validword in allvalidword:
        score1 = wordscore(validword[0], validword[2], validword[3], validword[4], validword[5])
        if len(validword[1]) > 0:
            for vword in validword[1]:
                score2 = wordscore(vword[0], vword[1], vword[2], vword[3], vword[4])
                score1 += score2
        if options.wordperturnbonus:
            score1 += options.wordperturnbonusvalue * (len(validword[1]))
        validword.append(score1)
    return allvalidword


def wordscore(word1, ii, jj, direction, lob1):
    """Az egyes szavak pontértékét számítja"""
    wordvaluemulti = 1
    wordscore1 = 0
    ul = 0
    if direction == "across":
        for x in range(len(word1)):
            if fields[ii][jj + x].type1 not in options.fieldsdict:
                if options.useoldbonus:
                    if options.oldbonusonly:
                        wordscore1 += options.useoldbonusvalue
                    else:
                        wordscore1 += options.useoldbonusvalue
                        wordscore1 += fields[ii][jj + x].value
                else:
                    wordscore1 += fields[ii][jj + x].value
            else:
                sc = int(lob1[x][1])
                wordvaluemulti *= int(lob1[x][2])
                if fields[ii][jj + x].type1 == "2W":
                    wordvaluemulti = 2 * wordvaluemulti
                elif fields[ii][jj + x].type1 == "3W":
                    wordvaluemulti = 3 * wordvaluemulti
                if fields[ii][jj + x].type1 == "2L":
                    wordscore1 += sc * 2
                elif fields[ii][jj + x].type1 == "3L":
                    wordscore1 += sc * 3
                else:
                    wordscore1 += sc
                if fields[ii][jj + x].type1 != "old":
                    ul += 1
    if direction == "down":
        for y in range(len(word1)):
            if fields[ii + y][jj].type1 not in options.fieldsdict:
                if options.useoldbonus:
                    if options.oldbonusonly:
                        wordscore1 += options.useoldbonusvalue
                    else:
                        wordscore1 += options.useoldbonusvalue
                        wordscore1 += fields[ii + y][jj].value
                else:
                    wordscore1 += fields[ii + y][jj].value
            else:
                sc = int(lob1[y][1])
                wordvaluemulti *= int(lob1[y][2])
                if fields[ii + y][jj].type1 == "2W":
                    wordvaluemulti = 2 * wordvaluemulti
                elif fields[ii + y][jj].type1 == "3W":
                    wordvaluemulti = 3 * wordvaluemulti
                if fields[ii + y][jj].type1 == "2L":
                    wordscore1 += sc * 2
                elif fields[ii + y][jj].type1 == "3L":
                    wordscore1 += sc * 3
                else:
                    wordscore1 += sc
                if fields[ii + y][jj].type1 != "old":
                    ul += 1
    wordscore1 = wordscore1 * wordvaluemulti
    if options.lengthbonus:
        if ul == 2:
            wordscore1 += options.twoletterbonus
        elif ul == 3:
            wordscore1 += options.threeletterbonus
        elif ul == 4:
            wordscore1 += options.fourletterbonus
        elif ul == 5:
            wordscore1 += options.fiveletterbonus
        elif ul == 6:
            wordscore1 += options.sixletterbonus
        elif ul == 7:
            wordscore1 += options.sevenletterbonus
        elif ul == 8:
            wordscore1 += options.eightletterbonus
        elif ul == 9:
            wordscore1 += options.nineletterbonus
        elif ul == 10:
            wordscore1 += options.tenletterbonus
    return wordscore1


def selectbestmove(allvalidwordscores):
    """Az érvényes szavak közül kiválasztja a legjobbat, majd normál játékban a finishmove() függvényt hívja"""
    global moveofai
    sortedlist = sorted(allvalidwordscores, key=itemgetter(6), reverse=False)
    choice1 = []
    for validword in reversed(sortedlist):
        if validword[6] == sortedlist[-1][6]:
            choice1.append(validword)
    selectedaimove = choice1[randrange(len(choice1))]
    finishmove(selectedaimove)


def finishmove(selectedaimove):
    """Befejezi a lépést. A kiválasztott szót elküldi a szervernek"""
    global board
    global fields
    global moveofai
    global aimove
    global ailettersonrackl
    global ailettersonfrackl
    lob1 = []
    ailettersonracklcopy = ailettersonrackl[:]
    ailettersonfracklcopy = ailettersonfrackl[:]
    indices = list(range(len(ailettersonrackl)))
    indices1 = list(range(len(ailettersonfrackl)))
    for l in range(len(selectedaimove[5])):
        found = False
        if selectedaimove[5][l] != ".":
            for z in indices:
                if ailettersonrackl[z] == selectedaimove[5][l]:
                    lob1.append(ailettersonracklcopy[z])
                    found = True
                    indices.remove(z)
                    break
            if not found:
                for z in indices1:
                    if ailettersonfrackl[z] == selectedaimove[5][l]:
                        lob1.append(ailettersonfracklcopy[z])
                        indices1.remove(z)
                        break
    ii = selectedaimove[2]
    jj = selectedaimove[3]
    lobch = ",".join(selectedaimove[0])
    wordsfieldss = list()
    wordsfieldss.append("".join(selectedaimove[0]))
    for n in range(len(selectedaimove[1])):
        wordsfieldss.append("".join(selectedaimove[1][n][0]))
    wordsinmove = "+".join(wordsfieldss)
    moveofai = "MOVE" + "," + wordsinmove + ";POS," + str(ii) + "," + str(jj) + ";DIR," + selectedaimove[4] \
               + ";SCORE," + str(selectedaimove[6]) + ";LOB" + letterlisttostr(lob1) + ";LOBCH," + lobch
    if int(time.time() - starttime) > options.aitimelimit - 2:
        # print("Time5")
        return
    # print("sent:", moveofai)
    if int(time.time() - starttime) < 10:
        time.sleep(10 - int(time.time() - starttime))
    queue1.put(moveofai)
    aimove = ["", [], ii, jj, selectedaimove[4], lob1, selectedaimove[0]]
    if not options.duplicate:
        manageboard(aimove, 0)


def letterlisttostr(letters):
    message1 = ""
    for brick in letters:
        message1 += ","
        message1 += str(brick[0])
        message1 += ","
        message1 += str(brick[1])
        message1 += ","
        message1 += str(brick[2])
    return message1


connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    connection.connect((host, port))
except socket.error:
    print("A kapcsolat meghiúsult.")
    sys.exit()
print("A kapcsolat létrejött a szerverrel.")
queue1 = queue.Queue()
th_E = ThreadEmission(connection, queue1)
th_R = ThreadReception(connection)
th_E.start()
th_R.start()
