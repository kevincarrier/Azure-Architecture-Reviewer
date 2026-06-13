from agents._call_agent import call_agent

def summarize_results(results, endpoint):
    my_agent = "architect-agent"
    my_version = "10"
    data = call_agent(
        endpoint=endpoint, 
        input=[{"role": "user", "content": f"{results}"}],
        agent=my_agent,
        version=my_version)
    return data