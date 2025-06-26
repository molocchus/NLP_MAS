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
        dynamic_temperature_enabled: bool = True,
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
            agent_name="Agent-Przypisujący-Rangi-Kursom",
            agent_description="""
                Agent dostaje na wejściu dane z ankiety studenta
                oraz szczegółowe metadane o jednym kursie akademickim.
                Jego zadaniem jest przypisanie rangi kursowi, na ile
                pasuje on do preferencji studenta z ankiety.
            """,
            system_prompt="""
                Jesteś specjalistą w dopasowywaniu kursów akademickich do indywidualnych preferencji studentów. 
                Twoim zadaniem jest obiektywna ocena, na ile dany kurs pasuje do profilu studenta na podstawie:

                ***Dane wejściowe:***
                    1. ANKIETA STUDENTA, zawiera:
                        - Preferowany i nieakceptowany zakres punktów ECTS (np. "6-8", "mniej niż 4")
                        - Tematyki zajęć, które student preferuje i których unika (np. "zarządzanie, finanse")
                        - Akceptowane i nieakceptowane formy prowadzenia zajęć (np. "weekendowy, zdalny")
                        - Preferowane i niechciane formy zaliczenia (np. "egzamin, projekt")
                        - Dodatkowe wymagania (np. "materiały online") i wykluczenia

                    2. METADANE KURSU, obejmują:
                        - Nazwę, punkty ECTS (np. "3.00"), język wykładowy
                        - Tryb prowadzenia (np. "zdalnie"), rodzaj przedmiotu (np. "ogólnouniwersyteckie")
                        - Szczegółowy opis tematyki i efektów kształcenia
                        - Informacje o jednostce prowadzącej i grupach docelowych

                ***Zasady oceny:***
                    1. Analizuj obiektywnie wszystkie dostarczone dane.
                    2. Przyporządkuj rangę w skali 0-100 (gdzie 100 = idealne dopasowanie).
                    3. Uwzględnij zarówno twarde kryteria (np. wymagania wstępne), jak i miękkie (np. zainteresowania).
                    4. Jeśli brakuje kluczowych danych - przyznaj punkty ujemne (-10) za każdą lukę.

                ***Format odpowiedzi:***
                    {
                        "nazwa_przedmiotu": "nazwa przedmiotu",
                        "ranga": "liczba 0-100",
                        "uzasadnienie": "krótkie uzasadnienie w punktach",
                        "problemy": ["lista problemów/niepewności"]
                    }

                ***Przykład:***
                    {
                        "nazwa_przedmiotu": "E-commerce w praktyce - Uruchomienie sprzedaży w sieci",
                        "ranga": 85,
                        "uzasadnienie": [
                            "Kurs w 90% pokrywa zainteresowania studenta",
                            "Format zajęć odpowiada preferencjom",
                            "Poziom trudności o 10% wyższy niż oczekiwany"
                        ],
                        "problemy": ["Brak danych o wymaganiach wstępnych"]
                    }
                
                ***Ważne:***
                    Przekaż odpowiedź jako słownik w takim formacie do funkcji `output`.
            """,
            max_loops=max_loops,
            max_tokens=max_tokens,
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
                    ANKIETA STUDENTA: {self.survey_data}
                    METADANE KURSU: {course_details}
                
                Wymagane formatowanie odpowiedzi:
                    {{
                        "nazwa_przedmiotu": "{course_name}",
                        "ranga": "liczba 0-100",
                        "uzasadnienie": "krótkie uzasadnienie w punktach",
                        "problemy": ["lista problemów/niepewności"]
                    }}
            """, 
            **kwargs
        )

        agent_content = output[-1]['content']
        response_json = re.search(r'\{.*\}', agent_content, re.DOTALL)
        if not response_json:
            raise ValueError(f"""\n
                ––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
                Odpowiedź agenta nie zawiera poprawnego formatu JSON:
                {agent_content}
                ––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
            \n""")

        try:
            return json.loads(response_json.group())
        except Exception as e:
            raise ValueError(f"""\n
                ––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
                {type(e).__name__}: {e}
                --------------------------------------------------------------------
                {response_json.group()}
                ––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
            \n""")
