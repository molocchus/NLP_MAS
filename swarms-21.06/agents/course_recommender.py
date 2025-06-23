#%%
from swarms import Agent
from general_tools import extract_courses_data

#%%
class CourseRecommender(Agent):
    """
    Course Recommender Agent
    This agent reads a JSON file containing academic courses and recommends courses based on user preferences collected in a survey. It analyzes the courses and provides a list of recommended courses along with their descriptions.
    
    Attributes:
        courses_file (str): Path to the JSON file containing course data.
        max_loops (int): Maximum number of loops for the agent to run.
        max_tokens (int): Maximum number of tokens for the model response.
        model_name (str): Name of the model to be used for generating responses.
        dynamic_temperature_enabled (bool): Whether to enable dynamic temperature for the model.
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
            agent_name="Course-Recommender-Agent",
            agent_description="""
            This agent reads a JSON file containing academic courses and, based on the preferences collected in a survey, recommends courses that match the user's interests and academic goals. The agent will analyze the courses and provide a list of recommended courses along with their descriptions.
            """,
            system_prompt=f"""
            You are a Course Recommender Agent. Your task is to read a JSON file containing academic courses and recommend courses based on user preferences that were collected in a survey. Your recommendations should be tailored to the user's interests and academic goals. You should recommened up to 5 courses that best match the user's preferences. Here are the courses data:
            {extract_courses_data(courses_file)}
            """,
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

    agent = CourseRecommender("academic_courses.json")
    agent.run("""
        ╭─────────────────── Agent Name Survey-Conductor-Agent [Max Loops: 1 ] ───────────────────╮
        │ Survey-Conductor-Agent: Function 'conduct_survey' result:                               │
        │ {                                                                                       │
        │   "How interested are you in Algebra?": "Not at all interested",                        │
        │   "How interested are you in Chemistry?": "Moderately interested",                      │
        │   "How interested are you in Poetry?": "Moderately interested",                         │
        │   "How interested are you in Prose?": "Moderately interested",                          │
        │   "Which category are you most interested in?": "Science",                              │
        │   "Are there any other subjects or topics you would like to see offered?":              │
        │ "Psychology",                                                                           │
        │   "How interested are you in Geometry?": "Not at all interested",                       │
        │   "How interested are you in Physics?": "Very interested"                               │
        │ }                                                                                       │
        ╰─────────────────────────────────────────────────────────────────────────────────────────╯
    """)
