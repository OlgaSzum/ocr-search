# OCR Search Assistant

Minimalny asystent: OCR + text search + image search.
Bez trenowania modeli na starcie.

ocr-search to narzędzie wspomagające przeszukiwanie zbiorów obrazów archiwalnych poprzez połączenie trzech mechanizmów: OCR, wyszukiwania tekstowego oraz wyszukiwania obrazowego opartego na podobieństwie wizualnym. 

OCR wykorzystywany jest wyłącznie do pozyskania treści tekstowej widocznej na obrazach i wsparcia wyszukiwania. Wyszukiwanie tekstowe działa na podstawie wyników OCR, natomiast wyszukiwanie obrazowe opiera się na porównywaniu cech wizualnych (embeddingów), niezależnie od opisu tekstowego.

Szczególnym przypadkiem są szyldy i znaki graficzne, które traktowane są jako rozpoznawalne ikony wizualne, a nie problemy tekstowe. W ich przypadku metodologicznie właściwe jest wyszukiwanie podobieństwa obrazów, z OCR jako mechanizmem pomocniczym.

System ma charakter etapowy. Na etapie początkowym stosowane są lekkie i tanie obliczeniowo metody (embeddingi i wyszukiwanie podobieństwa). Trening pełnych modeli rozpoznawania przewidziany jest wyłącznie na późniejszy etap, po zgromadzeniu danych oraz uzyskaniu uzasadnienia jakościowego.

Wyniki generowane przez system mają charakter propozycji i wymagają każdorazowej weryfikacji przez użytkownika.
