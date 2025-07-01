import json

def collect_survey():
    print("Podaj swoje preferencje dotyczące przedmiotów. Jeżeli nie masz preferencji pozostaw pole puste")

    def get_input(prompt):
        value = input(prompt)
        return value if value.strip() else "BRAK PREFERENCJI"

    survey = {
        "Preferowana ilość puntów ECTS": get_input("Podaj liczbę punktów ECTS lub przedział punktów: "),
        "Niewłaściwa ilość punktów ECTS": get_input("Podaj liczbę punktów ECTS, która nie jest dla Ciebie satysfakcjonująca: "),
        "Preferowna tematyka zajęć": get_input("Przedstaw swój obszar zainteresowań (mogą to być dziedziny takie jak historia, czy biologia), albo bardziej ogólne. Może być wiele: "),
        "Niewłaściwa tematyka zajęć": get_input("Z jakich obszarów nie chcesz przedmiotów: "),
        "Preferowany tryb prowadzenia zajęć": get_input("Czy masz preferowany tryb prowadzenia zajęć np. kurs internetowy albo warsztaty: "),
        "Niewłaściwy tryb prowadzenia zajęć": get_input("Czy nie chcesz jakiegoś trybu zajęć: "),
        "Preferowany rodzaj zaliczenia": get_input("Preferowany rodzaj zaliczenia (obecności / projekty / egzamin): "),
        "Niewłaściwy rodzaj zaliczenia": get_input("Czy nie chcesz jakiegoś rodzaju zaliczenia: "),
        "Dodatkowe preferencje": get_input("Podaj dodatkowe preferencje: "),
        "Niewłaściwe preferencje": get_input("Podaj dodatkowe ograniczenia: ")
    }

    json_output = json.dumps(survey, indent=4, ensure_ascii=False)

    return json_output

print(collect_survey())
