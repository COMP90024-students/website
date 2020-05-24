import os

COUCHDB_HOST = os.environ.get("COUCHDB_HOST", "localhost")
COUCHDB_USER = os.environ.get("COUCHDB_USER", "guest")
COUCHDB_PASSWORD = os.environ.get("COUCHDB_PASSWORD", "guest")
COUCHDB_URL = f"http://{COUCHDB_HOST}:5984"
