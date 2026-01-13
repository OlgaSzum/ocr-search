### Zakres funkcjonalny
	•	Automatyczne pozyskiwanie treści tekstowej z obrazów (OCR).
	•	Wyszukiwanie tekstowe na podstawie wyników OCR.
	•	Wyszukiwanie obrazowe oparte na podobieństwie wizualnym (embeddingi).
	•	Obsługa materiałów archiwalnych (fotografie, skany, kadry).

### OCR
	•	OCR służy wyłącznie do indeksowania i wyszukiwania.
	•	Ze względu na jakość materiałów archiwalnych wyniki OCR mogą zawierać błędy i mają charakter danych pomocniczych.

### Wyszukiwanie tekstowe
	•	Zapytania użytkownika porównywane są z tekstem wcześniej rozpoznanym na obrazach przez moduł OCR.
	•	System pokazuje fragment rozpoznanego tekstu, na podstawie którego zwrócono dany obraz.

### Wyszukiwanie obrazowe
	•	Wyszukiwanie obrazowe opiera się na porównywaniu cech wizualnych, niezależnie od opisu tekstowego.
	•	Mechanizm ten służy do identyfikowania podobieństw wizualnych między obrazami.

### Szyldy i znaki graficzne
	•	Szyldy traktowane są jako rozpoznawalne ikony wizualne, a nie problemy tekstowe.
	•	Podstawową metodą jest wyszukiwanie podobieństwa obrazów, natomiast OCR pełni funkcję pomocniczą.

### Ograniczenia
	•	Na etapie początkowym nie przewiduje się automatycznego uczenia modeli.
	•	Trening pełnych modeli możliwy jest dopiero po zgromadzeniu danych oraz uzyskaniu uzasadnienia jakościowego.
