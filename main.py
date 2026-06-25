from flask import Flask, jsonify, request
from sqlalchemy import select
from db import Session, Subject, db, obj_to_dict
import json

app = Flask("Focus Timer")
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///sqlite.db"
db.init_app(app)

with app.app_context():
    db.create_all()


@app.route("/")
def index():
    stmt = select(Subject).where(Subject.id == 1)
    subject = db.session.execute(stmt).scalar()
    return jsonify(obj_to_dict(subject))


@app.get("/subjects")
def get_subjects():
    stmt = select(Subject)
    subjects = list(db.session.execute(stmt).scalars())
    return jsonify([obj_to_dict(subject) for subject in subjects])


@app.post("/subjects")
def post_subjects():
    pass


@app.delete("/subjects/<int:id>")
def delete_subject(id: int):
    stmt = select(Subject).where(Subject.id == id)
    subject = db.session.execute(stmt).scalar()
    return jsonify(obj_to_dict(subject))


@app.get("/sessions")
def get_sessions():
    stmt = select(Session)
    sessions = list(db.session.execute(stmt).scalars())
    return jsonify([obj_to_dict(session) for session in sessions])


@app.post("/sessions")
def post_sessions():
    pass


@app.delete("/sessions/<int:id>")
def delete_sessions(id: int):
    pass


@app.get("/stats")
def stats():
    pass


if __name__ == "__main__":
    app.run(debug=True)
