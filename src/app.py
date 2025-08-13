from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from dotenv import load_dotenv
import os

# Load .env file
load_dotenv()

app = Flask(__name__)

# Config from .env or defaults
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL", 
"sqlite:///todos.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

# Database model
class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    done = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, 
nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "done": self.done,
            "created_at": self.created_at.isoformat(),
        }

# Create database tables
with app.app_context():
    db.create_all()

# Routes
@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/todos")
def get_todos():
    todos = Todo.query.order_by(Todo.created_at.desc()).all()
    return jsonify([t.to_dict() for t in todos])

@app.post("/todos")
def create_todo():
    data = request.get_json()
    if not data or not data.get("title"):
        return {"error": "title is required"}, 400
    todo = Todo(title=data["title"], done=bool(data.get("done", False)))
    db.session.add(todo)
    db.session.commit()
    return todo.to_dict(), 201

@app.patch("/todos/<int:todo_id>")
def update_todo(todo_id):
    todo = Todo.query.get(todo_id)
    if not todo:
        return {"error": "not found"}, 404
    data = request.get_json()
    if "title" in data:
        todo.title = data["title"]
    if "done" in data:
        todo.done = bool(data["done"])
    db.session.commit()
    return todo.to_dict()

@app.delete("/todos/<int:todo_id>")
def delete_todo(todo_id):
    todo = Todo.query.get(todo_id)
    if not todo:
        return {"error": "not found"}, 404
    db.session.delete(todo)
    db.session.commit()
    return {"deleted": True, "id": todo_id}

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="127.0.0.1", port=port, debug=True)

