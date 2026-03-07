import secrets

class Roll:

    def __init__ (self, dicestring):
        self.results = []
        self.hun_results = []
        self.hungry = False
        self.hunger_one = False
        self.hunger_ten = False
        self.critical = False
        self.num_successes = 0
        self.numdice = 0
        self.numhun = 0
        self.tens = 0
        if dicestring.find('h') != -1:
            self.hungry=True
            self.numdice = int(dicestring.partition('d')[0])
            self.numhun = int(dicestring.partition('d')[2].partition('h')[2])
            if (self.numdice-self.numhun) < 1:
                self.numhun = self.numdice
        else:
            self.numdice = dicestring.partition('d')[0]

    def __rolld10s(self,num):
        rolls = []
        for i in range(0,int(num)):
            rolls.append(secrets.choice(range(1,11)))

        return rolls

    def rollem(self):
        if self.hungry:
            self.results=self.__rolld10s(self.numdice-self.numhun)
            self.hun_results=self.__rolld10s(self.numhun)

            for i in self.hun_results:
                if i < 2:
                    self.hunger_one=True
                elif i > 9:
                    self.hunger_ten=True

        else:
            self.results=self.__rolld10s(self.numdice)

    def check_successes(self,rolls):
        if self.hungry:
            for i in rolls:
                if i > 5:
                    if i > 9:
                        self.tens += 1
                        if self.tens > 0 and self.tens % 2 == 0:
                            self.num_successes += 3
                            self.critical=True
                        else:
                            self.num_successes += 1
                    else:
                        self.num_successes += 1
        else:
            for i in rolls:
                if i > 5:
                    if i > 9:
                        self.tens += 1
                        if self.tens > 0 and self.tens % 2 == 0:
                            self.num_successes += 3
                            self.critical=True
                        else:
                            self.num_successes += 1
                    else:
                        self.num_successes += 1
