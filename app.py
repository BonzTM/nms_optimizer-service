# app.py
from flask import Flask, jsonify, request, Response
# from flask_sse import sse
from flask_cors import CORS
from optimizer import optimize_placement, get_tech_tree_json, Grid
from modules import modules
from grid_display import print_grid_compact, print_grid
import logging
import json
import queue
import time

logging.basicConfig(level=logging.INFO)

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

@app.route('/optimize', methods=['POST'])
def optimize_grid():
    """Endpoint to optimize the grid and send status updates via SSE."""
    data = request.get_json()
    ship = data.get("ship")
    tech = data.get('tech')
    player_owned_rewards = data.get('player_owned_rewards')
    print(f"Received request for ship: {ship}, tech: {tech}, player_owned_rewards: {player_owned_rewards}")
    
    if tech is None:
        return jsonify({'error': 'No tech specified'}), 400

    grid_data = data.get('grid')
    if grid_data is None:
        return jsonify({'error': 'No grid specified'}), 400

    grid = Grid.from_dict(grid_data)

    try:
        grid, max_bonus = optimize_placement(grid, ship, modules, tech, player_owned_rewards)
        return jsonify({'grid': grid.to_dict(), 'max_bonus': max_bonus})
    except ValueError as e:
        print_grid_compact(grid)
        return jsonify({'error': str(e)}), 500

@app.route('/tech_tree/<ship_name>')
def get_technology_tree(ship_name):
    """Endpoint to get the technology tree for a given ship."""
    try:
        tree_data = get_tech_tree_json(ship_name)
        return tree_data
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/ship_types', methods=['GET'])
def get_ship_types():
    """Endpoint to get the available ship types and their labels."""
    ship_types = {}
    for ship_key, ship_data in modules.items():
        ship_types[ship_key] = ship_data.get("label")

    print(f"Ship types: {ship_types}")
    return jsonify(ship_types)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)


