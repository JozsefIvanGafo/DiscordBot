import json
import logging
import os

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('discord')

class JsonManager:
    def __init__(self, filename):
        # Get correct path to data directory
        current_path = os.path.dirname(os.path.abspath(__file__))  # utils folder
        src_path = os.path.dirname(current_path)                   # src folder
        
        # Create data folder in src directory
        data_folder = os.path.join(src_path, 'data')
        os.makedirs(data_folder, exist_ok=True)
        self.filename = os.path.join(data_folder, filename)
        self.data = {}
        self.load()
        logger.info(f"Loaded JSON file: {self.filename}")

    def load(self):
        try:
            with open(self.filename, 'r') as f:
                self.data = json.load(f)
        except FileNotFoundError:
            self.data = {}
            # Create the file
            self.create()
        except json.JSONDecodeError:
            self.data = {}
            logger.error(f"Error decoding JSON file: {self.filename}")
        except Exception as e:
            logger.error(f"Error loading JSON file: {str(e)}")
            self.data = {}

    def save(self):
        try:
            with open(self.filename, 'w') as f:
                json.dump(self.data, f, indent=4)
        except Exception as e:
            logger.error(f"Error saving JSON file: {str(e)}")
    
    def create(self):
        try:
            with open(self.filename, 'w') as f:
                json.dump({}, f, indent=4)
        except Exception as e:
            logger.error(f"Error creating JSON file: {str(e)}")

    def get(self, key, default=None):
        return self.data.get(key, default)
    
    def set(self, key, value):
        self.data[key] = value
        self.save()

    def delete(self, key):
        try:
            del self.data[key]
        except KeyError:
            pass
        self.save()
        
    def get_all(self):
        """Return all data stored in the JSON file."""
        return self.data
