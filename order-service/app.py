
from flask import Flask, jsonify

app = Flask(__name__)

orders = [
    {"id": 101, "user_id": 1, "product_id": 1, "quantity": 1},
    {"id": 102, "user_id": 2, "product_id": 2, "quantity": 2}
]

@app.route("/health")
def health():
    return jsonify({"status": "healthy", "service": "order-service"})

@app.route("/orders", strict_slashes=False)
def get_orders():
    return jsonify(orders)

@app.route("/orders/<int:order_id>")
def get_order(order_id):
    order = next((o for o in orders if o["id"] == order_id), None)
    if order:
        return jsonify(order)
    return jsonify({"error": "Order not found"}), 404

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5003)
