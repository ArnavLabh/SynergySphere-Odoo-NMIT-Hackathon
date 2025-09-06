from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# Make sure models are imported when package is loaded
from . import models