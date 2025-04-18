import json
import os
from urllib.parse import urlparse

# Load credentials from the config file
def load_credentials():
    try:
        with open("e_sif.json", "r") as file:
            config = json.load(file)
            return config["email"], config["password"]
    except FileNotFoundError:
        print("Config file not found!")
        return None, None

def normalize_url(url):
    """Normalize the URL by removing query parameters and trailing slashes."""
    parsed_url = urlparse(url)
    normalized_url = parsed_url._replace(query='', fragment='').geturl().rstrip('/')
    return normalized_url
