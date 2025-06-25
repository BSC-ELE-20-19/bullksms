##THIS WILL MAKE THE WEBSITE FOLDER A PYTHON PACKAGE
from flask import Flask



def create_app():
    app=Flask(__name__)
    from auth import auths
    from views import views
    app.register_blueprint(auths, url_prefix='/')
    app.register_blueprint(views, url_prefix='/')
    return app
