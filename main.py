from flask import Flask, request

app = Flask("Focus Timer")


@app.route("/")
def index():
    return "hello"


@app.route("/subjects", methods=["GET", "POST"])
def subjects():
    if request.method == "GET":
        pass
    else:
        pass


@app.delete("/subjects/<int:id>")
def delete_subjects(id: int):
    pass


@app.route("/sessions", methods=["GET", "POST"])
def sessions():
    if request.method == "GET":
        pass
    else:
        pass


@app.delete("/sessions/<int:id>")
def delete_sessions(id: int):
    pass


@app.get("/stats")
def stats():
    pass


if __name__ == "__main__":
    app.run(debug=True)
