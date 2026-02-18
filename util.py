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

SEED_TYPES = ["village", "shipwreck", "treasure", "temple", "portal"]
SEED_ID_MAPPING = {f"{name}_seeds.json": SEED_TYPES.index(name) for name in SEED_TYPES}


def rate_limited(ip):
    """
    Rate limiting
    """

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
    """
    Returns information regarding the filtered seed:
    Overworld: seed & chunk coordinates of relevant starting structure
    Nether: seed & chunk of closest bastion
    """

    headers = {}
    seed_type = chose_type(arg)

    seed_id = SEED_ID_MAPPING[seed_type]
    overworld_response = requests.get(GIST_RAW_URL + seed_type, headers=headers, timeout=10)
    nether_response = requests.get(GIST_RAW_URL + "nether_seeds.json", headers=headers, timeout=10)

    if overworld_response.status_code != 200 or nether_response.status_code != 200:
        raise Exception("Failed to fetch gist")

    return {"overworld": overworld_response.json(), "nether": nether_response.json(), "type": seed_id}


def get_seed_counts():
    """
    Returns the size of the seed pool per seed type
    """

    headers = {}
    result = {}

    nether_response = requests.get(GIST_RAW_URL + "nether_seeds.json", headers=headers, timeout=10)

    for seed_type in SEED_TYPES:
        overworld_response = requests.get(GIST_RAW_URL + chose_type(seed_type), headers=headers, timeout=10)
        result[seed_type] = len(overworld_response.json())

    result["nether"] = len(nether_response.json())

    return result


def chose_type(arg):
    """
    Helper function for `fetch_seeds`
    Returns a set or random seed type based on `arg`
    """

    suffix = "_seeds.json"
    is_random = arg == "random"
    seed_type = random.choice(SEED_TYPES)

    if not is_random:
        return arg + suffix

    if seed_type != "portal":
        return seed_type + suffix

    prefix = "normal_"

    if random.random() <= 0.1:
        prefix = "bucket_"

    return prefix + seed_type + suffix

