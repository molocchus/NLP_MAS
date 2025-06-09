#%%
import os

from crewai import Agent, Crew, LLM, Task
from crewai.project import CrewBase, agent, task, crew
from crewai_tools import FileReadTool, FileWriterTool
from crewai import Agent, Task, Crew    
from dotenv import load_dotenv
from langchain.llms import HuggingFaceHub
from typing import List

#%% 
@CrewBase
class RecommendationCrew:
    agents: List[Agent]
    tasks: List[Task]

    read_oguns_tool = FileReadTool(file_path="oguny.json")
    write_answers_tool = FileWriterTool(file_path="classification_output.json")
    read_answers_tool = FileReadTool(file_path="classification_output.json")
    write_oguns_tool = FileWriterTool(file_path="recommended_oguns.txt")

    load_dotenv()

    llm = LLM(
        model="huggingface/meta-llama/Llama-3.1-8B-Instruct",
        api_key=os.getenv("HUGGINGFACEHUB_API_KEY"),
    )

    @agent
    def classification_agent(self) -> Agent:
        
        return Agent(
            role="Klasyfikacja przedmiotów",
            goal="Przeanalizuj listę przedmiotów akademickich (w języku polskim) i zaproponuj możliwe schematy ich klasyfikacji na podstawie treści. Wynik zapisz do pliku JSON output.",
            backstory="Jesteś analitykiem akademickim specjalizującym się w analizie oferty dydaktycznej. Twoim zadaniem jest przeglądanie listy przedmiotów zapisanej w pliku JSON (w języku polskim) i zaproponowanie sensownych kategorii klasyfikacji, które mogą pomóc studentom lepiej zrozumieć strukturę kursów.",
            output_file="classification_output.json",
            allow_delegation=False,
            verbose=True,
            llm=self.llm,
            tools=[self.read_oguns_tool],
        )

    @task
    def classify_task(self) -> Task:
        return Task(
            description="Przeczytaj plik JSON zawierający opisy przedmiotów akademickich w języku polskim i zaproponuj co najmniej trzy różne schematy ich klasyfikacji. Kategorie mogą dotyczyć np. dziedziny naukowej, poziomu trudności lub stylu prowadzenia zajęć. Wynik zapisz do pliku classification_output.json.",
            expected_output="Lista co najmniej trzech różnych sposobów klasyfikacji przedmiotów. Każdy sposób powinien zawierać krótki opis oraz przykładowe przypisanie kilku przedmiotów do kategorii.",
            agent=self.classification_agent(),
            tools=[self.read_oguns_tool],
        )

    @agent
    def questionnaire_agent(self) -> Agent:
        return Agent(
            role="Generator pytań do użytkownika",
            goal="Na podstawie klasyfikacji przygotuj pytania, które pomogą określić preferencje użytkownika względem przedmiotów.",
            backstory="Jesteś specjalistą od UX i potrafisz zadawać dobre pytania, które pozwalają wyciągnąć preferencje użytkownika.",
            allow_delegation=False,
            verbose=True,
            llm=self.llm,
            tools=[self.read_oguns_tool, self.write_answers_tool],
        )

    @task
    def question_task(self) -> Task:
        return Task(
            description="Wczytaj classification_output.json i na ich podstawie przygotuj pytania dla użytkownika. Zapisz pytania w user_questionnaire.json i zbierz odpowiedzi przez input(). Wyniki zapisz do user_preferences.json.",
            expected_output="Plik user_preferences.json zawierający odpowiedzi użytkownika",
            agent=self.questionnaire_agent(),
            tools=[self.read_oguns_tool, self.write_answers_tool],
        )

    @agent
    def recommendation_agent(self) -> Agent:
        return Agent(
            role="Rekomendator przedmiotów",
            goal="Na podstawie preferencji użytkownika i klasyfikacji wybierz przedmioty najlepiej dopasowane do preferencji.",
            backstory="Jesteś doradcą akademickim i umiesz wybierać kursy najlepiej dopasowane do osoby na podstawie wcześniejszych danych.",
            allow_delegation=False,
            verbose=True,
            llm=self.llm,
            tools=[self.read_oguns_tool, self.read_answers_tool, self.write_oguns_tool],
        )

    @task
    def recommend_task(self) -> Task:
        return Task(
            description="Wczytaj oguny.json i user_preferences.json, a potem wygeneruj listę polecanych przedmiotów. Zapisz je do pliku recommended_oguns.txt.",
            expected_output="Lista polecanych przedmiotów w pliku recommended_oguns.txt",
            agent=self.recommendation_agent(),
            tools=[self.read_oguns_tool, self.read_answers_tool, self.write_oguns_tool],
        )

    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=[self.classification_agent(), self.questionnaire_agent(), self.recommendation_agent()],
            tasks=[self.classify_task(), self.question_task(), self.recommend_task()],
            verbose=True,
        )

#%%
if __name__ == '__main__':
    CrewObject = RecommendationCrew()
    result = CrewObject.crew().kickoff()
    print(result)
