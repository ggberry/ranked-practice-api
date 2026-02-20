from flask import Flask, request, jsonify, abort
from util import *

app = Flask(__name__)


@app.route("/seed-counts", methods=["POST"])
def seed_counts():
    """
    Return seed count data
    """

    return get_seed_counts()


@app.route("/request-seed/<seed_type>", methods=["POST"])
def request_seed(seed_type):
    """
    Returns data for a random set of seeds (overworld + nether)
    """

    client_ip = request.remote_addr

    # Rate limit check
    if rate_limited(client_ip):
        abort(429, description="Too many requests")

    try:
        seed_info = fetch_seeds(seed_type)
        overworld_data = random.choice(seed_info["overworld"])
        nether_data = random.choice(seed_info["nether"])
        seed_type_id = seed_info["type"]

        return jsonify({
            "success": True,
            "overworld": overworld_data,
            "nether": nether_data,
            "type": seed_type_id
        })

    except Exception as error:
        return jsonify({
            "success": False,
            "error": str(error)
        }), 500


@app.route("/")
def index():
    """
    Index page
    """

    return "Ranked Practice seed API is running."

# RUN:
app.run()
# gunicorn app:app --bind 0.0.0.0:$PORT
