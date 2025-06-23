import time
from swarms import Agent

class RecommenderSystem:
    def __init__(
            self, 
            architecture,
            agents: list[Agent],
            max_loops
        ):
        """
        Initialize the recommender system with a specified architecture.
        """
        self.agents = agents
        self.architecture = architecture(
            agents=self.agents,
            max_loops=max_loops
        )

    def run(self, task: str):
        """
        Run the recommender system with the given task.
        """
        start_time = time.time()
        res = self.architecture.run(task)
        end_time = time.time()

        print(f"Execution time: {end_time - start_time:.2f} seconds")
        return res
