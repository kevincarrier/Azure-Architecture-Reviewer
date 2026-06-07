"""
Flask Application - Main Entry Point
"""
from flask import Flask, render_template, request, jsonify
import os

from parsers.bicep import bicep_to_json
from parsers.terraform import terraform_to_json

app = Flask(__name__)
app.config['DEBUG'] = True

@app.route('/')
def index():
    """Home page route"""
    return render_template('index.html')

@app.route('/review', methods=['POST'])
def review():
    """Review page route"""
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    file_contents = file.read().decode('utf-8')
    if file.filename.endswith('.bicep'):
        json_data = bicep_to_json(file_contents)
    elif file.filename.endswith('.tf'):
        json_data = terraform_to_json(file_contents)
    elif file.filename.endswith('.json'):
        json_data = file_contents
    else:
        return jsonify({'error': 'Unsupported file type'}), 400
    #html_response = f'''
    #<div class="success">
    #    <h3>File uploaded successfully!</h3>
    #    {json.dumps(json_data, indent=2)}
    #</div>
    #'''
    return jsonify({'message': json_data}), 200

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
