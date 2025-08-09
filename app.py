from flask import Flask, request, jsonify
import os
import requests
import json

app = Flask(__name__)

AGENT_ZERO_A2A_URL = os.getenv('AGENT_ZERO_A2A_URL')

@app.route('/webhook', methods=['POST'])
def webhook():
    if not AGENT_ZERO_A2A_URL:
        print("Error: AGENT_ZERO_A2A_URL environment variable not set.")
        return jsonify({"status": "error", "message": "Agent Zero A2A URL not configured"}), 500

    try:
        # Get the incoming JSON payload from Evolution API
        whatsapp_payload = request.json
        if not whatsapp_payload:
            print("Received empty or non-JSON payload.")
            return jsonify({"status": "error", "message": "Invalid payload"}), 400

        print(f"Received WhatsApp webhook payload: {whatsapp_payload}")

        # The Agent Zero A2A endpoint expects a 'user_message' key with the payload.
        agent_zero_message = {
            "user_message": json.dumps(whatsapp_payload)
        }

        # Send to Agent Zero's A2A endpoint
        agent_zero_response = requests.post(AGENT_ZERO_A2A_URL, json=agent_zero_message)
        agent_zero_response.raise_for_status() # Raise an exception for HTTP errors

        print(f"Forwarded to Agent Zero. Response: {agent_zero_response.text}")
        return jsonify({"status": "success", "message": "Payload forwarded to Agent Zero"}), 200

    except requests.exceptions.RequestException as e:
        print(f"Error forwarding to Agent Zero: {e}")
        if e.response is not None:
            print(f"Agent Zero Response content: {e.response.text}")
        return jsonify({"status": "error", "message": f"Failed to forward to Agent Zero: {e}"}), 500
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return jsonify({"status": "error", "message": f"An unexpected error occurred: {e}"}), 500

if __name__ == '__main__':
    # Render sets the PORT environment variable
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
