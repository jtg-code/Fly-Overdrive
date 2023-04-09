import anki_sdk.cars as cars
import anki_sdk.controller as controller
import anki_sdk.utils as utils
import time as t
import socket
import pickle
import threading
import inputs
import math
import keyboard
import config.Client as c
import sys
import discord
from flask import *
from zenora import APIClient

functionList = {}

app = Flask(__name__)



#serverRedirect = f"https://discord.com/api/oauth2/authorize?client_id=1090982969189077113&redirect_uri=http%3A%2F%2F127.0.0.1%3A{self.port}%2FserverMenu%2Fserver&response_type=code&scope=identify%20email%20connections%20rpc"

class colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


class appClass():
    def __init__(self, Active:bool):
        self.Active = Active
        #self.cars = ["CarOne", "CarTwo", "CarThree", "CarFour", "CarFive"]
        self.cars = []
        self.name = 'Player Name'
        self.serverIp = "127.0.0.1"
        self.serverPort = 6666
        self.port = 9000
        self.carAddress = ""
        self.redirectClient = APIClient(c.token, client_secret=c.secret)
        self.token = ""
        self.user = None
        self.clientWebsite()
        self.serverWebsite()
        self.webMenu()
        #self.connectServer()
    

        
    def myPrint(self):
        print("Hello world")
        
    def webMenu(self):
        @app.route("/", methods=["POST", "GET"])
        def mainMenu():
            if request.method == "GET":
                return render_template("index.html")
        
        def start():
            print("Starting webpannel")
            app.run(debug=False, port=self.port, use_reloader=False)
            print("Started webpannel")
            
        webThread = threading.Thread(target=start)
        webThread.run()
        
    def clientWebsite(self):
        @app.route("/clientMenu", methods=["POST", "GET"])
        
        def clientMenu():
            if request.method == "POST":
                if len(request.form) > 0:
                    self.serverIp = request.form["serverIp"]
                    self.serverPort = int(request.form["serverPort"])
                    print(f"{self.serverIp}:{self.serverPort}")
                    self.connectServer()
            else:
                print("Someone is loading page")
            return render_template("client.html")
        
    
    def serverWebsite(self):
        @app.route("/serverMenu", methods=["POST", "GET"])
        def serverMenu():
            if request.method == "POST":
                if len(request.form) > 0:
                    print(request.form)
                    self.serverPort = int(request.form["port"])
                    self.serverIp = request.form["ip"]
                    serverRedirect = f"https://discord.com/api/oauth2/authorize?client_id=1090982969189077113&redirect_uri=http%3A%2F%2F127.0.0.1%3A{self.port}%2FserverMenu%2Fserver&response_type=code&scope=identify%20email%20connections%20rpc"
                    self.connectServer()
                    return redirect(serverRedirect)
                else:
                    return render_template("serverMenu.html", data=self)
            else:
                print("Someone is loading page")
                return render_template("serverMenu.html", data=self)
        

        @app.route("/serverMenu/server")
        def server():
            if request.method == "POST":
                if len(request.form) > 0:
                    print(request.form)
    
                    self.serverPort = int(request.form["port"])
                    self.serverIp = request.form["ip"]
                    self.name = request.form["playerName"]
                    self.connectServer()
                    return render_template("server.html", data=self)
                else:
                    return render_template("server.html", data=self)
            else:
                code = str(request.args["code"])
                self.token = self.redirectClient.oauth.get_access_token(code, redirect_uri="http://127.0.0.1:9000/serverMenu/server").access_token
                bearerClient = APIClient(self.token, bearer=True)
                user = bearerClient.users.get_current_user()
                self.user = user
                self.name = user.username
                self.client.sendServer(data={"function": "registerDiscord", "discordName": self.name, "discordId": self.user.id})
                return render_template("server.html", data=self)
            
            
            
    
    def connectServer(self):
        self.client = clientClass(appClass=self, serverIP=self.serverIp, serverPort=self.serverPort)
        self.client.connectServer()
        #self.input = inputClass(self.client, False)
        
    def __str__(self):
        return self
    

    
class clientClass():
    def __init__(self, appClass, serverIP: str = "127.0.0.1", serverPort: int = 6666):
        self.carAddress = ""
        self.serverIp = str(serverIP)
        self.serverPort = serverPort
        self.appClass = appClass
        print((self.serverIp, self.serverPort))
        
        
    def registerFunction(func):
        functionList[func.__name__] = func
        return func
    
    def sendServer(self, data):
        data = pickle.dumps(data)
        self.socket.sendall(data)
        
        
    @registerFunction
    def disconnectServer(self, data = {}):
        self.sendServer(data={"function": "disconnect"})
        t.sleep(3)
        self.socket.close()
        sys.exit(data["reason"])
        
    def connectServer(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((self.serverIp, self.serverPort))
        t.sleep(3)
        self.sendServer(data={"function": "getCars", "type": "GET"})
        
        def receive():
            while True:
                rcv = self.socket.recv(16384)
                while rcv == b'':
                    t.sleep(0.1)
                data = pickle.loads(rcv)
                #print(data)
                functionList[data["function"]](self, data)

        rcvThread = threading.Thread(target=receive)
        rcvThread.start()
        print(f"Connected to {self.serverIp}:{self.serverPort}")
        
        
    @registerFunction
    def getCars(self, data):
        self.appClass.cars = data["cars"]
        #print(data["cars"])
        
        
    @registerFunction
    def myPrint(self, data):
        print(data["text"])
        
        
    
        
class inputClass():
    def __init__(self, clientClass: clientClass, controller: bool = False):
        self.clientClass = clientClass
        self.MAX_TRIG_VAL = math.pow(2, 8)
        self.MAX_JOY_VAL = math.pow(2, 15)
        self.LeftTrigger = 0
        self.RightTrigger = 0
        self.controller = controller
        
        self.speed = 0
        self.input()
        
        
    def input(self):
        def gamepad():
            while True:
                if self.controller == True:
                    events = inputs.get_gamepad()
                    for event in events:
                        if event.code == 'ABS_Z': # Left trigger
                            self.LeftTrigger = (event.state / self.MAX_TRIG_VAL) * 1000
                        elif event.code == 'ABS_RZ': # Right trigger
                            self.RightTrigger = (event.state / self.MAX_TRIG_VAL) * 1000 # normalize between 0 and 1
                else:
                    break
                        
        def keyBoard():
            while True:
                if keyboard.is_pressed("w"):
                    self.RightTrigger = (1 / self.MAX_TRIG_VAL) * 1000 # normalize between 0 and 1
                    
                if keyboard.is_pressed("s"):
                    self.LeftTrigger = (1 / self.MAX_TRIG_VAL) * 1000 # normalize between 0 and 1
                    
                if keyboard.is_pressed("esc"):
                    self.clientClass.disconnectServer()
                    sys.exit("Exited")
                    
        def speed():
            while True:
                if (self.speed + self.RightTrigger) < 1000 and (self.speed - self.LeftTrigger) > 350:
                    self.speed += self.RightTrigger
                    self.speed -= self.LeftTrigger
                if self.speed <= 350 and self.RightTrigger > 0:
                    self.speed = 360
                        
        controllerThread = threading.Thread(target=gamepad)
        keyboardThread = threading.Thread(target=keyBoard)
        controllerThread.start()
        keyboardThread.start()
    
    


    
    







print("1")
myApp = appClass(False)
print("3")


t.sleep(1)

