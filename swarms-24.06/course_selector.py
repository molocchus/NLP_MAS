#%%
import json
from swarms import Agent

#%%
class CourseSelector(Agent):
    """
    Agent dokonujący selekcji kursów na podstawie pełnych metadanych,
    uwzględniając wstępnie odfiltrowane kursy z CourseFiltrator.
    """

    not_matching_name_tolerance: float

    def get_courses_details(self, courses_names: set[str] | list[str]) -> dict[str, dict]:
        """
        Retrieves detailed metadata for the specified courses.

        Args:
            courses_names (set[str]): A set of course names for which to retrieve details.

        Returns:
            dict[str, dict]: A dictionary where keys are course names and values are their metadata.
        
        Raises:
            TypeError: If courses_names is not a set of strings.
            ValueError: If courses_names is empty or if no courses match the provided names.
            ValueError: If the number of matching courses is below the tolerance threshold.
        
        Example:
            >>> courses = {"Zarządzanie finansami", "Prawo pracy"}
            >>> details = self.get_courses_details(courses)
            >>> print(details)
            {
                "Zarządzanie finansami": {"ECTS": 6, "Mode": "online", ...},
                "Prawo pracy": {"ECTS": 8, "Mode": "in-person", ...}
            }
        """
        
        if not isinstance(courses_names, set) and not isinstance(courses_names, list):
            raise TypeError(f"""
                courses_names must be a set or list of strings.
                Received: {courses_names}
                Received type: {type(courses_names).__name__}
            """)
        
        if not courses_names:
            raise ValueError("courses_names cannot be empty.")
        
        with open(self.courses_filename, "r") as file:
            all_courses = json.load(file)

        courses_details = {}
        for name in courses_names:
            print(f"Trying to receive details for course: '{name}'...", end=" ")
            if name in all_courses:
                courses_details[name] = all_courses[name]
                print("success!")
            else:
                print("failed.")

        if not courses_details:
            raise ValueError("No courses found matching the provided names.")

        if len(courses_details) < self.not_matching_name_tolerance * len(courses_names):
            raise ValueError(f"Only {len(courses_details)} courses found instead of {len(courses_names)}, which is less than the tolerance threshold of {self.not_matching_name_tolerance * len(courses_names)}.")

        return courses_details
    

    def __init__(
            self,
            survey_data: dict[str, str],
            courses_filename: str,
            not_matching_name_tolerance: float = 0.3,
            max_loops: int = 1,
            max_tokens: int = 4096,
            model_name: str = "gemini/gemini-2.0-flash",
            dynamic_temperature_enabled: bool = True,
        ):
        super().__init__(
            agent_name="Course-Selector-Agent",
            agent_description="""
                Dokonuje selekcji kursów na podstawie pełnych metadanych,
                uwzględniając wszystkie kryteria z ankiety studenta.
            """,
            system_prompt=f"""
                Jesteś specjalistą od finalnej selekcji kursów akademickich. 
                
                DANE ANKIETY:
                    {survey_data}
                
                ZADANIE:
                    1. Używając narzędzia get_courses_details, uzyskaj PEŁNE metadane kursów (ECTS, tryb, zaliczenie itp.)
                    2. Oceń zgodność z WSZYSTKIMI kryteriami z ankiety
                    3. Zwróć tylko NAZWY KURSÓW spełniające WSZYSTKIE wymagania
                    4. Nie zwracaj METADANYCH, tylko NAZWY KURSÓW
                
                KRYTERIA WYBORU:
                    - Tematyka musi pasować do "Preferowana tematyka zajęć"
                    - ECTS musi mieścić się w preferowanym zakresie
                    - Tryb prowadzenia musi być akceptowalny
                    - Rodzaj zaliczenia musi być preferowany
                    - Musi spełniać wszystkie dodatkowe preferencje
                
                UWAGA:
                    - Uwzględnij tylko kursy z listy wstępnie przefiltrowanej
                    - Bądź restrykcyjny - odrzuć przy najmniejszej wątpliwości
                    - Format wyjścia: TYLKO NAZWY wybranych kursów, bez żadnych metadanych
            """,
            max_loops=max_loops,
            max_tokens=max_tokens,
            model_name=model_name,
            dynamic_temperature_enabled=dynamic_temperature_enabled,
            output_type="dict",
            tools=[
                self.get_courses_details,
            ]
        )

        self.survey_data = survey_data
        self.courses_filename = courses_filename
        self.not_matching_name_tolerance = not_matching_name_tolerance

#%%
# Test
if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()

    agent = CourseSelector(
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
            "Niewłaściwe preferencje": "wymagana fizyczna obecność na wykładach"
        },
        courses_filename="academic_courses.json",
    )

    output = agent.run("""
        ╭─────────────────── Agent Name Course-Name-Filtrator-Agent [Max Loops: 1 ] ────────────────────╮
        │ Course-Name-Filtrator-Agent: Wyfiltrowane kursy:                                              │
        │ - Kurs na Równość – przeciwdziałanie dyskryminacji na UW                                      │
        │ - Klimatyczne ABC. Interdyscyplinarne wprowadzenie do problemu zmiany klimatu i kryzysu       │
        │ ekologicznego.                                                                                │
        │ - Surowce krytyczne vs. polityka                                                              │
        │ - Gospodarowanie na obszarach zimnych                                                         │
        │ - Czarownice, zabójcy, rozwodnicy. Z dziejów prawa na ziemiach polskich XVI - XX w.           │
        │ - Metodologia badań jakościowych                                                              │
        │ - Kompleksowe zarządzanie sobą w czasie                                                       │
        │ - Climate Change “101” - Interdisciplinary introduction to the contemporary  climate crisis   │
        │ - Wolność słowa a Internet - język w mediach niezależnych                                     │
        │ - Władcy, dyplomaci, szpiedzy – z dziejów stosunków międzynarodowych w czasach Hammurabiego   │
        │ - Antropologia wina                                                                           │
        │ - E-commerce w praktyce - Uruchomienie sprzedaży w sieci                                      │
        │ - Prawo i płeć                                                                                │
        ╰───────────────────────────────────────────────────────────────────────────────────────────────╯
    """)

    import time
    time.sleep(1)
    print(output)
