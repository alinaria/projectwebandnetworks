from flask import Flask
from flask_bootstrap import Bootstrap5

app = Flask(__name__)
app.config['BOOTSTRAP_SERVE_LOCAL'] = True
bootstrap=Bootstrap5(app)

import os.path
def mkpath(p):
    """renvoie chemin complet du répertoire p passé en paramètre"""
    return os.path.normpath(
        os.path.join(
            os.path.dirname(__file__), p))

from flask_sqlalchemy import SQLAlchemy
app.config['MODIFICATIONS'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = ('sqlite:///'+ mkpath('../books.db'))
app.config['SECRET_KEY'] = '76409418-e9c9-4a04-b1f9-d3a910854964'
db=SQLAlchemy(app)

from flask_login import LoginManager
login_manager = LoginManager (app)
login_manager . login_view = "login"