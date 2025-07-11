from flask import Flask, request, jsonify, render_template
from pymongo import MongoClient
from datetime import datetime

app = Flask(__name__)
client = MongoClient("mongodb+srv://samakshdaksh21:Samaksh%4012@webhookcluster.ckrsogk.mongodb.net/") 
 # Update this mongodb://localhost:27017
db = client["webhook_db"]
collection = db["events"]

@app.route('/webhook', methods=['POST'])    
def webhook():
    data = request.json
    event = request.headers.get('X-GitHub-Event')
    
    if event == "push":
        entry = {
            "type": "push",
            "author": data["pusher"]["name"],
            "to_branch": data["ref"].split("/")[-1],
            "timestamp": datetime.utcnow()
        }

    elif event == "pull_request":
        pr = data["pull_request"]
        if data["action"] == "closed" and pr["merged"]:
            entry = {
                "type": "merge",
                "author": pr["user"]["login"],
                "from_branch": pr["head"]["ref"],
                "to_branch": pr["base"]["ref"],
                "timestamp": datetime.utcnow()
            }
        else:
            entry = {
                "type": "pull_request",
                "author": pr["user"]["login"],
                "from_branch": pr["head"]["ref"],
                "to_branch": pr["base"]["ref"],
                "timestamp": datetime.utcnow()
            }

    else:
        return "Event ignored", 200

    collection.insert_one(entry)
    return jsonify({"message": "Event stored"}), 200

@app.route('/events')
def get_events():
    events = list(collection.find({}, {"_id": 0}))
    return jsonify(events)

@app.route('/')
def home():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True, port=5000)
