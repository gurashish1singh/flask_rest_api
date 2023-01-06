from __future__ import annotations

from flask_sqlalchemy import SQLAlchemy

# Using expire_on_commit=False to access queried objects after session.commit
db = SQLAlchemy(session_options={"expire_on_commit": False})


class VideoModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    likes = db.Column(db.Integer, nullable=False)
    views = db.Column(db.Integer, nullable=False)

    def __repr__(self) -> str:
        return f"Video(name={self.name}, likes={self.likes}, views={self.views})"
