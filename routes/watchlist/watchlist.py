"""
routes/watchlist.py — CineLog (feature/watchlist branch)

Endpoints for the watchlist feature.
"""

from flask import Blueprint, jsonify, request

#changed import name from save_to_watchlist to add_to_watchlist
from services.watchlist_service import add_to_watchlist, get_watchlist
from services.collection_service import FilmNotFoundError

watchlist_bp = Blueprint("watchlist", __name__)


@watchlist_bp.route("/<user_id>", methods=["GET"])
def view_watchlist(user_id):
    """GET /watchlist/<user_id> — Return the user's watchlist."""
    films = get_watchlist(user_id)
    return jsonify(films)


@watchlist_bp.route("/<user_id>/add", methods=["POST"])
def add_film(user_id, film_id):
    """
    POST /watchlist/<user_id>/add

    Body: { "film_id": <UUID string > }
    """
    data = request.get_json()
    if not data or "film_id" not in data:
        return jsonify({"error": "film_id is required"}), 400

#changed from save_to_watchlist to add_to_watchlist in accordance with def name change 
    entry = add_to_watchlist(user_id=user_id, film_id=data["film_id"])
    return jsonify(entry.to_dict()), 201
