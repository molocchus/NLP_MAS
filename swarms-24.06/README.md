### Opis
Na razie mamy architekturę zcentralizowaną:
w pętli uruchamiany jest niejawnie osobny swarm z CourseFiltrator i CourseSelector, a jego outputem zarządza RecommendationsManager. 
<br/>*(Niejawnie, bo to wszystko dzieje się w środku metody **RecommendationsManager.run**)*

Zastanowię się czy da się ten flow jakoś uprościć, na razie zrobiłem tak, żeby po prostu działało.

<br/>

### Komenda uruchamiania:
```bash
python3 recommendations_manager.py
```
