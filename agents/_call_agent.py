import json
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient

def call_agent(endpoint, input, agent, version):
    project_client = AIProjectClient(
        endpoint=endpoint,
        credential=DefaultAzureCredential(),
    )
    openai_client = project_client.get_openai_client()
    response = openai_client.responses.create(
        input=input,
        extra_body={"agent_reference": {"name": agent, "version": version, "type": "agent_reference"}},
    )
    output = response.output_text.strip()

    if output.startswith("```json"):
        output = output[7:]
    if output.endswith("```"):
        output = output[:-3]
    output = output.strip()

    try:
        data = json.loads(output)
        print("Valid JSON")
    except json.JSONDecodeError as e:
        data = {"error": "Invalid JSON in response", "details": str(e)}
        print(f"Invalid JSON: {e}")
    return data
