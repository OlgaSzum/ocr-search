# Architecture

Dokument opisuje logiczną architekturę asystenta OCR oraz wyszukiwania tekstowego i obrazowego. Architektura ma charakter modularny i etapowy, z naciskiem na prostotę oraz możliwość późniejszej rozbudowy.

## Przegląd
System składa się z trzech głównych warstw:
1. warstwy przetwarzania danych (OCR i embeddingi),
2. warstwy indeksowania i wyszukiwania,
3. warstwy interfejsu użytkownika.

Każdy komponent pełni ściśle określoną rolę i może być rozwijany niezależnie.

## Komponenty

### Wejście danych
- Materiały wizualne: fotografie, skany, kadry archiwalne.
- Dane wejściowe traktowane są jako niezmienne; system nie modyfikuje oryginalnych plików.

### OCR
- Zewnętrzna usługa OCR przetwarza obrazy i zwraca rozpoznany tekst.
- Wyniki OCR zapisywane są w postaci ustrukturyzowanej i wykorzystywane wyłącznie do indeksowania oraz wyszukiwania tekstowego.

### Przetwarzanie wizualne
- Obrazy (lub ich wycinki) przekształcane są do reprezentacji wektorowych (embeddingów).
- Embeddingi opisują cechy wizualne obrazu i stanowią podstawę wyszukiwania obrazowego.

### Indeks
- Tekst z OCR oraz embeddingi wizualne zapisywane są w jednym spójnym indeksie.
- Indeks umożliwia:
  - wyszukiwanie tekstowe na podstawie treści OCR,
  - wyszukiwanie obrazowe na podstawie podobieństwa wektorowego.

### Wyszukiwanie
- Wyszukiwanie tekstowe porównuje zapytania użytkownika z treściami OCR zapisanymi w indeksie.
- Wyszukiwanie obrazowe porównuje embedding zapytania z embeddingami zapisanymi w indeksie.
- Wyniki mają charakter rankingów podobieństwa.

### Interfejs użytkownika
- Użytkownik może:
  - wprowadzić zapytanie tekstowe,
  - wgrać obraz jako zapytanie wizualne.
- System prezentuje wyniki wraz z podstawowym kontekstem (np. fragmentem tekstu OCR).

## Szyldy i znaki graficzne
- Szyldy mogą być wyszukiwane zarówno na podstawie treści tekstowej (OCR), jak i podobieństwa wizualnego.
- W przypadku szyldów o prostej, czytelnej formie tekstowej mechanizm OCR może być wystarczający.
- Wyszukiwanie obrazowe stosowane jest jako uzupełnienie, w szczególności dla szyldów o charakterze graficznym, stylizowanym lub słabo czytelnym.
- Oba mechanizmy mogą działać równolegle, a ich wyniki wymagają oceny użytkownika.

## Podejście etapowe
- Architektura zakłada brak trenowania modeli na etapie początkowym.
- Rozwiązanie oparte na embeddingach umożliwia szybkie uruchomienie i niskie koszty.
- Ewentualna rozbudowa o trening modeli możliwa jest bez zmiany podstawowej struktury systemu.

## Zakres odpowiedzialności
- System odpowiada za indeksowanie i wyszukiwanie.
- Interpretacja wyników oraz decyzje merytoryczne pozostają po stronie użytkownika.
