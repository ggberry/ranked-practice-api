from flask import Flask, request, jsonify, abort
from util import *

app = Flask(__name__)


@app.route("/seed-counts", methods=["POST"])
def seeds():
    return get_seed_counts()


@app.route("/request-seed", methods=["POST"])
def request_seed():
    client_ip = request.remote_addr

    # Rate limit check
    if rate_limited(client_ip):
        abort(429, description="Too many requests")

    try:
        seed_info = fetch_seeds()
        overworld_data = random.choice(seed_info["overworld"])
        nether_data = random.choice(seed_info["nether"])
        seed_type = seed_info["type"]

        return jsonify({
            "success": True,
            "overworld": overworld_data,
            "nether": nether_data,
            "type": seed_type
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route("/")
def index():
    return "Ranked Practice seed API is running."

# app.run()
# gunicorn app:app --bind 0.0.0.0:$PORT
