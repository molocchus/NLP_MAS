#%%
from swarms import SequentialWorkflow

from agents.course_categorizer import CourseCategorizer
from agents.survey_generator import SurveyGenerator
from agents.survey_conductor import SurveyConductor
from agents.course_recommender import CourseRecommender

#%%
courses_file = "academic_courses.json"

# Create the Agents
agent1 = CourseCategorizer(courses_file)
agent2 = SurveyGenerator()
agent3 = SurveyConductor()
agent4 = CourseRecommender(courses_file)

#%%
# Create the Sequential workflow
workflow = SequentialWorkflow(
  agents=[agent1, agent2, agent3, agent4],
  max_loops=1,
)

#%%
if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()

    # Run the workflow
    workflow.run(f"""
        Read the academic courses from {courses_file} and categorize them in order to generate a survey for students. Collect their preferences and recommend courses based on their responses.
    """)
