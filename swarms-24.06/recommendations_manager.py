#%%
from swarms import Agent, SequentialWorkflow

from course_filtrator import CourseFiltrator
from course_selector import CourseSelector

#%%
class RecommendationsManager(Agent):
    """
    Agent zarządzający rekomendacjami kursów akademickich.
    Gromadzi i przetwarza rekomendacje z różnych źródeł.
    """

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
            agent_description="""
                Zarządza rekomendacjami kursów akademickich, gromadząc i przetwarzając
                rekomendacje z różnych źródeł.
            """,
            system_prompt="""
                Jesteś specjalistą od zarządzania rekomendacjami kursów akademickich.
                Twoim zadaniem jest gromadzenie i przetwarzanie rekomendacji
                z różnych źródeł, aby stworzyć listę kursów do polecenia studentom.
                
                UWAGA:
                - Gromadź tylko unikalne rekomendacje
                - Odrzucaj duplikaty i nieistotne kursy
                - Zachowuj tylko te, które mają potencjał być przydatne dla studentów
            """,
            max_loops=max_loops,
            max_tokens=max_tokens,
            model_name=model_name,
            dynamic_temperature_enabled=dynamic_temperature_enabled,
            output_type="dict",
        )

        self.max_courses_per_chunk = max_courses_per_chunk
        self.min_recommended_courses = min_recommended_courses
        self.recommendations = set()

        self.workers_swarm = SequentialWorkflow(
            agents=[course_filtrator, course_selector],
            max_loops=max_loops,
        )

    def run(self, task: str):
        while len(self.recommendations) < self.min_recommended_courses:
            # .........
            
