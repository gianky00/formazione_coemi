#!/usr/bin/env python3
"""
SonarCloud ULTRA-COMPLETE Exporter per Jules (Google AI Agent)
===============================================================
Versione: 5.0 - DEFINITIVA COMPLETA CON TEST FAILURES

Esporta TUTTO da SonarCloud + dettagli test da junit.xml:
- Issues (RELIABILITY, SECURITY, MAINTAINABILITY)
- Security Hotspots
- Test Results con DETTAGLI COMPLETI (da junit.xml)
- Coverage details
- Quality Gate status

Output (salvati in OUTPUT_SALVATAGGIO):
1. SUMMARY_*.md - Riepilogo completo con statistiche e prompt
2. JULES_TEST_FAILURES_*.md - Test falliti con stack trace e suggerimenti
3. JULES_HOTSPOTS_*.md - Security Hotspots da revieware
4. JULES_RELIABILITY_ONLY_*.md - Bug di affidabilità
5. JULES_SECURITY_ONLY_*.md - Vulnerabilità (se presenti)
6. JULES_COMPACT_*.md - Tutti gli issues in formato compatto
7. JULES_ULTRA_COMPLETE_*.md - Tutti gli issues con TUTTE le informazioni
8. JULES_PROMPTS_*.md - Prompt ottimizzati per Jules

Requisiti: pip install requests
"""

import requests
import time
import re
import os
import json
import xml.etree.ElementTree as ET
from collections import defaultdict, Counter
from datetime import datetime
from functools import wraps
from pathlib import Path
import sys
import getpass  # Libreria per inserire password in modo sicuro

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
# ============================================================
# CONFIGURAZIONE SICURA
# ============================================================
SONARCLOUD_URL = "https://sonarcloud.io"
PROJECT_KEY = "gianky00_formazione_coemi"
ORGANIZATION = "gianky00"

# 1. Prova a prendere il token dall'ambiente (CI/CD GitHub o Env Variabili)
TOKEN = os.getenv("SONAR_TOKEN")

# 2. Se non lo trova (siamo in locale e senza file), lo chiede all'utente
if not TOKEN:
    print("⚠️  Nessun token rilevato nell'ambiente.")
    print("   Per evitare di inserirlo ogni volta, puoi impostare la variabile d'ambiente SONAR_TOKEN sul tuo OS.")
    try:
        # getpass nasconde quello che scrivi per sicurezza
        TOKEN = getpass.getpass("🔑 Inserisci ora il tuo SonarCloud Token (invio per confermare): ").strip()
    except Exception:
        pass

# 3. Controllo finale
if not TOKEN:
    print("\n❌ ERRORE: Token mancante. Impossibile contattare SonarCloud.")
    sys.exit(1)
# 4. Definisci i percorsi usando PROJECT_ROOT
# In questo modo salverà sempre in formazione_coemi/docs/bug
OUTPUT_SALVATAGGIO = os.path.join(PROJECT_ROOT, "docs", "bug")

# Cerca junit.xml nella root del progetto (dove lo crea pytest)
JUNIT_XML_PATH = os.path.join(PROJECT_ROOT, "junit.xml")

# Tipi di issues da esportare
SOFTWARE_QUALITIES = ['RELIABILITY', 'SECURITY', 'MAINTAINABILITY']

# Stati degli issues da includere (come su SonarCloud web)
ISSUE_STATUSES = 'OPEN,CONFIRMED,REOPENED'

# Recupera codice sorgente per questi tipi
FETCH_SOURCE_FOR = ['RELIABILITY', 'SECURITY', 'MAINTAINABILITY']

# Genera file separati per questi tipi
GENERATE_SEPARATE_FILES_FOR = ['RELIABILITY', 'SECURITY']

# Configurazione retry
MAX_RETRIES = 3
RETRY_DELAY = 2
REQUEST_TIMEOUT = 30

# Security Hotspots
HOTSPOT_STATUSES = 'TO_REVIEW'
# ============================================================

API_ISSUES = f"{SONARCLOUD_URL}/api/issues/search"
API_RULES = f"{SONARCLOUD_URL}/api/rules/show"
API_SOURCES = f"{SONARCLOUD_URL}/api/sources/lines"
API_HOTSPOTS = f"{SONARCLOUD_URL}/api/hotspots/search"
API_HOTSPOT_DETAIL = f"{SONARCLOUD_URL}/api/hotspots/show"
API_MEASURES = f"{SONARCLOUD_URL}/api/measures/component"
API_QUALITY_GATE = f"{SONARCLOUD_URL}/api/qualitygates/project_status"
HEADERS = {'Authorization': f'Bearer {TOKEN}'}
PAGE_SIZE = 500

# Cache e dati globali
rules_cache = {}
source_cache = {}
test_metrics = {}
quality_gate = {}
coverage_metrics = {}
test_failures_details = []  # Dettagli dai junit.xml

stats = {
    'api_calls': 0,
    'api_errors': 0,
    'retries': 0,
    'start_time': None,
    'end_time': None
}


# ============================================================
# UTILITY FUNCTIONS
# ============================================================

