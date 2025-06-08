from crewai import Agent, Crew, Task, LLM, Process
from crewai.project import CrewBase, agent, task, crew, before_kickoff
from crewai.agents.agent_builder.base_agent import BaseAgent
from crewai_bomb.tools import ExpertTool, DefuserTool
import os
from typing import List
from dotenv import load_dotenv
import asyncio
from game_mcp.game_client import Defuser

# Feel free to import any libraries you need - if needed change requirements.txt
# In this file it also applies to classes and functions :)

async def state_check():
    server_url = "http://localhost:8080"
    defuser_client = Defuser()
    await defuser_client.connect_to_server(server_url)
    result = await defuser_client.run("state")
    await defuser_client.cleanup()
    if "Bomb disarmed!" in result or "Bomb exploded!" in result:
        if "Bomb disarmed!" in result:
            return "WIN"
        elif "Bomb exploded!" in result:
            return "LOSE"
    else:
        return "CONTINUE"


msg = None

# YOUR CODE STARTS HERE
@CrewBase
class DefusalCrew:

    agents: List[BaseAgent]
    tasks: List[Task]

    @agent
    def expert(self) -> Agent:
        global msg
        print(msg)
        return Agent(
            role="Expert",
            goal="Analyze manual and communicate with defuser to help him defuse the bomb.",
            backstory=f"You are exierienced expert in communication with bomb defusers, you are helpful and careful. Defuser said:{msg}",
            tools=[ExpertTool()],
            verbose=True,
            llm=llm,
        )
    @agent
    def defuser(self) -> Agent:
        return Agent(
            role="Defuser",
            goal="Defuse the bomb.",
            backstory="Analyze bomb and communicate with expert to decide what action to take.",
            tools=[DefuserTool()],
            verbose=True,
            llm=llm,
        )


    @task
    def expert_task(self) -> Task:
        return Task(
            description="According to manual and defuser mesage say what should defuser do.",
            expected_output="Defuser should do action or ask:",
            agent= self.expert(),
            tools=[ExpertTool()],
            async_execution=True
        )

    @task
    def defuser_task(self) -> Task:
        return Task(
            description="Cooperate with an expert to determine what action to take. If Expert give you questions answer them properly.",
            expected_output="I should do action or ask:",
            agent= self.defuser(),
            tools=[DefuserTool()],
            async_execution=False
        )

    @crew
    def crew(self) -> Crew:
        return Crew(
            output_log_file="crew_logs.txt",
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
            )


# YOUR CODE ENDS HERE


if __name__ == '__main__':
    # YOUR CODE STARTS HERE
    load_dotenv()  # załaduj zmienne z pliku .env
    api_key = os.getenv("GEMINI_API_KEY")

    llm_args = {"temperature":0.7, "top_p":0.9, "top_k":0.7}

    llm = LLM(
        model="gemini/gemini-2.0-flash",
        temperature=0.7,
    )

    llm:llm

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)


    msg = "I have the bomb what should I do?"
    while loop.run_until_complete(state_check()) == "CONTINUE":
        CrewObject = DefusalCrew()
        crew_output = CrewObject.crew().kickoff()
        msg = crew_output.raw
    # YOUR CODE ENDS HERE
