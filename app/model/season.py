from appdb import db

class Season(db.Model):
    __tablename__ = 'season'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    description = db.Column(db.String(255), nullable=True)
    tournament_id = db.Column(db.Integer, db.ForeignKey('tournament.id'), nullable=False)

    def to_dict(self):
        return {
            c.name: getattr(self, c.name) for c in self.__table__.columns
        }