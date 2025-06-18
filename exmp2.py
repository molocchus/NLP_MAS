from swarms.structs.agent import Agent
import os
os.environ["GEMINI_API_KEY"] = 'AIzaSyBduble8lpssaKuTpVRBICqrO5sO3k5PUQ'
#swój klucz możesz odbrać tutaj: https://aistudio.google.com/apikey

# Initialize the agent with GPT-4o-mini model
agent = Agent(
    agent_name="Financial-Analysis-Agent",
    system_prompt="Analyze financial situations and provide advice...",
    max_loops=1,
    autosave=True,
    dashboard=False,
    verbose=True,
    saved_state_path="finance_agent.json",
    model_name="gemini/gemini-2.0-flash",
)

# Run your query
out = agent.run(
    "How can I establish a ROTH IRA to buy stocks and get a tax break? What are the criteria?"
)
print(out)
