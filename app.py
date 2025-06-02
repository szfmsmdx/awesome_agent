# app.py
import logging
from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS 

from config import Config
from llm.llm_agent import Agent
from api.request import InputRequest, AdvancedSearchRequest 
from api.response import ProcessResponse 
from pydantic import ValidationError

CFG = Config()
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

app = Flask(__name__, template_folder='frontend', static_folder='frontend')
CORS(app) 

llm_agent = Agent()

@app.route('/')
def index():
    """Serves the main HTML page."""
    return render_template('index.html')

@app.route('/<path:filename>')
def serve_static(filename):
    """Serves static files like CSS and JS from the frontend directory."""
    return send_from_directory(app.static_folder, filename)

# --- API Endpoints ---
@app.route('/api/get_keywords', methods=['POST'])
def get_keywords_and_suggestions_api():
    """
    API endpoint to get keywords and suggestions from text.
    Takes JSON: {"text": "your input text"}
    Returns JSON: ProcessResponse structure
    """
    try:
        json_data = request.get_json()
        if not json_data:
            return jsonify({"code": 400, "message": ["Bad Request: No JSON data received."]}), 400
        
        input_data = InputRequest(**json_data)
    except ValidationError as e:
        logging.error(f"Validation error for get_keywords: {e.errors()}")
        error_messages = [f"{err['loc'][0] if err['loc'] else 'input'}: {err['msg']}" for err in e.errors()]
        return jsonify({"code": 422, "message": error_messages}), 422
    except Exception as e:
        logging.error(f"Error parsing request for get_keywords: {e}")
        return jsonify({"code": 400, "message": [f"Bad Request: {str(e)}"]}), 400

    logging.info(f"API /get_keywords: Input text: {input_data.text}")
    
    response_data: ProcessResponse = llm_agent.get_keyword(input_data.text)
    
    return jsonify(response_data.model_dump())

@app.route('/api/search_github', methods=['POST'])
def search_github_api():
    """
    API endpoint for advanced GitHub search.
    Takes JSON matching AdvancedSearchRequest model.
    Returns JSON: ProcessResponse structure
    """
    try:
        json_data = request.get_json()
        if not json_data:
            return jsonify({"code": 400, "message": ["Bad Request: No JSON data received."]}), 400

        # Validate input using Pydantic model
        search_params = AdvancedSearchRequest(**json_data)
    except ValidationError as e:
        logging.error(f"Validation error for search_github: {e.errors()}")
        error_messages = [f"{err['loc'][0] if err['loc'] else 'input'}: {err['msg']}" for err in e.errors()]
        return jsonify({"code": 422, "message": error_messages}), 422
    except Exception as e:
        logging.error(f"Error parsing request for search_github: {e}")
        return jsonify({"code": 400, "message": [f"Bad Request: {str(e)}"]}), 400

    logging.info(f"API /search_github: Params: {search_params.model_dump(exclude_none=True)}")

    if not search_params.keywords:
        return jsonify({"code": 400, "message": ["Keywords list cannot be empty."]}), 400

    # Use the global llm_agent instance
    response_data: ProcessResponse = llm_agent.search_keyword(
        keywords=search_params.keywords,
        language=search_params.language,
        min_stars=search_params.min_stars,
        max_stars=search_params.max_stars,
        updated_after=search_params.updated_after,
        exclude_forks=search_params.exclude_forks
    )
    return jsonify(response_data.model_dump())

if __name__ == '__main__':
    app.run(host=CFG.app_host or '0.0.0.0', port=CFG.app_port or 7111, debug=True)