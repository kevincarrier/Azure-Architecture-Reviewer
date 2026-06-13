from agents._call_agent import call_agent

def analyze_security(json_data, format, endpoint):
    my_agent = "security-agent"
    my_version = "12"
    data = call_agent(
        endpoint=endpoint, 
        input=[{"role": "user", "content": f"Analyze the following resources from a {format} file for security issues: {json_data}"}],
        agent=my_agent,
        version=my_version)
    return data