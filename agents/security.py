# Before running the sample:
#    pip install azure-ai-projects>=2.1.0

#import os
import json

from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient

def analyze_security(json_data, format):

    AZURE_AI_FOUNDRY_ENDPOINT="https://azure-architect-agent-eastus2.services.ai.azure.com/api/projects/azure-architect-agent-eastus2"

    #print(f"Using Azure AI Foundry endpoint: {os.environ.get('AZURE_AI_FOUNDRY_ENDPOINT')}")

    project_client = AIProjectClient(
        endpoint=AZURE_AI_FOUNDRY_ENDPOINT,
        credential=DefaultAzureCredential(),
    )

    my_agent = "security-agent"
    my_version = "9"

    openai_client = project_client.get_openai_client()

    # Reference the agent to get a response
    response = openai_client.responses.create(
        input=[{"role": "user", "content": f"Analyze the following resources from a {format} file for security issues: {json_data}"}],
        extra_body={"agent_reference": {"name": my_agent, "version": my_version, "type": "agent_reference"}},
    )
    print(f"Response output: {response.output_text}")


    output = response.output_text.strip()

    if output.startswith("```json"):
        output = output[7:]  # remove ```json

    if output.endswith("```"):
        output = output[:-3]  # remove trailing ```

    output = output.strip()

    try:
        data = json.loads(output)
        print("Valid JSON")
    except json.JSONDecodeError as e:
        data = {"error": "Invalid JSON in response", "details": str(e)}
        print(f"Invalid JSON: {e}")
    return data