def retry_with_backoff(max_retries=MAX_RETRIES, base_delay=RETRY_DELAY):
    """Decorator per retry con backoff esponenziale."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except (requests.exceptions.RequestException,) as e:
                    stats['retries'] += 1
                    if attempt < max_retries - 1:
                        delay = base_delay * (2 ** attempt)
                        time.sleep(delay)
            stats['api_errors'] += 1
            return None
        return wrapper
    return decorator


def validate_configuration():
    """Valida la configurazione."""
    errors = []
    warnings = []
    
    if not PROJECT_KEY or PROJECT_KEY == "your_project_key":
        errors.append("PROJECT_KEY non configurato")
    if not ORGANIZATION or ORGANIZATION == "your_organization":
        errors.append("ORGANIZATION non configurato")
    if not TOKEN or len(TOKEN) < 20:
        errors.append("TOKEN non configurato")
    if PROJECT_KEY and ':' in PROJECT_KEY:
        warnings.append("PROJECT_KEY contiene ':' - usa '_'")
    
    return errors, warnings


def ensure_output_directory():
    """Crea la cartella di output."""
    if OUTPUT_SALVATAGGIO:
        os.makedirs(OUTPUT_SALVATAGGIO, exist_ok=True)
        return os.path.abspath(OUTPUT_SALVATAGGIO)
    return os.getcwd()


def get_output_path(filename):
    """Percorso completo file output."""
    if OUTPUT_SALVATAGGIO:
        return os.path.join(OUTPUT_SALVATAGGIO, filename)
    return filename


def parse_effort(effort_str):
    """Converte effort in minuti."""
    if not effort_str:
        return 0
    total = 0
    effort_str = effort_str.lower()
    h = re.search(r'(\d+)\s*h', effort_str)
    m = re.search(r'(\d+)\s*min', effort_str)
    d = re.search(r'(\d+)\s*d', effort_str)
    if h: total += int(h.group(1)) * 60
    if m: total += int(m.group(1))
    if d: total += int(d.group(1)) * 8 * 60
    return total


def format_duration(minutes):
    """Formatta minuti in stringa."""
    if minutes == 0:
        return "N/A"
    days = minutes // (8 * 60)
    remaining = minutes % (8 * 60)
    hours = remaining // 60
    mins = remaining % 60
    parts = []
    if days > 0: parts.append(f"{days}g")
    if hours > 0: parts.append(f"{hours}h")
    if mins > 0: parts.append(f"{mins}min")
    return " ".join(parts) if parts else "< 1min"


def clean_html(text, preserve_code_blocks=True):
    """Pulisce HTML in Markdown."""
    if not text:
        return ""
    
    code_blocks = []
    if preserve_code_blocks:
        code_blocks = re.findall(r'<pre[^>]*>(.*?)</pre>', text, flags=re.DOTALL)
        for i, block in enumerate(code_blocks):
            text = re.sub(r'<pre[^>]*>' + re.escape(block) + r'</pre>', f"__CODE_BLOCK_{i}__", text, count=1)
    
    text = re.sub(r'<code[^>]*>(.*?)</code>', r'`\1`', text)
    text = re.sub(r'<strong[^>]*>(.*?)</strong>', r'**\1**', text)
    text = re.sub(r'<em[^>]*>(.*?)</em>', r'*\1*', text)
    text = re.sub(r'<h[234][^>]*>(.*?)</h[234]>', r'\n### \1\n', text)
    text = re.sub(r'<li[^>]*>(.*?)</li>', r'- \1\n', text, flags=re.DOTALL)
    text = re.sub(r'<p[^>]*>(.*?)</p>', r'\1\n\n', text, flags=re.DOTALL)
    text = re.sub(r'<br\s*/?>', '\n', text)
    text = re.sub(r'<a[^>]*href="([^"]*)"[^>]*>(.*?)</a>', r'[\2](\1)', text)
    text = re.sub(r'<[^>]+>', '', text)
    
    entities = {'&nbsp;': ' ', '&lt;': '<', '&gt;': '>', '&amp;': '&', '&quot;': '"', '&#39;': "'"}
    for e, c in entities.items():
        text = text.replace(e, c)
    
    for i, block in enumerate(code_blocks):
        clean_block = re.sub(r'<[^>]+>', '', block)
        text = text.replace(f"__CODE_BLOCK_{i}__", f"\n```\n{clean_block.strip()}\n```\n")
    
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()


def get_severity_emoji(severity):
    return {'BLOCKER': '🔴', 'CRITICAL': '🔴', 'MAJOR': '🟡', 'MINOR': '🟢', 'INFO': '⚪'}.get(severity, '⚪')

def get_quality_emoji(quality):
    return {'RELIABILITY': '🔴', 'SECURITY': '🟣', 'MAINTAINABILITY': '🟡'}.get(quality, '⚪')

def get_quality_description(quality):
    return {
        'RELIABILITY': 'Bug che possono causare crash o comportamenti errati',
        'SECURITY': 'Vulnerabilità di sicurezza',
        'MAINTAINABILITY': 'Code smell che rendono il codice difficile da mantenere'
    }.get(quality, '')

def get_hotspot_risk_emoji(risk):
    return {'HIGH': '🔴', 'MEDIUM': '🟡', 'LOW': '🟢'}.get(risk, '⚪')

def get_hotspot_category_description(category):
    return {
        'auth': 'Autenticazione - Password/API key hardcoded',
        'weak-cryptography': 'Crittografia debole - random non sicuro',
        'dos': 'Denial of Service - Regex vulnerabile (ReDoS)',
        'sql-injection': 'SQL Injection',
        'xss': 'Cross-Site Scripting',
        'path-traversal': 'Path Traversal',
        'command-injection': 'Command Injection',
        'insecure-conf': 'Configurazione insicura',
        'others': 'Altri problemi di sicurezza'
    }.get(category, 'Problema di sicurezza')

def detect_language(file_path):
    """Rileva linguaggio dal file."""
    ext_map = {
        '.py': 'python', '.js': 'javascript', '.jsx': 'jsx', '.ts': 'typescript',
        '.tsx': 'tsx', '.java': 'java', '.go': 'go', '.rb': 'ruby', '.php': 'php',
        '.yml': 'yaml', '.yaml': 'yaml', '.json': 'json', '.xml': 'xml'
    }
    for ext, lang in ext_map.items():
        if file_path.lower().endswith(ext):
            return lang
    return ''

def get_error_type_info(error_type):
    """Restituisce informazioni dettagliate sul tipo di errore per i test."""
    error_info = {
        'AssertionError': {
            'emoji': '❌',
            'description': 'Il test ha verificato una condizione che si è rivelata falsa',
            'cause': 'Il valore atteso non corrisponde al valore ottenuto',
            'how_to_fix': '''1. Verifica che il valore atteso nel test sia corretto
2. Se il test è corretto, il bug è nel codice sotto test - correggilo
3. Se il comportamento è cambiato intenzionalmente, aggiorna il test
4. Controlla se ci sono effetti collaterali o stato condiviso tra test''',
            'resources': ['https://docs.pytest.org/en/stable/how-to/assert.html']
        },
        'AttributeError': {
            'emoji': '🔍',
            'description': 'Tentativo di accedere a un attributo inesistente',
            'cause': 'L\'oggetto non ha l\'attributo richiesto, potrebbe essere None o di tipo errato',
            'how_to_fix': '''1. Verifica che l'oggetto non sia None prima di accedere all'attributo
2. Controlla il tipo dell'oggetto con isinstance()
3. Verifica che l'attributo esista nella classe/modulo
4. Usa getattr() con un valore di default se l'attributo è opzionale''',
            'resources': ['https://docs.python.org/3/library/functions.html#getattr']
        },
        'TypeError': {
            'emoji': '🔄',
            'description': 'Operazione su tipo di dato non supportato',
            'cause': 'Funzione chiamata con argomenti di tipo errato o operazione non valida per il tipo',
            'how_to_fix': '''1. Verifica i tipi degli argomenti passati alla funzione
2. Aggiungi type hints e usa mypy per verificare
3. Controlla che le conversioni di tipo siano corrette
4. Verifica che i mock restituiscano il tipo corretto''',
            'resources': ['https://docs.python.org/3/library/typing.html']
        },
        'ValueError': {
            'emoji': '📊',
            'description': 'Valore non valido per l\'operazione',
            'cause': 'Il valore passato è del tipo corretto ma non è accettabile',
            'how_to_fix': '''1. Verifica i vincoli sui valori (range, formato, etc.)
2. Aggiungi validazione input prima dell'operazione
3. Gestisci i casi edge (stringhe vuote, liste vuote, None)
4. Documenta i valori accettati nei docstring''',
            'resources': ['https://docs.python.org/3/library/exceptions.html#ValueError']
        },
        'KeyError': {
            'emoji': '🔑',
            'description': 'Chiave non trovata nel dizionario',
            'cause': 'Tentativo di accedere a una chiave che non esiste',
            'how_to_fix': '''1. Usa dict.get(key, default) invece di dict[key]
2. Verifica l'esistenza della chiave con "if key in dict"
3. Controlla che i dati di test contengano tutte le chiavi necessarie
4. Usa defaultdict se appropriato''',
            'resources': ['https://docs.python.org/3/library/stdtypes.html#dict.get']
        },
        'IndexError': {
            'emoji': '📍',
            'description': 'Indice fuori dai limiti della sequenza',
            'cause': 'Tentativo di accedere a un elemento con indice non valido',
            'how_to_fix': '''1. Verifica la lunghezza della lista prima dell'accesso
2. Usa try/except IndexError per gestire liste vuote
3. Controlla i casi edge: liste vuote, singolo elemento
4. Considera l'uso di slice invece di indici diretti''',
            'resources': ['https://docs.python.org/3/tutorial/errors.html']
        },
        'FileNotFoundError': {
            'emoji': '📁',
            'description': 'File o directory non trovato',
            'cause': 'Il percorso specificato non esiste',
            'how_to_fix': '''1. Verifica che i file di test esistano (fixtures)
2. Usa tmp_path fixture di pytest per file temporanei
3. Crea i file necessari nel setup del test
4. Usa Path.exists() per verificare l'esistenza prima dell'accesso''',
            'resources': ['https://docs.pytest.org/en/stable/how-to/tmp_path.html']
        },
        'ImportError': {
            'emoji': '📦',
            'description': 'Errore nell\'importazione di un modulo',
            'cause': 'Modulo non trovato o errore di sintassi nel modulo',
            'how_to_fix': '''1. Verifica che il modulo sia installato (pip install)
2. Controlla il PYTHONPATH e la struttura del progetto
3. Verifica che __init__.py esista nelle directory
4. Controlla errori di sintassi nel modulo importato''',
            'resources': ['https://docs.python.org/3/reference/import.html']
        },
        'ConnectionError': {
            'emoji': '🌐',
            'description': 'Errore di connessione di rete',
            'cause': 'Impossibile stabilire connessione con il server',
            'how_to_fix': '''1. Usa mock per le chiamate di rete nei test
2. Usa responses o httpretty per mockare HTTP
3. Verifica che i test non dipendano da servizi esterni
4. Usa fixtures per simulare risposte di rete''',
            'resources': ['https://docs.pytest.org/en/stable/how-to/monkeypatch.html']
        },
        'TimeoutError': {
            'emoji': '⏱️',
            'description': 'Operazione scaduta per timeout',
            'cause': 'L\'operazione ha impiegato troppo tempo',
            'how_to_fix': '''1. Mocka le operazioni lente nei test
2. Aumenta il timeout se necessario
3. Verifica che non ci siano deadlock
4. Usa pytest-timeout per impostare limiti''',
            'resources': ['https://pypi.org/project/pytest-timeout/']
        },
        'RuntimeError': {
            'emoji': '⚡',
            'description': 'Errore generico a runtime',
            'cause': 'Errore durante l\'esecuzione non coperto da altre eccezioni',
            'how_to_fix': '''1. Leggi il messaggio di errore per dettagli specifici
2. Verifica lo stato dell'applicazione prima dell'operazione
3. Controlla che le risorse siano inizializzate correttamente
4. Verifica l'ordine delle operazioni''',
            'resources': ['https://docs.python.org/3/library/exceptions.html#RuntimeError']
        },
        'PermissionError': {
            'emoji': '🔒',
            'description': 'Permessi insufficienti per l\'operazione',
            'cause': 'Non hai i permessi per accedere alla risorsa',
            'how_to_fix': '''1. Usa tmp_path di pytest per file temporanei
2. Non scrivere in directory di sistema nei test
3. Mocka le operazioni su file system
4. Verifica i permessi nelle CI/CD pipelines''',
            'resources': ['https://docs.pytest.org/en/stable/how-to/tmp_path.html']
        }
    }
    
    # Cerca match parziale
    for err_name, info in error_info.items():
        if err_name.lower() in error_type.lower():
            return info
    
    # Default generico
    return {
        'emoji': '❓',
        'description': 'Errore durante l\'esecuzione del test',
        'cause': 'Verifica il messaggio di errore e lo stack trace per dettagli',
        'how_to_fix': '''1. Leggi attentamente il messaggio di errore
2. Analizza lo stack trace per trovare la riga problematica
3. Verifica i dati di input del test
4. Controlla se il comportamento del codice è cambiato''',
        'resources': ['https://docs.pytest.org/en/stable/how-to/failures.html']
    }


# ============================================================
# JUNIT.XML PARSER
# ============================================================

def parse_junit_xml():
    """Parsa il file junit.xml e estrae i dettagli dei test falliti."""
    global test_failures_details
    test_failures_details = []
    
    # Cerca il file junit.xml
    junit_paths = [
        JUNIT_XML_PATH,
        os.path.join(os.path.dirname(__file__), JUNIT_XML_PATH),
        os.path.join(os.getcwd(), JUNIT_XML_PATH),
        'junit.xml',
        'test-results.xml',
        'report.xml'
    ]
    
    junit_file = None
    for path in junit_paths:
        if os.path.exists(path):
            junit_file = path
            break
    
    if not junit_file:
        return None
    
    try:
        tree = ET.parse(junit_file)
        root = tree.getroot()
        
        summary = {
            'file': junit_file,
            'total': 0,
            'passed': 0,
            'failures': 0,
            'errors': 0,
            'skipped': 0,
            'time': 0
        }
        
        # Cerca testsuites o testsuite
        testsuites = root.findall('.//testsuite')
        if not testsuites and root.tag == 'testsuite':
            testsuites = [root]
        
        for testsuite in testsuites:
            summary['total'] += int(testsuite.get('tests', 0))
            summary['failures'] += int(testsuite.get('failures', 0))
            summary['errors'] += int(testsuite.get('errors', 0))
            summary['skipped'] += int(testsuite.get('skipped', 0))
            summary['time'] += float(testsuite.get('time', 0))
            
            for testcase in testsuite.findall('testcase'):
                classname = testcase.get('classname', '')
                name = testcase.get('name', '')
                time_taken = float(testcase.get('time', 0))
                
                # Converti classname in filepath
                filepath = classname.replace('.', '/') + '.py'
                
                failure = testcase.find('failure')
                error = testcase.find('error')
                skipped = testcase.find('skipped')
                
                if failure is not None or error is not None:
                    element = failure if failure is not None else error
                    status = 'FAILURE' if failure is not None else 'ERROR'
                    
                    message = element.get('message', '')
                    full_text = element.text or ''
                    
                    # Estrai tipo di errore
                    error_type = element.get('type', '')
                    if not error_type and ':' in message:
                        error_type = message.split(':')[0].strip()
                    
                    # Estrai riga dal traceback
                    line_match = re.search(r':(\d+):', full_text)
                    line = int(line_match.group(1)) if line_match else None
                    
                    test_failures_details.append({
                        'classname': classname,
                        'name': name,
                        'filepath': filepath,
                        'line': line,
                        'time': time_taken,
                        'status': status,
                        'error_type': error_type,
                        'message': message,
                        'traceback': full_text.strip(),
                        'error_info': get_error_type_info(error_type)
                    })
        
        summary['passed'] = summary['total'] - summary['failures'] - summary['errors'] - summary['skipped']
        
        return summary
        
    except Exception as e:
        print(f"   ⚠️ Errore parsing junit.xml: {e}")
        return None


# ============================================================
# API FUNCTIONS
# ============================================================

@retry_with_backoff()
def api_request(url, params):
    """Richiesta API con retry."""
    stats['api_calls'] += 1
    response = requests.get(url, headers=HEADERS, params=params, timeout=REQUEST_TIMEOUT)
    response.raise_for_status()
    return response.json()


def get_rule_details_full(rule_key):
    """Recupera dettagli regola."""
    if rule_key in rules_cache:
        return rules_cache[rule_key]
    
    try:
        data = api_request(API_RULES, {'key': rule_key, 'organization': ORGANIZATION})
        if data:
            rule = data.get('rule', {})
            sections = {}
            for section in rule.get('descriptionSections', []):
                key = section.get('key', '')
                content = clean_html(section.get('content', ''))
                if content:
                    sections[key] = content
            
            rules_cache[rule_key] = {
                'name': rule.get('name', ''),
                'description': clean_html(rule.get('htmlDesc', '')),
                'how_to_fix': sections.get('how_to_fix', ''),
                'root_cause': sections.get('root_cause', ''),
                'resources': sections.get('resources', ''),
                'tags': rule.get('sysTags', []),
            }
            return rules_cache[rule_key]
    except:
        pass
    
    rules_cache[rule_key] = {'name': rule_key, 'description': '', 'how_to_fix': '', 'root_cause': '', 'resources': '', 'tags': []}
    return rules_cache[rule_key]


def get_source_lines(component, start_line, end_line, context=3):
    """Recupera codice sorgente."""
    cache_key = f"{component}:{start_line}-{end_line}"
    if cache_key in source_cache:
        return source_cache[cache_key]
    
    try:
        data = api_request(API_SOURCES, {'key': component, 'from': max(1, start_line - context), 'to': end_line + context})
        if data:
            lines = []
            for src in data.get('sources', []):
                line_num = src.get('line', 0)
                code = re.sub(r'<[^>]+>', '', src.get('code', ''))
                marker = " >>> " if start_line <= line_num <= end_line else "     "
                lines.append(f"{marker}{line_num}: {code}")
            source_cache[cache_key] = '\n'.join(lines)
            return source_cache[cache_key]
    except:
        pass
    return None


def fetch_test_metrics():
    """Recupera metriche test da SonarCloud."""
    global test_metrics
    try:
        data = api_request(API_MEASURES, {
            'component': PROJECT_KEY,
            'metricKeys': 'tests,test_failures,test_errors,test_success_density,skipped_tests,test_execution_time'
        })
        if data:
            for m in data.get('component', {}).get('measures', []):
                test_metrics[m.get('metric')] = m.get('value')
    except:
        pass
    return test_metrics


def fetch_coverage_metrics():
    """Recupera metriche coverage."""
    global coverage_metrics
    try:
        data = api_request(API_MEASURES, {
            'component': PROJECT_KEY,
            'metricKeys': 'coverage,line_coverage,branch_coverage,uncovered_lines,lines_to_cover'
        })
        if data:
            for m in data.get('component', {}).get('measures', []):
                coverage_metrics[m.get('metric')] = m.get('value')
    except:
        pass
    return coverage_metrics


def fetch_quality_gate():
    """Recupera Quality Gate."""
    global quality_gate
    try:
        data = api_request(API_QUALITY_GATE, {'projectKey': PROJECT_KEY})
        if data:
            quality_gate = data.get('projectStatus', {})
    except:
        pass
    return quality_gate


def test_connection():
    """Test connessione."""
    try:
        response = requests.get(API_ISSUES, headers=HEADERS,
            params={'componentKeys': PROJECT_KEY, 'ps': 1, 'statuses': ISSUE_STATUSES},
            timeout=REQUEST_TIMEOUT)
        if response.status_code == 200:
            return True, response.json()
        return False, f"HTTP {response.status_code}"
    except Exception as e:
        return False, str(e)


def fetch_all_issues():
    """Recupera tutti gli issues."""
    all_issues = []
    issues_count = {q: 0 for q in SOFTWARE_QUALITIES}
    
    for quality in SOFTWARE_QUALITIES:
        print(f"\n   Estrazione {quality}...")
        page = 1
        quality_count = 0
        
        while True:
            data = api_request(API_ISSUES, {
                'componentKeys': PROJECT_KEY,
                'impactSoftwareQualities': quality,
                'statuses': ISSUE_STATUSES,
                'ps': PAGE_SIZE,
                'p': page,
                'additionalFields': 'comments,rules'
            })
            
            if not data:
                break
            
            issues = data.get('issues', [])
            total = data.get('total', 0)
            
            for issue in issues:
                issue['software_quality'] = quality
            
            all_issues.extend(issues)
            quality_count += len(issues)
            
            if total > 0:
                print(f"      Pagina {page}: {len(issues)} issues (totale: {total})")
            
            if len(issues) < PAGE_SIZE:
                break
            page += 1
            time.sleep(0.1)
        
        issues_count[quality] = quality_count
        print(f"   {'✓' if quality_count else '○'} {quality}: {quality_count} issues")
    
    return all_issues, issues_count


def fetch_security_hotspots():
    """Recupera Security Hotspots."""
    all_hotspots = []
    print(f"\n   Estrazione Security Hotspots...")
    page = 1
    
    while True:
        data = api_request(API_HOTSPOTS, {
            'projectKey': PROJECT_KEY,
            'status': HOTSPOT_STATUSES,
            'ps': PAGE_SIZE,
            'p': page
        })
        
        if not data:
            break
        
        hotspots = data.get('hotspots', [])
        total = data.get('paging', {}).get('total', 0)
        all_hotspots.extend(hotspots)
        
        if page == 1 and total > 0:
            print(f"      Totale: {total} hotspots")
        
        if len(hotspots) < PAGE_SIZE:
            break
        page += 1
        time.sleep(0.1)
    
    print(f"   {'✓' if all_hotspots else '○'} Security Hotspots: {len(all_hotspots)}")
    return all_hotspots


def fetch_hotspot_details(hotspots):
    """Recupera dettagli hotspots."""
    if not hotspots:
        return
    
    print(f"\n   Recupero dettagli per {len(hotspots)} hotspots...")
    
    for i, hotspot in enumerate(hotspots):
        try:
            data = api_request(API_HOTSPOT_DETAIL, {'hotspot': hotspot.get('key', '')})
            if data:
                rule = data.get('rule', {})
                hotspot['rule_name'] = rule.get('name', '')
                hotspot['risk_description'] = clean_html(rule.get('riskDescription', ''))
                hotspot['vulnerability_description'] = clean_html(rule.get('vulnerabilityDescription', ''))
                hotspot['fix_recommendations'] = clean_html(rule.get('fixRecommendations', ''))
                
                component = hotspot.get('component', '')
                line = hotspot.get('line', 0)
                if line and component:
                    hotspot['source_code'] = get_source_lines(component, line, line, context=3)
        except:
            pass
        
        if (i + 1) % 5 == 0:
            print(f"      [{i+1}/{len(hotspots)}]", end="\r")
        time.sleep(0.05)
    
    print(f"   ✓ Completato: {len(hotspots)} hotspots                    ")


def fetch_rules(issues):
    """Recupera regole."""
    unique_rules = set(i.get('rule', '') for i in issues if i.get('rule'))
    if not unique_rules:
        return
    
    print(f"\n   Recupero dettagli per {len(unique_rules)} regole...")
    for i, rule_key in enumerate(unique_rules):
        get_rule_details_full(rule_key)
        print(f"      [{i+1}/{len(unique_rules)}]", end="\r")
        time.sleep(0.05)
    print(f"   ✓ Completato: {len(unique_rules)} regole                    ")


def fetch_source_code(issues):
    """Recupera codice sorgente."""
    target = [i for i in issues if i.get('software_quality') in FETCH_SOURCE_FOR]
    if not target:
        return
    
    print(f"\n   Recupero codice sorgente per {len(target)} issues...")
    for i, issue in enumerate(target):
        component = issue.get('component', '')
        line = issue.get('line', 0)
        if line and component:
            tr = issue.get('textRange', {})
            issue['source_code'] = get_source_lines(component, tr.get('startLine', line), tr.get('endLine', line), 2)
        if (i + 1) % 50 == 0:
            print(f"      [{i+1}/{len(target)}]", end="\r")
        time.sleep(0.03)
    print(f"   ✓ Completato: {len(target)} snippet                    ")


# ============================================================
# ANALYSIS
# ============================================================

def analyze_issues(issues):
    """Analizza issues."""
    analysis = {
        'total': len(issues),
        'by_quality': {},
        'by_severity': Counter(),
        'by_file': defaultdict(list),
        'by_rule': Counter(),
        'top_rules': [],
        'total_effort_minutes': 0,
        'effort_by_quality': {},
        'files_count': 0,
        'languages': Counter()
    }
    
    for q in SOFTWARE_QUALITIES:
        qi = [i for i in issues if i.get('software_quality') == q]
        effort = sum(parse_effort(i.get('effort', '')) for i in qi)
        analysis['by_quality'][q] = len(qi)
        analysis['effort_by_quality'][q] = effort
        analysis['total_effort_minutes'] += effort
    
    for issue in issues:
        analysis['by_severity'][issue.get('severity', 'INFO')] += 1
        fp = issue.get('component', '').replace(f"{PROJECT_KEY}:", "")
        analysis['by_file'][fp].append(issue)
        analysis['by_rule'][issue.get('rule', '')] += 1
        lang = detect_language(fp)
        if lang:
            analysis['languages'][lang] += 1
    
    analysis['files_count'] = len(analysis['by_file'])
    analysis['top_rules'] = analysis['by_rule'].most_common(10)
    return analysis


def analyze_hotspots(hotspots):
    """Analizza hotspots."""
    analysis = {
        'total': len(hotspots),
        'by_category': defaultdict(list),
        'by_risk': Counter(),
        'by_file': defaultdict(list)
    }
    
    for h in hotspots:
        cat = h.get('securityCategory', 'others')
        risk = h.get('vulnerabilityProbability', 'MEDIUM')
        fp = h.get('component', '').replace(f"{PROJECT_KEY}:", "")
        analysis['by_category'][cat].append(h)
        analysis['by_risk'][risk] += 1
        analysis['by_file'][fp].append(h)
    
    return analysis


def analyze_test_failures():
    """Analizza test failures."""
    if not test_failures_details:
        return None
    
    analysis = {
        'total': len(test_failures_details),
        'by_error_type': Counter(),
        'by_file': defaultdict(list),
        'failures': 0,
        'errors': 0
    }
    
    for t in test_failures_details:
        analysis['by_error_type'][t.get('error_type', 'Unknown')] += 1
        analysis['by_file'][t.get('filepath', '')].append(t)
        if t.get('status') == 'FAILURE':
            analysis['failures'] += 1
        else:
            analysis['errors'] += 1
    
    return analysis


def group_by_file(issues):
    by_file = defaultdict(list)
    for issue in issues:
        fp = issue.get('component', '').replace(f"{PROJECT_KEY}:", "")
        by_file[fp].append(issue)
    return by_file


# ============================================================
# FILE GENERATORS
# ============================================================

def generate_test_failures_file(junit_summary, test_analysis, timestamp):
    """Genera file JULES_TEST_FAILURES con tutti i dettagli."""
    if not test_failures_details:
        return None, 0
    
    md = []
    md.append("# 🧪 Test Failures - Fix Guide")
    md.append("")
    md.append(f"**Progetto:** {PROJECT_KEY}")
    md.append(f"**Data:** {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    md.append(f"**File sorgente:** {junit_summary.get('file', 'junit.xml')}")
    md.append("")
    
    # Statistiche
    md.append("## 📊 Statistiche Test")
    md.append("")
    md.append("| Metrica | Valore |")
    md.append("|---------|--------|")
    md.append(f"| Test totali | {junit_summary.get('total', 0)} |")
    md.append(f"| ✅ Passati | {junit_summary.get('passed', 0)} |")
    md.append(f"| ❌ Falliti | {junit_summary.get('failures', 0)} |")
    md.append(f"| 💥 Errori | {junit_summary.get('errors', 0)} |")
    md.append(f"| ⏭️ Skippati | {junit_summary.get('skipped', 0)} |")
    md.append(f"| ⏱️ Tempo | {junit_summary.get('time', 0):.2f}s |")
    success_rate = (junit_summary.get('passed', 0) / junit_summary.get('total', 1)) * 100
    md.append(f"| Success Rate | {success_rate:.1f}% |")
    md.append("")
    
    # Tipi di errore
    md.append("## 🏷️ Tipi di Errore")
    md.append("")
    md.append("| Tipo | Count | Descrizione |")
    md.append("|------|-------|-------------|")
    for error_type, count in test_analysis['by_error_type'].most_common():
        info = get_error_type_info(error_type)
        md.append(f"| {info['emoji']} {error_type} | {count} | {info['description'][:40]}... |")
    md.append("")
    
    # Istruzioni
    md.append("## 📝 Istruzioni per Jules")
    md.append("")
    md.append("Per ogni test fallito troverai:")
    md.append("- 📍 **Posizione**: File e nome del test")
    md.append("- ❌ **Errore**: Messaggio e tipo di errore")
    md.append("- 📜 **Stack Trace**: Traceback completo")
    md.append("- ❓ **Perché fallisce**: Spiegazione del tipo di errore")
    md.append("- ✅ **Come risolvere**: Suggerimenti specifici")
    md.append("- 📚 **Risorse**: Link utili")
    md.append("")
    md.append("---")
    md.append("")
    
    # Raggruppa per file
    for filepath, tests in sorted(test_analysis['by_file'].items()):
        md.append(f"## 📄 `{filepath}`")
        md.append(f"**{len(tests)} test falliti**")
        md.append("")
        
        for test in tests:
            name = test.get('name', '')
            error_type = test.get('error_type', 'Unknown')
            message = test.get('message', '')
            traceback = test.get('traceback', '')
            status = test.get('status', 'FAILURE')
            line = test.get('line')
            error_info = test.get('error_info', {})
            
            status_emoji = "❌" if status == 'FAILURE' else "💥"
            
            md.append(f"### {status_emoji} `{name}`")
            md.append("")
            
            # Info tabella
            md.append("| Campo | Valore |")
            md.append("|-------|--------|")
            md.append(f"| Test | `{test.get('classname', '')}::{name}` |")
            md.append(f"| Tipo Errore | {error_info.get('emoji', '❓')} {error_type} |")
            md.append(f"| Status | {status} |")
            if line:
                md.append(f"| Riga | {line} |")
            md.append(f"| Tempo | {test.get('time', 0):.3f}s |")
            md.append("")
            
            # Messaggio errore
            md.append("**❌ Messaggio di Errore:**")
            md.append("")
            md.append(f"```")
            md.append(message[:500] if message else "Nessun messaggio")
            md.append("```")
            md.append("")
            
            # Stack trace
            if traceback:
                md.append("**📜 Stack Trace:**")
                md.append("")
                md.append("```python")
                # Limita lunghezza traceback
                tb_lines = traceback.split('\n')
                if len(tb_lines) > 30:
                    md.append('\n'.join(tb_lines[:15]))
                    md.append("... (troncato) ...")
                    md.append('\n'.join(tb_lines[-10:]))
                else:
                    md.append(traceback)
                md.append("```")
                md.append("")
            
            # Perché fallisce
            md.append("**❓ Perché fallisce:**")
            md.append("")
            md.append(error_info.get('description', 'Errore durante esecuzione del test'))
            md.append("")
            md.append(f"**Causa probabile:** {error_info.get('cause', 'Verifica il messaggio di errore')}")
            md.append("")
            
            # Come risolvere
            md.append("**✅ Come risolvere:**")
            md.append("")
            md.append(error_info.get('how_to_fix', 'Analizza lo stack trace per identificare il problema'))
            md.append("")
            
            # Risorse
            if error_info.get('resources'):
                md.append("**📚 Risorse:**")
                md.append("")
                for resource in error_info.get('resources', []):
                    md.append(f"- {resource}")
                md.append("")
            
            md.append("---")
            md.append("")
    
    filename = f"JULES_TEST_FAILURES_{timestamp}.md"
    filepath = get_output_path(filename)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write('\n'.join(md))
    
    return filename, len(test_failures_details)


def generate_dynamic_prompts(issues, analysis, issues_count, hotspots, hotspot_analysis, junit_summary, test_analysis):
    """Genera prompt dinamici."""
    prompts = {}
    
    total_issues = analysis['total']
    total_effort = format_duration(analysis['total_effort_minutes'])
    total_hotspots = len(hotspots)
    total_test_failures = len(test_failures_details) if test_failures_details else 0
    
    # PROMPT PRINCIPALE
    prompts['main'] = f"""# 🎯 Prompt per Jules - Fix Completo

