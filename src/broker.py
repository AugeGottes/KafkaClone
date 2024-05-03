import json
import argparse
import time
import sys
from pathlib import Path
from datetime import datetime
import requests
from flask import Flask, request

parser = argparse.ArgumentParser()
parser.add_argument("-p", "--port", help="Set broker port")
parser.add_argument("-i", "--id", help="Set broker ID")
args = parser.parse_args()


if not 1024 <=args.port <=65535:
    print("Port number must be between 1024 and 65535")
    sys.exit(1)

if args.id <0:
    print("Broker ID must be a positive integer")
    sys.exit(1)


app = Flask(__name__)

NO_BROKERS = 3
root = Path.cwd().resolve()
filename = f"Broker_{args.id}"
subscribe_list = root / "subscribe_list.json"
broker_fs = (root / filename).resolve()
logfile = (broker_fs / "logfile").resolve()


def logger(_id, timestamp, topic, action):
    try:
        if not logfile.exists():
            logfile.touch()

        with open(logfile, "a") as f:
            log = {
                "Time": timestamp,
                "Topic": topic,
                "ID": _id,
                "Action": action
            }
            f.write(f"{json.dumps(log)},\n")
    except Exception as e:
        print(f"Error logging: {str(e)}")

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
        except Exception :
            print("Retrying..")
        
    return res.content.decode()

def timehash(timestamp):
    return timestamp % NO_BROKERS

@app.route('/')
def main():
    return "test kafka broker"

@app.route('/beginning/<topic>', methods=['POST'])
def send_beg():
    dats = json.loads(request.data.encode())
    print(dats)


@app.route('/send_topic/<topic>', methods=['POST'])
def send_topic(topic):
    dat = json.loads(request.data.decode())
    topic_data = dat['data']
    timestamp = dat['time']
    m_id = dat['_id']

    try:
        with open(broker_fs / topic / f"p{timehash(timestamp)}", 'a+') as f:
            f.write(f"{timestamp} {topic_data}\n")
    except Exception as e:
        create_topic(topic)
        with open(broker_fs / topic / f"p{timehash(timestamp)}", 'a+') as f:
            f.write(f"{timestamp} {topic_data}\n")

    with open("subscribe_list.json") as f:
        ports = json.load(f)[topic]
    
    for port in ports:
        logger(m_id, timestamp, topic, "POST")
        post_request(f"http://127.0.0.1:{port}", topic_data)
    return "sent"

@app.route('/create_topic/<topic>')
def create_topic(topic):
    try:
        if not broker_fs.exists():
            broker_fs.mkdir()
        
        topic_fs = broker_fs / topic
        if not topic_fs.exists():
            topic_fs.mkdir()
        logger(args.id, int(time.time()), topic, "CREATE_TOPIC")
        return "created"
    except Exception as e:
        print(f"Error creating topic: {str(e)}")
        return "error"

@app.route('/subscribe_topic/<topic>', methods=['POST'])
def subscribe_topic(topic):
    dat = json.loads(request.data.decode())
    port = dat['port']
    timestamp = dat['time']
    _sid = dat['_id']
    data = {}
    print(port)
    if not subscribe_list.exists():
        subscribe_list.touch()
        data[topic] = [port]
    else:
        with open(subscribe_list) as f:
            try:
                data = json.load(f)
                if topic not in data.keys():
                    data[topic] = [port]
                elif port not in data[topic]:
                    data[topic].append(port)
                else:
                    return "port already registered"
            except Exception as e:
                data[topic] = [port]
    
    with open(subscribe_list, "w") as f:
        json.dump(data, f)
    logger(_sid, timestamp, topic, "SUBSCRIBE")
    return "subscribed"

@app.route('/unsub_topic/<topic>', methods=['POST'])
def unsub_topic(topic):
    dat = json.loads(request.data.decode())
    port = dat['port']
    timestamp = dat['time']
    _id = dat['_id']

    with open(subscribe_list) as f:
        data = json.load(f)
    
    if port in data[topic]:
        data[topic].remove(port)
    else:
        return "not subbed to this"
    
    with open(subscribe_list, "w") as f:
        json.dump(data, f)
    logger(_id, timestamp, topic, "UNSUBSCRIBE")

    return "unsubbed"

@app.route('/polling')
def poll():
    return filename


if __name__ == "__main__":
    app.run(port=args.port, debug=False, use_reloader=False)
