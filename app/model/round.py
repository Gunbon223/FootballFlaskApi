from appdb import db

class Round(db.Model):
    __tablename__ = 'round'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    season_id = db.Column(db.Integer, db.ForeignKey('season.id'), nullable=False)
    round_number = db.Column(db.Integer, nullable=False)
    round_date = db.Column(db.Date, nullable=False)
    is_finished = db.Column(db.Boolean, default=False)
