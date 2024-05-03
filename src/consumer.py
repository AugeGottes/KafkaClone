import time
import argparse
import json
import logging


log = logging.getLogger('werkzeug')
log.disabled = True

import requests
from flask import Flask, request




parser = argparse.ArgumentParser()
parser.add_argument("-z", "--port", help="zookeeper port", type=int, required=True)
parser.add_argument("-c", "--cport", help="consumer port", type=int, required=True)
parser.add_argument("-t", "--topic", help="enter the topic name", required=True)
parser.add_argument("-i", "--cid", help="enter the cid", required=True)
parser.add_argument("-b", "--from-beginning", type=int, help="receive topics information from start", default=0)
args = parser.parse_args()

app = Flask(__name__)
def get_request(url):
    flag = True
    while flag:
        try:
            res = requests.get(url, timeout=1)
            flag = False
        except Exception as e:
            print("Retrying..")
        
    return res.content.decode()

def post_request(url, data):
    flag = True
    while flag:
        try:
            res = requests.post(url, json=data, timeout=1)
            flag = False
        except Exception as e:
            print("Retrying..")
        
    return res.content.decode()

def get_leader():
    return get_request(f"http://127.0.0.1:{args.port}/find_leader")

@app.route('/', methods=['POST'])
def receive():
    data = json.loads(request.data.decode())
    print(data)
    return "Received"

def main():
    get_request(f"http://127.0.0.1:{get_leader()}/create_topic/{args.topic}")
    post_request(f"http://127.0.0.1:{get_leader()}/subscribe_topic/{args.topic}", data={"port": args.cport, "time": int(time.time()), "_id": args.cid, "beg": args.from_beginning})
    
    app.run(port=args.cport, debug=False, use_reloader=False)

if __name__ == "__main__":
    try:
        main()
        post_request(f"http://127.0.0.1:{get_leader()}/unsub_topic/{args.topic}", data={"port": args.cport, "time": int(time.time()), "_id": args.cid})
    except KeyboardInterrupt:
        pass