## Contesto
Repository con:
- **{total_issues} issues** di codice
- **{total_hotspots} security hotspots**
- **{total_test_failures} test falliti**

Tempo stimato: **{total_effort}**

## Priorità di correzione
"""
    
    if total_test_failures > 0:
        prompts['main'] += f"1. 🧪 **TEST FAILURES** ({total_test_failures}) - I test devono passare!\n"
    if total_hotspots > 0:
        prompts['main'] += f"2. 🔥 **SECURITY HOTSPOTS** ({total_hotspots}) - Vulnerabilità critiche\n"
    if issues_count.get('SECURITY', 0) > 0:
        prompts['main'] += f"3. 🟣 **SECURITY** ({issues_count['SECURITY']}) - Issues sicurezza\n"
    if issues_count.get('RELIABILITY', 0) > 0:
        prompts['main'] += f"4. 🔴 **RELIABILITY** ({issues_count['RELIABILITY']}) - Bug\n"
    if issues_count.get('MAINTAINABILITY', 0) > 0:
        prompts['main'] += f"5. 🟡 **MAINTAINABILITY** ({issues_count['MAINTAINABILITY']}) - Code smell\n"
    
    prompts['main'] += """
## Istruzioni
Per ogni problema:
1. Apri il file indicato
2. Vai alla riga specificata
3. Leggi "Perché è un problema"
4. Applica "Come risolvere"
5. Verifica che funzioni
"""

    # PROMPT TEST FAILURES
    if total_test_failures > 0:
        by_error = test_analysis['by_error_type'].most_common(5) if test_analysis else []
        
        prompts['test_failures'] = f"""# 🧪 Prompt per Jules - Fix Test Failures

