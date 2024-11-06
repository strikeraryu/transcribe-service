from flask import Flask
from flask_cors import CORS
from apis.core import core_bp
from apis.transcribe import transcribe_bp
from models import db
from flask_migrate import Migrate
import logging

# Setup App
app = Flask(__name__)
app.config['SECRET_KEY'] = 'I am a big secret'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
app.config['MAX_FORM_MEMORY_SIZE'] = 16 * 1024 * 1024

db.init_app(app)
migrate = Migrate(app, db)

# Setup CORS
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

# Register blueprints
app.register_blueprint(core_bp)
app.register_blueprint(transcribe_bp, url_prefix='/transcribe')

if __name__ == '__main__':
    # gunicorn_logger = logging.getLogger('gunicorn.error')
    # app.logger.handlers = gunicorn_logger.handlers
    # app.logger.setLevel(gunicorn_logger.level)    
    app.run(debug=True)
