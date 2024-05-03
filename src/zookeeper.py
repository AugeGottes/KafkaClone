import time
import threading
import random
import argparse

from pathlib import Path
from flask import Flask
import requests

parser = argparse.ArgumentParser()
parser.add_argument("-p", "--port", help="zookeeper port", type=int, required=True)
parser.add_argument("-b", "--brokers", help="Broker ports")
parser.add_argument("-t", "--time", help="polling interval", type=int, default=2)
pargs = parser.parse_args()

root = Path.cwd().resolve()
brokers = []
leader = None
app = Flask(__name__)

def polling(args):
    global leader

    flag = False
    while True:
        try:
            res = requests.get(f"http://127.0.0.1:{args}/polling", timeout=1)
            flag = True

            if args not in brokers:
                brokers.append(args)
            
            # The first broker 
            if not leader:
                leader = args

            if leader == args:
                print("---------Leader---------", args)
            else:
                print("---------Follower----------", args)
            
            print(res, threading.get_native_id(), brokers)
        except Exception as e:
            if flag:
                flag = False
                brokers.remove(args)
                if leader == args and brokers != []:
                    leader = random.choice(brokers)
                    print("------------New Leader----------", leader)
                print(f"-------{args}, has died-------")
            else:
                print("----Not Started----", args)        
        time.sleep(pargs.time)


@app.route('/find_leader')
def find_leader():
    return str(leader)

def main():
    broker_ports = [int(x) for x in pargs.brokers.split('-')]
    broker1 = threading.Thread(target=polling, args=(broker_ports[0],))
    broker1.daemon = True
    broker2 = threading.Thread(target=polling, args=(broker_ports[1],))
    broker2.daemon = True
    broker3 = threading.Thread(target=polling, args=(broker_ports[2],))
    broker3.daemon = True
    broker1.start()
    broker2.start()
    broker3.start()

    app.run(debug=False, use_reloader=False, port=pargs.port)
    

if __name__ == "__main__":
    main()
