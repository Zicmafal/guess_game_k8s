from flask import Blueprint, jsonify, request, current_app
import hashlib
import base64
import random
import string
from .discover import Guess, WrongAttempt

game_bp = Blueprint('game_bp', __name__)


def hash_password(password, salt):
    """Hash a password with the given salt."""
    hasher = hashlib.sha256()
    hasher.update(f"{salt}{password}".encode('utf-8'))
    return hasher.hexdigest()


@game_bp.route('/create', methods=['POST'])
def create_game():
    password = request.json['password']
    encoded_password = base64.b64encode(password.encode('utf-8')).decode()
    game_id = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
    data = {'password': f"{encoded_password}", 'attempts': []}
    current_app.db.store(game_id, data)
    return jsonify({'game_id': game_id})


@game_bp.route('/guess/<game_id>', methods=['POST'])
def guess(game_id):
    try:
        # Recupera o jogo do banco de dados
        data = current_app.db.retrieve(game_id)
        if data is None:
            current_app.logger.error(f"Game {game_id} not found")
            return jsonify({'error': 'Game not found'}), 404

        # Valida o corpo da requisição
        json_data = request.get_json(silent=True)
        if json_data is None:
            return jsonify({'error': 'Invalid JSON body'}), 400

        # Verifica se o campo 'guess' está presente
        myguess = json_data.get('guess')
        if myguess is None:
            return jsonify({'error': 'Field guess is required'}), 400

        # Decodifica a senha armazenada
        decoded_password = base64.b64decode(data['password']).decode()
        guess_obj = Guess(decoded_password)

        try:
            guess_obj.attempt(myguess)
        except WrongAttempt as e:
            return jsonify({'result': str(e)})

        return jsonify({'result': 'Correct'})

    except KeyError:
        current_app.logger.error(f"Game {game_id} not found")
        return jsonify({'error': 'Game not found'}), 404
