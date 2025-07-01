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
    from transformers import AutoModelForCausalLM, AutoTokenizer
    # from huggingface_hub import login
    # from swarm_models.huggingface import HuggingfaceLLM
    #
    # # Hugging Face login
    # hf_token = ### Your token goes here
    # login(token=hf_token)
    #
    # # Model path from hugging face
    # model_name = "speakleash/Bielik-1.5B-v3.0-Instruct"
    #
    # local_llm = HuggingfaceLLM(
    #     model_id=model_name,
    #     device="cuda",
    #     max_length=2000
    # )

    os.environ["OPENAI_API_KEY"] = ### Your token goes here

    model_name = "gpt-4.1-nano"

    test_data = pd.read_csv("oguny_unique1.csv")
    all_names = test_data["Nazwa"].values.tolist()

    courses_filename = "oguny.json"
    with open(courses_filename, "r", encoding="utf-8") as file:
        courses_data = json.load(file)

    features_dict = {
        "Tryb": ['zdalnie', 'mieszany: w sali i zdalnie', 'w sali'],
        "Kryteria": ['Esej/praca pisemna', 'Obecność/aktywność', 'Test/egzamin'],
        "Tematyka": ['Języki i kultury świata', 'Historia i archeologia', 'Socjologia i antropologia']
    }

    features_names = {}
    for features in features_dict:
        for feature in features_dict[features]:
            if features == "Tryb":
                features_names[feature] = test_data['Nazwa'].loc[test_data['Tryb'] == feature].values.tolist()
            elif features == "Kryteria":
                features_names[feature] = test_data['Nazwa'].loc[test_data[feature] == 1].values.tolist()
            elif features == "Tematyka":
                features_names[feature] = test_data['Nazwa'].loc[test_data['kategorie'] == feature].values.tolist()

    set1 = set(features_names['zdalnie']) & set(features_names['Test/egzamin']) & set(
        features_names['Języki i kultury świata'])
    set2 = set(features_names['mieszany: w sali i zdalnie']) & set(features_names['Test/egzamin']) & set(
        features_names['Historia i archeologia'])
    set3 = set(features_names['w sali']) & set(features_names['Test/egzamin']) & set(
        features_names['Języki i kultury świata'])

    features_names["w1"] = list(set1)
    features_names["w2"] = list(set2)
    features_names["w3"] = list(set3)

    start_time = time.time()

    Results = {}
    for i, feature in enumerate(['Tryb', 'Kryteria', 'Tematyka', 'wszystkie']):


        Results[feature] = {}

        if feature != "wszystkie":
            preferences = features_dict[feature]
        else:
            preferences = ['w1', 'w2', 'w3']

        for pref in preferences:
            survey_data = {
                "Preferowana tematyka zajęć": "nie mam preferencji",
                "Preferowany tryb prowadzenia zajęć": "nie mam preferencji",
                "Preferowany rodzaj zaliczenia": "nie mam preferencji",
            }

            if feature != "wszystkie":
                if feature == 'Tryb':
                    survey_data["Preferowany tryb prowadzenia zajęć"] = pref
                elif feature == 'Kryteria':
                    survey_data["Preferowany rodzaj zaliczenia"] = pref
                elif feature == 'Tematyka':
                    survey_data["Preferowana tematyka zajęć"] = pref
            else:
                if pref == 'w1':
                    survey_data["Preferowany tryb prowadzenia zajęć"] = 'zdalnie'
                    survey_data["Preferowany rodzaj zaliczenia"] = 'Test/egzamin'
                    survey_data["Preferowana tematyka zajęć"] = 'Języki i kultury świata'
                elif pref == 'w2':
                    survey_data["Preferowany tryb prowadzenia zajęć"] = 'mieszany: w sali i zdalnie'
                    survey_data["Preferowany rodzaj zaliczenia"] = 'Test/egzamin'
                    survey_data["Preferowana tematyka zajęć"] = 'Historia i archeologia'
                elif pref == 'w3':
                    survey_data["Preferowany tryb prowadzenia zajęć"] = 'w sali'
                    survey_data["Preferowany rodzaj zaliczenia"] = 'Test/egzamin'
                    survey_data["Preferowana tematyka zajęć"] = 'Języki i kultury świata'


            pref_names = features_names[pref]
            contr_names = list(set(all_names) - set(pref_names))
            pref_sample = random.choices(pref_names, k=10)
            contr_sample = random.choices(contr_names, k=10)

            Results[feature][pref] = {}

            for i, (n1, n2) in enumerate(zip(pref_sample, contr_sample)):
                ranker_agent1 = CourseRanker(
                    survey_data,
                    courses_filename,
                    # llm=local_llm
                    model_name = model_name
                )
                ranker_agent2 = CourseRanker(
                    survey_data,
                    courses_filename,
                    # llm=local_llm
                    model_name = model_name
                )

                course_names = [n1, n2]
                o1 = ranker_agent1.run(n1)
                o2 = ranker_agent2.run(n2)
                # o1 = {'zgodność trybu prowadzenia zajęć':1, 'zgodność rodzaju zaliczenia':1, 'zgodność tematyki zajęć':1}
                # o2 = {'zgodność trybu prowadzenia zajęć':1, 'zgodność rodzaju zaliczenia':1, 'zgodność tematyki zajęć':1}

                elapsed = time.time() - start_time

                hours = int(elapsed // 3600)
                minutes = int((elapsed % 3600) // 60)
                seconds = elapsed % 60

                print(f"progress: {i+1}/10, Elapsed time: {hours}h {minutes}m {seconds:.1f}s")
                print(feature, pref)
                print("Names:", n1, "###", n2)

                if feature != "wszystkie":
                    if o1['nazwa przedmiotu'] == 'Błąd' or o2['nazwa przedmiotu'] == 'Błąd':
                        Results[feature][pref][n1 + "_" + n2] = 'błąd'
                    else:
                        if feature == 'Tryb':
                            res1 = o1['zgodność trybu prowadzenia zajęć']
                            res2 = o2['zgodność trybu prowadzenia zajęć']
                        elif feature == 'Kryteria':
                            res1 = o1['zgodność rodzaju zaliczenia']
                            res2 = o2['zgodność rodzaju zaliczenia']
                        elif feature == 'Tematyka':
                            res1 = o1['zgodność tematyki zajęć']
                            res2 = o2['zgodność tematyki zajęć']


                        print(res1, res2)

                        Results[feature][pref][n1 + "_" + n2] = [res1, res2]

                else:
                    if o1['nazwa przedmiotu'] == 'Błąd' or o2['nazwa przedmiotu'] == 'Błąd':
                        Results[feature][pref][n1 + "_" + n2] = 'błąd'
                    else:
                        res1_try = o1['zgodność trybu prowadzenia zajęć']
                        res1_kry = o1['zgodność rodzaju zaliczenia']
                        res1_tem = o1['zgodność tematyki zajęć']

                        res2_try = o2['zgodność trybu prowadzenia zajęć']
                        res2_kry = o2['zgodność rodzaju zaliczenia']
                        res2_tem = o2['zgodność tematyki zajęć']

                        for label, r1, r2 in [
                            ('tryb', res1_try, res2_try),
                            ('kryterium', res1_kry, res2_kry),
                            ('tematyka', res1_tem, res2_tem)
                        ]:
                            print(r1, r2)
                            Results[feature][pref][f"{n1}_{n2}_{label}"] = [r1, r2]

            output_path = Path("output")
            output_path.mkdir(exist_ok=True)

            if pref == "mieszany: w sali i zdalnie":
                with open(f"output/scores_{feature}_mieszany.json", "w", encoding="utf-8") as file:
                    json.dump(Results[feature][pref], file, ensure_ascii=False, indent=2)
            else:
                with open(f"output/scores_{feature}_{pref.replace("/", "_")}.json", "w", encoding="utf-8") as file:
                    json.dump(Results[feature][pref], file, ensure_ascii=False, indent=2)

        with open(f"output/scores_{feature}.json", "w", encoding="utf-8") as file:
            json.dump(Results[feature], file, ensure_ascii=False, indent=2)

    with open(f"output/scores.json", "w", encoding="utf-8") as file:
        json.dump(Results, file, ensure_ascii=False, indent=2)