from crewai.tools import BaseTool
from pydantic import ConfigDict
from game_mcp.game_client import Defuser, Expert
import asyncio

# Feel free to import any libraries you need - if needed change requirements.txt
# In this file it also applies to classes and functions :)


class DefuserTool(BaseTool):
    # YOUR CODE STARTS HERE
    name: str = "Perform an action, avaiable commands: action commands (starts with: cut, press, hold, release), help, state"
    description: str = "Tool for the defuser, to interact with the game"

    model_config = ConfigDict(extra='ignore')

    def _run(self, argument: str) -> str:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        async def get_state(argument: str) -> str:
            server_url = "http://localhost:8080"
            defuser_client = Defuser()
            await defuser_client.connect_to_server(server_url)
            if argument.startswith(("cut", "press", "hold", "release", "help", "state")):
                bomb_state = await defuser_client.run(argument)
            else:
                bomb_state = await defuser_client.run("state")
            await defuser_client.cleanup()
            return bomb_state

        return loop.run_until_complete(get_state(argument))

    # YOUR CODE ENDS HERE


class ExpertTool(BaseTool):
    # YOUR CODE STARTS HERE
    name: str = "Get manual"
    description: str = "Tool to get manual for the expert"

    model_config = ConfigDict(extra='ignore')

    def _run(self) -> str:

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        async def get_manual():
            server_url = "http://localhost:8080"
            expert_client = Expert()
            await expert_client.connect_to_server(server_url)
            manual = await expert_client.run()
            await expert_client.cleanup()
            return manual

        return loop.run_until_complete(get_manual())

    # YOUR CODE ENDS HERE
