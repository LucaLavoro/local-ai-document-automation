import ollama
import pdfplumber
import json
import os
import shutil
from pdf2image import convert_from_path
import pytesseract

# CONFIGURAZIONE PERCORSO TESSERACT (Modifica se lo hai installato altrove)
# Di solito è: C:\\Program Files\\Tesseract-OCR\\tesseract.exe
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# 1. CONFIGURAZIONE
PERCORSO_PDF_INPUT = "./documenti_da_processare/"
PERCORSO_PDF_OUTPUT = "./archivio_ordinato/"
MODELLO_LLM = "qwen2.5:7b" # Assicurati di averlo scaricato: ollama pull qwen2.5:7b

# 2. IL NUOVO PROMPT DI SISTEMA (Aggressivo e Specifico)
PROMPT_SISTEMA = """
Sei un esperto classificatore e estrattore di dati da documenti. 
Analizza il testo fornito e restituisci ESCLUSIVAMENTE un oggetto JSON valido con queste chiavi:
- "tipo_documento": Scegli SOLO una di queste opzioni esatte: 'Fattura', 'Contratto', 'Denuncia', 'Curriculum', 'Busta Paga', 'Altro'.
- "mittente": Il nome dell'azienda, dell'ente o della persona che ha emesso il documento. Se non chiaro, metti "Sconosciuto".
- "importo": Il valore numerico principale (es. totale fattura, stipendio netto). Se non è un documento finanziario, metti 0.0.
- "data": La data principale del documento in formato AAAA-MM-GG. Se non trovata, metti null.

REGOLE FERREE DI CLASSIFICAZIONE:
1. Se il testo contiene parole come "denuncia", "querela", "sinistro", "carabinieri", "polizia", classificato come 'Denuncia'.
2. Se contiene "curriculum", "esperienza lavorativa", "istruzione", "competenze", classificato come 'Curriculum'.
3. Se contiene "cedolino", "stipendio", "IRPEF", "trattenute", "datore di lavoro", classificato come 'Busta Paga'.
4. Restituisci SOLO il JSON. Niente markdown (```json), niente spiegazioni, niente testo aggiuntivo.
"""

def estrai_testo_da_pdf(percorso_file):
    """Estrae il testo da un PDF, usando OCR come fallback se è una scansione."""
    testo = ""
    
    # TENTATIVO 1: Lettura diretta (veloce, per PDF nativi)
    try:
        with pdfplumber.open(percorso_file) as pdf:
            for pagina in pdf.pages:
                testo += pagina.extract_text() + "\n"
    except Exception as e:
        print(f"[-] Errore pdfplumber: {e}")

    # CONTROLLO: Se il testo è troppo corto, probabilmente è una scansione
    if len(testo.strip()) < 50:
        print("[*] Testo insufficiente rilevato. Attivazione fallback OCR...")
        testo_ocr = ""
        try:
            # PERCORSO DI POPPLER (Modificalo se hai estratto Poppler altrove)
            PERCORSO_POPPLER = r"C:\poppler\Library\bin"
            
            # Converte il PDF in immagini usando Poppler
            immagini = convert_from_path(percorso_file, poppler_path=PERCORSO_POPPLER)
            
            for i, immagine in enumerate(immagini):
                # Esegue l'OCR sull'immagine
                testo_pagina = pytesseract.image_to_string(immagine, lang='ita')
                testo_ocr += testo_pagina + "\n"
            testo = testo_ocr
        except Exception as e:
            return f"ERRORE CRITICO OCR: {e}"
            
    return testo

def analizza_con_llm(testo):
    """Invia il testo a Ollama e forza la risposta JSON."""
    try:
        risposta = ollama.chat(model=MODELLO_LLM, messages=[
            {'role': 'system', 'content': PROMPT_SISTEMA},
            {'role': 'user', 'content': testo}
        ])
        contenuto = risposta['message']['content'].strip()
        
        # Pulizia robusta per rimuovere eventuali markdown residui
        if contenuto.startswith("```json"):
            contenuto = contenuto[7:]
        if contenuto.startswith("```"):
            contenuto = contenuto[3:]
        if contenuto.endswith("```"):
            contenuto = contenuto[:-3]
        
        return json.loads(contenuto.strip())
    except json.JSONDecodeError:
        return {"errore": "LLM non ha restituito JSON valido", "raw": contenuto}
    except Exception as e:
        return {"errore": str(e)}

def main():
    print("--- AVVIO MOTORE DI AUTOMAZIONE ---")
    os.makedirs(PERCORSO_PDF_INPUT, exist_ok=True)
    os.makedirs(PERCORSO_PDF_OUTPUT, exist_ok=True)

    for file_name in os.listdir(PERCORSO_PDF_INPUT):
        if file_name.endswith(".pdf"):
            percorso_completo = os.path.join(PERCORSO_PDF_INPUT, file_name)
            print(f"\n[+] Analisi in corso: {file_name}")
            
            # 1. Estrai
            testo = estrai_testo_da_pdf(percorso_completo)
            if testo.startswith("Errore"):
                print(testo)
                continue
                
            # DEBUG: Mostriamo cosa vede davvero l'IA
            print(f"[*] DEBUG TESTO ESTRATTO (primi 300 caratteri):\n{testo[:300].replace(chr(10), ' ')}...")
            
            # 2. Analizza
            print("[*] Interrogazione LLM Locale...")
            dati_estratti = analizza_con_llm(testo)
            print(f"[✓] Dati estratti: {dati_estratti}")
            
            # 3. Archivia
            tipo = dati_estratti.get("tipo_documento", "Altro").replace(" ", "_")
            # Gestione del caso in cui il tipo è None o vuoto
            if not tipo or tipo == "null":
                tipo = "Altro"
                
            cartella_destinazione = os.path.join(PERCORSO_PDF_OUTPUT, tipo)
            os.makedirs(cartella_destinazione, exist_ok=True)
            
            shutil.move(percorso_completo, os.path.join(cartella_destinazione, file_name))
            print(f"[✓] File spostato in: {cartella_destinazione}")

if __name__ == "__main__":
    main()