from appdb import db

class Tournament(db.Model):
    __tablename__ = 'tournament'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100))
    country = db.Column(db.String(100))
    seasons = db.relationship('Season', backref='tournament', lazy=True)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "country": self.country,
            "seasons": [season.to_dict() for season in self.seasons]
        }