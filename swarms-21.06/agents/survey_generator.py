#%%
from swarms import Agent

#%%
class SurveyGenerator(Agent):
    """
    This agent is designed to assist with survey generation by loading data from provided files and saving information about unique course categories to output files. It inherits from the Agent class and implements methods to extract course data from files.

    Methods:
        __init__(max_loops, max_tokens, model_name, dynamic_temperature_enabled):
            Initializes the SurveyGenerator agent with specified parameters.
        load_course_categories(filename):
            Reads course category data from the specified file and appends it to the system prompt.
    """

    def __init__(
            self, 
            max_loops=1, 
            max_tokens=4096, 
            model_name="gemini/gemini-2.0-flash", 
            dynamic_temperature_enabled=True, 
        ):
        super().__init__(
            agent_name="Survey-Generator-Agent",
            agent_description="An autonomous agent designed to assist with survey generation based on the course categorisation data, generating questions for students to collect their preferences.",
            system_prompt=f"You are a Survey Generator agent. Your task is to assist with survey generation based on the course categorisation data. You will generate questions for students to collect their preferences, in a JSON format.",
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

    survey_generator = SurveyGenerator()
    survey_generator.run("""
        CourseCategorizer: 
            Category 1: Mathematics
                Subjects:
                    - Algebra
                    - Geometry
            Category 2: Science
                Subjects:
                    - Physics
                    - Chemistry
            Category 3: Literature
                Subjects:
                    - Poetry
                    - Prose
        """)
