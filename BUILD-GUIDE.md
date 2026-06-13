# How I Built The Architecture Reviewer

## What You Need

- Python 3.13
- Azure CLI
- Microsoft Azure Subscription
- Bicep Installed

## Azure Resources and Azure AI Search Setup

1. I created a new resource group in East US 2 called `azure-architect-agent`
2. Create a new Foundry Project called `azure-architect-agent-eastus2`
3. Create a new Azure AI Search resource in Central US called `azure-architect-agent-centralus-search`
4. Inside Foundry under knowledge create a new connection to the Azure AI Search and create a new knowledge based called `azure-best-practices-knowledgebase`.
5. Make sure the model is `gpt-4.1-mini` to be consistent with the agents.
6. Create a new knowledge web source called `azure-best-practices`. Add any links to documentation here for the agents to get knowledge of, in the `Advanced tab > Allowed URLs`.

## Azure Agents Setup

1. Create a new agent called `security-agent` with the `gpt-4.1-mini` model.
2. Add instructions to the agent, can be found [here](./agents/instructions/).
3. In the knowledge section link the knowledgebase `azure-best-practices-knowledgebase`.
4. Test the agent by making a call in the chat tab.
5. If everything is working properly go to the call agent tab and grab the Python code (this is just starter code will update later).
6. Repeat the rest of the agents:
   - cost-agent
   - identity-agent
   - reliability-agent
   - architect-agent

## Frontend Setup

1. The homepage is [here](./templates/index.html) along with the [styles](./static/style.css) and [script](./static/script.js)
2. The script does all the frontend work including showing the statuses and the ability to download the summary

## Backend Setup

1. The backend is built with Python Flask.
2. You will need to create a `.env` file at root directory and include your Azure AI Foundry Endpoint Configuration. This is currently not committed to the repo and is included in the `.gitignore`.

```bash
# Azure AI Foundry Configuration
AZURE_AI_FOUNDRY_ENDPOINT="REPLACE_WITH_YOUR_ENDPOINT"
```

3. The [app.py] is the heart of the project with 2 endpoints:
   - The default route `/` the presents the `index.html` page.
   - The review route `/review` that performs the work of getting the contents of the infrastructure file and passing the contents to each of the agents.
4. If the file is `.json` the contents are not transformed, if the file if either `.tf` or `.bicep` there is a transformation that happens to convert to json so the input is consistent everytime for the agents.
5. Each agent is setup with their own individual file inside the [agents](./agents/) directory and calls the agent using [\_call_agent.py](./agents/_call_agent.py).
6. The jobs is used to show the frontend status progress when one agent finishes and another one begins.

## Running Locally

### 1. Create a Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Run the Application

```bash
python app.py
```

The application will be available at `http://localhost:5000`
