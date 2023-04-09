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
import config.Client as config
import sys
from flask import Flask, render_template


app = Flask(__name__)

class appC():
    def __init__(self, Active: bool):
        self.Active = Active
        self.cars = self.getVehicles()
        self.Players = []
        self.selectCar = None
        self.myPlayer = None
    
    def addPlayer(self, datas):
        self.Players = datas
            
    def getVehicles(self):
        cars = [car.address for car in utils.scanner(self.Active)]
        return cars
    
    def selectVehicle(self):
        config.carAddress = self.selectCar.get()
        myPlayer = "TestName"
        self.myPlayer = myPlayer
    
    @app.route('/')
    def index(self):
        self.addPlayer('John')
        self.selectCar = 'car1'
        self.selectVehicle()
        return render_template('index.html', app=self)
    
    def __str__(self):
        return str(self.__dict__)

if __name__ == '__main__':
    my_app = appC(True)
    app.run(debug=True)
