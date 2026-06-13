from agents._call_agent import call_agent

def analyze_reliability(json_data, format, endpoint):
    my_agent = "reliability-agent"
    my_version = "10"
    data = call_agent(
        endpoint=endpoint, 
        input=[{"role": "user", "content": f"Analyze the following resources from a {format} file for reliability opportunities: {json_data}"}],
        agent=my_agent,
        version=my_version)
    return data