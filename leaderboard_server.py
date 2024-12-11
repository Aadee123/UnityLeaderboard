from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# SQLite (local testing) or Replace with RDS URL for production
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///leaderboard.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Leaderboard(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False, unique=True)
    score = db.Column(db.Integer, nullable=False)

    def to_dict(self):
        return {"username": self.username, "score": self.score}

@app.before_request
def create_tables():
    if not hasattr(app, 'db_initialized'):
        db.create_all()
        app.db_initialized = True


@app.route('/submit_score', methods=['POST'])
def submit_score():
    data = request.get_json()
    username = data['username']
    score = data['score']

    player = Leaderboard.query.filter_by(username=username).first()
    if player:
        if score > player.score:
            player.score = score
    else:
        player = Leaderboard(username=username, score=score)

    db.session.add(player)
    db.session.commit()
    return jsonify({"message": "Score updated!"}), 200

@app.route('/leaderboard', methods=['GET'])
def get_leaderboard():
    top_scores = Leaderboard.query.order_by(Leaderboard.score.desc()).limit(10).all()
    return jsonify([player.to_dict() for player in top_scores]), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

