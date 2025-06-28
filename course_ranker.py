#%%
import json
import re
import time
from typing import Any

from swarms import Agent

#%%
class CourseRanker(Agent):
    """
    Agent oceniający kursy akademickie na podstawie ich szczegółowych metadanych.
    Odrzuca kursy, które nie spełniają określonych kryteriów.
    """

    def __init__(
        self,
        survey_data: dict[str, Any],
        courses_filename: str,
        ranked_courses_filename: str = "ranked_courses.json",
        max_loops: int = 1,
        max_tokens: int = 4096,
        model_name: str = "gemini/gemini-2.0-flash",
        dynamic_temperature_enabled: bool = False,
        output_type: str = "dict",
        **kwargs: Any,
    ):
        """
        Inicjalizuje agenta CourseRanker.
        Parametry:
            survey_data (dict[str, Any]): Dane z ankiety studenta.
            courses_filename (str): Ścieżka do pliku z metadanymi kursów.
            max_loops (int): Maksymalna liczba pętli przetwarzania.
            max_tokens (int): Maksymalna liczba tokenów w odpowiedzi.
            model_name (str): Nazwa modelu AI do użycia.
            dynamic_temperature_enabled (bool): Czy dynamiczna temperatura jest włączona.
        """
        
        super().__init__(
            agent_name="Pomocnik oceniający dopasowanie przedmiotów do preferencji studenta.",
            agent_description="""
                Jesteś obiektywnym doradcą akademickim wyspecjalizowanym w dopasowywaniu kursów do preferencji studentów. Komunikujesz się bezpośrednio ze studentem.
            """,
            system_prompt="""
                Na podstawie preferencji studenta oraz opisu przedmiotu przydziel ocenę przedmiotu, uzasadnienie tej oceny, obejmujące wady i zalety przedmiotu. Odpowiedź zwróć w formacie:
                odpowiedź:{
                    'nazwa_przedmiotu': {nazwa przedmiotu},
                    'zgodność punktów ECTS':{Czy ilość punktów ECTS jest zgodna z preferencjami studenta? liczba 0-100 odzwierciedlająca dopasowanie}
                    'zgodność tematyki zajęć':{Czy tematyka zajęć jest zgodna z preferencjami studenta? liczba 0-100 odzwierciedlająca dopasowanie}
                    'zgodność trybu prowadzenia zajęć':{Czy trybu prowadzenia zajęć jest zgodny z preferencjami studenta? liczba 0-100 odzwierciedlająca dopasowanie}
                    'zgodność rozdzaju zaliczenia':{Czy rozdzaj zaliczenia jest zgodny z preferencjami studenta? liczba 0-100 odzwierciedlająca dopasowanie}
                    'zgodność dodatkowych preferencji':{Czy dodatkowe preferencje są zgodne z preferencjami studenta? liczba 0-100 odzwierciedlająca dopasowanie}
                    'ocena': {liczba 0-100 odzwierciedlająca dopasowanie przedmiotu do preferencji},    
                }
            """,
            max_loops=max_loops,
            max_tokens=max_tokens,
            temperature=0.0,
            model_name=model_name,
            dynamic_temperature_enabled=dynamic_temperature_enabled,
            output_type=output_type, # type: ignore
            **kwargs,
        )
        
        self.survey_data = survey_data
        self.courses_filename = courses_filename
        self.ranked_courses_filename = ranked_courses_filename


    def get_course_details(self, course_name: str) -> dict[str, Any]:
        """
        Pobiera szczegółowe metadane kursu z pliku JSON.
        
        Parametry:
            course_name (str): Nazwa kursu do wyszukania.
        """

        with open(self.courses_filename, "r") as file:
            courses_data = json.load(file)
        
        if course_name in courses_data:
            return courses_data[course_name]
        
        raise ValueError(f"""\n
            ––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
            Kurs '{course_name}' nie znaleziony w pliku {self.courses_filename}.
            ––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
        \n""")


    def run(self, course_name: str, **kwargs) -> dict[str, Any]:
        """
        Uruchamia agenta do oceny kursu na podstawie metadanych i ankiety studenta.
        
        Parametry:
            course_name (str): Nazwa kursu do oceny.
        """

        time.sleep(1)
        print(f"""\n
            –––––––––––––––––––––––––––––––––––––––––––––––––––––––
            Running {self.agent_name} with course: 
            "{course_name}"...
            –––––––––––––––––––––––––––––––––––––––––––––––––––––––
        \n""")

        course_details = self.get_course_details(course_name)
        
        output = super().run(f"""
                Ocen kurs '{course_name}' na podstawie poniższych danych:
                    Preferencje studenta: {self.survey_data}
                    Opis kursu: {course_details}
                    Koniec wiadomości.
                    {self.agent_name}: odpowiedź:
            """, 
            **kwargs
        )

        agent_content = output[-1]['content']
        pattern = re.compile(
            r"odpowiedź:\s*(\{.*?\})",
            re.DOTALL | re.IGNORECASE
        )

        matches = pattern.findall(agent_content)
        print(matches)
        # if not response_json:
        #     raise ValueError(f"""\n
        #         ––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
        #         Odpowiedź agenta nie zawiera poprawnego formatu JSON:
        #         {agent_content}
        #         ––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
        #     \n""")
        #
        # try:
        #     return json.loads(response_json.group())
        # except Exception as e:
        #     raise ValueError(f"""\n
        #         ––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
        #         {type(e).__name__}: {e}
        #         --------------------------------------------------------------------
        #         {response_json.group()}
        #         ––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
        #     \n""")
