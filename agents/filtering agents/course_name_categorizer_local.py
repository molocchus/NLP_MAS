#%%
import json
import pandas as pd
from course_ranker_local import CourseRanker
import random
from pathlib import Path
import time
import os

#%%
if __name__ == "__main__":
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer
    from huggingface_hub import login
    from swarm_models.huggingface import HuggingfaceLLM

    # Hugging Face login
    hf_token = ### Your token goes here
    login(token=hf_token)

    # Model path from hugging face
    model_name = "speakleash/Bielik-1.5B-v3.0-Instruct"

    local_llm = HuggingfaceLLM(
        model_id=model_name,
        device="cuda",
        max_length=1000
    )

    test_data = pd.read_csv("oguny_unique1.csv")
    all_names = test_data["Nazwa"].values.tolist()
    categories = test_data["kategorie"].values.tolist()
    features_list = test_data["kategorie"].value_counts().sort_values(ascending=False).index[:4].tolist()

    courses_filename = "oguny.json"
    with open(courses_filename, "r", encoding="utf-8") as file:
        courses_data = json.load(file)

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
                llm=local_llm
            )

            print("############## preferowana:", pref, "kategoria", cat, "##############")

            o = filter_agent1.run(n1)

            elapsed = time.time() - start_time

            hours = int(elapsed // 3600)
            minutes = int((elapsed % 3600) // 60)
            seconds = elapsed % 60

            print(f"############## progress: {i+1}/111, Elapsed time: {hours}h {minutes}m {seconds:.1f}s ##############")

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