## Obiettivo
Correggi tutti i **{total_test_failures} test falliti** per far passare la CI/CD.

## Tipi di errore trovati
"""
        for error_type, count in by_error:
            info = get_error_type_info(error_type)
            prompts['test_failures'] += f"- {info['emoji']} **{error_type}** ({count}x)\n"
        
        prompts['test_failures'] += f"""
## Strategia di fix

### Per AssertionError:
1. Verifica se il test o il codice è sbagliato
2. Se il comportamento è cambiato, aggiorna il test
3. Se il test è corretto, correggi il codice

### Per errori di tipo (TypeError, AttributeError, KeyError):
1. Controlla i tipi dei dati
2. Aggiungi controlli null/None
3. Verifica che i mock siano configurati correttamente

### Per errori di connessione/file:
1. Mocka le dipendenze esterne
2. Usa fixtures per dati di test
3. Non dipendere da risorse esterne

## File da modificare
"""
        if test_analysis:
            for filepath in list(test_analysis['by_file'].keys())[:10]:
                count = len(test_analysis['by_file'][filepath])
                prompts['test_failures'] += f"- `{filepath}` ({count} test)\n"
        
        prompts['test_failures'] += """
## Comando per verificare
```bash
pytest -v --tb=short
```

## Commit suggerito
```
git add -A && git commit -m "test: fix failing tests"
```
"""

    # PROMPT HOTSPOTS
    if total_hotspots > 0:
        prompts['hotspots'] = f"""# 🔥 Prompt per Jules - Fix Security Hotspots

