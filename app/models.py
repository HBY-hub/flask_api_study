from app import db
import datetime


class log(db.Model):
    __tablename__ = 'log'
    id = db.Column(db.Integer, primary_key=True)
    info = db.Column(db.String(100))
    ok = db.Column(db.SmallInteger, default=0)
    addtime = db.Column(db.DateTime, index=True, default=datetime.datetime.now())
    deadtime = db.Column(db.DateTime)

    def __repr__(self):
        return "<log %r>" % self.id


