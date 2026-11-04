
from flask import Flask, jsonify

app = Flask(__name__)

users = [
    {"id": 1, "name": "John", "email": "john@example.com"},
    {"id": 2, "name": "David", "email": "david@example.com"}
]

@app.route("/health")
def health():
    return jsonify({"status": "healthy", "service": "user-service"})

@app.route("/users", strict_slashes=False)
def get_users():
    return jsonify(users)

@app.route("/users/<int:user_id>")
def get_user(user_id):
    user = next((u for u in users if u["id"] == user_id), None)
    if user:
        return jsonify(user)
    return jsonify({"error": "User not found"}), 404

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)
