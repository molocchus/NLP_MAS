#%%
from swarms import Agent
from general_tools import extract_courses_data

#%%
class CourseCategorizer(Agent):
    """
    This agent is designed to assist with course classification by loading data from provided files and saving information about unique course categories to output files. It inherits from the Agent class and implements methods to extract course data from files.
    
    Attributes:
        base_system_prompt (str): The base system prompt for the agent, which provides instructions for course categorization.
    
    Methods:
        __init__(max_loops, max_tokens, model_name, dynamic_temperature_enabled):
            Initializes the CourseCategorizer agent with specified parameters.
    """
    
    def __init__(
            self,
            courses_file,
            max_loops=1, 
            max_tokens=4096, 
            model_name="gemini/gemini-2.0-flash", 
            dynamic_temperature_enabled=True, 
        ):
        super().__init__(
            agent_name="Course-Categorizer-Agent",
            agent_description="An autonomous agent designed to assist with course categorization by loading data from provided files and saving information about unique course categories to output files.",
            system_prompt=f"You are a specialized assistant for course categorization. Analyze input files to identify unique course categories and present them in a JSON format. Come up with up to 5 categories. Data: {extract_courses_data(courses_file)}",
            max_loops=max_loops,
            max_tokens=max_tokens,
            model_name=model_name,
            dynamic_temperature_enabled=dynamic_temperature_enabled,
            output_type="dict-final",
        )
    
#%% 
# Test
if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()

    agent = CourseCategorizer('academic_courses.json')
    agent.run("Read the courses and perform the categorization.")
