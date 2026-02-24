import os
import random
import requests
import time

from collections import defaultdict
from dotenv import load_dotenv

load_dotenv()

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


def fetch_seeds(arg):
    headers = {}
    seed_type = chose_type(arg)

    seed_id = SEED_ID_MAPPING[seed_type]
    overworld_response = requests.get(GIST_RAW_URL + seed_type, headers=headers, timeout=10)
    nether_response = requests.get(GIST_RAW_URL + "nether_seeds.json", headers=headers, timeout=10)

    if overworld_response.status_code != 200 or nether_response.status_code != 200:
        raise Exception("Failed to fetch gist")

    return {"overworld": overworld_response.json(), "nether": nether_response.json(), "type": seed_id}


def get_seed_counts():
    headers = {}
    result = {}

    nether_response = requests.get(GIST_RAW_URL + "nether_seeds.json", headers=headers, timeout=10)

    for seed_type in SEED_TYPES:
        overworld_response = requests.get(GIST_RAW_URL + chose_type(False, seed_type), headers=headers, timeout=10)
        result[seed_type] = len(overworld_response.json())

    result["nether"] = len(nether_response.json())

    return result


def chose_type(arg):
    suffix = "_seeds.json"
    is_random = arg == "random"

    if is_random:
        return random.choice(SEED_TYPES) + suffix

    return arg + suffix