## Obiettivo
Revisiona e correggi **{total_hotspots} Security Hotspots**.

## Categorie trovate
"""
        for cat, items in hotspot_analysis['by_category'].items():
            risk = items[0].get('vulnerabilityProbability', 'MEDIUM') if items else 'MEDIUM'
            emoji = get_hotspot_risk_emoji(risk)
            desc = get_hotspot_category_description(cat)
            prompts['hotspots'] += f"\n### {emoji} {cat.upper()} ({len(items)})\n{desc}\n"
        
        prompts['hotspots'] += """
## Istruzioni
1. Leggi la descrizione del rischio
2. Analizza il codice
3. Se è un vero problema → applica il fix
4. Se falso positivo → aggiungi `# NOSONAR` con commento
"""

    # PROMPT RAPIDO
    prompts['quick'] = f"""# ⚡ Prompt Rapido

Fix: {total_test_failures} test + {total_hotspots} hotspots + {total_issues} issues

Ordine:
1. 🧪 Test (devono passare!)
2. 🔥 Hotspots (sicurezza)
3. 🔴 Reliability (bug)
4. 🟡 Maintainability (smell)

Tempo: {total_effort}
"""

    # PROMPT PER QUALITY
    for quality in SOFTWARE_QUALITIES:
        count = issues_count.get(quality, 0)
        if count == 0:
            continue
        
        qi = [i for i in issues if i.get('software_quality') == quality]
        effort = format_duration(analysis['effort_by_quality'].get(quality, 0))
        emoji = get_quality_emoji(quality)
        desc = get_quality_description(quality)
        
        prompts[quality.lower()] = f"""# {emoji} Prompt per Jules - Fix {quality}

