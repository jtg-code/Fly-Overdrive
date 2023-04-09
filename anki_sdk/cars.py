import asyncio
import bleak as b
import struct
import time as t
import threading

class carClass():
    
    def __init__(self, address: str):
        self.connected = False
        # UUIDs für das Schreiben und Lesen von Charakteristiken
        self.WRITE_UUID = "BE15BEE1-6186-407E-8381-0BD89C4D8DF4"
        self.SERVICE_UUID = "BE15BEEF-6186-407E-8381-0BD89C4D8DF4"
        self.READ_UUID = "BE15BEE0-6186-407E-8381-0BD89C4D8DF4"
        # Fahrzeug Mac-Adresse
        self.address = address
        # Variablen vehicle
        self.trackNotifyFunc = lambda data: print(data)
        #Code für den Start
        #Schienenwechsel
        #await self.client.start_notify(self.READ_UUID, self.trackNotifyFunc)
        
        
    def __str__(self):
        return self
    
    async def _sendCommand(self, command, awaited:bool=True):
        finalCommand = struct.pack("B", len(command)) + command
        await self.client.write_gatt_char(self.WRITE_UUID, finalCommand)
        if awaited == False and awaited != None:
            self.sendCommandloop.close()

    async def _connect(self, awaited:bool=True):
        self.client = b.BleakClient(self.address)
        t.sleep(1) # make sure that bleakClient is ready
        await self.client.connect()
        #print("Connected!")
        sdk_command = b"\x90\x01\x01"
        await self._sendCommand(sdk_command) # Enable SDK Mode
        #print("SDK Mode on!")
        await self._notification()
        print(f"Connected to {self.address}")
        if awaited == False and awaited != None:
            self.connectLoop.close()
            
    async def _getName(self):
        pass
            
    async def _disconnect(self, awaited:bool=True):
        break_command = struct.pack("<BHHB", 0x24, 0, 1000, 0x01)
        await self._sendCommand(break_command) # Slow down
        if awaited == False and awaited != None:
            await self.client.disconnect()
        
        
    async def _getLane(self):
        lane = await self.client.read_gatt_char(self.READ_UUID)
        return lane
    
    
    async def _notification(self):
        async def newLane():
            while True:
                await self.client.start_notify(self.READ_UUID, self.trackNotifyFunc)
            

        lane = threading.Thread(target=await newLane())
        lane.start()
    
    
    async def _setTrackNotify(self, function):
        self.trackNotifyFunc = function
#------------------------------------------------------------------- 

    def sendCommand(self, command):
        self.sendCommandloop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.sendCommandloop)
        self.sendCommandloop.run_until_complete(self._sendCommand(command))
        #asyncio.run(self._sendCommand(command))
        
    def connect(self):
        self.connectLoop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.connectLoop)
        self.connectLoop.run_until_complete(self._connect())
        #asyncio.run(self._connect())
        
    def disconnect(self):
        self.disconnectLoop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.disconnectLoop)
        self.disconnectLoop.run_until_complete(self._disconnect())
        #asyncio.run(self._disconnect())
        
    def getLane(self):
        result = asyncio.run(self._getLane())
        return result
        
    def setTrackNotify(self, function):
        self.trackNotifyFunc = function

        
    #-------Threads-------#
    
    # def _startTrackNotify(self):
    #     self.trackloop = asyncio.new_event_loop()
    #     asyncio.set_event_loop(self.trackloop)
    #     self.trackloop.run_until_complete(self._trackNotify())
        
    