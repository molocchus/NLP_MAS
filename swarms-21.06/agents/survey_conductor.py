#%%
from swarms import Agent

#%%
class SurveyConductor(Agent):
    """
    This agent is designed to conduct a survey from questions and possible answers provided by the SurveyGenerator agent.
    """
    
    def conduct_survey(self, questions_data: dict[str, list[str]]) -> dict[str, str]:
        """
        Conducts an interactive survey based on the provided questions and possible answers.

        Args:
            questions_data (dict[str, list[str]]): 
                A dictionary where each key is a question (str) and each value is a list of possible answers (list of str).

        Returns:
            dict[str, str]: 
                A dictionary mapping each question to the answer selected by the user.
        
        Raises:
            ValueError: 
                If the questions_data is empty, a question is not a string or is empty, 
                or answers are not provided as a list.
        
        Example:
            >>> questions_data = { \
                "What is your favorite color?": ["Red", "Blue", "Green"], \
                "What is your preferred mode of transport?": ["Car", "Bicycle", "Walking"] \
            }
            >>> survey_answers = conduct_survey(questions_data)
            >>> print(survey_answers)
            {'What is your favorite color?': 'Blue', \
             'What is your preferred mode of transport?': 'Car'}
        """

        if not questions_data:
            raise ValueError("No questions data provided for the survey.")
        
        answers_data: dict[str, str] = {}
        question_number = 0

        for question, answers in questions_data.items():
            if not isinstance(question, str):
                raise ValueError("Each question must be a string.")
            if not question.strip():
                raise ValueError("Question cannot be empty.")
            
            if not isinstance(answers, list):
                raise ValueError(f"Answers for question '{question}' must be a list.")
            
            question_number += 1
            answer_char = max_answer_char = 97  # ASCII value for 'a'

            print(f"Question {question_number}. {question}")
            
            for answer in answers:
                if not isinstance(answer, str):
                    raise ValueError(f"Each answer for question '{question}' must be a string.")
                if not answer.strip():
                    raise ValueError(f"Answer cannot be empty for question '{question}'.")
                
                print(f"\t{chr(answer_char)}) {answer}")
                max_answer_char = answer_char
                answer_char += 1
            
            user_input = None
            while user_input is None:
                if not answers:
                    user_input = input(f"Please enter your answer (open-ended): ").strip()
                    if not user_input:
                        print(f"Input cannot be empty for question '{question}'.")
                        continue
                
                else:
                    user_input = input("Please select an answer (a, b, c, ...): ").strip().lower()
                    
                    if not user_input:
                        print(f"Input cannot be empty")
                        continue
                    if len(user_input) != 1:
                        print(f"Input must be a single character for question '{question}'.")
                        user_input = None
                        continue
                    if ord(user_input) < 97 or ord(user_input) > max_answer_char:
                        print(f"Invalid input '{user_input}' for question '{question}'. Please select a valid answer.")
                        user_input = None
                        continue
            
            if not answers:
                answers_data[question] = user_input
                print(f"You answered: {user_input}\n")
            else:
                answer_index = ord(user_input) - 97  # Convert 'a' to 0, 'b' to 1, etc.
                answers_data[question] = answers[answer_index]
                print(f"You selected: {answers[answer_index]}\n")
            
        return answers_data
    
    def __init__(
            self,
            max_loops=1, 
            max_tokens=4096, 
            model_name="gemini/gemini-2.0-flash", 
            dynamic_temperature_enabled=True
        ):
        super().__init__(
            agent_name="Survey-Conductor-Agent",
            agent_description="This agent conducts a survey based on questions and possible answers provided.",
            system_prompt="""
                    You are a survey conductor agent. Your task is to conduct a survey based on the questions and possible answers provided to you. 
                    You will have to transform the questions and answers into a specific format that can be used as an argument for the conduct_survey method. 
                    You will then call the conduct_survey method to interactively ask the user the questions and collect their answers, and show the output that the method returns.
                """,
            max_loops=max_loops,
            max_tokens=max_tokens,
            model_name=model_name,
            dynamic_temperature_enabled=dynamic_temperature_enabled,
            output_type="dict-final",
            tools=[self.conduct_survey]
        )

