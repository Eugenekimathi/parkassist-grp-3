from flask import Flask
from app import create_app, db

app = create_app()

if __name__ == "__main__":
    app.run(port=5555, debug=True)
