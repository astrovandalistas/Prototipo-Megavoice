# -*- coding: utf-8 -*-

import sys, time, subprocess
sys.path.append("../LocalNet")
from interfaces import PrototypeInterface, runPrototype
import langid

FESTIVAL_ES = "voice_cstr_upc_upm_spanish_hts"
FESTIVAL_EN = "voice_kal_diphone"
FESTIVALBIN = "./festival"
FESTIVALCMD = "echo \"(LANG) (SayText \\\"XXXXX\\\")\" | "

class Megavoice(PrototypeInterface):
    """ Megavoice prototype class
        all prototypes must define setup() and loop() functions
        self.messageQ will have all messages coming in from LocalNet """
    def setup(self):
        ## subscribe to all receivers
        self.subscribeToAll()
        """
        ## or pick which ones
        for k in self.allReceivers.keys():
            self.subscribeTo(k)
        ## or subscribe to osc
            self.subscribeTo('osc')
        """
        ## some variables
        self.queueDelay = 30
        self.lastQueueCheck = time.time()
        ## turn up the volume
        subprocess.call("amixer set PCM -- -0", shell=True)

        ## for language identification
        langid.set_languages(['en','es'])
    def loop(self):
        ## check state
        if ((not self.messageQ.empty()) and
            (time.time() - self.lastQueueCheck > self.queueDelay)):
            (locale,type,txt) = self.messageQ.get()

            ## detect language!
            mLanguage = FESTIVAL_ES if(langid.classify(txt)[0] == 'es') else FESTIVAL_EN

            ## then remove accents and nonAscii characters
            txt = self.removeNonAscii(self.removeAccents(txt.encode('utf-8')))
            toSay = (FESTIVALCMD+FESTIVALBIN).replace("LANG",mLanguage)
            toSay = toSay.replace("XXXXX",txt)
            subprocess.call(toSay, shell=True)
            self.lastQueueCheck = time.time()
            if(self.messageQ.qsize() > 50):
                self.queueDelay = 1
            else:
                self.queueDelay = 5

if __name__=="__main__":
    ## TODO: get ip and ports from command line
    mM = Megavoice(8989,"127.0.0.1",8888)
    runPrototype(mM)
