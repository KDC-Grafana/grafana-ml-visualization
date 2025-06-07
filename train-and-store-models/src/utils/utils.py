import configparser
import os

import numpy as np


class Utils:
    @staticmethod
    def to_native(value):
        """
        Convierte valores de tipos NumPy (np.generic) a tipos nativos de Python.
        """
        
        if isinstance(value, np.generic):
            return value.item()  
        return value
    
    @staticmethod
    def load_feature_flags():
        config_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'config', 'config.ini'))
        config = configparser.ConfigParser()
        config.read(config_path)
        features = config["features"]
        return {
            "task_notifications": features.getboolean("task_notifications", fallback=True),
            "general_notifications": features.getboolean("general_notifications", fallback=True),
            "generate_summary": features.getboolean("generate_summary", fallback=False)
        }
        
    @staticmethod
    def get_scheduler_interval():
        config_path =  os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'config', 'config.ini'))
        parser = configparser.ConfigParser()
        parser.read(config_path)

        return int(parser['scheduler']['interval_minutes'])
