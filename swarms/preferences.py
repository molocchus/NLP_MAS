#%%
import csv
import json

from swarm import run_swarm

#%%
name = "Preferences Collection"
description = "A swarm that classifies academic courses and collects student preferences through interactive questions."

courses = json.load(open("oguny.json", "r", encoding="utf-8"))

task = f"""
    Perform a two-phase academic course analysis process:
    PHASE 1: COURSE CLASSIFICATION
    ------------------------------
    Analyze the course catalog from 'oguny.json' (structure example below) and:
    1. Identify 3-5 meaningful classification dimensions (e.g. by:
       - Subject area (computer science, mathematics, etc.)
       - Difficulty level (beginner, intermediate, advanced)
       - Course type (mandatory, elective, workshop)
       - Teaching style (lecture, lab, project-based)
       - Semester availability
    2. For each dimension, create clear categories in Polish
    3. Map all courses to these categories
    Course structure: {courses}
    PHASE 2: PREFERENCE COLLECTION
    -----------------------------
    Using the created classification schema, generate 8-12 clear multiple-choice questions in Polish to understand:
       - Student's academic level (year of study)
       - Major/faculty
       - Preferred course types
       - Workload tolerance
       - Learning style preferences
       - Interest areas
    REQUIREMENTS:
    - All outputs must be in Polish
    - Questions should be based on actual course attributes from oguny.json
    - Handle both mandatory ('obowiązkowy') and elective ('fakultatywny') courses
    - Include ECTS points consideration in workload questions
"""

#%%
with open("agents.csv", newline='') as csvfile:
    reader = csv.DictReader(csvfile)
    agents = [row for row in reader]

architecture = "SequentialWorkflow"

run_swarm(name, description, task, agents[:-1], architecture)
