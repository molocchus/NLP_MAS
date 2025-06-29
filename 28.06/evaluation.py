#%%
import json
import pandas as pd
import time
from typing import Any

from course_name_categorizer import CourseNameCategorizer

#%%
def accuracy(confusion_matrix: dict[str, int]) -> float | None:
    """
    Calculate the accuracy of the classification based on the confusion matrix.

    Parameters:
        confusion_matrix (dict[str, int]): A dictionary containing the counts of True Positives (TP), True Negatives (TN), False Positives (FP), and False Negatives (FN).

    Returns:
        float: The accuracy of the classification.
        OR 
        None: If the total count in the confusion matrix is zero.
    """

    total = sum(confusion_matrix.values())
    if total == 0:
        return None
    
    return (confusion_matrix['TP'] + confusion_matrix['TN']) / total


def precision(confusion_matrix: dict[str, int]) -> float | None:
    """
    Calculate the precision of the classification based on the confusion matrix.

    Parameters:
        confusion_matrix (dict[str, int]): A dictionary containing the counts of True Positives (TP), True Negatives (TN), False Positives (FP), and False Negatives (FN).

    Returns:
        float: The precision of the classification.
        OR 
        None: If the True Positives and False Positives are both zero.
    """

    positives = confusion_matrix['TP'] + confusion_matrix['FP']
    if positives == 0:
        return None
    
    return confusion_matrix['TP'] / positives


def recall(confusion_matrix: dict[str, int]) -> float | None:
    """
    Calculate the recall of the classification based on the confusion matrix.

    Parameters:
        confusion_matrix (dict[str, int]): A dictionary containing the counts of True Positives (TP), True Negatives (TN), False Positives (FP), and False Negatives (FN).

    Returns:
        float: The recall of the classification.
        OR 
        None: If the True Positives and False Negatives are both zero.
    """

    actual_positives = confusion_matrix['TP'] + confusion_matrix['FN']
    if actual_positives == 0:
        return None
    
    return confusion_matrix['TP'] / actual_positives

