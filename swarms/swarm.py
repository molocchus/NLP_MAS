#%%
import os
from dotenv import load_dotenv
import requests
import json
from datetime import datetime

#%%
load_dotenv()

API_KEY = os.getenv("SWARMS_API_KEY")
API_BASE_URL = "https://api.swarms.world"
HEADERS = {
    "x-api-key": API_KEY,
    "Content-Type": "application/json"
}

#%%
def run_swarm(name, description, task, agents, architecture):
    print(f"Running swarm: {name}...")

    swarm_spec = {
        "name": name,
        "description": description,
        "agents": agents,
        "max_loops": 2,
        "swarm_type": architecture,
        "task": task,
        "return_history": True
    }

    response = requests.post(
        f"{API_BASE_URL}/v1/swarm/completions",
        headers=HEADERS,
        json=swarm_spec,
        timeout=300
    )

    response.raise_for_status()
    result = response.json()

    timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    basename = f"{name.replace(' ', '-')}_{timestamp}.json"
    directory = "Outputs"
    os.makedirs(directory, exist_ok=True)
    filename = os.path.join(directory, basename)

    with open(filename, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)

    print(f"Swarm completed successfully.\nOutput saved to {filename}.")
    return result
