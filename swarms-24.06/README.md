## Środa, 25 czerwca
### Opis
Na razie mamy architekturę zcentralizowaną:
w pętli uruchamiany jest niejawnie osobny swarm z CourseFiltrator i CourseSelector, a jego outputem zarządza RecommendationsManager. 
<br/>*(Niejawnie, bo to wszystko dzieje się w środku metody **RecommendationsManager.run**)*

Zastanowię się czy da się ten flow jakoś uprościć, na razie zrobiłem tak, żeby po prostu działało.

<br/>

### Komenda uruchamiania:
```bash
python recommendations_manager.py
```

<br/>

## Czwartek, 26 czerwca
### Opis
Agenci CourseRankers działają równolegle, na razie bez managera w postaci LLMa (pytanie na ile w ogóle jest potrzebny)

<br/>

### Komenda uruchamiania:
```bash
python get_best_courses_concurrently_local_LLM.py
```
