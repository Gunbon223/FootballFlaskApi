from appdb import db

class Lineup(db.Model):
    __tablename__ = 'lineup'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    match_id = db.Column(db.Integer, db.ForeignKey('match.id'), nullable=False)
    player_id = db.Column(db.Integer, db.ForeignKey('player.id'), nullable=False)
    team_id = db.Column(db.Integer, db.ForeignKey('team.id'), nullable=False)
    is_starting = db.Column(db.Boolean, default=False)
    time_in = db.Column(db.Integer, nullable=True)
    time_out = db.Column(db.Integer, nullable=True)