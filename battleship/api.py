import http

import flask

from battleship.models import Game

app = flask.Flask(__name__)

# Global game instance
game = Game()


@app.route('/battleship', methods=['POST'])
def create_battleship_game():
    """Create a new battleship game with the specified ships."""
    data = flask.request.get_json()
    
    if not data or 'ships' not in data:
        return flask.jsonify({'error': 'Missing ships data'}), http.HTTPStatus.BAD_REQUEST
    
    success, error = game.create_game(data['ships'])
    
    if not success:
        return flask.jsonify({'error': error}), http.HTTPStatus.BAD_REQUEST
    
    return flask.jsonify({}), http.HTTPStatus.OK


@app.route('/battleship', methods=['PUT'])
def shot():
    """Process a shot at the specified coordinates."""
    data = flask.request.get_json()
    
    if not data or 'x' not in data or 'y' not in data:
        return flask.jsonify({'error': 'Missing coordinates'}), http.HTTPStatus.BAD_REQUEST
    
    result, error = game.process_shot(data['x'], data['y'])
    
    if error:
        return flask.jsonify({'error': error}), http.HTTPStatus.BAD_REQUEST
    
    return flask.jsonify({'result': result.value}), http.HTTPStatus.OK


@app.route('/battleship', methods=['DELETE'])
def delete_battleship_game():
    """Delete the current game."""
    game.delete_game()
    return flask.jsonify({}), http.HTTPStatus.OK
