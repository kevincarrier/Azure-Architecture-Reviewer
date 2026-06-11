"""
Flask Application - Main Entry Point
"""
from flask import Flask, render_template, request, jsonify
import os
import json
import time

from parsers.bicep import bicep_to_json
from parsers.terraform import terraform_to_json
from agents.security import analyze_security
from agents.cost import analyze_cost
from agents.identity import analyze_identity
from agents.reliability import analyze_reliability

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
        format = 'bicep'
    elif file.filename.endswith('.tf'):
        json_data = terraform_to_json(file_contents)
        json_data = json.dumps(json_data)  # Convert dict to JSON string for analysis
        format = 'terraform'
    elif file.filename.endswith('.json'):
        json_data = file_contents
        format = 'json'
    else:
        return jsonify({'error': 'Unsupported file type'}), 400
    
    render_template(
        "report.html", 
        loading_message="🔍 Security Agent is reviewing Azure resources...", 
        score=0)
    security_output = analyze_security(json_data, format)
    security_score = security_output.get("score", 0)
    render_template(
        "report.html", 
        loading_message=" ✅ Security analysis complete. 🔍 Cost Agent is reviewing Azure resources...", 
        )
    cost_output = analyze_cost(json_data, format)
    cost_score = cost_output.get("score", 0)
    render_template(
        "report.html", 
        loading_message="✅ Cost analysis complete. 🔍 Identity Agent is reviewing Azure resources...", 
        )
    identity_output = analyze_identity(json_data, format)
    identity_score = identity_output.get("score", 0)
    render_template(
        "report.html", 
        loading_message="✅ Identity analysis complete. 🔍 Reliability Agent is reviewing Azure resources...", 
        )
    reliability_output = analyze_reliability(json_data, format)
    reliability_score = reliability_output.get("score", 0)
    render_template(
        "report.html",
        loading_message="✅ Reliability analysis complete. Finalizing report..."
    )
    time.sleep(2)  # Simulate finalization delay

    return render_template(
        "report.html",
        loading_message="",
        score=security_score + cost_score + identity_score + reliability_score,
        security_score=security_output.get("score"),
        security_issues=security_output.get("resources", []),
        cost_score=cost_output.get("score"),
        cost_issues=cost_output.get("resources", []),
        identity_score=identity_output.get("score"),
        identity_issues=identity_output.get("resources", []),
        reliability_score=reliability_output.get("score"),
        reliability_issues=reliability_output.get("resources", [])
    )

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
