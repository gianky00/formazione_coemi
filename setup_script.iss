; Script Inno Setup per Intelleo
; 1. Compila prima il progetto Python con "build_dist.py"
; 2. Apri questo file con Inno Setup Compiler e premi "Run" (F9)

#define MyAppName "Intelleo AI"
#define MyAppVersion "1.0"
#define MyAppPublisher "La Tua Azienda"
#define MyAppExeName "Intelleo.exe"
#define OutputDir "dist_installer"

[Setup]
; ID univoco dell'app (Generato casualmente, non cambiarlo per gli aggiornamenti futuri di questa app)
AppId={{A1B2C3D4-E5F6-7890-1234-56789ABCDEF0}

AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}

; --- CONFIGURAZIONE EULA (Fondamentale) ---
LicenseFile=EULA.txt
; ------------------------------------------

; Opzioni estetiche
WizardStyle=modern
Compression=lzma
SolidCompression=yes
OutputDir={#OutputDir}
OutputBaseFilename=Setup_Intelleo_v{#MyAppVersion}
SetupIconFile=desktop_app\icons\icon.ico
; Se non hai un'icona .ico, commenta la riga sopra con un punto e virgola

; Richiedi permessi amministratore per installare in Program Files
PrivilegesRequired=admin

[Languages]
Name: "italian"; MessagesFile: "compiler:Languages\Italian.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
; Il file eseguibile principale generato da PyInstaller
Source: "dist\package\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion

; Includi il file di licenza PyArmor (FONDAMENTALE)
Source: "dist\package\pyarmor.rkey"; DestDir: "{app}"; Flags: ignoreversion

; Includi eventuali altre cartelle se necessario (es. database locali non inglobati)
; Source: "dist\package\altri_file\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
; Avvia l'app dopo l'installazione
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#MyAppName}}"; Flags: nowait postinstall skipifsilent