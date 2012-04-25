from cmdOp import *

# update  the db in time 
def monitor():
    while(1):
        Timer(5,vmdb_update,()).start()
        time.sleep(5)
#test:        
monitor()