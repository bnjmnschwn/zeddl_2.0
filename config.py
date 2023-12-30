import os


basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    SQLALCHEMY_DATABASE_URI = "postgresql://koyeb-adm:bKFvslL19MrQ@ep-hidden-poetry-04269976.eu-central-1.aws.neon.tech/zeddl"
    # SQLALCHEMY_TRACK_MODIFICATIONS = False