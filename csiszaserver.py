# coding: utf-8
import copy
import os
import queue
import socket
import threading
import time
from random import *

import csiszaoptions

games = []


class Game:
    """A játékok osztálya"""

    def __init__(self, board, numberofplayers, sack, q):
        self.state = 0  # 0=nyitott; 1=megtelt,fut; 2=megszakadt; 3=felfüggesztett; 4=befejeződött
        self.board = board
        self.fieldrc = 1
        self.fieldcc = 1
        self.players = []
        self.options = csiszaoptions.Options()
        self.numberofplayers = numberofplayers
        self.currentplayer = 0
        self.firstplayer = 0
        self.sack = sack
        self.sack1 = copy.deepcopy(self.sack)
        self.optionsstr = ""
        self.turns = 0
        self.countofpasses = 0
        self.countofidleturns = 0
        self.starttime = None
        self.plwanttochange = 0
        self.novalidword = False
        self.q = q

    @staticmethod
    def strtobool(strg):
        if strg == "1":
            return True
        else:
            return False

    def manageoptions(self, optionslist):
        self.options.racksize = int(optionslist[0].split(',')[1])
        self.options.randommultiplier = self.strtobool(optionslist[1].split(',')[1])
        self.options.connect = self.strtobool(optionslist[2].split(',')[1])
        self.options.startfield = self.strtobool(optionslist[3].split(',')[1])
        self.options.startfieldx = int(optionslist[3].split(',')[2])
        self.options.startfieldy = int(optionslist[3].split(',')[3])
        self.options.lengthbonus = self.strtobool(optionslist[4].split(',')[1])
        self.options.twoletterbonus = int(optionslist[4].split(',')[2])
        self.options.threeletterbonus = int(optionslist[4].split(',')[3])
        self.options.fourletterbonus = int(optionslist[4].split(',')[4])
        self.options.fiveletterbonus = int(optionslist[4].split(',')[5])
        self.options.sixletterbonus = int(optionslist[4].split(',')[6])
        self.options.sevenletterbonus = int(optionslist[4].split(',')[7])
        self.options.eightletterbonus = int(optionslist[4].split(',')[8])
        self.options.nineletterbonus = int(optionslist[4].split(',')[9])
        self.options.tenletterbonus = int(optionslist[4].split(',')[10])
        self.options.oldbonusonly = self.strtobool(optionslist[5].split(',')[1])
        self.options.useoldbonus = self.strtobool(optionslist[5].split(',')[2])
        self.options.useoldbonusvalue = int(optionslist[5].split(',')[3])
        self.options.wordperturnbonus = self.strtobool(optionslist[6].split(',')[1])
        self.options.wordperturnbonusvalue = int(optionslist[6].split(',')[2])
        self.options.turnlimit = self.strtobool(optionslist[7].split(',')[1])
        self.options.turnlimitcount = int(optionslist[7].split(',')[2])
        self.options.resetsack = self.strtobool(optionslist[8].split(',')[1])
        self.options.resetall = self.strtobool(optionslist[9].split(',')[1])
        self.options.randomlettervalue = self.strtobool(optionslist[10].split(',')[1])
        self.options.checkdictionary = self.strtobool(optionslist[11].split(',')[1])
        self.options.dontchangejoker = self.strtobool(optionslist[12].split(',')[1])
        self.options.onedirection = self.strtobool(optionslist[13].split(',')[1])
        self.options.usefletters = self.strtobool(optionslist[14].split(',')[1])
        self.options.fletters = []
        fl = optionslist[14].split(',')[2:]
        for i in range(len(fl) // 5):
            self.options.fletters.append(",".join(fl[i * 5:(i + 1) * 5]))
        self.options.valueofchangedletter = self.strtobool(optionslist[15].split(',')[1])
        self.options.duplicate = self.strtobool(optionslist[16].split(',')[1])
        self.options.timelimit = int(optionslist[17].split(',')[1])
        self.options.aitimelimit = int(optionslist[18].split(',')[1])
        self.options.bonusforusingall = self.strtobool(optionslist[19].split(',')[1])
        self.options.fixpoint = self.strtobool(optionslist[20].split(',')[1])
        self.options.pointforfinish = int(optionslist[21].split(',')[1])
        self.options.valueforeachletter = self.strtobool(optionslist[22].split(',')[1])
        self.options.pointforeachletter = int(optionslist[23].split(',')[1])
        self.options.penaltyforleft = self.strtobool(optionslist[24].split(',')[1])
        self.options.pvalueforeachletter = self.strtobool(optionslist[25].split(',')[1])
        self.options.ppointforeachletter = int(optionslist[26].split(',')[1])
        self.options.independentboards = self.strtobool(optionslist[27].split(',')[1])
        self.options.changeincreasepasses = self.strtobool(optionslist[28].split(',')[1])
        self.optionsstr = ";".join(optionslist)
        if self.options.resetsack and not self.options.resetall:
            self.options.lettersetmode = 2
        elif self.options.resetsack and self.options.resetall:
            self.options.lettersetmode = 3
        else:
            self.options.lettersetmode = 1

    def giveletters(self, pla, letter):
        """Letter számú új betűt ad az adott játékosnak (duplicate módban az elsőnek, de mindegyik  játékos ezt
        használja)"""
        newletters = []
        if letter > len(self.sack):
            letter = len(self.sack)
        self.players[pla].lettersonracksave = []
        jokeronrack = False
        for i in range(len(self.players[pla].lettersonrack)):
            for j in range(len(self.sack1)):
                if self.players[pla].lettersonrack[i][0] == '*':
                    jokeronrack = True
                if self.players[pla].lettersonrack[i][0] == self.sack1[j][0]:
                    self.players[pla].lettersonracksave.append(copy.deepcopy(self.sack1[j]))
                    break
        # print("sack:", len(self.sack))
        for i in range(letter):
            while 1:  # Ha a zsákból nem fogy a betű (lettersetmode 2 vagy 3), akkor nem lehet senkinek egynél több
                # dzsóker a tartóján
                randomnumber = randrange(len(self.sack))
                if self.options.lettersetmode != 1 and self.sack[randomnumber][0] == '*' and jokeronrack:
                    continue
                break
            if self.sack[randomnumber][0] == '*':
                jokeronrack = True
            self.players[pla].lettersonrack.append(self.sack[randomnumber])
            self.players[pla].lettersonracksave.append(copy.deepcopy(self.sack[randomnumber]))
            newletters.append(self.sack[randomnumber])
            if self.options.randomlettervalue:
                if self.players[pla].lettersonrack[-1][0] != '*' or self.options.dontchangejoker:
                    values = copy.deepcopy(self.options.values)
                    rn = randrange(len(values))
                    self.players[pla].lettersonrack[-1][1] = str(values[rn])
                    values.pop(rn)
            if self.options.randommultiplier:
                if self.players[pla].lettersonrack[-1][0] != '*' or self.options.dontchangejoker:
                    mvalues = copy.deepcopy(self.options.mvalues)
                    rn = randrange(len(mvalues))
                    if mvalues[rn] > 1:
                        typestrs = ["letter", "word", "letter", "letter", "letter", "letter", "letter", "word",
                                    "letter", "letter", "letter"]
                        rntype = randrange(len(typestrs))
                        if typestrs[rntype] == "letter":
                            self.players[pla].lettersonrack[-1][1] = str(
                                int(self.players[pla].lettersonrack[-1][1]) * mvalues[rn])
                        if typestrs[rntype] == "word":
                            self.players[pla].lettersonrack[-1][2] = str(mvalues[rn])
            del self.sack[randomnumber]
        if self.options.duplicate and (self.plwanttochange == len(self.players) or self.novalidword):
            newlettersstr = "DUPSWAP" + "," + str(len(newletters) * 3) + self.letterlisttostr(newletters)
        else:
            newlettersstr = "NEWLETTERS" + "," + str(len(newletters) * 3) + self.letterlisttostr(newletters)
        return newlettersstr

    def gamestart(self):
        """Normál módban itt indul a játék"""
        boardstr = self.boardtostr()
        sackstr = "SACK" + self.letterlisttostr(self.sack)
        randomnumber = randrange(len(self.players))
        self.currentplayer = randomnumber
        self.firstplayer = self.currentplayer
        sendmessage(self.players, ("NUMOFPLAYERS," + self.numberofplayers + "|").encode())
        time.sleep(.5)
        sendmessage(self.players, ("OPTIONS;" + self.optionsstr + "|").encode())
        time.sleep(.5)
        sendmessage(self.players, (boardstr + "|").encode())
        time.sleep(.5)
        sendmessage(self.players, (sackstr + "|").encode())
        if self.options.usefletters:
            for player in self.players:
                for l in self.options.fletters:
                    letterlist = l.split(',')
                    letter1 = [letterlist[0], int(letterlist[2]), 1]
                    player.frack.append(letter1)
        time.sleep(.5)
        for player in self.players:
            self.giveletters(self.players.index(player), self.options.racksize)
            leonrastr = ""
            for le in range(len(player.lettersonrack)):
                z1 = "," + player.lettersonrack[le][0] + "," + player.lettersonrack[le][1] + "," + str(
                    player.lettersonrack[le][2])
                leonrastr += z1
            lettersonrackstr = "LETTERSONRACK" + "," + str(3 * len(player.lettersonrack)) + leonrastr
            sendmessage([player], (lettersonrackstr + "|").encode())
        time.sleep(.5)
        sendmessage(self.players, "START|".encode())
        time.sleep(.5)
        for player in self.players:
            sendmessage([player], ("NEXT," + self.players[self.currentplayer].name + "|").encode())
            if self.players.index(player) == self.currentplayer:
                time.sleep(.2)
                sendmessage([player], ("TURN," + str(self.turns) + "|").encode())
                self.starttime = time.time()

    def gamestartdup(self):
        """Duplicate módban itt indul a játék"""
        boardstr = self.boardtostr()
        sackstr = "SACK" + self.letterlisttostr(self.sack)
        sendmessage(self.players, ("NUMOFPLAYERS," + str(self.numberofplayers + "|")).encode())
        time.sleep(.5)
        self.giveletters(0, self.options.racksize)
        sendmessage(self.players, ("OPTIONS;" + self.optionsstr + "|").encode())
        time.sleep(.5)
        sendmessage(self.players, (boardstr + "|").encode())
        time.sleep(.5)
        sendmessage(self.players, (sackstr + "|").encode())
        time.sleep(.5)
        leonrastr = ""
        for le in range(len(self.players[0].lettersonrack)):
            z1 = "," + self.players[0].lettersonrack[le][0] + "," + self.players[0].lettersonrack[le][1] + "," + str(
                self.players[0].lettersonrack[le][2])
            leonrastr += z1
        lettersonrackstr = "LETTERSONRACK," + str(3 * len(self.players[0].lettersonrack)) + leonrastr
        sendmessage(self.players, (lettersonrackstr + "|").encode())
        time.sleep(.5)
        sendmessage(self.players, "START|".encode())
        time.sleep(.5)
        sendmessage(self.players, "Helyezd el a szót a táblán\n|".encode())
        time.sleep(.2)
        for player in self.players:
            sendmessage([player], ("TURN," + str(self.turns) + "|").encode())
        self.starttime = time.time()

    def selectbestmove(self):
        """Duplicate módban a legjobb lépést választja ki stb"""
        # for player in self.players:
        #    print(player.dupmove)
        bestmove = [0, "", "", ""]
        plnotvalidword = 0
        for player in self.players:
            if player.dupmove != "":
                commandlist = player.dupmove.split(';')
                messagelist1 = commandlist[3].split(',')
                player.turnscore = int(messagelist1[1])
                player.totalscore += player.turnscore
                self.countofidleturns = 0
                if player.turnscore > bestmove[0]:
                    bestmove = [player.turnscore, player.dupmove, player.name, player.thread]
            if player.dupmove == "":
                plnotvalidword += 1
        if plnotvalidword == len(self.players):
            if len(self.sack) >= self.options.racksize:
                # print("Nincs érvényes szó, az összes betű cserélődik")
                sendmessage(self.players, "Nincs érvényes szó, az összes betű cserélődik\n|".encode())
                self.novalidword = True
                messagelistx = []
                for le in self.players[0].lettersonrack:
                    messagelistx.append(le[0])
                    messagelistx.append(le[1])
                    messagelistx.append(le[2])
                self.changeletters(messagelistx, self.players[0].thread)
                self.nextturndup()
                time.sleep(.5)
                self.countofidleturns += 1
                if self.countofidleturns == 2:
                    # print("Két fordulóban nem volt érvényes szó, vége a játéknak".encode())
                    time.sleep(3)
                    sendmessage(self.players, "Két fordulóban nem volt érvényes szó, vége a játéknak.\n\n|".encode())
                    time.sleep(.5)
                    sendmessage(self.players, "END|".encode())
                    self.state = 4
                return
            else:
                # print("Nincs érvényes szó")
                self.novalidword = True
                self.nextturndup()
                sendmessage(self.players, "Nincs érvényes szó\n|".encode())
                time.sleep(.5)
                self.countofidleturns += 1
                if self.countofidleturns == 2:
                    # print("Két fordulóban nem volt érvényes szó, vége a játéknak")
                    time.sleep(3)
                    sendmessage(self.players, "Két fordulóban nem volt érvényes szó, vége a játéknak.\n\n|".encode())
                    time.sleep(.5)
                    sendmessage(self.players, "END|".encode())
                    self.state = 4
                return
        if self.options.independentboards:
            for player in self.players:
                if player.dupmove != "":
                    sendmessage([player], (player.dupmove + "|").encode())
                else:
                    sendmessage([player], "Nincs érvényes szavad ebben a fordulóban\n|".encode())
        else:
            for player in self.players:
                sendmessage([player], (bestmove[1] + ";" + bestmove[2] + "|").encode())
        self.sendscore()
        self.writeboard(bestmove[1], bestmove[3])
        self.plwanttochange = 0
        self.nextturndup()

    def nextturndup(self):
        """Duplicate módban a következő fordulóra vált"""
        self.turns += 1
        if self.options.turnlimit and self.turns == self.options.turnlimitcount:
            sendmessage(self.players, "A körök száma elérte a beállított értéket, vége a játéknak.\n\n|".encode())
            time.sleep(.5)
            sendmessage(self.players, "END|".encode())
            self.state = 4
            return
        sendmessage(self.players, ("TURN," + str(self.turns) + "|").encode())
        self.starttime = time.time()
        for player in self.players:
            player.turnscore = 0
            player.dupmove = ""

    def boardtostr(self):
        message1 = "BOARD" + "," + str(len(self.board)) + "," + str(len(self.board[0]))
        for i in range(len(self.board)):
            for j in range(len(self.board[0])):
                message1 += ","
                message1 += str(self.board[i][j])
        return message1

    @staticmethod
    def letterlisttostr(letters):
        message1 = ""
        for i in range(len(letters)):
            message1 += ","
            message1 += str(letters[i][0])
            message1 += ","
            message1 += str(letters[i][1])
            message1 += ","
            message1 += str(letters[i][2])
        return message1

    def writeboard(self, receivedmessage, name):
        """Az új lépést a táblára rakja (független táblánál nem!)"""
        commandlist = receivedmessage.split(';')
        messagelist1 = commandlist[1].split(',')
        i = int(messagelist1[1])
        j = int(messagelist1[2])
        b = 1
        messagelist2 = commandlist[2].split(',')
        direction = messagelist2[1]
        messagelist3 = commandlist[4].split(',')
        messagelist5 = commandlist[5].split(',')
        z = 1
        lob = []
        while z < len(messagelist3[1:]):
            lob.append(messagelist3[z:z + 3])
            z += 3
        if not self.options.duplicate:
            messagelist4 = commandlist[3].split(',')
            for player in self.players:
                if player.thread == name:
                    player.turnscore = int(messagelist4[1])
                    player.totalscore += player.turnscore
                    # player.turnscore = 0
                    break
        if not self.options.independentboards:
            k = 0
            if direction == "across":
                while k < len(lob):
                    if self.board[i][j] in self.options.fieldsdict:
                        if lob[k][0] == '*' and self.options.dontchangejoker:
                            self.board[i][j] = lob[k][0]
                        else:
                            self.board[i][j] = messagelist5[b]
                        j += 1
                        b += 1
                        k += 1
                    else:
                        j += 1
                        b += 1
            elif direction == "down":
                while k < len(lob):
                    if self.board[i][j] in self.options.fieldsdict:
                        if lob[k][0] == '*' and self.options.dontchangejoker:
                            self.board[i][j] = lob[k][0]
                        else:
                            self.board[i][j] = messagelist5[b]
                        i += 1
                        b += 1
                        k += 1
                    else:
                        i += 1
                        b += 1
            sor = ""
            for i in range(self.fieldrc):
                for j in range(self.fieldcc):
                    if len(self.board[i][j]) == 1:
                        sor += self.board[i][j] + " "
                    else:
                        sor += self.board[i][j]
                # print(sor)
                sor = ""
        if self.options.duplicate:
            self.managerack(lob, self.players[0].thread)
        else:
            self.managerack(lob, name)

    def managerack(self, lob, th):
        """A tartóról törli a felhasznált betűket és feltölti újakkal"""
        for player in self.players:
            lettersfromfrack = 0
            if player.thread == th:
                if self.options.resetsack:
                    if self.options.resetall:
                        lob = player.lettersonrack[:]
                        self.sack.extend(player.lettersonracksave)
                    else:
                        for i in range(len(lob)):
                            for j in range(len(player.lettersonracksave)):
                                if lob[i][0] == player.lettersonracksave[j][0]:
                                    self.sack.append(player.lettersonracksave[j])
                                    player.lettersonracksave.pop(j)
                                    break
                for i in range(len(lob)):
                    foundonrack = False
                    for ltor in player.lettersonrack:                              # Felhasznált betű törlése
                        if ltor[0] == lob[i][0]:
                            player.lettersonrack.remove(ltor)
                            foundonrack = True
                            break
                    if self.options.usefletters and not foundonrack:
                        for ltofr in player.frack:
                            if ltofr[0] == lob[i][0]:
                                player.frack.remove(ltofr)
                                lettersfromfrack += 1
                                break
                if len(self.sack) > 0:
                    if self.options.duplicate:
                        time.sleep(2)
                    newlettersstr = self.giveletters(self.players.index(player), len(lob) - lettersfromfrack)
                    if self.options.duplicate:
                        time.sleep(1)
                        sendmessage(self.players, (newlettersstr + "|").encode())
                        self.novalidword = False
                    else:
                        sendmessage([player], (newlettersstr + "|").encode())
                    time.sleep(2)
                    break
                else:
                    if self.options.duplicate:
                        if len(self.players[0].lettersonrack) == 0:
                            # print("A betűk elfogytak")
                            time.sleep(3)
                            sendmessage(self.players, "A betűk elfogytak, a játéknak vége.\n\n|".encode())
                            time.sleep(.5)
                            sendmessage(self.players, "END|".encode())
                            self.state = 4
                    else:
                        if len(player.lettersonrack) == 0 and len(player.frack) == 0:
                            # print(player.name + " betűi elfogytak  sack:", self.sack)
                            time.sleep(2)
                            sendmessage(self.players,
                                        (player.name + " betűi elfogytak, a játéknak vége.\n\n|").encode())
                            if self.options.bonusforusingall:
                                lettersleft = 0
                                valueleft = 0
                                for player1 in self.players:
                                    lettersleft += len(player1.lettersonrack)
                                    for j in range(len(player1.lettersonrack)):
                                        valueleft += int(player1.lettersonrack[j][1])
                                if self.options.fixpoint:
                                    player.totalscore += self.options.pointforfinish
                                else:
                                    if self.options.valueforeachletter:
                                        player.totalscore += valueleft
                                    else:
                                        player.totalscore += lettersleft * options.pointforeachletter
                            self.endofgame()

    def sendscore(self):
        """Elküldi a pillanatnyi állást a klienseknek"""
        scorestr = "SCORE"
        for player in self.players:
            scorestr = scorestr + ";" + player.name + "," + str(player.turnscore) + "," + str(player.totalscore)
        sendmessage(self.players, (scorestr + "|").encode())
        time.sleep(0.5)

    def endofgame(self):
        """A játék végén az esetleges pontlevonásokat számolja és a végeredményt elküldi a klienseknek"""
        if self.options.penaltyforleft:
            for player in self.players:
                for j in range(len(player.lettersonrack)):
                    if self.options.pvalueforeachletter:
                        player.totalscore -= int(player.lettersonrack[j][1])
                    else:
                        player.totalscore -= int(self.options.ppointforeachletter)
        time.sleep(.5)
        self.sendscore()
        sendmessage(self.players, "END|".encode())
        self.state = 4

    def manageturn(self):
        """Normál módban a következő játékosra vált"""
        time.sleep(.01)
        if self.currentplayer < len(self.players) - 1:
            self.currentplayer += 1
        else:
            self.currentplayer = 0
        if self.currentplayer == self.firstplayer:
            self.turns += 1
            if self.options.turnlimit and self.turns == self.options.turnlimitcount:
                sendmessage(self.players, "A körök száma elérte a beállított értéket, vége a játéknak.\n\n|".encode())
                time.sleep(.5)
                sendmessage(self.players, "END|".encode())
                self.state = 4
                return
        for player in self.players:
            sendmessage([player], ("NEXT," + self.players[self.currentplayer].name + "|").encode())
            if self.players.index(player) == self.currentplayer:
                time.sleep(.2)
                sendmessage([player], ("TURN," + str(self.turns) + "|").encode())
        time.sleep(.5)

    def changeletters(self, messagelist, name):
        """Csere"""
        changedletters = []
        for i in range(len(messagelist) // 3):
            changedletters.append(messagelist[i * 3:(i + 1) * 3])
        self.managerack(changedletters, name)
        for i in range(len(changedletters)):
            for j in range(len(self.sack1)):
                if changedletters[i][0] == self.sack1[j][0]:
                    changedletters[i][1] = self.sack1[j][1]
                    break
        if not self.options.duplicate:
            self.sack.extend(changedletters)

    def checkrack(self, receivedmessage, th):
        """"Ellenőrzi, hogy az üzenetben hivatkozott betűk a játékos tartóján vannak-e (pl: idő lejárta után beérkezett
        üzenet esetén, ha már megváltozott a tartó)"""

        return 1   # Meg kellene oldani, hogy szinkronban maradjon...

        commandlist = receivedmessage.split(';')
        messagelist3 = commandlist[4].split(',')
        z = 1
        lob = []
        while z < len(messagelist3[1:]):
            lob.append(messagelist3[z:z + 3])
            z += 3
        for player in self.players:
            if player.thread == th:
                for i in range(len(player.frack)):
                    player.frack[i][1] = str(player.frack[i][1])
                    player.frack[i][2] = str(player.frack[i][2])
                for i in range(len(lob)):
                    foundonrack = False
                    foundonfrack = False
                    if self.options.duplicate:
                        rack1 = self.players[0].lettersonrack
                    else:
                        rack1 = player.lettersonrack
                    for lr in rack1:
                        if lr == lob[i]:
                            foundonrack = True
                            break
                    if self.options.usefletters and not foundonrack:
                        for lfr in player.frack:
                            if lfr == lob[i]:
                                foundonfrack = True
                                break
                    if not foundonrack and not foundonfrack:
                        return 0
        return 1

    def waitok(self):
        while 1:
            time.sleep(0.1)
            if not self.q.empty():
                qvar = self.q.get()
                if qvar[0] == "OK":
                    return


class Player:
    """A játékosok osztálya"""

    def __init__(self, thread, connection, name):
        self.thread = thread
        self.connection = connection
        self.name = name
        self.totalscore = 0
        self.turnscore = 0
        self.lettersonrack = []
        self.lettersonracksave = []
        self.frack = []
        self.dupmove = ""
        self.completed = False


class ThreadClient(threading.Thread):
    """Az egyes kliensekkel kommunikáló szál osztálya"""

    def __init__(self, conn, q, qf):
        threading.Thread.__init__(self)
        self.connection = conn
        self.q = q
        self.qf = qf
        self.gamenumber = None                      # a játék, amelynek ez a kliens résztvevője
        self.messagereceived = False
        self.playername = None
        self.messagebuffer = ''

    @staticmethod
    def strtoboard(messagelist):
        board = []
        for i in range(int(messagelist[1])):
            board.append(messagelist[3 + i * int(messagelist[2]):3 + (i + 1) * int(messagelist[2])])
        return board

    @staticmethod
    def strtosack(messagelist):
        sack = []
        for i in range(len(messagelist) // 3):
            sack.append(messagelist[i * 3:(i + 1) * 3])
        return sack

    def managebuffer(self, receivedmessage):
        self.messagebuffer += receivedmessage
        allmessages = []
        while 1:
            position = self.messagebuffer.find("|")
            if position == -1:
                break
            if self.messagebuffer[:4] == "CHAT":
                allmessages.append(self.messagebuffer[:position + 1])
            else:
                allmessages.append(self.messagebuffer[:position])
            self.messagebuffer = self.messagebuffer[position + 1:]
        return allmessages

    def treatmessage(self, name, message):
        messagelist = message.split(',')
        if message == "END":
            if games[self.gamenumber].state != 4:
                games[self.gamenumber].state = 3
                sendmessage(games[self.gamenumber].players, (self.playername + " elhagyta a játékot\n" + "|").encode())
                print(self.playername + " elhagyta a játékot\n")
                time.sleep(.5)
            return "break"
        if messagelist[0] == "GAME":
            found = False
            for i in range(len(games)):
                if games[i].state == 0:
                    conn_client[name].send("GAMEEXIST|".encode())
                    found = True
                    break
            if not found:
                conn_client[name].send("NOGAME|".encode())
        elif messagelist[0] == "LAUNCH":
            commandlist = message.split(';')
            messagelist1 = commandlist[1].split(',')
            board = self.strtoboard(messagelist1)
            numberofplayers = commandlist[3]
            messagelist2 = commandlist[2].split(',')
            sack = self.strtosack(messagelist2[1:])
            locking.acquire()
            games.append(Game(board, numberofplayers, sack, queue1))
            self.gamenumber = len(games) - 1
            locking.release()
            games[self.gamenumber].fieldrc = int(messagelist1[1])
            games[self.gamenumber].fieldcc = int(messagelist1[2])
            # print("Gamenumber: " + str(self.gamenumber))
            games[self.gamenumber].manageoptions(commandlist[5:])
            messagelist1 = commandlist[0].split(',')
            self.playername = messagelist[1].split(';')[0]
            games[self.gamenumber].players.append(Player(name, conn_client[name], messagelist1[1]))
            # print("Új játék indul")
            # print(len(games[self.gamenumber].players))
            # print(int(games[self.gamenumber].numberofplayers))
            if len(games[self.gamenumber].players) == int(
                    games[self.gamenumber].numberofplayers):                           # Egyszemélyes hálózati játék
                time.sleep(.5)
                games[self.gamenumber].state = 1
                # print("Indulhat a játék")
                self.qf.put((startgame, self.gamenumber))
        elif messagelist[0] == "NAME":
            for i in range(len(games)):
                if games[i].state == 0:
                    break
            found = False
            for j in range(len(games[i].players)):
                if games[i].players[j].name == messagelist[1]:
                    found = True
                    break
            if found:
                conn_client[name].send("INUSE|".encode())
                return "continue"
            else:
                conn_client[name].send("OK|".encode())
            locking.acquire()
            self.playername = messagelist[1]
            games[i].players.append(Player(name, conn_client[name], messagelist[1]))
            self.gamenumber = i
            locking.release()
            # print(messagelist[1] + " csatlakozott egy játékhoz")
            smessage = ""
            for player in games[self.gamenumber].players:
                smessage = smessage + player.name + "\n"
            if int(games[self.gamenumber].numberofplayers) - len(games[self.gamenumber].players) > 0:
                smessage = "\n" + smessage + "a játékban, még " + str(int(games[self.gamenumber].numberofplayers) - len(
                    games[self.gamenumber].players)) + " játékos szükséges\n\n"
            else:
                smessage = "\n" + smessage + "a játékban. A játék megtelt.\n\n"
            # print(smessage)
            for player in games[self.gamenumber].players:
                player.connection.send((smessage + "|").encode())
            # print(games[self.gamenumber].numberofplayers)
            # print(len(games[self.gamenumber].players))
            if len(games[self.gamenumber].players) == int(games[self.gamenumber].numberofplayers):
                time.sleep(.5)
                games[self.gamenumber].state = 1
                # print("Indulhat a játék")
                smessage = "PLAYERS"
                for player in games[self.gamenumber].players:
                    smessage = smessage + ',' + player.name
                for player in games[self.gamenumber].players:
                    player.connection.send((smessage + "|").encode())
                time.sleep(.5)
                self.qf.put((startgame, self.gamenumber))
        elif messagelist[0] == "MOVE":
            if games[self.gamenumber].checkrack(message, name):
                if games[self.gamenumber].options.duplicate:
                    found = False
                    for player in games[self.gamenumber].players:
                        if player.thread == name:
                            player.dupmove = message
                            found = True
                            break
                    # if found:
                        # print("Játékos: " + player.thread)
                    # for player in games[self.gamenumber].players:
                    #    print(player.dupmove)
                else:
                    games[self.gamenumber].starttime = time.time()
                    games[self.gamenumber].countofpasses = 0
                    # print(name + " lépése: %s" % message)
                    for i in range(len(games[self.gamenumber].players)):
                        if i != games[self.gamenumber].currentplayer:
                            sendmessage([games[self.gamenumber].players[i]], (
                                                             message + ";" + games[self.gamenumber].players[
                                                             games[self.gamenumber].currentplayer].name + "|").encode())
                    time.sleep(.3)
                    games[self.gamenumber].writeboard(message, name)
                    games[self.gamenumber].sendscore()
                    if games[self.gamenumber].state == 1:
                        games[self.gamenumber].manageturn()
        elif messagelist[0] == "COMPLETED":
            if games[self.gamenumber].options.duplicate:
                for player in games[self.gamenumber].players:
                    if player.thread == name:
                        player.completed = True
                        break
                allcompleted = True
                for player in games[self.gamenumber].players:
                    if not player.completed:
                        allcompleted = False
                        break
                if allcompleted:
                    for player in games[self.gamenumber].players:
                        player.completed = False
                    games[self.gamenumber].selectbestmove()
        elif messagelist[0] == "PASS":
            if games[self.gamenumber].options.duplicate:
                games[self.gamenumber].countofpasses += 1
            else:
                games[self.gamenumber].starttime = time.time()
                games[self.gamenumber].countofpasses += 1
                for player in games[self.gamenumber].players:
                    if games[self.gamenumber].countofpasses < len(games[self.gamenumber].players) * 2:
                        sendmessage([player], (games[self.gamenumber].players[
                                                   games[self.gamenumber].currentplayer].name + " passzolt\n" + str(
                            len(games[self.gamenumber].players) * 2 - games[
                                self.gamenumber].countofpasses) + " passz és a játéknak vége\n|").encode())
                    else:
                        sendmessage([player], (games[self.gamenumber].players[games[
                            self.gamenumber].currentplayer].name + " passzolt\nA játéknak vége\n\n|").encode())
                        time.sleep(.5)
                        sendmessage([player], "END|".encode())
                        games[self.gamenumber].state = 4
                # print(name + " passzolt")
                if games[self.gamenumber].state == 1:
                    games[self.gamenumber].manageturn()
        elif messagelist[0] == "CHANGE":
            if games[self.gamenumber].options.duplicate:
                games[self.gamenumber].plwanttochange += 1
                # print(str(games[self.gamenumber].plwanttochange) + " játékos akar cserélni")
                sendmessage(games[self.gamenumber].players, (self.playername + " cserélni szeretne\n|").encode())
                time.sleep(.5)
                if games[self.gamenumber].plwanttochange == len(games[self.gamenumber].players):
                    sendmessage(games[self.gamenumber].players, "Az összes betű cserélődik\n|".encode())
                    time.sleep(.5)
                    # print("Az összes betű cserélődik")
                    # print(games[self.gamenumber].players[0].lettersonrack)
                    messagelistx = []
                    for letter in games[self.gamenumber].players[0].lettersonrack:
                        messagelistx.append(letter[0])
                        messagelistx.append(letter[1])
                        messagelistx.append(letter[2])
                    games[self.gamenumber].changeletters(messagelistx, games[self.gamenumber].players[0].thread)
                    games[self.gamenumber].nextturndup()
                    games[self.gamenumber].plwanttochange = 0
            else:
                games[self.gamenumber].starttime = time.time()
                if not games[self.gamenumber].options.changeincreasepasses:
                    games[self.gamenumber].countofpasses = 0
                    # print(name + " cserélt")
                    # print(messagelist)
                    sendmessage(games[self.gamenumber].players, (games[self.gamenumber].players[games[
                        self.gamenumber].currentplayer].name + " cserélt\n|").encode())
                else:
                    games[self.gamenumber].countofpasses += 1
                    for player in games[self.gamenumber].players:
                        # print("countofpasses", games[self.gamenumber].countofpasses)
                        if games[self.gamenumber].countofpasses < len(games[self.gamenumber].players) * 2:
                            sendmessage([player], (games[self.gamenumber].players[
                                                       games[self.gamenumber].currentplayer].name + " cserélt\n" + str(
                                len(games[self.gamenumber].players) * 2 - games[
                                    self.gamenumber].countofpasses) + " passz és a játéknak vége\n|").encode())
                        else:
                            sendmessage([player], (games[self.gamenumber].players[games[
                                self.gamenumber].currentplayer].name + " cserélt\n" + "A játéknak vége\n\n|").encode())
                            sendmessage([player], "END|".encode())
                            games[self.gamenumber].state = 4
                time.sleep(.5)
                games[self.gamenumber].changeletters(messagelist[2:], name)
                if games[self.gamenumber].state == 1:
                    games[self.gamenumber].manageturn()
        elif messagelist[0] == "OK":
            self.q.put(["OK", name])
        elif messagelist[0] == "CHAT":
            for player in games[self.gamenumber].players:
                try:
                    sendmessage([player], message.encode())
                except Exception:
                    pass
            time.sleep(.01)
        else:
            sendmessage(games[self.gamenumber].players, (message + "|").encode())
            time.sleep(.01)

    def run(self):
        name = self.getName()                                             # thread neve
        while 1:
            receivedmessage = self.connection.recv(3064).decode()
            rmessage = "%s: %s" % (name, receivedmessage)
            # print("received from", rmessage)
            if receivedmessage == "":
                if games[self.gamenumber].state != 4:
                    games[self.gamenumber].state = 2
                    sendmessage(games[self.gamenumber].players,
                                (self.playername + " kapcsolata megszakadt a szerverrel\n|").encode())
                    # print(self.playername + " kapcsolata megszakadt\n")
                    time.sleep(.5)
                break
            allmessages = self.managebuffer(receivedmessage)
            returnvalue = None
            for message in allmessages:
                returnvalue = self.treatmessage(name, message)
            if returnvalue == "break":
                break
            elif returnvalue == "continue":
                continue
        self.connection.close()
        del conn_client[name]
        # print("Kliens %s lekapcsolódott." % name)


conn_client = {}


def server():
    """Létrehozza a socketet, fogadja a kliensek kapcsolódását, minden klienshez külön szálat rendel"""
    host = "localhost"
    port = 40000

    mysocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        mysocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)         # állítólag nem ajánlott Windows-on
        mysocket.bind((host, port))
    except socket.error:
        print("A socket összekapcsolása a választott címmel nem sikerült.")
        os._exit(1)
    print("Várakozás a kliensekre ...")
    mysocket.listen(5)
    while 1:
        connection, addr = mysocket.accept()
        th = ThreadClient(connection, queue1, queue2)
        th.daemon = True
        th.start()
        it = th.getName()
        conn_client[it] = connection
        print("Kliens ", it, " felkapcsolódott, IP cím ", addr[0], " port ", addr[1])
        connection.send("".encode())


def startgame(gamenumber):
    """Elindítja a játékot"""
    if games[gamenumber].options.duplicate:
        games[gamenumber].gamestartdup()
    else:
        games[gamenumber].gamestart()


def sendmessage(players, message):
    """Elküldi az üzenetet a kliensnek"""
    locking.acquire()
    for player in players:
        try:
            # print("sent to "+player.thread+"("+player.name+"):", message.decode())
            player.connection.send(message)
        except Exception:
            print("Nincs kapcsolat?")
    locking.release()


def managetime():
    """Az egyes lépésekre megadott időt figyeli"""
    for u in range(len(games)):
        if games[u].state == 1:
            if games[u].starttime is not None:
                if int(time.time() - games[u].starttime) > games[u].options.timelimit + 2:
                    # print("Letelt az idő")
                    for player in games[u].players:
                        if games[u].options.duplicate:
                            sendmessage([player], "Letelt a gondolkodási idő\n|".encode())
                        else:
                            if games[u].players.index(player) == games[u].currentplayer:
                                sendmessage([player], "TIMEOUT|".encode())
                                time.sleep(.5)
                            if games[u].countofpasses < len(games[u].players) * 2 - 1:
                                sendmessage([player], ("\n" + games[u].players[
                                    games[u].currentplayer].name + " gondolkodási ideje letelt\n" + str(
                                    len(games[u].players) * 2 - games[
                                        u].countofpasses - 1) + " passz és a játéknak vége\n|").encode())
                            else:
                                sendmessage([player], (games[u].players[games[
                                    u].currentplayer].name + " passzolt\nA játéknak vége\n\n|").encode())
                                time.sleep(.5)
                    if games[u].options.duplicate:
                        # for player in games[u].players:
                        #    print(player.dupmove)
                        games[u].selectbestmove()
                    else:
                        if games[u].countofpasses == len(games[u].players) * 2 - 1:
                            games[u].endofgame()
                        else:
                            games[u].countofpasses += 1
                            games[u].manageturn()
                            games[u].starttime = time.time()


queue1 = queue.Queue()
queue2 = queue.Queue()
locking = threading.Lock()
t = threading.Thread(target=server)
t.start()
options = csiszaoptions.Options()
while 1:
    time.sleep(.1)
    if not queue2.empty():
        (f, arg) = queue2.get()
        f(arg)
    managetime()