#%%
def evaluate(
    self, 
    preferred_category: str,
    convergence_threshold: int = 0, # 0-binary
    courses_filename: str = "oguny_unique1.csv",
    how_many_courses: int = 0, # 0-all
    delay_between_requests: int = 1, # seconds
) -> dict[str, Any]:
    """
    Evaluate courses based on a preferred category and a convergence threshold. 
    
    This function runs the course name categorizer for each course in the provided CSV file, checking if the course matches the preferred category based on the convergence threshold.

    Parameters:
        preferred_category (str): The category that the student prefers.
        convergence_threshold (int): The threshold for convergence. If 0, the evaluation is binary (yes/no). If greater than 0, it is numerical (0-100).
        courses_filename (str): The path to the CSV file containing course data.
        how_many_courses (int): The number of courses to evaluate. If 0, all courses are evaluated.
        delay_between_requests (int): The delay between requests to the agent (in seconds).

    Returns:
        dict[str, Any]: A dictionary containing the results for preferred and non-preferred courses, along with evaluation metrics.

    Raises:
        ValueError: If parameters' values are not valid, or if the agent's response is empty or not in the expected format.
    """

    print(f"""\n
          –––––––––––––––––––––––––––––––––––––––––
          Evaluating courses for preferred category: {preferred_category}
          with convergence threshold: {convergence_threshold}
          –––––––––––––––––––––––––––––––––––––––––
    \n""")

    # Check if the number of courses to evaluate is valid
    if how_many_courses < 0:
        raise ValueError("Number of courses to evaluate must be non-negative.")

    # Ensure that the convergence threshold is a number from 0 to 100
    if convergence_threshold < 0:
        raise ValueError("Convergence threshold must be non-negative.")
    if convergence_threshold >= 100:
        raise ValueError("Convergence threshold must be smaller than 100.")
    
    # Ensure that the convergence threshold is compatible with the binary_answer setting
    if convergence_threshold == 0 and self.binary_answer is False:
        raise ValueError("Convergence threshold is 0, but binary_answer is set to False. Set binary_answer to True for binary evaluation.")
    if convergence_threshold > 0 and self.binary_answer is True:
        raise ValueError("Convergence threshold is greater than 0, but binary_answer is set to True. Set binary_answer to False for numerical evaluation.")

    df = pd.read_csv(
        courses_filename,
        on_bad_lines='warn'
    )
    if df.empty or len(df) == 0:
        raise ValueError(f"CSV file '{courses_filename}' is empty or not found.")

    results_for_preferred = {}
    results_for_non_preferred = {}
    courses_count = 0

    for course in df.to_dict(orient='records'):
        if how_many_courses > 0 and courses_count >= how_many_courses:
            break
        
        courses_count += 1
        course_name = course['Nazwa']

        agent_result_raw = self.run(
            course_name=course_name,
            student_preferences={
                'preferowana tematyka zajęć': preferred_category,
            }
        )
        if not agent_result_raw:
            raise ValueError(f"Agent's response for course '{course_name}' is empty.")
        if delay_between_requests > 0:
            print(f"Delay: {delay_between_requests} second(s)...")
            time.sleep(delay_between_requests)

        # Get the raw convergence value from the agent's response
        course_convergence_raw = agent_result_raw['zgodność tematyki zajęć']

        if convergence_threshold == 0:
            # If the convergence threshold is 0, we expect a binary answer ('tak' or 'nie')
            course_convergence = course_convergence_raw.strip().lower() == 'tak'
        else:
            # If the raw convergence value is not a number, try to convert it to an integer
            if not isinstance(course_convergence_raw, (int, float)):
                course_convergence_raw = int(course_convergence_raw.strip())

            # Check if the raw convergence value is greater than or equal to the threshold (which would mean that the course matches the preferred category)
            course_convergence = course_convergence_raw >= convergence_threshold

        # Create a confusion matrix that will be used to calculate evaluation metrics
        confusion_matrix = {
            'TP': 0,  # True Positives
            'TN': 0,  # True Negatives
            'FP': 0,  # False Positives
            'FN': 0   # False Negatives
        }

        # If the course is in the preferred category, store the result in results_for_preferred (otherwise in results_for_non_preferred)
        if preferred_category in course['kategorie']:
            results_for_preferred[course_name] = course_convergence
            if course_convergence:
                confusion_matrix['TP'] += 1
            else:
                confusion_matrix['FN'] += 1
        else:
            results_for_non_preferred[course_name] = course_convergence
            if course_convergence:
                confusion_matrix['FP'] += 1
            else:
                confusion_matrix['TN'] += 1

    # Calculate evaluation metrics based on the confusion matrix
    evaluation_metrics = {
        'preferred_courses_count': len(results_for_preferred),
        'non_preferred_courses_count': len(results_for_non_preferred),
        'accuracy': accuracy(confusion_matrix),
        'precision': precision(confusion_matrix),
        'recall': recall(confusion_matrix),
    }

    print("Evaluation Metrics:")
    print(json.dumps(evaluation_metrics, indent=4, ensure_ascii=False))

    return {
        'results_for_preferred': results_for_preferred,
        'results_for_non_preferred': results_for_non_preferred,
        'metrics': evaluation_metrics
    }

#%%
CourseNameCategorizer.evaluate = evaluate

if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()

    preferred_category = "Programowanie"
    convergence_threshold = 0

    categorizer = CourseNameCategorizer(
        binary_answer=(convergence_threshold == 0),
    )

    results = categorizer.evaluate(
        preferred_category=preferred_category,
        convergence_threshold=convergence_threshold,
        courses_filename="oguny_unique1.csv",
        how_many_courses=10,  # Limit to 10 for testing purposes
    )

    print(f"\nResults for preferred category '{preferred_category}':")
    print(json.dumps(results, indent=4, ensure_ascii=False))
