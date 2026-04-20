from datetime import timedelta

class Config:
    SECRET_KEY = 'your-secret-key-here'
    DEBUG = True
    HOST = '0.0.0.0'
    PORT = 5000
    
    MONGODB_URI = 'mongodb://localhost:27017/'
    MONGODB_DB_NAME = 'medical_ai_db'
    
    GROQ_API_KEY = 'api key'
    GROQ_MODEL = 'meta-llama/llama-4-scout-17b-16e-instruct'
    
    UPLOAD_FOLDER = 'uploads'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024
    ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg'}
    
    PERMANENT_SESSION_LIFETIME = timedelta(hours=24)
    SESSION_COOKIE_SECURE = False
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    APP_NAME = 'Medical AI'
    APP_VERSION = '1.0.0'
    
    SUPPORTED_LANGUAGES = {
        'English': 'English',
        'Telugu': 'తెలుగు',
        'Hindi': 'हिंदी',
        'Tamil': 'தமிழ்',
        'Kannada': 'ಕನ್ನಡ'
    }
    
    @staticmethod
    def init_app(app):
        pass

class DevelopmentConfig(Config):
    DEBUG = True
    TESTING = False

class ProductionConfig(Config):
    DEBUG = False
    TESTING = False
    SESSION_COOKIE_SECURE = True
    
    @classmethod
    def init_app(cls, app):
        Config.init_app(app)

class TestingConfig(Config):
    TESTING = True
    DEBUG = True
    MONGODB_DB_NAME = 'medical_ai_test_db'

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}

def get_config(config_name='development'):
    return config.get(config_name, config['default'])