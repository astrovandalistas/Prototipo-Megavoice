import sys
sys.path.append("../LocalNet")
from interfaces import PrototypeInterface, runPrototype

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
    def loop(self):
        ## check state
        ## if (not self.messageQ.empty())
        pass

if __name__=="__main__":
    ## TODO: get ip and ports from command line
    mM = Megavoice(8989,"127.0.0.1",8888)
    runPrototype(mM)
