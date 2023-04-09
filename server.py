import socket
import threading
import time as t
import pickle
import sys
import config.Server as c
import discord
from discord.ext import tasks
import anki_sdk.utils as utils
import anki_sdk.controller as controller
import anki_sdk.cars as cars
import API.discordAPI as discordAPI


serverFunctionList = {}
serverCommandFunctionList = {}

admins = c.admins

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
    

def registerFunction(func):
    serverFunctionList[func.__name__] = func
    return func



# def registerCommandFunction(func):
#     serverCommandFunctionList[func.__name__] = func
#     return func
    
    
def registerCommandFunction(funcName, admin):
    def wrapper(func):
        serverCommandFunctionList[funcName] = {"function": func, "admin": admin}
        return func
    return wrapper

class serverClass():
    def __init__(self, address:str = socket.gethostname(),port: int = 6666, connections: int = 10):
        self.cars = self.getVehicles(False)
        self.address = address
        self.port = port
        self.maxConnections = connections
        self.clients = {}
        self.discordClass = None
        
    def sendClient(self, address, data):
        data = pickle.dumps(data)
        #print(f"Target: {address}, Data: {data}")
        self.clients[address]["socket"].sendall(data)
        
    def getVehicles(self, active):
        cars = [car.address for car in utils.scanner(active)]
        return cars
            
        
    def openServer(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((self.address, self.port))
        self.socket.listen(self.maxConnections)
        print(f"Server running on: {self.address}:{self.port}")
        
        def waitClients():
            while True:
                try:
                    client_socket, addr = self.socket.accept()
                    print(f"Connecting: {addr}")
                    
                    clientListen = threading.Thread(target=listenClients, args=(client_socket, addr))
                    self.clients[addr] = {"socket": client_socket, "address": addr, "thread": clientListen, "discordName": "none", "admin": False}
                    clientListen.start()
                    print(f"{addr} is connected")
                    #self.sendClient(addr, data={"function": "myPrint", "text": "This is the text"})
                except KeyboardInterrupt or self.stop == True or Exception or ConnectionResetError:
                    print("Connection stopped")
                    break
                    
        
        def listenClients(client_socket, address):
            while address in self.clients:
                try:
                    data = client_socket.recv(16384)
                    while data == b'':
                        t.sleep(0.1)
                        
                    data = pickle.loads(data)
                    a = "address"
                    data["address"] = f"{address[0]}:{address[1]}"
                    data["addr"] = address
                    #print(data)
                    
                    if data["function"] == "disconnect":
                        self.disconnectClient(data)
                    else:
                        if data.get("type") == "GET" or data.get("type") == "get":
                            self.sendClient(address, data=(serverFunctionList[data["function"]](self, data)))
                        else:
                            serverFunctionList[data["function"]](self, data)
                        
                    t.sleep(0.1)
                except KeyboardInterrupt or self.stop == True:
                    self.disconnectClient(data={"addr": address})
                    print("Stopped listener")
                    break
        
        
        clientWait = threading.Thread(target=waitClients)
        clientWait.start()
        print("READY")
        
    
    def kick(self, data):
        self.sendClient((data["ip"], data["port"]), {"function": "disconnectServer", "reason": data["reason"]})
    
    def disconnectClient(self, data):
        del self.clients[data["addr"]]
        
    @registerFunction
    def registerDiscord(self, data):
        print(data["addr"])
        self.clients[data["addr"]]["discordName"] = data["discordName"]
        self.clients[data["addr"]]["discordId"] = data["discordId"]
        self.clients[data["addr"]]["admin"] = str(data["discordId"]) in admins
        f = open(c.bannList, "r")
        if str(data["discordId"]) in f.read():
            data = {
                "ip": data["addr"][0],
                "port": data["addr"][1],
                "reason": ""
            }
            self.kick(data)
        
    @registerFunction
    def setValue(self, data):
        for k, v in data.items():
            if k != "function":
                self.clients[data["addr"]][k] = v
                print(f'{data["addr"]}: {k} = {v}')
        
    @registerFunction
    def getCars(self, data):
        print(f'Sending vehicles')
        d = {"function": "getCars", "cars": self.cars}
        return d
        
        
        
        

class discordClass():
    def __init__(self, token, server: serverClass = serverClass):
        self.token = token
        self.server = server
        
        intents = discord.Intents.default()
        intents.message_content = True
        
        client = self.discordBot(intents=intents, dc=self)
        client.run(self.token)
        
        # discordThread = threading.Thread(name="discordThread", target=self.client.run, args=[self.token])
        # discordThread.start()
        
    
    
    class discordBot(discord.Client):
        def __init__(self, dc, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.discordClass = dc
            self.server = dc.server
            # an attribute we can access from our task
            self.counter = 0
            
            self.commands = {
                ">web": "http://127.0.0.1:9000",
                ">dev": "https://discord.gg/UgXRH9K5",
                ">ip": f"http://{socket.gethostname()}/"
            }
            

        async def on_ready(self):
            print(f'Bot: {colors.OKBLUE}{self.user}{colors.ENDC} | Id: {colors.OKBLUE}{self.user.id}{colors.ENDC}')
            print('------')
            await self.setActivity()
            
        async def send_message(self, message, channel):
            self.get_channel(channel).send(message)
            
        async def setActivity(self):
            stream = discord.Streaming(name="Fly Overdrive", url="http://127.0.0.1:9000")
            await self.change_presence(status=discord.Status.online, activity=stream)
            
            
        @registerCommandFunction(">ip", False)
        def getIP(self, message):
            return f"IP: {c.server[0]} | Port: {c.server[1]}"
            
        
        @registerCommandFunction(">players", False)
        def getPlayers(self, message):
            players = self.server.clients
            count = str(len(players))
            string = "__**Spielerliste**__: \n"
            if str(message.author.id) in admins:
                for k, v in players.items():
                    if v["admin"]:
                        string += f'''```html\n<{v["discordName"]}> | {v["address"]}\n```\n'''
                    else: 
                        string += f'''```{v["discordName"]}```\n'''
            else:
                for k, v in players.items():
                    if v["admin"]:
                        string += f'```html\n<{v["discordName"]}>\n```\n'
                    else: 
                        string += f'''```{v["discordName"]}```\n'''
            max = str(self.server.maxConnections)
            string += f"**{count}/{max}** Players"
            return string
        
        @registerCommandFunction(">kick", True)
        def kickPlayer(self, message):
            args = message.content.split(" ")
            data = {
                "reason": f"Kicked by {message.author}",
                "ip": args[1],
                "port": args[2]
            }
            self.server.kick(message)
            return f"Kicked {args[1]}:{args[2]}"
            #return text
        
        def getAnswer(self, message):
            options = [message.content.startswith(">")]
            if all(options):
                first = message.content.split(" ")[0]
                if message.content in self.commands:
                    answer = self.commands[message.content]
                    t = str(type(answer))
                    t = t.lower()
                    return answer
                elif first in serverCommandFunctionList.keys():
                    if serverCommandFunctionList[first]["admin"] == True:
                        if str(message.author.id) in admins:
                            return serverCommandFunctionList[first]["function"](self, message)
                        else:
                            return "Du hast **keine** Berechtigung dazu"
                    else:
                        return serverCommandFunctionList[first]["function"](self, message)
                        
                else: 
                    return "Befehl nicht gefunden"

        async def on_message(self, message):
            # don't respond to ourselves
            if message.author == self.user:
                return

            print(f"Author: {message.author}, Message: {message.content}")
            answer = self.getAnswer(message)
            if answer != None:
                await message.reply(answer, mention_author=True)
        
        async def on_message_edit(self, old_message, new_message):
            print(f"Edited message {old_message.content} | {new_message.content}")
            await self.on_message(new_message)

    

                
        
server = serverClass(address=c.server[0], port=c.server[1], connections=c.maxConnections)
server.openServer()
myDiscord = discordClass(c.token, server=server)
server.discordClass = myDiscord