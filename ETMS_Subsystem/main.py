from flask import Flask
from app.presentation.views import views
import os
import secrets


app = Flask(__name__, static_folder=os.path.join('app', 'static'), template_folder=os.path.join('app', 'templates'))
app.register_blueprint(views)

# Secret key for session management
app.secret_key = secrets.token_hex(16)

if __name__ == "__main__":
    app.run(debug=True)
