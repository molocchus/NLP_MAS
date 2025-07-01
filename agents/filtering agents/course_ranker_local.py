# %%
import json
import time
from typing import Any
from swarms import Agent
import re
import ast


def find_key_positions(text, keys):
    """Find all key positions in the text."""
    positions = []
    for key in keys:
        for match in re.finditer(re.escape(key), text):
            positions.append((match.start(), key))
    # Sort by position in the text
    return sorted(positions, key=lambda x: x[0])


def extract_values_between_keys(text, keys):
    positions = find_key_positions(text, keys)
    results = {'nazwa przedmiotu': 'ok',
               'prawidłowość przedmiotu': 'ok',
               'zgodność tematyki zajęć': -1}

    for i, (start_idx, key) in enumerate(positions):
        key_end = start_idx + len(key)
        end_idx = positions[i + 1][0] if i + 1 < len(positions) else len(text)
        snippet = text[key_end:end_idx]

        if "liczba" in snippet:
            continue  # Skip this snippet if it contains "Liczba"

        if key == 'prawidłowość przedmiotu':
            match = snippet
            if len(snippet) > 2:
                results[key] = match
        else:
            match = re.search(r'\d{1,3}', snippet)
            if match:
                try:
                    val = int(match.group())
                    if key != '}' and val > results[key]:
                        results[key] = val
                except ValueError:
                    continue  # Skip if not an int

    return results


# %%
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
            max_tokens: int = 3000,
            model_name: str = "gemini/gemini-2.0-flash",
            dynamic_temperature_enabled: bool = False,
            output_type: str = "string",
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
                Na podstawie preferencji studenta oraz samej nazwy przedmiotu przydziel ocenę oraz uzasadnienie tej oceny, obejmujące wady i zalety przedmiotu. Odpowiedź zwróć w formacie:
                odpowiedź:{
                    'nazwa przedmiotu': {nazwa przedmiotu},
                    'prawidłowość przedmiotu':{tak/nie w zależności od tego czy pasuje czy nie}
                    'zgodność tematyki zajęć':{liczba 0-10 odzwierciedlająca dopasowanie Opisu kursu do Preferencje studenta}
                }
            """,
            max_loops=max_loops,
            max_tokens=max_tokens,
            temperature=0.0,
            model_name=model_name,
            dynamic_temperature_enabled=False,
            output_type=output_type,  # type: ignore
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

        with open(self.courses_filename, "r", encoding='utf-8') as file:
            courses_data = json.load(file)

        course = courses_data[course_name]
        courses_dict = course["Nazwa przedmiotu"]
        return courses_dict

    def run(self, course_name: str, **kwargs) -> dict[str, Any]:
        """
        Uruchamia agenta do oceny kursu na podstawie metadanych i ankiety studenta.

        Parametry:
            course_name (str): Nazwa kursu do oceny.
        """
        print(f"""\n
            –––––––––––––––––––––––––––––––––––––––––––––––––––––––
            Running {self.agent_name} with course: 
            "{course_name}"...
            –––––––––––––––––––––––––––––––––––––––––––––––––––––––
        \n""")

        course_details = self.get_course_details(course_name)

        prompt = f"""
                Ocen kurs '{course_name}' na podstawie poniższych danych:
                    Preferencje studenta: {self.survey_data}
                    Nazwa przedmiotu: {course_details}
                    Koniec wiadomości.
                    {self.agent_name}: odpowiedź:
            """

        output = super().run(prompt,
                             **kwargs
                             )

        keys = [
            'prawidłowość przedmiotu',
            'zgodność tematyki zajęć',
            '}'
        ]

        matches = extract_values_between_keys(output, keys)

        print(matches)

        matches['nazwa przedmiotu'] = course_details

        return matches