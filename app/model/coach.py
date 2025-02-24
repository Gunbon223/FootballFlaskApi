from appdb import db

class Coach(db.Model):
    __tablename__ = 'coach'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), nullable=False)
    nationality = db.Column(db.String(100), nullable=False)
    date_of_birth = db.Column(db.Date, nullable=False)
    experience_years = db.Column(db.Integer, nullable=False)