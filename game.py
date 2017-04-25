from collections import Counter

from user import User
from bot import Bot
from threading import Lock
from flask_socketio import send, emit
from uuid import uuid1

# The game logic. It mainly manages connected users and the current users involved in a bet.
class Game:
    def __init__(self):
        self.connectedUsersLock = Lock()
        self.connectedUsers = {}
        for i in range(0, 6):
            bot = Bot()
            self.connectedUsers[bot.id] = bot

        self.game_lock = Lock()
        self.playing = False
        self.playing_users = {}
        self.currentGame = None

    def login(self, userId, user_name):
        currentUser = User(userId, user_name)
        notifyUsers = None
        with self.connectedUsersLock:
            self.connectedUsers[currentUser.id] = currentUser
            print "Currently connected users: " + str(self.connectedUsers)
            notifyUsers = dict([(user.id, user.serialize()) for (id, user) in self.connectedUsers.items()])
        emit('current users', notifyUsers, broadcast=True)
        return currentUser

    def removeUser(self, userId):
        print userId + " is logging out"
        notifyUsers = None
        with self.connectedUsersLock:
            del self.connectedUsers[userId]
            print "Currently connected users after LOGOUT: " + str(self.connectedUsers)
            notifyUsers = dict([(user.id, user.serialize()) for (id, user) in self.connectedUsers.items()])
        with self.game_lock:
            if self.playing:
                del self.playing_users[userId]
        self.notifyPlayingUsers()
        self.checkEndGame()
        emit('current users', notifyUsers, broadcast=True)

    def addBet(self, userId, bet):
        bet = int(bet)
        with self.game_lock:
            if not self.playing:
                # When someone bets for the first time, it starts a new game.
                # Current users are copied and only them can play this round.
                self.playing = True
                self.currentGame = str(uuid1())
                with self.connectedUsersLock:
                    self.playing_users = dict(self.connectedUsers)
            if self.playing:
                filterRes = filter(lambda (id, user): id == userId, self.playing_users.items())
                if len(filterRes) == 0:
                    print "Not playing"
                else:
                    user = filterRes[0][1]
                    if user.getBet() is None:
                        user.setBet(bet)
                        print user.name + " is now playing!"
        self.notifyPlayingUsers()
        self.checkEndGame()

    def getWinner(self, bets):
        c = Counter(bets.values())
        res = [(user, bet) for (user, bet) in bets.items() if c[bet] == 1]
        res.sort(key=lambda x: x[1])  # Sort by bet
        if len(res) > 0:
            return res[0]
        else:
            return None

    def notifyPlayingUsers(self):
        # Notify the clients with the current players (for UI purposes).
        json = None
        with self.game_lock:
            json = dict([(user.id, user.serialize()) for (id, user) in self.playing_users.items()])
        emit('playing users', json, broadcast=True)

    def checkEndGame(self):
        json = {}
        notify = False
        with self.game_lock:
            if self.playing and all(player.getBet() is not None for (id, player) in self.playing_users.items()):
                bets = dict([(user, user.getBet()) for (id, user) in self.playing_users.items()])
                # get the winner and reser the logic.
                winningUser = self.getWinner(bets)

                if winningUser:
                    print "The winner is : " + str(winningUser[0]) + " with a bet of " + str(winningUser[0].bet)
                    json = {
                        'id': winningUser[0].id,
                        'name': winningUser[0].name,
                        'bet': winningUser[0].bet,
                        'game': self.currentGame
                    }
                else:
                    print "No winner"

                notify = True
                # Reset playing state
                self.playing = False
                for (id, player) in self.playing_users.items():
                    player.setIsWinner(winningUser is not None and winningUser[0].id == player.id)
                    player.setBet(None)
                self.playing_users = {}
                self.currentGame = None

        # Notify clients after realeasing the lock, due to Flask's possible emit lock (however, now that I'm using
        # eventlet, this may go back to where it was.
        if notify:
            emit('winner', json, broadcast=True)
