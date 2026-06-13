from agents._call_agent import call_agent

def analyze_cost(json_data, format, endpoint):
    my_agent = "cost-agent"
    my_version = "9"
    data = call_agent(
        endpoint=endpoint, 
        input=[{"role": "user", "content": f"Analyze the following resources from a {format} file for cost optimization opportunities: {json_data}"}],
        agent=my_agent,
        version=my_version)
    return data