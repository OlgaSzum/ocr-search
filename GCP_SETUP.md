# GCP_SETUP.md
## Konfiguracja Google Cloud dla asystenta OCR i wyszukiwania

Dokument opisuje minimalne wymagania infrastrukturalne potrzebne do uruchomienia asystenta OCR oraz wyszukiwania tekstowego i obrazowego w środowisku Google Cloud. Przeznaczony jest dla zespołu IT / administratorów.

## 1. Konto i projekt Google Cloud
- Należy utworzyć konto Google Cloud (organizacyjne).
- W ramach konta należy założyć nowy projekt (np. `ocr-search`).
- Do projektu musi być podpięty billing.

Aktywny billing jest wymagany do korzystania z Cloud Vision API, również w przypadku użycia darmowego limitu.

## 2. Wymagane usługi (API)
- Cloud Vision API
- Cloud Storage
- Cloud Run (opcjonalnie)

## 3. Region i lokalizacja danych
- Zasoby należy tworzyć w regionie europejskim.
- Rekomendowany region: europe-west4 (Holandia).
- Dane muszą pozostawać w obrębie Unii Europejskiej.

## 4. Dostęp i role
- Administrator projektu (IT).
- Użytkownicy końcowi (bez dostępu do konsoli GCP).

## 5. Limity i koszty
- Cloud Vision API: ~1000 obrazów OCR / miesiąc (free tier).
- Zalecane alerty budżetowe z niskim progiem.

## Podsumowanie
Projekt GCP z billingiem, Cloud Vision API, Cloud Storage (opcjonalnie Cloud Run) w regionie europe-west4.
