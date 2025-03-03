from appdb import db

class Transfer_History(db.Model):
    __tablename__ = 'transfer_history'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    player_id = db.Column(db.Integer, db.ForeignKey('player.id'), nullable=False)
    from_team_id = db.Column(db.Integer, db.ForeignKey('team.id'), nullable=False)
    to_team_id = db.Column(db.Integer, db.ForeignKey('team.id'), nullable=False)
    transfer_date = db.Column(db.Date, nullable=False)
    season_id = db.Column(db.Integer, db.ForeignKey('season.id'), nullable=False)
    transfer_fee = db.Column(db.Integer, nullable=False)
    title = db.Column(db.String(255), nullable=False)