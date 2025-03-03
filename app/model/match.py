from appdb import db

class Match(db.Model):
    __tablename__ = 'match'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    season_id = db.Column(db.Integer, db.ForeignKey('season.id'), nullable=False)
    home_team_id = db.Column(db.Integer, db.ForeignKey('team.id'), nullable=False)
    away_team_id = db.Column(db.Integer, db.ForeignKey('team.id'), nullable=False)
    match_start_date = db.Column(db.DateTime, nullable=False)
    match_end_date = db.Column(db.DateTime, nullable=False)
    home_score = db.Column(db.Integer, default=0)
    away_score = db.Column(db.Integer, default=0)
    referee = db.Column(db.String(100), nullable=True)
    round_id = db.Column(db.Integer, db.ForeignKey('round.id'), nullable=False)
    round = db.relationship('Round', backref='matches', lazy=True)
    stadium = db.Column(db.String(100), nullable=True)
