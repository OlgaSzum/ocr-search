# GCP_SETUP.md
## Konfiguracja Google Cloud dla asystenta OCR i wyszukiwania

Dokument opisuje minimalne wymagania infrastrukturalne potrzebne do uruchomienia asystenta OCR oraz wyszukiwania tekstowego i obrazowego w środowisku Google Cloud. Przeznaczony jest dla zespołu IT / administratorów.

## 1. Konto i projekt Google Cloud
- Należy utworzyć konto Google Cloud (organizacyjne).
- W ramach konta należy założyć nowy projekt (np. `ocr-search`).
- Do projektu musi być podpięty billing.

Aktywny billing jest wymagany do korzystania z Cloud Vision API, również w przypadku użycia darmowego limitu.

## 2. Wymagane usługi (API)
## 2.1 Cloud Storage
Console → Cloud Storage → Buckets → Create
Ustawienia:
	•	Location type: Region  
	•	Region: europe-west4 (Netherlands)  
	•	Storage class: Standard  
	•	Access control: Uniform  
	•	Public access prevention: Enabled  
	•	Data protection:  
	•	Object versioning: OFF  
	•	Retention policy: OFF (jeśli brak wymagań formalnych)  
	•	Encryption: Google-managed encryption key (domyślne)  

Wymóg:  
	•	Bucket musi być regionalny (europe-west4).  
	•	Niedozwolone: Multi-region, Dual-region.  

## 2.2 Cloud Vision API (OCR)  
Console → APIs & Services → Enable APIs and Services  
Włącz:  
	•	Cloud Vision API  

Ustawienia:  
	•	Brak wyboru regionu po stronie API.  
	•	Lokalizacja danych wejściowych (Cloud Storage) determinuje rezydencję danych.  
	•	Obrazy muszą znajdować się w bucketach w europe-west4.  

Opcjonalnie:  
	•	Quotas: pozostawić domyślne   
  
## 2.3 Cloud Run (opcjonalnie – backend / API)  

Console → Cloud Run → Create service  

Ustawienia:  
	•	Region: europe-west4 (Netherlands)  
	•	Platform: Fully managed  
	•	CPU: 1 vCPU  
	•	Memory: 512 MiB  
	•	Autoscaling:  
	- Min instances: 0  
	- Max instances: 1  
	•	Ingress: All lub Internal (wg architektury)  
	•	Authentication: wg potrzeb projektu  

Wymóg:  
	•	Usługa musi być uruchomiona w europe-west4.  

## 3. Region i lokalizacja danych  
- Zasoby należy tworzyć w regionie europejskim.  
- Rekomendowany region: europe-west4 (Holandia).  

## 4. Dostęp i role
- Administrator projektu (IT).
- Użytkownicy końcowi (bez dostępu do konsoli GCP).

## 5. Limity i koszty
Cloud Vision API:
	•	Free tier: ok. 1000 obrazów OCR / miesiąc.
Zalecane:
	•	ustawienie budget alerts na niskim progu (np. 1–5 USD).
  
## Podsumowanie  
Minimalna konfiguracja obejmuje:  
	•	projekt GCP z billingiem,  
	•	Cloud Storage (regionalny: europe-west4),  
	•	Cloud Vision API,  
	•	opcjonalnie Cloud Run (europe-west4)  
