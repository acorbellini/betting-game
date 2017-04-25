from game import Game
import string

# A simple test (not a unit test though, I need to practice python unit testing).
game = Game();
players = list(string.ascii_lowercase[:7])
print game.getWinner(dict(zip(players,[1,2,3,4,1,1,2])))
print game.getWinner(dict(zip(players,[10,2,3,4,9,3,2])))
print game.getWinner(dict(zip(players,[1,2,2,4,1,1,4])))
