import os
import datetime
from flask import Flask, request, jsonify
from google.cloud import firestore

app = Flask(__name__)

# Initialize Firestore DB
# This relies on the GOOGLE_APPLICATION_CREDENTIALS environment variable
# or default service account permissions when deployed to Google Cloud.
try:
    if os.path.exists("service-account.json"):
        db = firestore.Client.from_service_account_json("service-account.json")
        print("Firestore Client Initialized using service-account.json")
    else:
        db = firestore.Client()
        print("Firestore Client Initialized Successfully using default credentials")
except Exception as e:
    print(f"Warning: Failed to initialize Firestore client: {e}")
    db = None

@app.route('/api/log_disease', methods=['POST'])
def log_disease():
    if db is None:
        return jsonify({"error": "Firestore not initialized properly."}), 500

    data = request.json
    if not data:
        return jsonify({"error": "No JSON payload provided"}), 400

    disease_name = data.get('disease_name')
    sprayed_times = data.get('sprayed_times', 0)
    history_type = data.get('history_type', 'scan')

    if not disease_name:
        return jsonify({"error": "Missing 'disease_name' in payload"}), 400

    # Prepare document to be saved
    record = {
        "disease_name": disease_name,
        "sprayed_times": sprayed_times,
        "history_type": history_type,
        "timestamp": datetime.datetime.now(datetime.timezone.utc)
    }

    try:
        # Save to a collection named 'plant_history'
        doc_ref = db.collection("plant_history").add(record)
        return jsonify({
            "message": "Record saved successfully", 
            "id": doc_ref[1].id
        }), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "ok"}), 200

if __name__ == '__main__':
    # Run locally (usually on port 8080 as per Google Cloud run default)
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=True)
