from flask import Flask 
from flask_cors import CORS
from flask_mail import Mail
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from config import Config

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app=app)
migrate = Migrate(app=app, db=db)
mail = Mail(app)
cors = CORS(resources={r"/*": {"origins": "*"}}, app=app)
import domain_routes
import user_routes
import news



