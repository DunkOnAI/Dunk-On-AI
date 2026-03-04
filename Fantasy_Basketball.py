import sqlalchemy as sa
import sqlalchemy.orm as so
from Backend import create_app, db  #this imports the create_app function that creates the app and db instance
from Backend.models import  User, Player, Team, News, GameStat, AITeam, Matchup

app = create_app()

@app.shell_context_processor
def make_shell_context():
    return {
        'sa': sa, 
        'so': so, 
        'db': db, 
        'User': User, 
        'Player': Player,
        'Team': Team,
        'News': News,
        'GameStat': GameStat,
        'AITeam': AITeam,
        'Matchup': Matchup
    }

#this function registers a shell context processor with the Flask app
#it makes certain objects automatically available in the Flask shell
#when you run flask shell from the command line