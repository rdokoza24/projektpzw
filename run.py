import os
from dotenv import load_dotenv
from flask import Flask
from flask_pymongo import PyMongo

# Učitaj .env varijable (samo za lokalni razvoj)
load_dotenv()

# Dohvati MongoDB URI iz environment varijable
MONGO_URI = os.environ.get("MONGO_URI")
if not MONGO_URI:
    raise ValueError("MONGO_URI environment variable is not set!")

# Kreiraj Flask aplikaciju
from app import create_app
app = create_app()

# Konfiguracija MongoDB
app.config["MONGO_URI"] = MONGO_URI
mongo = PyMongo()
mongo.init_app(app)

# Lokalni razvoj
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
