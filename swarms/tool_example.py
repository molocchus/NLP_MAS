import os
import requests
from dotenv import load_dotenv
import json
import inspect

load_dotenv()

API_KEY = os.getenv("SWARMS_API_KEY")
BASE_URL = "https://api.swarms.world"

headers = {"x-api-key": API_KEY, "Content-Type": "application/json"}


def run_health_check():
    response = requests.get(f"{BASE_URL}/health", headers=headers)
    return response.json()

def get_available_courses_data(json_filepath: str = "oguny.json") -> dict[str, dict[str, str]]:
    """
    Load available courses from a JSON file.

    Args:
        json_filepath (str): Path to the JSON file containing course data.

    Returns:
        list: List of available courses.
    """
    with open(json_filepath, "r", encoding="utf-8") as file:
        courses = json.load(file)
    return courses


def run_single_swarm():
    # Register the tool function in the payload as a stringified code (if API supports code tools)
    # Or, if the API expects a tools list at the top level, move it there.
    # Most likely, you need to provide the function code as a string in a "tools" field.

    # Read the function code from this file

    function_code = inspect.getsource(get_available_courses_data)

    payload = {
        "name": "Test Odczytania Przedmiotów Akademickich",
        "description": "Swarm do testowania odczytu przedmiotów z pliku",
        "agents": [
            {
                "agent_name": "Tester Listy Przedmiotów",
                "description": "Wczytuje i wypisuje listę przedmiotów akademickich z pliku oguny.json w języku polskim",
                "system_prompt": (
                    "Jesteś ekspertem w dziedzinie edukacji akademickiej. "
                    "Wczytaj listę przedmiotów akademickich z pliku oguny.json i wypisz je wszystkie w języku polskim. "
                    "Nie grupuj, nie analizuj, po prostu wypisz jakie przedmioty znalazłeś."
                ),
                "model_name": "gpt-4o",
                "role": "worker",
                "max_loops": 1,
                "max_tokens": 8192,
                "temperature": 0.3,
                "auto_generate_prompt": False,
                "tools_dictionary": [
                    {
                        "type": "function",
                        "function": {
                            "name": "get_available_courses_data",
                            "description": "Wczytuje listę przedmiotów akademickich z pliku oguny.json znajdującego się w tym samym folderze.",
                            "parameters": {
                                "type": "object",
                                "properties": {},
                                "required": [],
                            },
                            "code": function_code,
                        },
                    },
                ],
            },
            {
                "agent_name": "Tester Listy Przedmiotów",
                "description": "Wczytuje i wypisuje listę przedmiotów akademickich z pliku oguny.json w języku polskim",
                "system_prompt": (
                    "Jesteś ekspertem w dziedzinie edukacji akademickiej. "
                    "Wczytaj listę przedmiotów akademickich z pliku oguny.json i wypisz je wszystkie w języku polskim. "
                    "Nie grupuj, nie analizuj, po prostu wypisz jakie przedmioty znalazłeś."
                ),
                "model_name": "gpt-4o",
                "role": "worker",
                "max_loops": 1,
                "max_tokens": 8192,
                "temperature": 0.3,
                "auto_generate_prompt": False,
                "tools_dictionary": [
                    {
                        "type": "function",
                        "function": {
                            "name": "get_available_courses_data",
                            "description": "Wczytuje listę przedmiotów akademickich z pliku oguny.json znajdującego się w tym samym folderze.",
                            "parameters": {
                                "type": "object",
                                "properties": {},
                                "required": [],
                            },
                            "code": function_code,
                        },
                    },
                ],
            },
        ],
        "max_loops": 1,
        "swarm_type": "ConcurrentWorkflow",
        "task": (
            "Wczytaj listę przedmiotów akademickich z pliku oguny.json i wypisz je wszystkie w języku polskim. "
            "Nie grupuj, nie analizuj, po prostu wypisz jakie przedmioty znalazłeś."
        ),
        "output_type": "dict",
    }

    response = requests.post(
        f"{BASE_URL}/v1/swarm/completions",
        headers=headers,
        json=payload,
    )

    print(response)
    print(response.status_code)
    output = response.json()

    return json.dumps(output, indent=4)


if __name__ == "__main__":
    result = run_single_swarm()
    print("Swarm Result:")
    print(result)