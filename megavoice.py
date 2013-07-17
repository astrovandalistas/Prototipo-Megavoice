# -*- coding: utf-8 -*-

import sys, time, subprocess, getopt
from Queue import Queue
from random import random
sys.path.append("../LocalNet")
from interfaces import PrototypeInterface, runPrototype
import langid
from nltk import UnigramTagger, BigramTagger
from cPickle import dump, load

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
        self.queueDelay = 3
        self.lastQueueCheck = time.time()

        ## turn up the volume
        subprocess.call("amixer set PCM -- -0", shell=True)

        ## for language identification
        langid.set_languages(['en','es'])

        ## for tagging
        input = open('uniTag.en.pkl', 'rb')
        self.enTagger = load(input)
        input.close()
        input = open('uniTag.es.pkl', 'rb')
        self.esTagger = load(input)
        input.close()
        self.tagDict = {}

    def loop(self):
        ## check state
        if ((not self.messageQ.empty()) and
            (time.time() - self.lastQueueCheck > self.queueDelay)):
            (locale,type,txt) = self.messageQ.get()

            ## detect language!
            mLanguage = FESTIVAL_ES if(langid.classify(txt)[0] == 'es') else FESTIVAL_EN
            mTagger = self.esTagger if(mLanguage == FESTIVAL_ES) else self.enTagger

            ##words.sort(cmp=(lambda w0,w1:(len(w0)-len(w1))))

            ## make up a message
            madeUpMessage = txt.lower()
            txtWords = madeUpMessage.replace(",","").replace(".","").replace("?","").replace("!","").split()
            replaceCount = 0
            longishWords = 0
            for (word,tag) in mTagger.tag(txtWords):
                if(len(word) > 4):
                    longishWords += 1
                if((tag in self.tagDict) and 
                    (not word == self.tagDict[tag]) and 
                    (len(word) > 4) and (len(self.tagDict[tag])) and
                    (random() < 0.66)):
                    print "%s <-%s-> %s"%(word,tag,self.tagDict[tag])
                    madeUpMessage = madeUpMessage.replace(word,self.tagDict[tag])
                    replaceCount += 1
                # put this (word,tag) in dictionary
                if((tag) and 
                    ((not tag in self.tagDict) or (random() < 0.66))):
                    self.tagDict[tag] = word
            
            if(float(replaceCount)/longishWords > 0.5):
                print "pushing madeup message: "+madeUpMessage
                self.messageQ.put((locale,type,madeUpMessage))

            ## then remove accents and nonAscii characters
            txt = self.removeNonAscii(self.removeAccents(txt.encode('utf-8')))
            toSay = (FESTIVALCMD+FESTIVALBIN).replace("LANG",mLanguage)
            toSay = toSay.replace("XXXXX",txt)
            subprocess.call(toSay, shell=True)
            self.lastQueueCheck = time.time()
            if(self.messageQ.qsize() > 50):
                self.queueDelay = 1
            else:
                self.queueDelay = 3

if __name__=="__main__":
    (inPort, localNetAddress, localNetPort) = (8989, "127.0.0.1", 8888)
    opts, args = getopt.getopt(sys.argv[1:],"i:n:o:",["inport=","localnet=","localnetport="])
    for opt, arg in opts:
        if(opt in ("--inport","-i")):
            inPort = int(arg)
        elif(opt in ("--localnet","-n")):
            localNetAddress = str(arg)
        elif(opt in ("--localnetport","-o")):
            localNetPort = int(arg)

    mM = Megavoice(inPort, localNetAddress, localNetPort)
    runPrototype(mM)
