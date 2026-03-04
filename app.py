from flask import Flask, request, jsonify, abort
from werkzeug.middleware.proxy_fix import ProxyFix

from util.seed_fetcher import *
from util.filter_status import FilterInfo

app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1)

filter_info = FilterInfo()


@app.route("/filter-status", methods=["GET", "POST"])
def filter_status():
    """
    See the status of current filtering
    """

    if request.method == "GET":
        return filter_info.get_status()

    if not request.is_json:
        abort(400, description="Request must be JSON")

    ip = request.headers.get("X-Forwarded-For", request.remote_addr)

    if ip and "," in ip:
        ip = ip.split(",")[0].strip()

    data = request.get_json()
    filter_info.status_update(ip, data)

    return f"Received data: {data}"


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

    return '<span style="font-family: Consolas; font-size: 16px;">Ranked Practice seed API is running.</span>'

# RUN:
app.run(debug=True)
# gunicorn app:app --bind 0.0.0.0:$PORT
