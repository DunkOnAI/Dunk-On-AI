
import os


basedir = os.path.abspath(os.path.dirname(__file__))
#basedir = main directory path of the app

class Config:
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///' + os.path.join(basedir, 'app.db')

#this takes the location of the applications database from SQLALCHEMY_DATABASE_URI config variable
#in this case the database is either 'DATABASE_URL'(environment variable that the user enters) 
# if that is not defined, we use an sqlite database that we make(name: app.db)
