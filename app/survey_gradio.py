import gradio as gr
import json

def collect_survey_gradio(ects, ects_neg, interests, interests_neg, type_, type_neg, zaliczenie, zaliczenie_neg, dodatkowe, dodatkowe_neg):
    def clean_input(value):
        return value.strip() if value.strip() else "BRAK PREFERENCJI"

    survey = {
        "Preferowana ilość puntów ECTS": clean_input(ects),
        "Niewłaściwa ilość punktów ECTS": clean_input(ects_neg),
        "Preferowna tematyka zajęć": clean_input(interests),
        "Niewłaściwa tematyka zajęć": clean_input(interests_neg),
        "Preferowany tryb prowadzenia zajęć": clean_input(type_),
        "Niewłaściwy tryb prowadzenia zajęć": clean_input(type_neg),
        "Preferowany rodzaj zaliczenia": clean_input(zaliczenie),
        "Niewłaściwy rodzaj zaliczenia": clean_input(zaliczenie_neg),
        "Dodatkowe preferencje": clean_input(dodatkowe),
        "Niewłaściwe preferencje": clean_input(dodatkowe_neg)
    }

    return json.dumps(survey, indent=4, ensure_ascii=False)

# Gradio Interface
iface = gr.Interface(
    fn=collect_survey_gradio,
    inputs=[
        gr.Textbox(label="Podaj liczbę punktów ECTS lub przedział punktów"),
        gr.Textbox(label="Podaj liczbę punktów ECTS, która nie jest dla Ciebie satysfakcjonująca"),
        gr.Textbox(label="Przedstaw swój obszar zainteresowań"),
        gr.Textbox(label="Z jakich obszarów nie chcesz przedmiotów"),
        gr.Textbox(label="Czy masz preferowany tryb prowadzenia zajęć"),
        gr.Textbox(label="Czy nie chcesz jakiegoś trybu zajęć"),
        gr.Textbox(label="Preferowany rodzaj zaliczenia"),
        gr.Textbox(label="Czy nie chcesz jakiegoś rodzaju zaliczenia"),
        gr.Textbox(label="Podaj dodatkowe preferencje"),
        gr.Textbox(label="Podaj dodatkowe ograniczenia")
    ],
    outputs=gr.Textbox(label="Preferencje w formacie JSON"),
    title="Ankieta preferencji dotyczących przedmiotów",
    description="Wypełnij pola poniżej. Jeśli nie masz preferencji, pozostaw puste – zostaną zapisane jako 'BRAK PREFERENCJI'."
)

iface.launch()
