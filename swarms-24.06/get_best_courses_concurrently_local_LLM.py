#%%
import concurrent.futures
import json

from course_ranker import CourseRanker

#%%
def process_course(course_name, ranker_instance):
    output = ranker_instance.run(course_name)
    return output['ranga'], course_name

def get_best_courses(course_names, ranker_agents, how_many=3):
    course_ranks = {}
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=len(ranker_agents)) as executor:
        # Rozpocznij taski z odpowiednimi instancjami rankera
        future_to_course = {}
        for i, name in enumerate(course_names):
            ranker_instance = ranker_agents[i % len(ranker_agents)]
            future = executor.submit(process_course, name, ranker_instance)
            future_to_course[future] = name
        
        # Zbierz wyniki
        for future in concurrent.futures.as_completed(future_to_course):
            try:
                rank, name = future.result()
                course_ranks[rank] = name
            except Exception as e:
                print(f"Błąd przetwarzania kursu {future_to_course[future]}: {e}")
    
    return dict(sorted(course_ranks.items(), reverse=True)[:how_many])

#%%
if __name__ == "__main__":
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer
    from huggingface_hub import login
    from swarm_models.huggingface import HuggingfaceLLM

    # Hugging Face login
    hf_token = "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"
    login(token=hf_token)

    # TinyLLaMA model
    model_name = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"

    local_llm = HuggingfaceLLM(
        model_id=model_name,
        device="cpu",
        max_length=5000
    )

    survey_data={
        "Preferowana ilość puntów ECTS": "6-8",
        "Niewłaściwa ilość punktów ECTS": "mniej niż 4",
        "Preferowna tematyka zajęć": "zarządzanie, finanse, prawo pracy",
        "Niewłaściwa tematyka zajęć": "języki obce",
        "Preferowany tryb prowadzenia zajęć": "weekendowy, zdalny",
        "Niewłaściwy tryb prowadzenia zajęć": "codzienne poranne",
        "Preferowany rodzaj zaliczenia": "projekt praktyczny",
        "Niewłaściwy rodzaj zaliczenia": "kolokwia co tydzień",
        "Dodatkowe preferencje": "materiały dostępne online",
        "Niewłaściwe preferencje": "wymagana fizyczna obecność na wykładach",
    }

    courses_filename = "academic_courses.json"

    # Tworzymy listę agentów (każdy ma swoją własną instancję, będą mogli działać równolegle)
    ranker_agents = [
        CourseRanker(
            survey_data, 
            courses_filename,
            llm=local_llm,
        ) 
        for _ in range(1)  # niezależne instancje
    ]

    with open(courses_filename, "r", encoding="utf-8") as file:
        courses_data = json.load(file)

    course_names = list(courses_data.keys())[:1] # Limitujemy liczbę kursów dla testów

    best_courses = get_best_courses(course_names, ranker_agents, how_many=3)
    print(json.dumps(best_courses, indent=4, ensure_ascii=False))
