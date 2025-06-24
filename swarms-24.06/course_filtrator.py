#%%
from swarms import Agent

#%%
class CourseFiltrator(Agent):
    """
    Agent filtrujący kursy akademickie TYLKO na podstawie nazwy przedmiotu.
    Odrzuca przedmioty, których nazwy ewidentnie nie pasują do preferencji z ankiety.
    """
    def __init__(
            self,
            course_names: set[str],
            survey_data: dict[str, str],
            max_loops=1,
            max_tokens=4096, 
            model_name="gemini/gemini-2.0-flash", 
            dynamic_temperature_enabled=True, 
        ):
        super().__init__(
            agent_name="Course-Name-Filtrator-Agent",
            agent_description="""
                Filtruje kursy wyłącznie na podstawie nazwy przedmiotu,
                odrzucając te, których nazwy wyraźnie nie pasują do preferencji.
            """,
            system_prompt=f"""
                Jesteś specjalistą od wstępnej selekcji kursów akademickich. 
                
                DANE ANKIETY:
                {survey_data}
                
                ZADANIE:
                1. Przenalizuj nazwy kursów (nie patrz na ECTS, tryb prowadzenia itp.)
                2. Odrzuć TYLKO kursy, których nazwy EWIDENTNIE nie pasują do:
                   - "Preferowana tematyka zajęć"
                   - "Niewłaściwa tematyka zajęć"
                3. Zachowaj WSZYSTKIE inne kursy (nawet jeśli nie jesteś pewien)
                
                PRZYKŁADY ODRZUCENIA:
                - Nazwa: "Zaawansowana biologia molekularna" 
                  gdy w "Niewłaściwa tematyka": "biologia" → ODRZUĆ
                - Nazwa: "Wprowadzenie do fizyki kwantowej"
                  gdy w "Preferowana tematyka": "historia" → ODRZUĆ
                
                FORMAT WYJŚCIA:
                - Taki zbiór jak wejściowy course_names, ale tylko z pasującymi kursami
                - Nie modyfikuj struktur danych!
            """,
            max_loops=max_loops,
            max_tokens=max_tokens,
            model_name=model_name,
            dynamic_temperature_enabled=dynamic_temperature_enabled,
            output_type="dict",
        )
        self.course_names = course_names
        self.survey_data = survey_data
    
#%% 
# Test
if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()

    from general_tools import extract_course_names
    course_names = extract_course_names("academic_courses.json")

    agent = CourseFiltrator(
        course_names=course_names,
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

    agent.run("Przetwórz kursy na podstawie ankiety.")
