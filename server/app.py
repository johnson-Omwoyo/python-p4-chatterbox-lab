from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_migrate import Migrate

from models import db, Message

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///app.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

CORS(app)
migrate = Migrate(app, db)
db.init_app(app)


@app.route("/messages", methods=["GET", "POST"])
def handle_messages():
    if request.method == "GET":
        all_messages = Message.query.order_by(Message.created_at).all()
        return jsonify([msg.to_dict() for msg in all_messages]), 200

    if request.method == "POST":
        payload = request.get_json()
        new_message = Message(
            body=payload.get("body"), username=payload.get("username")
        )

        db.session.add(new_message)
        db.session.commit()
        return jsonify(new_message.to_dict()), 201


@app.route("/messages/<int:message_id>", methods=["PATCH", "DELETE"])
def modify_message(message_id):
    message_instance = Message.query.get(message_id)

    if request.method == "PATCH":
        updates = request.get_json()
        for key, value in updates.items():
            setattr(message_instance, key, value)

        db.session.commit()
        return jsonify(message_instance.to_dict()), 200

    if request.method == "DELETE":
        db.session.delete(message_instance)
        db.session.commit()
        return jsonify({"deleted": True}), 200


if __name__ == "__main__":
    app.run(port=5555)
