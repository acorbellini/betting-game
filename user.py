from player import Player

# The real player
class User(Player):
    bet = None
    def __init__(self, id, name):
        self.id = id
        self.name = name

    def setBet(self, bet):
        self.bet = bet
        
    def getBet(self):
        return self.bet
