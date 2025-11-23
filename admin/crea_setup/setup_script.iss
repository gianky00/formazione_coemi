; Script generato per Intelleo (Formazione Coemi)
; Compatibile con struttura PyInstaller OneDir

#define MyAppName "Intelleo"
#define MyAppPublisher "Giancarlo Allegretti"
#define MyAppExeName "Intelleo.exe"

; Default values if not defined via command line
#ifndef MyAppVersion
  #define MyAppVersion "1.0"
#endif
#ifndef BuildDir
  #define BuildDir "..\offusca\dist\Intelleo"
#endif

[Setup]
; ID univoco per l'applicazione (generato casualmente, non cambiarlo per aggiornamenti futuri)
AppId={{A1B2C3D4-E5F6-7890-1234-567890ABCDEF}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
; Installa in C:\Program Files\Intelleo
DefaultDirName={autopf}\{#MyAppName}
DisableProgramGroupPage=yes
; Crea il file di setup nella cartella dist\Intelleo
OutputDir=dist\Intelleo
OutputBaseFilename=Intelleo_Setup_v{#MyAppVersion}
Compression=lzma
SolidCompression=yes
WizardStyle=modern
WizardSizePercent=120
WizardResizable=yes
UninstallFilesDir={app}\Disinstalla
; Licenza EULA (RTF Professionale)
LicenseFile=EULA.rtf
; Immagini personalizzate per l'installer
WizardImageFile=..\..\desktop_app\assets\installer_wizard.bmp
WizardSmallImageFile=..\..\desktop_app\assets\installer_small.bmp
; Icona del setup
SetupIconFile=..\..\desktop_app\icons\icon.ico

[Languages]
Name: "italian"; MessagesFile: "compiler:Languages\Italian.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Registry]
; Menu contestuale "Analizza con Intelleo"
Root: HKCR; Subkey: "Directory\shell\IntelleoAnalyze"; ValueType: string; ValueName: ""; ValueData: "Analizza con Intelleo"; Flags: uninsdeletekey
Root: HKCR; Subkey: "Directory\shell\IntelleoAnalyze"; ValueType: string; ValueName: "Icon"; ValueData: "{app}\{#MyAppExeName}"; Flags: uninsdeletekey
Root: HKCR; Subkey: "Directory\shell\IntelleoAnalyze\command"; ValueType: string; ValueName: ""; ValueData: """{app}\{#MyAppExeName}"" --analyze ""%1"""; Flags: uninsdeletekey

[Files]
; === ESEGUIBILE E DIPENDENZE PYTHON (Output di PyInstaller) ===
; Copia tutto il contenuto della cartella compilata (escludendo i setup precedenti)
Source: "{#BuildDir}\*"; DestDir: "{app}"; Excludes: "Intelleo_Setup_*.exe"; Flags: ignoreversion recursesubdirs createallsubdirs

; === LICENZA ===
; REMOVED from Files section to prevent it being visible in installation folder.
; It is still embedded in the installer via LicenseFile directive.

; === ASSET GRAFICI (Come da indicazioni di Jules) ===
; Mantiene la struttura delle cartelle 'desktop_app' necessaria per i path relativi Python
Source: "..\..\desktop_app\assets\*"; DestDir: "{app}\desktop_app\assets"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "..\..\desktop_app\icons\*"; DestDir: "{app}\desktop_app\icons"; Flags: ignoreversion recursesubdirs createallsubdirs

; === CONFIGURAZIONE ===
; .env handling moved to [Code] section to use User Data Directory (AppData)

; === DATABASE ===
; Database is no longer installed to Program Files.
; It will be created or migrated to AppData on first run by the application.

; === DOCUMENTAZIONE JULES ===
; Copia l'intera cartella docs (rinominata da .jules-docs)
Source: "..\..\docs\*"; DestDir: "{app}\docs"; Flags: ignoreversion recursesubdirs createallsubdirs skipifsourcedoesntexist

[UninstallDelete]
; Forza la cancellazione di file generati dopo l'installazione per una pulizia completa
Type: files; Name: "{app}\.env"
Type: files; Name: "{app}\database_documenti.db"
Type: files; Name: "{app}\database.db"
Type: files; Name: "{app}\scadenzario.db"
Type: files; Name: "{app}\pyarmor.rkey"
Type: files; Name: "{app}\dettagli_licenza.txt"
Type: filesandordirs; Name: "{app}\_internal"
Type: dirifempty; Name: "{app}"
Type: files; Name: "{app}\*.log"
; Clean up User Data (Optional, but good for clean uninstall)
Type: files; Name: "{localappdata}\Intelleo\.env"
Type: files; Name: "{localappdata}\Intelleo\database_documenti.db"
Type: files; Name: "{localappdata}\Intelleo\*.lock"
Type: dirifempty; Name: "{localappdata}\Intelleo"

[Icons]
Name: "{autoprograms}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon
Name: "{app}\Dati Applicazione"; Filename: "{localappdata}\Intelleo"

[Run]
; Avvia l'app dopo l'installazione
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#MyAppName}}"; Flags: nowait postinstall skipifsilent

[Code]
var
  ConfigPage1: TInputQueryWizardPage;
  ConfigPage2: TInputQueryWizardPage;
  ConfigPage3: TInputQueryWizardPage;
  TipsLabel: TNewStaticText;

procedure InitializeWizard;
begin
  // Pagina 1: Impostazioni Cloud e AI
  ConfigPage1 := CreateInputQueryPage(wpSelectTasks,
    'Configurazione Generale', 'Impostazioni Cloud e Intelligenza Artificiale',
    'Inserisci i dati richiesti. Se lasciati vuoti, verranno mantenuti i valori esistenti.');

  ConfigPage1.Add('Gemini API Key:', False);
  ConfigPage1.Add('Google Cloud Project ID:', False);
  ConfigPage1.Add('GCS Bucket Name:', False);

  // Pagina 2: Impostazioni Email (SMTP Server)
  ConfigPage2 := CreateInputQueryPage(ConfigPage1.ID,
    'Configurazione Server Email', 'Impostazioni SMTP per le notifiche (Server)',
    'Configura il server di posta in uscita.');

  ConfigPage2.Add('SMTP Host:', False);
  ConfigPage2.Add('SMTP Port:', False);
  ConfigPage2.Add('SMTP User:', False);
  ConfigPage2.Add('SMTP Password:', True);

  // Pagina 3: Destinatari Email
  ConfigPage3 := CreateInputQueryPage(ConfigPage2.ID,
    'Configurazione Destinatari', 'Indirizzi Email per le notifiche',
    'Definisci chi riceverà gli avvisi di scadenza.');

  ConfigPage3.Add('Email A (separati da virgola):', False);
  ConfigPage3.Add('Email CC (separati da virgola):', False);

  // Ingrandisci il logo in alto a destra
  WizardForm.WizardSmallBitmapImage.Width := ScaleX(110);
  WizardForm.WizardSmallBitmapImage.Left := WizardForm.ClientWidth - ScaleX(110);

  // Suggerimenti Professionali (Creato nascosto, mostrato in CurPageChanged)
  TipsLabel := TNewStaticText.Create(WizardForm);
  TipsLabel.Parent := WizardForm.InstallingPage;
  TipsLabel.Visible := False;
  TipsLabel.WordWrap := True;
  TipsLabel.Caption := 'Funzionalit' + #224 + ' Professionali Avanzate:' + #13#10 + #13#10 +
                       '- Analisi Documentale Avanzata con AI Gemini Pro Multimodale' + #13#10 +
                       '- Estrazione Automatica Dati da PDF e Immagini' + #13#10 +
                       '- Scadenzario Predittivo con Calcolo Validità Intelligente' + #13#10 +
                       '- Sistema di Notifiche Email Configurabile e Automatico' + #13#10 +
                       '- Gestione Sicura Crittografata (AES-256) dei Dati Aziendali' + #13#10 +
                       '- Reportistica PDF Professionale e Dashboard Interattiva' + #13#10 +
                       '- Architettura Resiliente con Database In-Memory';
  TipsLabel.Font.Style := [fsBold, fsItalic];
  TipsLabel.Font.Color := clWindowText;
end;

procedure CurPageChanged(CurPageID: Integer);
begin
  if CurPageID = wpInstalling then
  begin
    TipsLabel.Visible := True;
    // Posizionato sotto la barra di progresso con margine aumentato
    TipsLabel.Top := WizardForm.ProgressGauge.Top + WizardForm.ProgressGauge.Height + ScaleY(40);
    TipsLabel.Left := 0;
    TipsLabel.Width := WizardForm.InstallingPage.ClientWidth;
  end
  else
    TipsLabel.Visible := False;
end;

// Helper function to safely update environment variables in the Lines array
procedure UpdateEnvVar(var Lines: TArrayOfString; Key, Value: String);
var
  J: Integer;
  Found: Boolean;
begin
  Found := False;
  for J := 0 to GetArrayLength(Lines) - 1 do
  begin
    if Pos(Key + '=', Lines[J]) = 1 then
    begin
      Lines[J] := Key + '=' + Value;
      Found := True;
      Break;
    end;
  end;
  if not Found then
  begin
    SetArrayLength(Lines, GetArrayLength(Lines) + 1);
    Lines[GetArrayLength(Lines) - 1] := Key + '=' + Value;
  end;
end;

procedure CurStepChanged(CurStep: TSetupStep);
var
  Lines: TArrayOfString;
  EnvPath: String;
  AppDataDir: String;
  Val: String;
begin
  if CurStep = ssPostInstall then
  begin
    // Write configuration to User Local AppData to match Python's LOCALAPPDATA
    AppDataDir := ExpandConstant('{localappdata}\Intelleo');
    if not DirExists(AppDataDir) then ForceDirectories(AppDataDir);

    EnvPath := AppDataDir + '\.env';

    // Try to load existing file, otherwise start with empty array
    if not LoadStringsFromFile(EnvPath, Lines) then
      SetArrayLength(Lines, 0);

    // Page 1 Values
    Val := ConfigPage1.Values[0];
    if Val <> '' then UpdateEnvVar(Lines, 'GEMINI_API_KEY', '"' + Val + '"');

    Val := ConfigPage1.Values[1];
    if Val <> '' then UpdateEnvVar(Lines, 'GOOGLE_CLOUD_PROJECT', '"' + Val + '"');

    Val := ConfigPage1.Values[2];
    if Val <> '' then UpdateEnvVar(Lines, 'GCS_BUCKET_NAME', '"' + Val + '"');

    // Page 2 Values (Server)
    Val := ConfigPage2.Values[0];
    if Val <> '' then UpdateEnvVar(Lines, 'SMTP_HOST', '"' + Val + '"');

    Val := ConfigPage2.Values[1];
    if Val <> '' then UpdateEnvVar(Lines, 'SMTP_PORT', Val);

    Val := ConfigPage2.Values[2];
    if Val <> '' then UpdateEnvVar(Lines, 'SMTP_USER', '"' + Val + '"');

    Val := ConfigPage2.Values[3];
    if Val <> '' then UpdateEnvVar(Lines, 'SMTP_PASSWORD', '"' + Val + '"');

    // Page 3 Values (Recipients)
    Val := ConfigPage3.Values[0];
    if Val <> '' then UpdateEnvVar(Lines, 'EMAIL_RECIPIENTS_TO', '"' + Val + '"');

    Val := ConfigPage3.Values[1];
    if Val <> '' then UpdateEnvVar(Lines, 'EMAIL_RECIPIENTS_CC', '"' + Val + '"');

    // Only save if we have data (or file existed)
    // Actually, force save if we created the file
    SaveStringsToFile(EnvPath, Lines, False);
  end;
end;
