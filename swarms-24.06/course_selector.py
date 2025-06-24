#%%
from swarms import Agent

#%%
class CourseSelector(Agent):
    """
    Agent dokonujący selekcji kursów na podstawie pełnych metadanych,
    uwzględniając wstępnie odfiltrowane kursy z CourseFiltrator.
    """
    def __init__(
            self,
            courses_data: dict[str, dict[str, str]],
            survey_data: dict[str, str],
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
                1. Przeanalizuj PEŁNE metadane kursów (ECTS, tryb, zaliczenie itp.)
                2. Oceń zgodność z WSZYSTKIMI kryteriami z ankiety
                3. Zwróć tylko kursy spełniające WSZYSTKIE wymagania
                
                KRYTERIA WYBORU:
                - Tematyka musi pasować do "Preferowana tematyka zajęć"
                - ECTS musi mieścić się w preferowanym zakresie
                - Tryb prowadzenia musi być akceptowalny
                - Rodzaj zaliczenia musi być preferowany
                - Musi spełniać wszystkie dodatkowe preferencje
                
                UWAGA:
                - Uwzględnij tylko kursy z listy wstępnie przefiltrowanej
                - Bądź restrykcyjny - odrzuć przy najmniejszej wątpliwości
                - Format wyjścia: słownik z pełnymi metadanymi wybranych kursów
            """,
            max_loops=max_loops,
            max_tokens=max_tokens,
            model_name=model_name,
            dynamic_temperature_enabled=dynamic_temperature_enabled,
            output_type="dict",
        )
        self.courses_data = courses_data
        self.survey_data = survey_data

#%%
# Test
if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()

    from general_tools import extract_courses_data
    courses_data = extract_courses_data("academic_courses.json")

    agent = CourseSelector(
        courses_data=courses_data,
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
    )

    agent.run("""
        ╭───────────── Agent Name Course-Name-Filtrator-Agent [Max Loops: 1 ] ─────────────╮
        │ Course-Name-Filtrator-Agent: ```python                                           │
        │ course_names = [                                                                 │
        │     "Zarządzanie finansami przedsiębiorstw",                                     │
        │     "Prawo pracy i ubezpieczeń społecznych",                                     │
        │     "Marketing strategiczny",                                                    │
        │     "Język angielski dla biznesu",                                               │
        │     "Etyka w biznesie",                                                          │
        │     "Podstawy programowania w Pythonie",                                         │
        │     "Finanse osobiste",                                                          │
        │     "Negocjacje w biznesie",                                                     │
        │     "Prawo handlowe",                                                            │
        │     "Język niemiecki dla początkujących",                                        │
        │     "Analiza danych w finansach",                                                │
        │     "Zarządzanie projektami",                                                    │
        │     "Wprowadzenie do rachunkowości",                                             │
        │     "Język hiszpański",                                                          │
        │     "Kontrola zarządcza",                                                        │
        │     "Psychologia zarządzania",                                                   │
        │     "Prawo cywilne",                                                             │
        │     "Język francuski",                                                           │
        │     "Bankowość centralna",                                                       │
        │     "Zarządzanie zasobami ludzkimi"                                              │
        │ ]                                                                                │
        │ ```                                                                              │
        │ Analizuję nazwy kursów i odrzucam te, które ewidentnie nie pasują do             │
        │ preferowanej tematyki (zarządzanie, finanse, prawo pracy) lub pasują do          │
        │ niewłaściwej tematyki (języki obce).                                             │
        │                                                                                  │
        │ Odrzucone kursy:                                                                 │
        │ * "Język angielski dla biznesu"                                                  │
        │ * "Język niemiecki dla początkujących"                                           │
        │ * "Język hiszpański"                                                             │
        │ * "Język francuski"                                                              │
        │                                                                                  │
        │ ```python                                                                        │
        │ filtered_course_names = [                                                        │
        │     "Zarządzanie finansami przedsiębiorstw",                                     │
        │     "Prawo pracy i ubezpieczeń społecznych",                                     │
        │     "Marketing strategiczny",                                                    │
        │     "Etyka w biznesie",                                                          │
        │     "Podstawy programowania w Pythonie",                                         │
        │     "Finanse osobiste",                                                          │
        │     "Negocjacje w biznesie",                                                     │
        │     "Prawo handlowe",                                                            │
        │     "Analiza danych w finansach",                                                │
        │     "Zarządzanie projektami",                                                    │
        │     "Wprowadzenie do rachunkowości",                                             │
        │     "Kontrola zarządcza",                                                        │
        │     "Psychologia zarządzania",                                                   │
        │     "Prawo cywilne",                                                             │
        │     "Bankowość centralna",                                                       │
        │     "Zarządzanie zasobami ludzkimi"                                              │
        │ ]                                                                                │
        │ ```                                                                              │
        ╰──────────────────────────────────────────────────────────────────────────────────╯
    """)
