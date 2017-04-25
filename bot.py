from uuid import uuid1
from player import Player
from collections import Counter
import random


# A bot player with and auto-generated name.
# The betting logic is very simple (although I tried different approaches):
class Bot(Player):
    NAMES = ["Bird", "Cat", "Dog", "Horse", "Owl", "Rabbit", "Dove"]
    COLORS = ["Blue", "Red", "White", "Yellow"]

    def setIsWinner(self, result):
        if not result:
            self.loses += 1
            # if the bots loses a certain amount of times, it resets the bet to a number between 0 a 2.
            if self.loses == self.max_loses:
                self.previous_bet = random.randint(0, 2)
                self.loses = 0

    def __init__(self):
        self.id = str(uuid1())
        self.name = self.COLORS[random.randint(0, len(self.COLORS) - 1)] + " " + self.NAMES[
            random.randint(0, len(self.NAMES) - 1)]
        self.bet = None
        self.previous_bet = 0
        self.loses = 0
        self.max_loses = 3

    def setBet(self, bet):
        self.bet = bet

    def getBet(self):
        if self.bet is None:
            # The previous bet is used 85% of the time. 15% of the times the bot jumps to a random number bw 0 and 100
            self.bet = self.previous_bet if random.random() < 0.85 else random.randint(0, 100)
            self.previous_bet = self.bet
        return self.bet
