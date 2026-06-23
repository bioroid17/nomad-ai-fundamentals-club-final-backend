from flask import Flask, request

app = Flask("Focus Timer")


@app.route("/")
def index():
    return "hello"


@app.get("/subjects")
def get_subjects():
    pass


@app.post("/subjects")
def post_subjects():
    pass


@app.delete("/subjects/<int:id>")
def delete_subject(id: int):
    pass


@app.get("/sessions")
def get_sessions():
    pass


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
