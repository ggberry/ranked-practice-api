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

SEED_TYPES = ["bucket_portal", "normal_portal", "village", "shipwreck", "treasure", "temple"]


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

    overworld_response = requests.get(GIST_RAW_URL + chose_type(is_random=is_random), headers=headers, timeout=10)
    nether_response = requests.get(GIST_RAW_URL + "nether_seeds.json", headers=headers, timeout=10)

    if overworld_response.status_code != 200 or nether_response.status_code != 200:
        raise Exception("Failed to fetch gist")

    return [overworld_response.json(), nether_response.json()]


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
        seeds = fetch_seeds()
        overworldData = random.choice(seeds[0])
        netherData = random.choice(seeds[1])

        return jsonify({
            "success": True,
            "overworld": overworldData,
            "nether": netherData
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