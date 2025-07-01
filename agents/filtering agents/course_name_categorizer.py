#%%
import json
import pandas as pd
from course_ranker import CourseRanker
import random
from pathlib import Path
import time
import os

#%%
if __name__ == "__main__":
    import torch

    os.environ["OPENAI_API_KEY"] = ### Your token goes here

    model_name = "gpt-4o-mini"

    test_data = pd.read_csv("oguny_unique1.csv")
    all_names = test_data["Nazwa"].values.tolist()
    categories = test_data["kategorie"].values.tolist()

    courses_filename = "oguny.json"
    with open(courses_filename, "r", encoding="utf-8") as file:
        courses_data = json.load(file)

    features_list = test_data["kategorie"].value_counts().sort_values(ascending=False).index[:4].tolist()

    start_time = time.time()

    Results = {}

    feature = "Tematyka"
    for pref in features_list:
        Results[pref] = {}

        survey_data = {
            "Preferowana tematyka zajęć": pref,
        }

        for i, (n1, cat) in enumerate(zip(all_names, categories)):
            filter_agent1 = CourseRanker(
                survey_data,
                courses_filename,
                # llm=local_llm
                model_name = model_name
            )

            print("############## preferowana:", pref, "kategoria", cat, "##############")

            o = filter_agent1.run(n1)

            elapsed = time.time() - start_time

            hours = int(elapsed // 3600)
            minutes = int((elapsed % 3600) // 60)
            seconds = elapsed % 60

            print(f"############## progress: {i+1}, Elapsed time: {hours}h {minutes}m {seconds:.1f}s ##############")

            res1 = o['zgodność tematyki zajęć']
            res2 = o['prawidłowość przedmiotu']
            print(res1)
            Results[pref][n1] = [res1, res2, cat]

        output_path = Path("output")
        output_path.mkdir(exist_ok=True)
        with open(f"output/scores_{pref}.json", "w", encoding="utf-8") as file:
            json.dump(Results[pref], file, ensure_ascii=False, indent=2)

with open(f"output/scores.json", "w", encoding="utf-8") as file:
    json.dump(Results, file, ensure_ascii=False, indent=2)