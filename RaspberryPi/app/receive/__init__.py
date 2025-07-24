# app/receive/__init__.py

# Marks the 'receive' folder as a package.
# You can import your Flask server or HTTP handling code here if needed.

# Example:
# from .server import app  # if you have a Flask app instance in server.py


## Sample
# app/receive/__init__.py

# app/receive/__init__.py

from .server import app  # So you can do: from app.receive import app
 # Import Flask app or key functions here if any
    # For example:
    # app  # if you have a Flask instance named app in server.py
    # Otherwise leave empty
