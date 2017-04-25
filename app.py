from flask import Flask, session
from flask_socketio import SocketIO, send
from game import Game
from uuid import uuid1

# Flask and Socket IO initialization
app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, ping_timeout=10, ping_interval=5)

# The game logic
game = Game()


# The only static content in the game
@app.route('/')
def root():
    return app.send_static_file('index.html')


# From now on, these functions receive events from the client/s
@socketio.on("login")
def login(user_name):
    if 'name' in session:
        print "Already logged."
        return
    print user_name + " has logged in"
    session['name'] = user_name
    currentUser = game.login(session['id'], user_name)
    return currentUser.serialize()


@socketio.on("relogin")
def reconnect(user):
    if 'name' in session:
        print "Already logged."
        return
    print user['name'] + " has re-logged in"
    session['name'] = user['name']
    return game.login(session['id'], user['name']).serialize()


@socketio.on("connect")
def connect():
    session['id'] = str(uuid1())
    print "Client connected: " + session['id']


@socketio.on("disconnect")
def disconnect():
    if 'name' in session:
        print session['name'] + " has logged out"
        game.removeUser(session['id'])


@socketio.on("send bet")
def sendBet(bet):
    game.addBet(session['id'], bet)


if __name__ == "__main__":
    socketio.run(app)
