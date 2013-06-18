# -*- coding: utf-8 -*-

import sys, time, subprocess
sys.path.append("../LocalNet")
from interfaces import PrototypeInterface, runPrototype

FESTIVAL_ES = "voice_cstr_upc_upm_spanish_hts"
FESTIVAL_EN = "voice_cstr_upc_upm_spanish_hts"
FESTIVALBIN = "/Users/thiago/Dev/festival-2.1/SpanishHTSVoice-ver0.8/build/festival/bin/festival"
FESTIVALCMD = "echo \"(LANG) (SayText \\\"XXXXX\\\")\" | "

class Megavoice(PrototypeInterface):
    """ Megavoice prototype class
        all prototypes must define setup() and loop() functions
        self.messageQ will have all messages coming in from LocalNet """
    def setup(self):
        ## pick what to subscribe to
        self.subscribeToAll()
        ## or....
        for k in self.allReceivers.keys():
            self.subscribeTo(k)
        ## some variables
        self.queueDelay = 30
        self.lastQueueCheck = time.time()
    def loop(self):
        ## check state
        if ((not self.messageQ.empty()) and
            (time.time() - self.lastQueueCheck > self.queueDelay)):
            (locale,type,txt) = self.messageQ.get()
            txt = txt.replace("#","")
            ## TODO: detect language!
            ## TODO: sanitize text message
            ##       #tag -> something else
            ##       á -> aa, etc
            ## then remove any nonAscii characters
            txt = self.removeNonAscii(txt.encode('utf-8'))
            toSay = (FESTIVALCMD+FESTIVALBIN).replace("LANG",FESTIVAL_ES)
            toSay = toSay.replace("XXXXX",txt)
            subprocess.call(toSay, shell=True)
            self.lastQueueCheck = time.time()
            if(self.messageQ.qsize() > 50):
                self.queueDelay = 10
            elif(self.messageQ.qsize() > 10):
                self.queueDelay = 20
            else:
                self.queueDelay = 30

if __name__=="__main__":
    ## TODO: get ip and ports from command line
    mM = Megavoice(8989,"127.0.0.1",8888)
    runPrototype(mM)
