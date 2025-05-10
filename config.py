import os 

class Config(object):
    SECRET_KEY= os.environ.get('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = 'sqlite:///'+ 'app.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # email config
    
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = os.environ.get('MAIL_PORT')
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    
    MAIL_DEBUG = os.environ.get('MAIL_DEBUG')
    MAIL_USE_TLS = False
    MAIL_USE_SSL = True
    DEFAULT_FROM_EMAIL = os.environ.get('MAIL_USERNAME')
    
    NAMESILO_KEY = os.environ.get('NAMESILO_KEY')