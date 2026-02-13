import os
import time
import random
import requests
from flask import Flask, request, jsonify, abort
from collections import defaultdict

app = Flask(__name__)

GIST_RAW_URL = os.getenv("GIST_RAW_URL")

requests_log = defaultdict(list)
RATE_LIMIT = 30
WINDOW_SECONDS = 60

SEED_TYPES = ["village", "shipwreck", "treasure", "temple", "bucket_portal", "normal_portal"]
SEED_ID_MAPPING = {f"{name}_seeds.json": SEED_TYPES.index(name) for name in SEED_TYPES}


def rate_limited(ip):
    now = time.time()
    requests_log[ip] = [
        t for t in requests_log[ip]
        if now - t < WINDOW_SECONDS
    ]

    if len(requests_log[ip]) >= RATE_LIMIT:
        return True

    requests_log[ip].append(now)
    return False


def fetch_seeds(is_random=True):
    headers = {}
    seed_type = chose_type(is_random=is_random)

    seed_id = SEED_ID_MAPPING[seed_type]
    overworld_response = requests.get(GIST_RAW_URL + seed_type, headers=headers, timeout=10)
    nether_response = requests.get(GIST_RAW_URL + "nether_seeds.json", headers=headers, timeout=10)

    if overworld_response.status_code != 200 or nether_response.status_code != 200:
        raise Exception("Failed to fetch gist")

    return {"overworld": overworld_response.json(), "nether": nether_response.json(), "type": seed_id}


def chose_type(is_random=True, *args):
    if is_random:
        return random.choice(SEED_TYPES) + "_seeds.json"

    return args[0] + "_seeds.json"


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