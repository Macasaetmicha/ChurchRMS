from flask import Flask
#from flask_login import LoginManager

import os

import app.api as api
import app.db as db
import app.frontend as frontend

from flask_login import LoginManager

app=Flask(__name__, static_url_path="")
app.secret_key = os.urandom(32)

# add http routes / endpoints
app.register_blueprint(api.bp)
app.register_blueprint(frontend.bp)

# configure flask-login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "frontend.login"

app.config.update(
    #use secure cookies
    SESSION_COOKIE_SECURE=True,
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE='strict',

    #store state in session and not in URL
    USE_SESSION_FOR_NEXT=True
)

@login_manager.user_loader
def load_user(user_id):
    return db.load_user(user_id=user_id)

def main():
    app.run(
        host="0.0.0.0", 
        port=5000, 
        #ssl_context=("ssl/cert.pem", "ssl/key.pem"),
        debug=True)

if __name__ == "__main__":
    main()