## Obiettivo
Correggi **{count} issues {quality}**
Tempo stimato: **{effort}**

## Descrizione
{desc}

## Istruzioni
1. Apri `JULES_{quality}_ONLY_*.md`
2. Per ogni issue: file → riga → fix
3. Testa dopo ogni modifica

## Commit
```
git add -A && git commit -m "fix({quality.lower()}): risolti {count} issues"
```
"""

    return prompts


def generate_summary(issues, analysis, issues_count, hotspots, hotspot_analysis, 
                     junit_summary, test_analysis, timestamp, generated_files):
    """Genera SUMMARY."""
    total_effort = format_duration(analysis['total_effort_minutes'])
    
    md = []
    md.append("# 📊 SonarCloud Analysis Summary")
    md.append("")
    md.append(f"**Progetto:** {PROJECT_KEY}")
    md.append(f"**Data:** {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    md.append(f"**Versione:** SonarCloud Exporter v5.0")
    md.append(f"**Filtro issues:** {ISSUE_STATUSES}")
    md.append("")
    md.append("---")
    md.append("")
    
    # Quality Gate
    if quality_gate:
        status = quality_gate.get('status', 'N/A')
        emoji = "✅" if status == "OK" else "❌"
        md.append(f"## 🚦 Quality Gate: {emoji} {status}")
        md.append("")
        conditions = quality_gate.get('conditions', [])
        if conditions:
            md.append("| Metrica | Valore | Soglia | Stato |")
            md.append("|---------|--------|--------|-------|")
            for c in conditions:
                c_emoji = "✅" if c.get('status') == "OK" else "❌"
                md.append(f"| {c.get('metricKey', '')} | {c.get('actualValue', 'N/A')} | {c.get('errorThreshold', 'N/A')} | {c_emoji} |")
            md.append("")
    
    # Test Results
    md.append("## 🧪 Test Results")
    md.append("")
    
    if junit_summary:
        md.append(f"**📁 Sorgente:** `{junit_summary.get('file', 'junit.xml')}`")
        md.append("")
        md.append("| Metrica | Valore |")
        md.append("|---------|--------|")
        md.append(f"| Test totali | {junit_summary.get('total', 0)} |")
        md.append(f"| ✅ Passati | {junit_summary.get('passed', 0)} |")
        md.append(f"| ❌ Falliti | {junit_summary.get('failures', 0)} |")
        md.append(f"| 💥 Errori | {junit_summary.get('errors', 0)} |")
        md.append(f"| ⏭️ Skippati | {junit_summary.get('skipped', 0)} |")
        md.append(f"| ⏱️ Tempo | {junit_summary.get('time', 0):.2f}s |")
        if junit_summary.get('total', 0) > 0:
            rate = (junit_summary.get('passed', 0) / junit_summary['total']) * 100
            md.append(f"| Success Rate | {rate:.1f}% |")
        md.append("")
        
        if test_analysis and test_analysis['by_error_type']:
            md.append("### Tipi di errore")
            md.append("")
            for error_type, count in test_analysis['by_error_type'].most_common(5):
                info = get_error_type_info(error_type)
                md.append(f"- {info['emoji']} **{error_type}**: {count}")
            md.append("")
    elif test_metrics:
        md.append("| Metrica | Valore |")
        md.append("|---------|--------|")
        md.append(f"| Test totali | {test_metrics.get('tests', 0)} |")
        md.append(f"| ❌ Falliti | {test_metrics.get('test_failures', 0)} |")
        md.append(f"| 💥 Errori | {test_metrics.get('test_errors', 0)} |")
        md.append(f"| Success Rate | {test_metrics.get('test_success_density', 'N/A')}% |")
        md.append("")
        md.append("⚠️ **Per dettagli completi dei test falliti:**")
        md.append("1. Esegui `pytest --junitxml=junit.xml`")
        md.append("2. Metti `junit.xml` nella stessa cartella dello script")
        md.append("3. Riesegui lo script")
        md.append("")
    else:
        md.append("⚠️ **Nessun dato test disponibile**")
        md.append("")
        md.append("Per abilitare:")
        md.append("1. `sonar-project.properties`: aggiungi `sonar.python.xunit.reportPath=junit.xml`")
        md.append("2. Esegui `pytest --junitxml=junit.xml`")
        md.append("")
    
    # Coverage
    if coverage_metrics:
        md.append("## 📈 Coverage")
        md.append("")
        md.append("| Metrica | Valore |")
        md.append("|---------|--------|")
        md.append(f"| Coverage totale | **{coverage_metrics.get('coverage', 'N/A')}%** |")
        md.append(f"| Line coverage | {coverage_metrics.get('line_coverage', 'N/A')}% |")
        if coverage_metrics.get('branch_coverage'):
            md.append(f"| Branch coverage | {coverage_metrics.get('branch_coverage', 'N/A')}% |")
        md.append(f"| Linee da coprire | {coverage_metrics.get('lines_to_cover', 'N/A')} |")
        md.append(f"| Non coperte | {coverage_metrics.get('uncovered_lines', 'N/A')} |")
        md.append("")
    
    # Issues
    md.append("## 📋 Issues")
    md.append("")
    md.append("| Categoria | Issues | Tempo | Priorità |")
    md.append("|-----------|--------|-------|----------|")
    priority_map = {'SECURITY': '🔴 CRITICA', 'RELIABILITY': '🟠 ALTA', 'MAINTAINABILITY': '🟡 MEDIA'}
    for q in SOFTWARE_QUALITIES:
        count = issues_count.get(q, 0)
        if count > 0:
            emoji = get_quality_emoji(q)
            effort = format_duration(analysis['effort_by_quality'].get(q, 0))
            md.append(f"| {emoji} {q} | {count} | {effort} | {priority_map.get(q, '')} |")
    md.append(f"| **TOTALE** | **{analysis['total']}** | **{total_effort}** | |")
    md.append("")
    
    # Hotspots
    if hotspots:
        md.append("## 🔥 Security Hotspots")
        md.append("")
        md.append(f"**Totale:** {len(hotspots)} da revieware")
        md.append("")
        md.append("| Categoria | Count | Rischio |")
        md.append("|-----------|-------|---------|")
        for cat, items in sorted(hotspot_analysis['by_category'].items(), key=lambda x: -len(x[1])):
            risk = items[0].get('vulnerabilityProbability', 'MEDIUM') if items else 'MEDIUM'
            emoji = get_hotspot_risk_emoji(risk)
            md.append(f"| {cat} | {len(items)} | {emoji} {risk} |")
        md.append("")
    
    # Top Rules
    if analysis['top_rules']:
        md.append("## 🏆 Top 10 Regole Violate")
        md.append("")
        md.append("| # | Regola | Count |")
        md.append("|---|--------|-------|")
        for i, (rule, count) in enumerate(analysis['top_rules'], 1):
            name = rules_cache.get(rule, {}).get('name', rule)[:40]
            md.append(f"| {i} | {name} | {count} |")
        md.append("")
    
    # Files
    md.append("## 📁 File Generati")
    md.append("")
    for fname, desc in generated_files:
        fpath = get_output_path(fname)
        if os.path.exists(fpath):
            size = os.path.getsize(fpath) / 1024
            md.append(f"- **{fname}** ({size:.1f} KB) - {desc}")
    md.append("")
    
    # Prompts
    prompts = generate_dynamic_prompts(issues, analysis, issues_count, hotspots, hotspot_analysis, junit_summary, test_analysis)
    
    md.append("---")
    md.append("")
    md.append("## 🤖 Prompt per Jules")
    md.append("")
    
    for name in ['main', 'test_failures', 'hotspots', 'quick']:
        if name in prompts:
            title = {'main': 'Principale', 'test_failures': '🧪 Test Failures', 'hotspots': '🔥 Hotspots', 'quick': '⚡ Rapido'}.get(name, name)
            md.append(f"### {title}")
            md.append("")
            md.append("```")
            md.append(prompts[name])
            md.append("```")
            md.append("")
    
    filename = f"SUMMARY_{timestamp}.md"
    with open(get_output_path(filename), 'w', encoding='utf-8') as f:
        f.write('\n'.join(md))
    
    return filename, prompts


def generate_prompts_file(prompts, timestamp):
    """Genera file prompts."""
    md = ["# 🤖 Prompt per Jules", "", f"**Data:** {datetime.now().strftime('%Y-%m-%d %H:%M')}", "", "---", ""]
    
    titles = {
        'main': '🎯 Principale',
        'test_failures': '🧪 Test Failures',
        'hotspots': '🔥 Security Hotspots',
        'quick': '⚡ Rapido',
        'reliability': '🔴 RELIABILITY',
        'security': '🟣 SECURITY',
        'maintainability': '🟡 MAINTAINABILITY'
    }
    
    for name, prompt in prompts.items():
        md.append(f"## {titles.get(name, name.upper())}")
        md.append("")
        md.append(prompt)
        md.append("")
        md.append("---")
        md.append("")
    
    filename = f"JULES_PROMPTS_{timestamp}.md"
    with open(get_output_path(filename), 'w', encoding='utf-8') as f:
        f.write('\n'.join(md))
    return filename


def generate_hotspots_file(hotspots, hotspot_analysis, timestamp):
    """Genera file hotspots."""
    if not hotspots:
        return None, 0
    
    md = ["# 🔥 Security Hotspots", "", f"**Totale:** {len(hotspots)}", ""]
    md.append("## Statistiche")
    md.append("")
    md.append("| Rischio | Count |")
    md.append("|---------|-------|")
    for risk in ['HIGH', 'MEDIUM', 'LOW']:
        count = hotspot_analysis['by_risk'].get(risk, 0)
        if count:
            md.append(f"| {get_hotspot_risk_emoji(risk)} {risk} | {count} |")
    md.append("")
    md.append("---")
    md.append("")
    
    for cat, items in sorted(hotspot_analysis['by_category'].items(), key=lambda x: -len(x[1])):
        desc = get_hotspot_category_description(cat)
        md.append(f"## 📁 {cat.upper()} ({len(items)})")
        md.append(f"**{desc}**")
        md.append("")
        
        for h in items:
            fp = h.get('component', '').replace(f"{PROJECT_KEY}:", "")
            line = h.get('line', '?')
            msg = h.get('message', '')
            risk = h.get('vulnerabilityProbability', 'MEDIUM')
            lang = detect_language(fp)
            
            md.append(f"### {get_hotspot_risk_emoji(risk)} `{fp}:{line}`")
            md.append("")
            md.append(f"**Problema:** {msg}")
            md.append("")
            
            if h.get('source_code'):
                md.append(f"```{lang}")
                md.append(h['source_code'])
                md.append("```")
                md.append("")
            
            if h.get('risk_description'):
                md.append("**❓ Rischio:**")
                md.append(h['risk_description'][:500])
                md.append("")
            
            if h.get('fix_recommendations'):
                md.append("**✅ Come risolvere:**")
                md.append(h['fix_recommendations'][:600])
                md.append("")
            
            md.append("---")
            md.append("")
    
    filename = f"JULES_HOTSPOTS_{timestamp}.md"
    with open(get_output_path(filename), 'w', encoding='utf-8') as f:
        f.write('\n'.join(md))
    return filename, len(hotspots)


def generate_quality_specific_file(issues, quality, output_file):
    """Genera file per quality specifica."""
    qi = [i for i in issues if i.get('software_quality') == quality]
    if not qi:
        return 0
    
    by_file = group_by_file(qi)
    effort = sum(parse_effort(i.get('effort', '')) for i in qi)
    emoji = get_quality_emoji(quality)
    
    md = [f"# {emoji} {quality} Issues", "", f"**Totale:** {len(qi)}", f"**Tempo:** {format_duration(effort)}", "", "---", ""]
    
    for fp, file_issues in sorted(by_file.items(), key=lambda x: -len(x[1])):
        lang = detect_language(fp)
        md.append(f"## 📄 `{fp}` ({len(file_issues)})")
        md.append("")
        
        for issue in sorted(file_issues, key=lambda x: x.get('line', 0) or 0):
            line = issue.get('line', '?')
            msg = issue.get('message', '')
            rule = issue.get('rule', '')
            severity = issue.get('severity', '')
            source = issue.get('source_code', '')
            rule_info = rules_cache.get(rule, {})
            
            md.append(f"### Riga {line} {get_severity_emoji(severity)}")
            md.append(f"**Problema:** {msg}")
            md.append("")
            
            if source:
                md.append(f"```{lang}")
                md.append(source)
                md.append("```")
                md.append("")
            
            if rule_info.get('root_cause'):
                md.append("**❓ Perché:**")
                md.append(rule_info['root_cause'][:600])
                md.append("")
            
            if rule_info.get('how_to_fix'):
                md.append("**✅ Come risolvere:**")
                md.append(rule_info['how_to_fix'][:800])
                md.append("")
            
            if rule_info.get('resources'):
                md.append("**📚 Risorse:**")
                md.append(rule_info['resources'][:400])
                md.append("")
            
            md.append("---")
            md.append("")
    
    with open(get_output_path(output_file), 'w', encoding='utf-8') as f:
        f.write('\n'.join(md))
    return len(qi)


def generate_compact(issues, output_file):
    """Genera file compatto."""
    by_file = group_by_file(issues)
    counts = {q: sum(1 for i in issues if i.get('software_quality') == q) for q in SOFTWARE_QUALITIES}
    
    md = ["# 📋 Quick Fix List", "", f"**Totale:** {len(issues)} issues", ""]
    for q in SOFTWARE_QUALITIES:
        if counts[q]:
            md.append(f"- {get_quality_emoji(q)} {q}: {counts[q]}")
    md.append("")
    md.append("---")
    md.append("")
    
    for fp, file_issues in sorted(by_file.items(), key=lambda x: -len(x[1])):
        md.append(f"### {fp}")
        for issue in sorted(file_issues, key=lambda x: x.get('line', 0) or 0):
            line = issue.get('line', '?')
            msg = issue.get('message', '')[:60]
            q = issue.get('software_quality', '')
            md.append(f"- **L{line}** {get_quality_emoji(q)} {msg}")
        md.append("")
    
    with open(get_output_path(output_file), 'w', encoding='utf-8') as f:
        f.write('\n'.join(md))
    return len(issues)


def generate_ultra_complete(issues, output_file):
    """Genera file ultra-completo."""
    by_file = group_by_file(issues)
    effort = sum(parse_effort(i.get('effort', '')) for i in issues)
    
    md = ["# 🔧 ULTRA-COMPLETE Fix Guide", "", f"**Totale:** {len(issues)} issues", f"**Tempo:** {format_duration(effort)}", "", "---", ""]
    
    for fp, file_issues in sorted(by_file.items(), key=lambda x: -len(x[1])):
        lang = detect_language(fp)
        md.append(f"## 📄 `{fp}`")
        md.append("")
        
        for issue in sorted(file_issues, key=lambda x: x.get('line', 0) or 0):
            line = issue.get('line', '?')
            msg = issue.get('message', '')
            rule = issue.get('rule', '')
            severity = issue.get('severity', '')
            quality = issue.get('software_quality', '')
            source = issue.get('source_code', '')
            rule_info = rules_cache.get(rule, {})
            
            md.append(f"### Riga {line} {get_quality_emoji(quality)} {get_severity_emoji(severity)}")
            md.append(f"**Problema:** {msg}")
            md.append(f"**Regola:** `{rule}` - {rule_info.get('name', '')}")
            md.append("")
            
            if source:
                md.append(f"```{lang}")
                md.append(source)
                md.append("```")
                md.append("")
            
            if rule_info.get('root_cause'):
                md.append("**❓ Perché è un problema:**")
                md.append(rule_info['root_cause'][:800])
                md.append("")
            
            if rule_info.get('how_to_fix'):
                md.append("**✅ Come risolvere:**")
                md.append(rule_info['how_to_fix'][:1000])
                md.append("")
            
            if rule_info.get('resources'):
                md.append("**📚 Risorse:**")
                md.append(rule_info['resources'][:500])
                md.append("")
            
            md.append("---")
            md.append("")
    
    with open(get_output_path(output_file), 'w', encoding='utf-8') as f:
        f.write('\n'.join(md))
    return len(issues)


# ============================================================
# MAIN
# ============================================================

def main():
    stats['start_time'] = datetime.now()
    
    print("=" * 70)
    print("🚀 SONARCLOUD ULTRA-COMPLETE EXPORTER v5.0")
    print("=" * 70)
    print(f"Progetto: {PROJECT_KEY}")
    print(f"Output: {OUTPUT_SALVATAGGIO}")
    print(f"JUnit XML: {JUNIT_XML_PATH}")
    print("=" * 70)
    
    # Validazione
    print("\n0. Validazione...")
    errors, warnings = validate_configuration()
    for w in warnings:
        print(f"   ⚠️ {w}")
    if errors:
        for e in errors:
            print(f"   ❌ {e}")
        return
    print("   ✓ OK")
    
    # Output directory
    print("\n1. Preparazione output...")
    output_dir = ensure_output_directory()
    print(f"   📁 {output_dir}")
    
    # Connessione
    print("\n2. Test connessione...")
    success, result = test_connection()
    if not success:
        print(f"   ❌ {result}")
        return
    print("   ✓ Connesso")
    
    # Metriche generali
    print("\n3. Recupero metriche...")
    fetch_test_metrics()
    fetch_coverage_metrics()
    fetch_quality_gate()
    
    # Parse junit.xml
    print("\n4. Parsing junit.xml...")
    junit_summary = parse_junit_xml()
    test_analysis = None
    
    if junit_summary:
        print(f"   ✓ {junit_summary['file']}")
        print(f"      Tests: {junit_summary['total']}, Failed: {junit_summary['failures']}, Errors: {junit_summary['errors']}")
        test_analysis = analyze_test_failures()
    else:
        print(f"   ○ junit.xml non trovato")
        print(f"      Per abilitare: pytest --junitxml=junit.xml")
    
    if test_metrics:
        print(f"   ✓ SonarCloud: {test_metrics.get('tests', 0)} test, {test_metrics.get('test_failures', 0)} falliti")
    
    if coverage_metrics:
        print(f"   ✓ Coverage: {coverage_metrics.get('coverage', 'N/A')}%")
    
    if quality_gate:
        status = quality_gate.get('status', 'N/A')
        print(f"   {'✓' if status == 'OK' else '✗'} Quality Gate: {status}")
    
    # Issues
    print("\n5. Estrazione issues...")
    all_issues, issues_count = fetch_all_issues()
    print(f"   ✓ Totale: {len(all_issues)}")
    
    # Hotspots
    print("\n6. Estrazione hotspots...")
    all_hotspots = fetch_security_hotspots()
    
    # Dettagli
    if all_issues:
        print("\n7. Recupero regole...")
        fetch_rules(all_issues)
        print("\n8. Recupero codice...")
        fetch_source_code(all_issues)
    
    if all_hotspots:
        print("\n9. Dettagli hotspots...")
        fetch_hotspot_details(all_hotspots)
    
    # Analisi
    print("\n10. Analisi...")
    analysis = analyze_issues(all_issues) if all_issues else {
        'total': 0, 'by_quality': {}, 'by_severity': Counter(), 'by_file': {},
        'by_rule': Counter(), 'top_rules': [], 'total_effort_minutes': 0,
        'effort_by_quality': {}, 'files_count': 0, 'languages': Counter()
    }
    hotspot_analysis = analyze_hotspots(all_hotspots)
    
    print(f"   ✓ {analysis['total']} issues, {len(all_hotspots)} hotspots, {len(test_failures_details)} test falliti")
    
    # Genera file
    print("\n11. Generazione file...")
    timestamp = datetime.now().strftime('%Y%m%d_%H%M')
    generated_files = []
    
    # Test failures
    if test_failures_details:
        fname, count = generate_test_failures_file(junit_summary, test_analysis, timestamp)
        if fname:
            size = os.path.getsize(get_output_path(fname)) / 1024
            print(f"   ✓ {fname} ({count} test, {size:.1f} KB)")
            generated_files.append((fname, f"{count} test falliti con dettagli"))
    
    # Hotspots
    if all_hotspots:
        fname, count = generate_hotspots_file(all_hotspots, hotspot_analysis, timestamp)
        if fname:
            size = os.path.getsize(get_output_path(fname)) / 1024
            print(f"   ✓ {fname} ({count} hotspots, {size:.1f} KB)")
            generated_files.append((fname, f"{count} security hotspots"))
    
    # Quality specific
    for q in GENERATE_SEPARATE_FILES_FOR:
        if issues_count.get(q, 0) > 0:
            fname = f"JULES_{q}_ONLY_{timestamp}.md"
            count = generate_quality_specific_file(all_issues, q, fname)
            size = os.path.getsize(get_output_path(fname)) / 1024
            print(f"   ✓ {fname} ({count} issues, {size:.1f} KB)")
            generated_files.append((fname, f"{count} issues {q}"))
    
    # Compact & Ultra
    if all_issues:
        fname = f"JULES_COMPACT_{timestamp}.md"
        count = generate_compact(all_issues, fname)
        size = os.path.getsize(get_output_path(fname)) / 1024
        print(f"   ✓ {fname} ({count} issues, {size:.1f} KB)")
        generated_files.append((fname, "Quick reference"))
        
        fname = f"JULES_ULTRA_COMPLETE_{timestamp}.md"
        count = generate_ultra_complete(all_issues, fname)
        size = os.path.getsize(get_output_path(fname)) / 1024
        print(f"   ✓ {fname} ({count} issues, {size:.1f} KB)")
        generated_files.append((fname, "Documentazione completa"))
    
    # Summary & Prompts
    print("\n12. Summary e Prompts...")
    fname_summary, prompts = generate_summary(
        all_issues, analysis, issues_count, all_hotspots, hotspot_analysis,
        junit_summary, test_analysis, timestamp, generated_files
    )
    print(f"   ✓ {fname_summary}")
    
    fname_prompts = generate_prompts_file(prompts, timestamp)
    print(f"   ✓ {fname_prompts}")
    
    # Fine
    stats['end_time'] = datetime.now()
    duration = (stats['end_time'] - stats['start_time']).total_seconds()
    
    print("\n" + "=" * 70)
    print("✅ COMPLETATO!")
    print("=" * 70)
    print(f"\n📊 Durata: {duration:.1f}s | API: {stats['api_calls']} | Retry: {stats['retries']}")
    print(f"\n📁 Output: {output_dir}")
    
    # Riepilogo
    print("\n📌 FILE GENERATI:")
    if test_failures_details:
        print(f"   🧪 JULES_TEST_FAILURES_{timestamp}.md - {len(test_failures_details)} test falliti")
    if all_hotspots:
        print(f"   🔥 JULES_HOTSPOTS_{timestamp}.md - {len(all_hotspots)} hotspots")
    for q in GENERATE_SEPARATE_FILES_FOR:
        if issues_count.get(q, 0) > 0:
            print(f"   {get_quality_emoji(q)} JULES_{q}_ONLY_{timestamp}.md")
    if all_issues:
        print(f"   📄 JULES_COMPACT_{timestamp}.md")
        print(f"   📚 JULES_ULTRA_COMPLETE_{timestamp}.md")
    print(f"   📊 {fname_summary}")
    print(f"   🤖 {fname_prompts}")
    
    print("\n" + "=" * 70)
    print("💡 ORDINE CONSIGLIATO:")
    print("=" * 70)
    order = 1
    if test_failures_details:
        print(f"   {order}. 🧪 TEST FAILURES - I test devono passare!")
        order += 1
    if all_hotspots:
        print(f"   {order}. 🔥 HOTSPOTS - Sicurezza")
        order += 1
    for q in ['SECURITY', 'RELIABILITY', 'MAINTAINABILITY']:
        if issues_count.get(q, 0) > 0:
            print(f"   {order}. {get_quality_emoji(q)} {q}")
            order += 1
    
    print(f"\nTempo stimato: {format_duration(analysis['total_effort_minutes'])}")
    print("=" * 70)


if __name__ == "__main__":
    main()