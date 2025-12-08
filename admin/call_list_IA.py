import google.generativeai as genai

# --- CONFIGURAZIONE ---
import os
# Incolla la tua API Key qui sotto tra le virgolette
api_key = os.getenv("IA_API_KEY", "INSERISCI_API_KEY") # NOSONAR

genai.configure(api_key=api_key)

print("Sto recuperando la lista dei modelli disponibili...")
print("-" * 50)

try:
    count = 0
    # Itera su tutti i modelli e filtra quelli che supportano la generazione di testo
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(f"Nome modello: {m.name}")
            count += 1
            
    if count == 0:
        print("Nessun modello trovato.")
    else:
        print("-" * 50)
        print(f"Trovati {count} modelli utilizzabili.")
        print("Copia uno dei nomi sopra (es: models/gemini-1.5-flash) per usarlo nel tuo codice.")

except Exception as e:
    print(f"Errore durante la ricerca: {e}")