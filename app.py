from dotenv import load_dotenv
import os
from flask import Flask, render_template, request, jsonify
import uuid
import threading
import json

from parsers.bicep import bicep_to_json
from parsers.terraform import terraform_to_json
from agents.security import analyze_security
from agents.cost import analyze_cost
from agents.identity import analyze_identity
from agents.reliability import analyze_reliability
from agents.architect import summarize_results

app = Flask(__name__)
jobs = {}
load_dotenv()
endpoint = os.environ["AZURE_AI_FOUNDRY_ENDPOINT"]

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/review", methods=["POST"])
def review():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
    
    file = request.files["file"]
    
    if file.filename == "":
        return jsonify({"error": "No file selected"}), 400

    file_contents = file.read().decode("utf-8")

    if file.filename.endswith(".bicep"):
        json_data = bicep_to_json(file_contents)
        review_format = "bicep"

    elif file.filename.endswith(".tf"):
        json_data = terraform_to_json(file_contents)
        json_data = json.dumps(json_data)
        review_format = "terraform"

    elif file.filename.endswith(".json"):
        json_data = file_contents
        review_format = "json"

    else:
        return jsonify({"error": "Unsupported file type"}), 400

    job_id = str(uuid.uuid4())

    jobs[job_id] = {
        "messages": [],
        "done": False,
        "score": 0
    }

    thread = threading.Thread(
        target=run_review,
        args=(job_id, json_data, review_format)
    )

    thread.start()

    return jsonify({
        "job_id": job_id
    })


@app.route("/status/<job_id>")
def status(job_id):

    if job_id not in jobs:
        return jsonify({"error": "Job not found"}), 404

    return jsonify(jobs[job_id])


def run_review(job_id, json_data, review_format):

    jobs[job_id]["messages"].append(
        "🔍 Security Review Started"
    )

    security = analyze_security(json_data, review_format, endpoint)

    jobs[job_id]["messages"].append(
        f"✅ Security Review Complete - Score: {security.get('score', 0)}/25"
    )

    jobs[job_id]["messages"].append(
        "💰 Cost Review Started"
    )

    cost = analyze_cost(json_data, review_format, endpoint)

    jobs[job_id]["messages"].append(
        f"✅ Cost Review Complete - Score: {cost.get('score', 0)}/25"
    )

    jobs[job_id]["messages"].append(
        "🔐 Identity Review Started"
    )

    identity = analyze_identity(json_data, review_format, endpoint)

    jobs[job_id]["messages"].append(
        f"✅ Identity Review Complete - Score: {identity.get('score', 0)}/25"
    )

    jobs[job_id]["messages"].append(
        "⚙️ Reliability Review Started"
    )

    reliability = analyze_reliability(json_data, review_format, endpoint)

    jobs[job_id]["messages"].append(
        f"✅ Reliability Review Complete - Score: {cost.get('score', 0)}/25"
    )

    security_score = security.get("score", 0)
    jobs[job_id]["securityScore"] = security_score
    jobs[job_id]["securityIssues"] = security.get("issues", [])
    cost_score = cost.get("score", 0)
    jobs[job_id]["costScore"] = cost_score
    jobs[job_id]["costIssues"] = cost.get("issues", [])
    identity_score = identity.get("score", 0)
    jobs[job_id]["identityScore"] = identity_score
    jobs[job_id]["identityIssues"] = identity.get("issues", [])
    reliability_score = reliability.get("score", 0)
    jobs[job_id]["reliabilityScore"] = reliability_score
    jobs[job_id]["reliabilityIssues"] = reliability.get("issues", [])
    total_score = security_score + cost_score + identity_score + reliability_score
    jobs[job_id]["totalScore"] = total_score

    results = [security, cost, identity, reliability]
    jobs[job_id]["messages"].append(
        "💼 Summary Review Started"
    )

    summary = summarize_results(results, endpoint)
    executive_summary = summary.get("executive_summary", {}) 
    jobs[job_id]["keyRisks"] = executive_summary.get("key_risks", [])
    jobs[job_id]["topArchitecturalRisks"] = executive_summary.get("top_architectural_risks", [])
    jobs[job_id]["businessImpact"] = executive_summary.get("business_impact", "")
    jobs[job_id]["remediationPlan"] = summary.get("remediation_plan", [])

    jobs[job_id]["messages"].append(
        f"✅ Summary Review Complete - Total Score: {total_score}/100"
    )

    jobs[job_id]["done"] = True


if __name__ == "__main__":
    app.run(debug=True)