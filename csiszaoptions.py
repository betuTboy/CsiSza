# coding: utf-8


class Options:
    """"A beállítások kezelése"""

    def __init__(self):
        self.fieldsdict = {}
        self.gamemode = 1
        self.aiopponent = 1
        self.networkopponent = 1
        self.username = "Jatekos"
        self.host = "localhost"
        self.port = "40000"
        self.duplicate = False
        self.independentboards = False                 # szükséges: duplicate, kizárt: csere

        self.racksize = 10
        self.size = 27
        self.fieldsize = self.size
        self.gap = 2
        self.letterfont = None
        self.letterfontsize = 15
        self.valuefont = None
        self.valuefontsize = 7
        self.fixletterfont = None
        self.fixletterfontsize = 15

        self.colornormal = "#a9a9a9"
        self.colorfix = "#00ff00"
        self.colordoubleL = "#e0a9e6"
        self.colortripleL = "#db00ff"
        self.colordoubleW = "#0edbf0"
        self.colortripleW = "#888ef8"
        self.colorwall = "#bebebe"

        self.numbering = True

        self.colorborder = "#bebebe"
        self.colortext = "#0000e1"
        self.colornormalbrick = "#33c5c5"
        self.colordoublebrick = "#cc956b"
        self.colortriplebrick = "#7368e5"
        self.colordoublewordbrick = "#ffab4b"
        self.colortriplewordbrick = "#7c8900"
        self.colorborderbrick = "#000000"
        self.colortextbrick = "#000000"
        self.colorvaluebrick = "#000000"
        self.colorchangedbrick = "#ffff00"
        self.fborder = "False"
        self.bborder = "True"

        self.bricksize = 33
        self.wx = 6
        self.wy = 6

        # Véletlenszerű szorzó a betűértékekhez:
        self.randommultiplier = True                         # kizárt: randomlettervalue
        self.mvalues = [1, 2, 1, 1, 1, 1, 2, 1, 1, 1, 1, 1, 3, 1, 2, 1, 1, 1, 1, 1, 1, 3, 1, 1, 1, 1, 3, 1, 1, 2, 1, 1,
                        1, 2, 1, 1, 2, 1, 1, 1]
        # Kőtelező-e kapcsolódni az új szónak a már táblán levőkkel:
        self.connect = True
        # Előre beállított helyen kell-e kezdeni a játékot:
        self.startfield = True
        self.startfieldx = 4
        self.startfieldy = 10
        # A lerakott betűk száma után járó jutalom:
        self.lengthbonus = True
        self.twoletterbonus = 0
        self.threeletterbonus = 0
        self.fourletterbonus = 0
        self.fiveletterbonus = 0
        self.sixletterbonus = 40
        self.sevenletterbonus = 60
        self.eightletterbonus = 60
        self.nineletterbonus = 60
        self.tenletterbonus = 60
        # A táblán levő betűk felhasználásáért jár-e jutalom, és csak az jár, vagy a saját értékük is:
        self.oldbonusonly = False
        self.useoldbonus = False
        self.useoldbonusvalue = 5
        # Az egy körön belül létrejövő szavak száma alapján járó jutalom:
        self.wordperturnbonus = False
        self.wordperturnbonusvalue = 5
        # Hány körös a játék, ha van korlát:
        self.turnlimit = False
        self.turnlimitcount = 24
        # A cserék száma beleszámítson-e a passzok számába
        self.changeincreasepasses = False
        # Minden lépés után pótlódnak a zsákban a táblára került betűk:
        self.resetsack = False
        # Csak a táblára kerültek pótlódnak vagy mind visszakerül:
        self.resetall = False
        if self.resetsack and not self.resetall:
            self.lettersetmode = 2
        elif self.resetsack and self.resetall:
            self.lettersetmode = 3
        else:
            self.lettersetmode = 1
            # A betűk értéke véletlenszám:
        self.randomlettervalue = False
        if self.randomlettervalue:
            self.valuemode = 2
        else:
            self.valuemode = 1
        self.rlvmin = 0
        self.rlvmax = 9

        self.values = [9, 1, 7, 6, 3, 2, 4, 8, 5, 3, 8, 4, 2, 7, 5, 9, 1, 6, 7, 5, 1, 6, 9, 3, 2, 8, 4, 7, 4, 9, 5, 8,
                       3, 2, 6, 1]
        # Ellenőrzés szótár alapján:
        self.checkdictionary = True
        if self.checkdictionary:
            self.checkmode = 1
        else:
            self.checkmode = 2
        # Lerakott dzsóker a táblán is dzsóker marad:
        self.dontchangejoker = False
        # Csak a lerakott betűk irányában kialakult szóra jár pont, a keresztező szavakra nem:
        self.onedirection = False
        # Fix betűk:
        self.usefletters = False                    # kizárt: duplicate
        self.fletters = []
        # Dzsókerek értéke:
        self.valueofchangedletter = False           # kizárt: dontchangejoker, gamemode=2, 3

        self.fieldtype = '.'
        self.rowmin = 0
        self.rowmax = 99
        self.columnmin = 0
        self.columnmax = 99
        self.width = 17
        self.height = 17
        self.timelimit = 30
        self.aitimelimit = 30

        self.wordlengthlist = ['True', 'True', 'True', 'True', 'True', 'True', 'True',
                               'True', 'True', 'True', ]
        self.lastopenedcfg = None
        self.lastsavedgame = None

        self.bonusforusingall = True                # kizárt: duplicate, turnlimit
        self.fixpoint = False                       # kizárt: valueforeachletter
        self.pointforfinish = 20
        self.valueforeachletter = True              # kizárt: fixpoint
        self.pointforeachletter = 5
        self.penaltyforleft = True
        self.pvalueforeachletter = True
        self.ppointforeachletter = 5

        self.createfieldsdict()

    def createfieldsdict(self):
        """Mezők viselkedése (szín, megjelenítendő-e a szövege, írható-e)"""
        self.fieldsdict = {".": [self.colornormal, 0, 1], "2L": [self.colordoubleL, 0, 1],
                           "3L": [self.colortripleL, 0, 1], "2W": [self.colordoubleW, 0, 1],
                           "3W": [self.colortripleW, 0, 1], "!": [self.colorwall, 0, 0]}
