from flask import Flask, render_template, jsonify, request
from db import (
    init_db, add_keycap, get_keycaps, update_keycap, delete_keycap,
    store_scrape_results, get_latest_scrape
)
from scraper import scrape_s_craft
import os
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Initialize MongoDB connection
if not init_db():
    logger.error("Failed to initialize database connection")

@app.route('/')
def index():
    """Render the main page."""
    return render_template('index.html')

@app.route('/api/keycaps', methods=['GET', 'POST'])
def handle_keycaps():
    """Handle keycap collection operations."""
    try:
        if request.method == 'GET':
            vendor = request.args.get('vendor')
            keycaps = get_keycaps(vendor)
            return jsonify(keycaps)
        
        elif request.method == 'POST':
            data = request.json
            if not data:
                return jsonify({"error": "No data provided"}), 400
            keycap_id = add_keycap(data)
            return jsonify({"id": keycap_id}), 201
            
    except Exception as e:
        logger.error(f"Error in handle_keycaps: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/keycaps/<keycap_id>', methods=['PUT', 'DELETE'])
def handle_keycap(keycap_id):
    """Handle individual keycap operations."""
    try:
        if request.method == 'PUT':
            updates = request.json
            if not updates:
                return jsonify({"error": "No updates provided"}), 400
            success = update_keycap(keycap_id, updates)
            return jsonify({"success": success})
        
        elif request.method == 'DELETE':
            success = delete_keycap(keycap_id)
            return jsonify({"success": success})
            
    except Exception as e:
        logger.error(f"Error in handle_keycap: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/drops')
def get_drops():
    """Get the latest S-Craft drops."""
    try:
        force_scrape = request.args.get('force', '').lower() == 'true'
        
        if force_scrape:
            # Perform new scrape
            drops = scrape_s_craft()
            if drops:
                store_scrape_results(drops)
        else:
            # Get latest stored scrape
            drops = get_latest_scrape()
            if not drops:
                # If no stored scrape exists, perform new scrape
                drops = scrape_s_craft()
                if drops:
                    store_scrape_results(drops)
        
        return jsonify(drops)
    except Exception as e:
        logger.error(f"Error in get_drops: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/debug/scraper')
def debug_scraper():
    """Debug endpoint to test the scraper directly."""
    try:
        drops = scrape_s_craft()
        if drops:
            store_scrape_results(drops)
        return jsonify({
            "status": "success",
            "count": len(drops),
            "drops": drops[:5]  # Return first 5 items for debugging
        })
    except Exception as e:
        logger.error(f"Error in debug_scraper: {str(e)}")
        return jsonify({
            "status": "error",
            "error": str(e)
        }), 500

if __name__ == '__main__':
    app.run(debug=True, port=5001)
