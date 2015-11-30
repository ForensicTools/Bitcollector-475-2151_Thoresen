import os
basedir = os.path.abspath(os.path.dirname(__file__))

# List of os variables -
# SECRET_KEY
# MAIL_USERNAME
# MAIL_PASSWORD
# ADMIN

class Config:
    APP_NAME = "BitCollector"
    SECRET_KEY = "SOME_SECRET_STRING!_THAT_ISNT_REALLY_USED!"
    SSL_DISABLE = False

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'data-dev.sqlite')

class TestingConfig(Config):
    TESTING = True
    WTF_CSRF_ENABLED = False

config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
