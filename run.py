from app import create_app
from dotenv import load_dotenv
import os

# Učitaj .env varijable
load_dotenv()

# Kreiraj Flask aplikaciju
app = create_app()

# Samo za lokalni razvoj
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
