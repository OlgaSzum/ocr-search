# OCR Search Assistant

Minimalny asystent: OCR + text search + image search.
Bez trenowania modeli na starcie.

ocr-search to narzędzie wspomagające przeszukiwanie zbiorów obrazów archiwalnych poprzez połączenie trzech mechanizmów: OCR, wyszukiwania tekstowego oraz wyszukiwania obrazowego opartego na podobieństwie wizualnym. 

OCR wykorzystywany jest wyłącznie do pozyskania treści tekstowej widocznej na obrazach i wsparcia wyszukiwania. Wyszukiwanie tekstowe działa na podstawie wyników OCR, natomiast wyszukiwanie obrazowe opiera się na porównywaniu cech wizualnych (embeddingów), niezależnie od opisu tekstowego.

Szczególnym przypadkiem są szyldy i znaki graficzne, które mogą mieć zarówno formę prostych napisów, jak i bardziej złożonych form wizualnych. W zależności od charakteru materiału wyszukiwanie może opierać się na OCR (dla szyldów czytelnych tekstowo) oraz na podobieństwie wizualnym (dla form graficznych), przy czym oba mechanizmy mogą się wzajemnie uzupełniać.

System ma charakter etapowy. Na etapie początkowym stosowane są lekkie i tanie obliczeniowo metody (embeddingi i wyszukiwanie podobieństwa). Trening pełnych modeli rozpoznawania przewidziany jest wyłącznie na późniejszy etap, po zgromadzeniu danych oraz uzyskaniu uzasadnienia jakościowego.

Wyniki generowane przez system mają charakter propozycji i wymagają każdorazowej weryfikacji przez użytkownika.
