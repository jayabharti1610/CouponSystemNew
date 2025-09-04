# Add these imports and initialization to your existing app.py

from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from config import config
from supabase_service import supabase_service
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def create_app(config_name=None):
    app = Flask(__name__)
    
    # Load configuration
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')
    
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    
    # Initialize extensions
    CORS(app)
    
    # Initialize Supabase
    supabase_service.init_app(app)
    
    # Optional: Initialize SQLAlchemy if you want to use both
    # db.init_app(app)
    
    return app

# Create the app
app = create_app()

# Import routes (either add them to this file or import from separate files)
# You can copy the routes from the previous artifact here

if __name__ == '__main__':
    app.run(debug=True)
