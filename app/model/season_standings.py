from appdb import db

class Season_Standings(db.Model):
    __tablename__ = 'season_standings'
    id = db.Column(db.Integer, db.ForeignKey('team_season.standing_id'), primary_key=True)
    matches_played = db.Column(db.Integer, default=0)
    wins = db.Column(db.Integer, default=0)
    draws = db.Column(db.Integer, default=0)
    losses = db.Column(db.Integer, default=0)
    goals_for = db.Column(db.Integer, default=0)
    goals_against = db.Column(db.Integer, default=0)
    goal_difference = db.Column(db.Integer, default=0)
    points = db.Column(db.Integer, default=0)
    ranking = db.Column(db.Integer, nullable=False)