#%%
# Test
if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()

    conductor = SurveyConductor()
    conductor.run("""
        ╭─────────────────── Agent Name Survey-Generator-Agent [Max Loops: 1 ] ───────────────────╮
        │ Survey-Generator-Agent: ```json                                                         │
        │  {                                                                                      │
        │   "surveyTitle": "Course Preference Survey",                                            │
        │   "introduction": "This survey aims to gather your preferences regarding different      │
        │ academic subjects to help us tailor course offerings to your interests.",               ���
        │   "sections": [                                                                         │
        │    {                                                                                    │
        │     "sectionTitle": "Mathematics",                                                      │
        │     "description": "Please indicate your interest in the following mathematics          │
        │ subjects.",                                                                             │
        │     "questions": [                                                                      │
        │      {                                                                                  │
        │       "questionType": "rating",                                                         │
        │       "questionText": "How interested are you in Algebra?",                             │
        │       "options": [                                                                      │
        │        "Not at all interested",                                                         │
        │        "Slightly interested",                                                           │
        │        "Moderately interested",                                                         │
        │        "Very interested",                                                               │
        │        "Extremely interested"                                                           │
        │       ]                                                                                 │
        │      },                                                                                 │
        │      {                                                                                  │
        │       "questionType": "rating",                                                         │
        │       "questionText": "How interested are you in Geometry?",                            │
        │       "options": [                                                                      │
        │        "Not at all interested",                                                         │
        │        "Slightly interested",                                                           │
        │        "Moderately interested",                                                         │
        │        "Very interested",                                                               │
        │        "Extremely interested"                                                           │
        │       ]                                                                                 │
        │      }                                                                                  │
        │     ]                                                                                   │
        │    },                                                                                   │
        │    {                                                                                    │
        │     "sectionTitle": "Science",                                                          │
        │     "description": "Please indicate your interest in the following science subjects.",  │
        │     "questions": [                                                                      │
        │      {                                                                                  │
        │       "questionType": "rating",                                                         │
        │       "questionText": "How interested are you in Physics?",                             │
        │       "options": [                                                                      │
        │        "Not at all interested",                                                         │
        │        "Slightly interested",                                                           │
        │        "Moderately interested",                                                         │
        │        "Very interested",                                                               │
        │        "Extremely interested"                                                           │
        │       ]                                                                                 │
        │      },                                                                                 │
        │      {                                                                                  │
        │       "questionType": "rating",                                                         │
        │       "questionText": "How interested are you in Chemistry?",                           │
        │       "options": [                                                                      │
        │        "Not at all interested",                                                         │
        │        "Slightly interested",                                                           │
        │        "Moderately interested",                                                         │
        │        "Very interested",                                                               │
        │        "Extremely interested"                                                           │
        │       ]                                                                                 │
        │      }                                                                                  │
        │     ]                                                                                   │
        │    },                                                                                   │
        │    {                                                                                    │
        │     "sectionTitle": "Literature",                                                       │
        │     "description": "Please indicate your interest in the following literature           │
        │ subjects.",                                                                             │
        │     "questions": [                                                                      │
        │      {                                                                                  │
        │       "questionType": "rating",                                                         │
        │       "questionText": "How interested are you in Poetry?",                              │
        │       "options": [                                                                      │
        │        "Not at all interested",                                                         │
        │        "Slightly interested",                                                           │
        ��        "Moderately interested",                                                         │
        │        "Very interested",                                                               │
        │        "Extremely interested"                                                           │
        │       ]                                                                                 │
        │      },                                                                                 │
        │      {                                                                                  │
        │       "questionType": "rating",                                                         │
        │       "questionText": "How interested are you in Prose?",                               │
        │       "options": [                                                                      │
        │        "Not at all interested",                                                         │
        │        "Slightly interested",                                                           │
        │        "Moderately interested",                                                         │
        │        "Very interested",                                                               │
        │        "Extremely interested"                                                           │
        │       ]                                                                                 │
        │      }                                                                                  │
        │     ]                                                                                   │
        │    },                                                                                   │
        │    {                                                                                    │
        │     "sectionTitle": "General Preferences",                                              │
        │     "description": "Please answer the following questions about your general            │
        │ preferences.",                                                                          │
        │     "questions": [                                                                      │
        │      {                                                                                  │
        │       "questionType": "multipleChoice",                                                 │
        │       "questionText": "Which category are you most interested in?",                     │
        │       "options": [                                                                      │
        │        "Mathematics",                                                                   │
        │        "Science",                                                                       │
        │        "Literature"                                                                     │
        │       ]                                                                                 │
        │      },                                                                                 │
        │      {                                                                                  │
        │       "questionType": "openEnded",                                                      │
        │       "questionText": "Are there any other subjects or topics you would like to see     │
        │ offered?"                                                                               │
        │      }                                                                                  │
        │     ]                                                                                   │
        │    }                                                                                    │
        │   ],                                                                                    │
        │   "closingMessage": "Thank you for completing this survey. Your feedback is valuable!"  │
        │  }                                                                                      │
        │  ```                                                                                    │
        ╰────────────────────────────────────────────────────��────────────────────────────────────╯
    """)
