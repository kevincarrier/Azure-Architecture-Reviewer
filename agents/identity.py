from agents._call_agent import call_agent

def analyze_identity(json_data, format, endpoint):
    my_agent = "identity-agent"
    my_version = "8"
    data = call_agent(
        endpoint=endpoint, 
        input=[{"role": "user", "content": f"Analyze the following resources from a {format} file for identity management opportunities: {json_data}"}],
        agent=my_agent,
        version=my_version)
    return data