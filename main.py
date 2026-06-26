from flask import Flask, jsonify, request
from sqlalchemy import delete, select
from db import Session, Subject, db, obj_to_dict
from sqlalchemy.orm.exc import UnmappedInstanceError
import json

app = Flask("Focus Timer")
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///sqlite.db"
db.init_app(app)

with app.app_context():
    db.create_all()


@app.route("/")
def index():
    stmt = select(Subject).where(Subject.id == 1)
    delete_subject = db.session.execute(stmt).scalar()
    try:
        db.session.delete(delete_subject)
        db.session.commit()
        return {"success": True}
    except UnmappedInstanceError:
        return {"success": False, "msg": "존재하지 않는 인스턴스입니다."}


@app.get("/subjects")
def get_subjects():
    stmt = select(Subject)
    subjects = list(db.session.execute(stmt).scalars())
    return jsonify([obj_to_dict(subject) for subject in subjects])


@app.post("/subjects")
def post_subjects():
    body = request.get_json()

    name = body.get("name")
    subject = Subject(name=name)
    db.session.add(subject)
    db.session.commit()
    return jsonify(obj_to_dict(subject))


@app.delete("/subjects/<int:id>")
def delete_subject(id: int):
    stmt = select(Subject).where(Subject.id == id)
    delete_subject = db.session.execute(stmt).scalar()
    try:
        db.session.delete(delete_subject)
        db.session.commit()
        return {"success": True}
    except UnmappedInstanceError:
        return {"success": False, "msg": "존재하지 않는 인스턴스입니다."}


@app.get("/sessions")
def get_sessions():
    stmt = (
        select(
            Session.id,
            Session.subject_id,
            Session.duration,
            Session.created_at,
            Subject.name,
        )
        .select_from(Session)
        .join(Subject)
    )
    print(stmt)
    sessions = list(db.session.execute(stmt).scalars())
    return jsonify([obj_to_dict(session) for session in sessions])


@app.post("/sessions")
def post_sessions():
    pass


@app.delete("/sessions/<int:id>")
def delete_sessions(id: int):
    stmt = select(Session).where(Session.id == id)
    delete_session = db.session.execute(stmt).scalar()
    try:
        db.session.delete(delete_session)
        db.session.commit()
        return {"success": True}
    except UnmappedInstanceError:
        return {"success": False, "msg": "존재하지 않는 인스턴스입니다."}


@app.get("/stats")
def stats():
    pass


if __name__ == "__main__":
    app.run(debug=True)
