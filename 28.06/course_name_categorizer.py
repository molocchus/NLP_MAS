#%%
import json
import pandas as pd
import re
import time
from typing import Any

from swarms import Agent

#%%
class CourseNameCategorizer(Agent):
    """
    Agent agregujący nazwy kursów akademickich na podstawie ich nazw.
    Odrzuca kursy, które nie pasują do preferowanych kategorii.
    """

    def __init__(
        self,
        binary_answer: bool,
        max_loops: int = 1,
        max_tokens: int = 4096,
        model_name: str = "gemini/gemini-2.0-flash",
        dynamic_temperature_enabled: bool = False,
        output_type: str = "dict",
        **kwargs: Any,
    ):
        """
        Inicjalizuje agenta CourseNameCategorizer.

        Parametry:
            course_name (str): Nazwa kursu do oceny.
            max_loops (int): Maksymalna liczba pętli przetwarzania.
            max_tokens (int): Maksymalna liczba tokenów w odpowiedzi.
            model_name (str): Nazwa modelu AI do użycia.
            dynamic_temperature_enabled (bool): Czy dynamiczna temperatura jest włączona.
        """
        
        if binary_answer:
            convergence_prompt = "'Tak' jeśli nazwa kursu pasuje do preferencji studenta, 'Nie' jeśli nie pasuje."
        else:
            convergence_prompt = "Liczba od 0 do 100, gdzie 0 oznacza brak dopasowania, a 100 pełne dopasowanie."

        super().__init__(
            agent_name="Pomocnik oceniający dopasowanie nazwy przedmiotu akademickiego do preferencji studenta",
            agent_description="""
                Jesteś obiektywnym doradcą akademickim wyspecjalizowanym w dopasowywaniu nazw kursów akademickich do preferencji studentów. Komunikujesz się bezpośrednio ze studentem.
            """,
            system_prompt="""
                Na podstawie preferencji studenta oraz nazwy przedmiotu przydziel przedmiotowi ocenę, wraz z uzasadnieniem, na ile pasuje on do podanych preferencji. Odpowiedź zwróć w formacie:
                odpowiedź: {
                    'nazwa_przedmiotu': {nazwa przedmiotu},
                    'zgodność tematyki zajęć': {Czy tematyka zajęć jest zgodna z preferencjami studenta?""" + convergence_prompt + """}
                }
            """,
            max_loops=max_loops,
            max_tokens=max_tokens,
            temperature=0.0,
            model_name=model_name,
            dynamic_temperature_enabled=dynamic_temperature_enabled,
            output_type=output_type,
            **kwargs,
        )


    def get_course_data(
        self,
        course_name: str,
        filename: str = "oguny_unique1.csv",
        key_names: list[str] = ["Nazwa", "kategorie"],
    ) -> dict[str, str]:
        """
        Wczytuje dane kursów z pliku CSV i zwraca słownik z nazwami kursów jako kluczami i ich kategoriami jako wartościami.
        
        Parametry:
            course_name (str): Nazwa kursu do wyszukania.
            filename (str): Ścieżka do pliku CSV z danymi kursów.
            key_names (list[str]): Lista kluczy, które mają być zwrócone w słowniku.

        Zwraca:
            dict[str, str]: Słownik z nazwami kursów i ich kategoriami.
        
        Wyjątki:
            ValueError: Jeśli kurs o podanej nazwie nie zostanie znaleziony.
        """

        df = pd.read_csv(
            filename,
            on_bad_lines='warn'
        )

        for course in df.to_dict(orient='records'):
            if course['Nazwa'] == course_name:
                return {key: course[key] for key in key_names if key in course}

        raise ValueError(f"""\n
            ––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
            Kurs '{course_name}' nie znaleziony w pliku '{filename}'.
            ––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
        \n""")


    def run(
        self, 
        course_name: str, 
        student_preferences: dict[str, Any],
        **kwargs
    ) -> dict:
        """
        Uruchamia agenta do oceny nazwy kursu na podstawie preferencji studenta.

        Parametry:
            course_name (str): Nazwa kursu do oceny.
            student_preferences (dict[str, Any]): Preferencje studenta.
        """

        time.sleep(1)
        print(f"""\n
            –––––––––––––––––––––––––––––––––––––––––––––––––––––––
            Running the agent:
            '{self.agent_name}' 
            
            with course: 
            '{course_name}',
            
            and preferences:\n{json.dumps(student_preferences, indent=4)}
            –––––––––––––––––––––––––––––––––––––––––––––––––––––––
        \n""")

        course_data = self.get_course_data(course_name)

        if course_data:
            print("\nSuccessfully retrieved the course's data:")
            print(json.dumps(course_data, indent=4), "\n")
        else:
            raise ValueError(f"Course data for '{course_name}' is empty.")

        output = super().run(f"""
                Oceń kurs '{course_name}' na podstawie poniższych danych:
                    Preferencje studenta: {student_preferences}
                    Opis kursu: {course_data}
                    Koniec wiadomości.
                    {self.agent_name}: odpowiedź:
            """, 
            **kwargs
        )

        agent_content = output[-1]['content']
        pattern = re.compile(
            r"(\{.*\})",
            re.DOTALL | re.IGNORECASE
        )

        matches = pattern.findall(agent_content)
        if not matches:
            raise ValueError("""\n
                –––––––––––––––––––––––––––––––––––––––
                Agent did not return a valid response.
                Please check the agent's output.
                –––––––––––––––––––––––––––––––––––––––
            \n""")

        response = json.loads(matches[0])
        print(f"""\n
            –––––––––––––––––––––––––––––––––––––––
            Agent's response:\n{json.dumps(response, indent=4)}
            –––––––––––––––––––––––––––––––––––––––
        \n""")

        if not "nazwa_przedmiotu" in response \
          or not "zgodność tematyki zajęć" in response:
            raise ValueError("""\n
                –––––––––––––––––––––––––––––––––––––––
                Agent's response is missing required fields.
                Expected keys: 'nazwa_przedmiotu', 'zgodność tematyki zajęć'.
                –––––––––––––––––––––––––––––––––––––––
            \n""")
        
        return response

#%%
# Example usage
if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()

    categorizer = CourseNameCategorizer(binary_answer=False)
    course_name = "Biologia zapylania roślin"
    
    student_preferences = {
        "interesuje_mnie": ["programowanie", "algorytmy"],
        "nie_interesuje_mnie": ["matematyka", "fizyka"]
    }
    
    categorizer.run(course_name, student_preferences)

    # EXPECTED OUTPUT:
    #     –––––––––––––––––––––––––––––––––––––––
    #     Agent's response:
    # {
    # "nazwa_przedmiotu": "Biologia zapylania roślin",
    # "zgodność tematyki zajęć": 10
    # }
    #     –––––––––––––––––––––––––––––––––––––––
