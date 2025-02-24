from appdb import db

class Player_Achievement(db.Model):
    __tablename__ = 'player_achievement'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    player_id = db.Column(db.Integer, db.ForeignKey('player.id'), nullable=False)
    season_id = db.Column(db.Integer, db.ForeignKey('season.id'), nullable=False)
    match_id = db.Column(db.Integer, db.ForeignKey('match.id'), nullable=False)
    award_name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)