from flask import Flask, request, jsonify, abort
from util.seed_fetcher import *
from util.filter_status import FilterInfo

app = Flask(__name__)
filter_info = FilterInfo()


@app.route("/filter-status", methods=["GET", "POST"])
def filter_status():
    if request.method == "GET":
        return filter_info.get_status()

    if not request.is_json:
        abort(400, description="Request must be JSON")

    data = request.get_json()

    required = ["enabled", "percentage", "current", "total"]
    if any(key not in data for key in required):
        abort(400, description="Invalid request")

    filter_info.enabled = data["enabled"]
    filter_info.percentage = data["percentage"]
    filter_info.current = data["current"]
    filter_info.total = data["total"]

    return f"Received data: {data}"


@app.route("/request-seed/<seed_type>", methods=["POST"])
def request_seed(seed_type):
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


@app.route("/seed-counts", methods=["POST"])
def seeds():
    return get_seed_counts()


@app.route("/")
def index():
    return "Ranked Practice seed API is running."


if __name__ == "__main__":
    app.run(port=4000)
# gunicorn app:app --bind 0.0.0.0:$PORT
