#%%
from swarms import Agent

#%%
class CourseCategorizer(Agent):
    """
    This agent is designed to assist with course classification by loading data from provided files and saving information about unique course categories to output files. It inherits from the Agent class and implements methods to extract course data from files.
    
    Attributes:
        base_system_prompt (str): The base system prompt for the agent, which provides instructions for course categorization.
    
    Methods:
        __init__(max_loops, max_tokens, model_name, dynamic_temperature_enabled):
            Initializes the CourseCategorizer agent with specified parameters.
        extract_courses_data(filename):
            Reads course data from the specified file and appends it to the system prompt.
    """
    
    def extract_courses_data(self, filename: str) -> str:
        """
        Reads course data from the specified file and returns its content.
        
        Args:
            filename (str): The name of the file containing course data.
    
        Returns:
            str: The content of the file as a string.
        
        Example:
            >>> content = extract_courses_data("courses.txt")
            >>> print(content)
        """
        
        with open(filename, "r", encoding="utf-8") as file:
            return file.read()
    
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
            system_prompt=f"You are a specialized assistant for course categorization. Analyze input files to identify unique course categories and present them in a JSON format. Come up with up to 5 categories. Data: {self.extract_courses_data(courses_file)}",
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
