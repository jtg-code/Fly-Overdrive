import requests
import json
import pypresence
import discord
import threading
import sys
import time as t

class Discord():
    def __init__(self, token: str = "", clientID: str = "", webHookURL: str = ""):
        self.clientID = clientID
        self.webHookURL = webHookURL
        self.running = False
        self.rpcData = {}
        self.Token = token
        self.connected = False
        #self._rpc()
        
    ### Easy code
    def _rpc(self):
        self.rpc = pypresence.Presence(self.clientID)
        self.rpc.connect()
        self.connected = True
        
    def webHook(self, message):
        r = requests.post(url=self.webHookURL, data=json.dumps(message), headers={"Content-Type": "application/json"})
        return(r)
        
    def RichPresence(self, data):
        if self.connected == False:
            self._rpc()
            
        for k, v in data.items():
            self.rpcData[k] = v
            
        self.state = self.rpcData.get("state");
        self.details = self.rpcData.get("details");
        self.startTimestamp = self.rpcData.get("startTimestamp");
        self.endTimestamp = self.rpcData.get("endTimestamp");
        self.largeImageKey = self.rpcData.get("largeImageKey");
        self.largeImageText = self.rpcData.get("largeText");
        self.smallImageKey = self.rpcData.get("smallImageKey");
        self.smallImageText = self.rpcData.get("smallText");
        self.partyId = self.rpcData.get("partyID");
        self.partySize = self.rpcData.get("partySize");
        self.partyMax = self.rpcData.get("partyMax");
        self.joinSecret = self.rpcData.get("joinSecret");
        
        def run():
            while True:
                self.running = True
                if self.rpc != None and self.rpcData != {}:
                    try:
                        print(self.state, self.details, self.startTimestamp, self.endTimestamp, self.largeImageKey, self.largeImageText, self.smallImageKey, self.smallImageText,self.partyId, self.partySize, self.joinSecret)
                        self.rpc.update(state=self.state, details=self.details, 
                                        start=self.startTimestamp, end=self.endTimestamp, 
                                        large_image=self.largeImageKey, large_text=self.largeImageText, 
                                        small_image=self.smallImageKey, small_text=self.smallImageText,
                                        party_id=self.partyId, party_size=self.partySize, join=self.joinSecret
                                        )
                    except KeyboardInterrupt:
                        self.rpc = None
                        self.rpcData = {}
                        break
                    
                    t.sleep(5)
                    
            sys.exit()
        
        if self.running == False:    
            self.rpcThread = threading.Thread(target=run)
            self.rpcThread.start()
            self.running = True
        
    
    




if __name__ == "__main__":
    #dc = Discord("MTA5MDk4Mjk2OTE4OTA3NzExMw.GfUN0T.huXambQL3twk-T-7FhXfBp79nFxjkG8Xixz174", "1090982969189077113", "https://discord.com/api/webhooks/1036293548384985199/i3O31R4UFua4n-4Pwgl1Q7NkJluHZy3n5BNWC7ADWELp7B7l-r3tWIhmaTYaNwLcl6T4")
    #dc.RichPresence({"state": "Old State", "details": "Old Detail", "largeImageKey": "anki_big"})
    print("Finished")