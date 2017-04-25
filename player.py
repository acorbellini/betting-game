# An abstract player.
class Player:
    def __str__(self):
        return self.name + ":" + self.id

    def __repr__(self):
        return self.name + ":" + self.id

    def setIsWinner(self, result):
        pass

    def serialize(self):
        return {
            'name': self.name,
            'id': self.id,
            'bet': self.bet
        }
