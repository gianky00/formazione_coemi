# Report Audit su Licenza e Avvio dell'Applicazione

Questo documento analizza il comportamento dell'**interfaccia grafica utente (GUI)** dell'applicazione durante la fase di avvio e login, in relazione allo stato della licenza. Tutte le descrizioni si riferiscono a elementi visibili all'interno della finestra del programma.

### Definizioni dei Tipi di UI

-   **Etichetta di Stato (nel pannello):** Un'area di testo situata nel pannello blu a sinistra della schermata di login. Viene usata per mostrare i dettagli della licenza (nome cliente, scadenza, Hardware ID).
-   **Etichetta di Stato (inline):** Un messaggio di testo che appare direttamente all'interno del modulo di login per comunicare un errore che impedisce l'accesso.
-   **Finestra Pop-up:** Una nuova finestra di dialogo che appare al centro dello schermo, bloccando l'interazione con il resto dell'applicazione.

---

## Comportamenti dell'Interfaccia Utente

| Condizione Scatenante | Tipo di UI | Titolo della Finestra | Messaggio / Descrizione Visibile | Comportamento Risultante |
| :--- | :--- | :--- | :--- | :--- |
| **Licenza Valida** | Etichetta di Stato (nel pannello) | N/A | `Cliente: {Nome Cliente}\nScadenza: {Data Scadenza}\nHardware ID: {ID Hardware}` | Il modulo di login è attivo. L'utente può procedere. |
| **Licenza in Scadenza (< 7 gg.)** | Etichetta di Stato (nel pannello) | N/A | I dettagli della licenza sono mostrati in **colore giallo**. | Funzionalità normale, ma con un avviso visivo per l'utente. |
| **File `pyarmor.rkey` Mancante/Invalido**| Etichetta di Stato (inline) | N/A | `Licenza non valida o scaduta. Aggiornala per continuare.` | Il modulo di login è disabilitato. |
| **File `config.dat` Mancante** | Etichetta di Stato (nel pannello) | N/A | `Dettagli licenza non disponibili. Procedere con l'aggiornamento.` | L'utente può tentare il login, ma non vedrà i dettagli della licenza. |
| **ID Hardware non Corrispondente** | Finestra Pop-up | `Errore di Licenza` | `L'Hardware ID della licenza non corrisponde a quello di questa macchina...` | Il login è bloccato. L'utente non può procedere. |
| **Orologio di Sistema Non Sincronizzato** | Finestra Pop-up | `Errore di Sincronizzazione Ora` | `L'orologio del sistema non è sincronizzato...` | L'applicazione si chiude dopo la conferma dell'utente. |
| **Database Bloccato all'Avvio** | Finestra Pop-up | `Errore Critico Database` | `Impossibile avviare l'applicazione:\n\n{dettaglio}` | L'applicazione si chiude immediatamente. |
| **Aggiornamento Licenza: Successo** | Finestra Pop-up | `Successo` | `...È necessario riavviare l'applicazione per applicare le modifiche.` | Una finestra con il pulsante "Riavvia Ora" permette il riavvio automatico dell'applicazione. |
| **Aggiornamento Licenza: Fallimento** | Finestra Pop-up | `Errore Aggiornamento` | `{messaggio di errore specifico}` | L'utente torna alla schermata di login e può tentare nuovamente l'aggiornamento. |
| **Licenza Scaduta (in background)** | Finestra Pop-up | `Licenza Scaduta` | `La licenza è scaduta. L'applicazione verrà chiusa.` | L'utente viene disconnesso forzatamente e l'applicazione si chiude. |

---

## Riepilogo Funzionalità di Sicurezza Implementate

-   **Controllo Corrispondenza Hardware ID:** Al login, l'ID hardware della licenza viene verificato.
-   **Controllo Sincronizzazione Orologio:** All'avvio, l'ora di sistema viene confrontata con un server NTP per prevenire manomissioni.
-   **Controllo Scadenza in Tempo Reale:** Un timer verifica ogni ora la validità della licenza, disconnettendo l'utente se scade.
-   **Avviso Periodo di Grazia:** Una licenza vicina alla scadenza viene segnalata visivamente.
-   **Messaggi di Errore Sicuri:** Gli errori durante l'aggiornamento della licenza non espongono URL o dettagli tecnici.
-   **Riavvio Automatico Post-Aggiornamento:** Il processo di aggiornamento è stato reso più fluido con un riavvio automatico.
