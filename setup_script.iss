; Script generato per Intelleo (Formazione Coemi)
; Compatibile con struttura PyInstaller OneDir

#define MyAppName "Intelleo"
#define MyAppVersion "1.0"
#define MyAppPublisher "Giancarlo Allegretti"
#define MyAppURL "https://github.com/gianky00/formazione_coemi"
#define MyAppExeName "Intelleo.exe"
; Cartella dove si trova l'output di PyInstaller (modificare se diverso)
#define BuildDir "dist\Intelleo"

[Setup]
; ID univoco per l'applicazione (generato casualmente, non cambiarlo per aggiornamenti futuri)
AppId={{A1B2C3D4-E5F6-7890-1234-567890ABCDEF}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
; Installa in C:\Program Files\Intelleo
DefaultDirName={autopf}\{#MyAppName}
DisableProgramGroupPage=yes
; Crea il file di setup sul Desktop o nella cartella Output
OutputDir=Output
OutputBaseFilename=Intelleo_Setup_v{#MyAppVersion}
Compression=lzma
SolidCompression=yes
WizardStyle=modern
; Icona del setup (opzionale, decommenta se hai un .ico)
; SetupIconFile=desktop_app\icons\app_icon.ico

[Languages]
Name: "italian"; MessagesFile: "compiler:Languages\Italian.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
; === ESEGUIBILE E DIPENDENZE PYTHON (Output di PyInstaller) ===
; Copia tutto il contenuto della cartella compilata
Source: "{#BuildDir}\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

; === ASSET GRAFICI (Come da indicazioni di Jules) ===
; Mantiene la struttura delle cartelle 'desktop_app' necessaria per i path relativi Python
Source: "desktop_app\assets\*"; DestDir: "{app}\desktop_app\assets"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "desktop_app\icons\*"; DestDir: "{app}\desktop_app\icons"; Flags: ignoreversion recursesubdirs createallsubdirs

; === CONFIGURAZIONE ===
; Copia .env.example rinominandolo in .env solo se non esiste
Source: ".env.example"; DestDir: "{app}"; DestName: ".env"; Flags: onlyifdoesntexist uninsneveruninstall

; === DATABASE ===
; IMPORTANTE: Aggiungiamo i permessi di scrittura (Permissions: users-modify) 
; perché in Program Files l'utente standard non può scrivere di default.
Source: "database.db"; DestDir: "{app}"; Flags: onlyifdoesntexist uninsneveruninstall; Permissions: users-modify

; === DOCUMENTAZIONE (opzionale, solo se i file esistono) ===
Source: "README.md"; DestDir: "{app}"; Flags: ignoreversion skipifsourcedoesntexist
Source: "AGENTS.md"; DestDir: "{app}"; Flags: ignoreversion skipifsourcedoesntexist

; === DOCUMENTAZIONE JULES ===
; Copia tutti i file .md dalla cartella .jules-docs
Source: ".jules-docs\*.md"; DestDir: "{app}\.jules-docs"; Flags: ignoreversion recursesubdirs createallsubdirs skipifsourcedoesntexist

[Icons]
Name: "{autoprograms}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
; Avvia l'app dopo l'installazione
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#MyAppName}}"; Flags: nowait postinstall skipifsilent

[Code]
// Sezione codice opzionale per controlli avanzati
// (Esempio: Verificare se il database esiste già in AppData, se si volesse spostarlo lì)