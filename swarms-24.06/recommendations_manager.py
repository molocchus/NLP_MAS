#%%
import json
from swarms import Agent, SequentialWorkflow

from course_filtrator import CourseFiltrator
from course_selector import CourseSelector

#%%
class RecommendationsManager(Agent):
    """
    Agent zarządzający rekomendacjami kursów akademickich.
    Gromadzi i przetwarza rekomendacje z różnych źródeł.
    """

    recommendations: set[str]

    def update_recommendations_set(self, new_recommendations: set[str]) -> None:
        """
        Updates the set of recommendations with new recommendations.

        Args:
            new_recommendations (set[str]): A set of new course recommendations to be added.

        Returns:
            None

        Raises:
            ValueError: If the new recommendations set is empty.

        Example:
            >>> print(self.recommendations)
            {"Course A"}
            >>> self.update_recommendations_set({"Course B", "Course C"})
            >>> print(self.recommendations)
            {"Course A", "Course B", "Course C"}
        """
        
        if not new_recommendations:
            raise ValueError("New recommendations set cannot be empty.")
        
        self.recommendations.update(new_recommendations)

    
    def __init__(
            self,
            course_filtrator: CourseFiltrator,
            course_selector: CourseSelector,
            max_courses_per_chunk = 10,
            min_recommended_courses = 5,
            max_loops: int = 1,
            max_tokens: int = 4096,
            model_name: str = "gemini/gemini-2.0-flash",
            dynamic_temperature_enabled: bool = True,
        ):
        """
            Inicjalizuje agenta RecommendationsManager.
            :param course_filtrator: Agent filtrujący kursy na podstawie nazwy przedmiotu.
            :param course_selector: Agent wybierający kursy na podstawie preferencji użytkownika.
            :param max_courses_per_chunk: Maksymalna liczba kursów w jednym przetwarzanym kawałku.
            :param min_recommended_courses: Minimalna liczba rekomendowanych kursów.
            :param max_loops: Maksymalna liczba pętli przetwarzania.
            :param max_tokens: Maksymalna liczba tokenów do przetworzenia.
            :param model_name: Nazwa modelu do użycia.
            :param dynamic_temperature_enabled: Czy dynamiczna temperatura jest włączona.
        """

        super().__init__(
            agent_name="Recommendations-Manager-Agent",
            agent_description="",
            system_prompt="",
            max_loops=max_loops,
            max_tokens=max_tokens,
            model_name=model_name,
            dynamic_temperature_enabled=dynamic_temperature_enabled,
            output_type="dict",
            tools=[
                self.update_recommendations_set
            ]
        )

        self.recommendations = set()
        self.max_courses_per_chunk = max_courses_per_chunk
        self.min_recommended_courses = min_recommended_courses

        self.workers_swarm = SequentialWorkflow(
            agents=[course_filtrator, course_selector],
            max_loops=max_loops,
            verbose=False,
            output_type="dict",
        )

        workers_str = str(self.workers_swarm.agents)[1:-1]
        self.agent_description = f"""
            Zarządza rekomendacjami kursów akademickich, gromadząc i przetwarzając
            rekomendacje na podstawie outputu od swoich pracowników: {workers_str}.
        """
        self.system_prompt = f"""
            Zarządzasz rekomendacjami przedmiotów uniwersyteckich. 
            
            WEJŚCIE:
            Otrzymujesz output od swojego zespołu workerów: {workers_str}. 
            Musisz go przetworzyć, weryfikując, czy każda propozycja:
            - Ma pełną nazwę akademicką
            - Jest związana z dziedziną studiów
            - Nie zawiera błędów formatowania

            WYJŚCIE:
            Użyj narzędzia update_recommendations_set, aby zaktualizować zestaw rekomendacji
            (chyba, że nie dostałeś ani jednej prawidłowej rekomendacji).
        """


    def run(self, task: str, courses_filename: str, max_iters: int):
        with open(courses_filename, "r") as file:
            courses_data = json.load(file)  

        iter_count = 0
        all_courses = list(courses_data.items())

        while len(self.recommendations) < self.min_recommended_courses and iter_count < max_iters:
            iter_count += 1
        
            start_idx = iter_count * self.max_courses_per_chunk
            end_idx = start_idx + self.max_courses_per_chunk
            courses_chunk = dict(all_courses[start_idx:end_idx])  # Get next chunk

            workers_output = self.workers_swarm.run(f"""
                ***ZADANIE:***
                {task.strip()}

                ***DANE O PRZEDMIOTACH:***
                {courses_chunk}
            """)

            import time
            time.sleep(1)
            print("Waiting 20 seconds...")
            time.sleep(19)

            super().run(f"""
                ***ZADANIE:***
                Przetwórz output od swojego zespołu workerów, aby zaktualizować rekomendacje kursów.
                        
                ***OUTPUT OD WORKERÓW:***
                {workers_output}
            """)
            
            print(f"""\n
                –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
                    Obecne rekomendacje: 
                    {self.recommendations}
                –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
            \n""")

#%%
# Test
if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()

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
    
    course_filtrator = CourseFiltrator(
        survey_data=survey_data,
    )

    course_selector = CourseSelector(
        survey_data=survey_data,
        courses_filename="academic_courses.json",
    )

    recommendations_manager = RecommendationsManager(
        course_filtrator=course_filtrator,
        course_selector=course_selector,
    )

    recommendations_manager.run(
        task="Zarządzaj rekomendacjami kursów akademickich.",
        courses_filename="academic_courses.json",
        max_iters=1,
    )
