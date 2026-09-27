🤖 Local AI Document Automation Engine

Un motore di automazione documentale progettato per le PMI che necessitano di elaborare dati sensibili mantenendo la conformità GDPR al 100%.
Il sistema legge, classifica ed estrae dati da documenti non strutturati (PDF, scansioni) utilizzando Large Language Models (LLM) eseguiti interamente in locale (On-Premise). Nessun dato viene mai inviato a server cloud esterni.

🎯 Caso d'Uso (Business Value)

Le aziende ricevono quotidianamente decine di documenti (fatture, contratti, denunce, buste paga). L'inserimento manuale è lento, costoso e soggetto a errori. 
Questo sistema:
Monitora una cartella o una casella email.

Riconosce il tipo di documento (anche se è una scansione/image-only tramite OCR).

Estrae metadati chiave (Mittente, Importo, Data).

Archivia automaticamente il file nella cartella corretta.

Invia un report strutturato via Telegram.

🛠️ Stack Tecnologico

Linguaggio: Python 3.10+

AI Engine: Ollama (Llama-3 / Qwen-2.5) - 100% Local & Private

OCR Engine: Tesseract + Poppler (Per scansioni e immagini)

Alerting: Telegram Bot API

🚀 Installazione e Setup

(Istruzioni brevi per mostrare che sai documentare)
1) Installare Ollama e scaricare il modello: ollama pull qwen2.5:7b
2) Installare Tesseract OCR e Poppler per Windows/Linux.
3) Installare le dipendenze Python:

   pip install -r requirements.txt

4) Eseguire lo script:
   
   python src/motore_automazione.py

Sicurezza e Privacy
Questo progetto è stato architettato con il principio Zero-Cloud. Tutti i modelli AI girano sull'hardware locale del cliente. Ideale per studi legali, medici, commercialisti e aziende manifatturiere che gestiscono dati sensibili.
