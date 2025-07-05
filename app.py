from flask import Flask, request, jsonify
from pymongo import MongoClient
from flask import render_template

app = Flask(__name__)

# MongoDB connection
client = MongoClient("mongodb://localhost:27017")
db = client["webhook_db"]
events_collection = db["events"]

@app.route('/webhook', methods=['POST'])
def github_webhook():
    event_type = request.headers.get('X-GitHub-Event')
    data = request.json

    # handle push events
    if event_type == "push":
        author = data['pusher']['name']
        to_branch = data['ref'].split('/')[-1]
        timestamp = data['head_commit']['timestamp']
        event_doc = {
            "event_type": "push",
            "author": author,
            "from_branch": None,
            "to_branch": to_branch,
            "timestamp": timestamp
        }
        events_collection.insert_one(event_doc)
        print(f"Stored PUSH event: {event_doc}")

    # handle pull_request events
    elif event_type == "pull_request":
        author = data['pull_request']['user']['login']
        from_branch = data['pull_request']['head']['ref']
        to_branch = data['pull_request']['base']['ref']
        timestamp = data['pull_request']['created_at']
        event_doc = {
            "event_type": "pull_request",
            "author": author,
            "from_branch": from_branch,
            "to_branch": to_branch,
            "timestamp": timestamp
        }
        events_collection.insert_one(event_doc)
        print(f"Stored PULL REQUEST event: {event_doc}")

    else:
        # other events you don't handle
        print(f"Unhandled event type: {event_type}")

    return jsonify({"status": "stored"}), 200
@app.route('/events', methods=['GET'])
def get_events():
    events = list(events_collection.find({}, {"_id": 0}))  # exclude _id
    return jsonify(events)

@app.route('/')
def home():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(port=5000, debug=True)
