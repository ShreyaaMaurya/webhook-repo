from flask import Flask, request, render_template, jsonify
from flask_pymongo import PyMongo
from datetime import datetime
import pytz  # Step 1: Import pytz

app = Flask(__name__)

app.config["MONGO_URI"] = "mongodb://localhost:27017/github_events"
mongo = PyMongo(app)

# Step 2: Create a helper function for IST
def get_ist_time():
    # Define India Timezone
    india_tz = pytz.timezone('Asia/Kolkata')
    # Get current time in India
    return datetime.now(india_tz)

def format_timestamp(dt):
    day = dt.day
    # Logic for 1st, 2nd, 3rd, 4th...
    suffix = 'th' if 11 <= day <= 13 else {1: 'st', 2: 'nd', 3: 'rd'}.get(day % 10, 'th')
    # Use %B for full month name (e.g., March) and %I:%M %p for 12-hour AM/PM
    return dt.strftime(f"{day}{suffix} %B %Y - %I:%M %p IST")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    if not data:
        return jsonify({"error": "No data received"}), 400

    payload = None

    # Handle Pull Request and Merge
    if 'pull_request' in data:
        is_merged = data.get('pull_request', {}).get('merged', False)
        
        if data['action'] == 'closed' and is_merged:
            action_type = "MERGE"
        elif data['action'] == 'opened':
            action_type = "PULL_REQUEST"
        else:
            return jsonify({"status": "ignored_pr_action"}), 200
        
        payload = {
            "author": data['pull_request']['user']['login'],
            "action": action_type,
            "from_branch": data['pull_request']['head']['ref'],
            "to_branch": data['pull_request']['base']['ref'],
            "timestamp": format_timestamp(get_ist_time()) # Using IST here
        }

    # Handle Push
    elif 'ref' in data and 'pusher' in data:
        # Ignore internal GitHub refs
        if 'base_ref' in data and data['base_ref'] is not None:
             return jsonify({"status": "ignored_push_ref"}), 200

        payload = {
            "author": data['pusher']['name'],
            "action": "PUSH",
            "from_branch": "None", 
            "to_branch": data['ref'].split('/')[-1],
            "timestamp": format_timestamp(get_ist_time()) # Using IST here
        }

    if payload:
        mongo.db.actions.insert_one(payload)
        print(f"--- Saved to MongoDB (IST): {payload['action']} by {payload['author']} ---")
        return jsonify({"status": "success"}), 200

    return jsonify({"status": "ignored"}), 200

@app.route('/api/get-actions', methods=['GET'])
def get_actions():
    # Sort by _id -1 to show latest actions at the top
    actions = list(mongo.db.actions.find({}, {'_id': 0}).sort('_id', -1).limit(10))
    return jsonify(actions)

if __name__ == '__main__':
    app.run(port=5000, debug=True)