; Script generato per Intelleo (Formazione Coemi)
; Compatibile con struttura PyInstaller OneDir

#define MyAppName "Intelleo"
#define MyAppVersion "1.0"
#define MyAppPublisher "Giancarlo Allegretti"
#define MyAppExeName "Intelleo.exe"
; Cartella dove si trova l'output di PyInstaller (modificare se diverso)
#define BuildDir "..\offusca\dist\Intelleo"

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
; Copia il file di licenza nella cartella di installazione
Source: "EULA.rtf"; DestDir: "{app}"; Flags: ignoreversion

; === ASSET GRAFICI (Come da indicazioni di Jules) ===
; Mantiene la struttura delle cartelle 'desktop_app' necessaria per i path relativi Python
Source: "..\..\desktop_app\assets\*"; DestDir: "{app}\desktop_app\assets"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "..\..\desktop_app\icons\*"; DestDir: "{app}\desktop_app\icons"; Flags: ignoreversion recursesubdirs createallsubdirs

; === CONFIGURAZIONE ===
; Copia .env.example rinominandolo in .env solo se non esiste
Source: "..\..\.env.example"; DestDir: "{app}"; DestName: ".env"; Flags: onlyifdoesntexist uninsneveruninstall

; === DATABASE ===
; IMPORTANTE: Aggiungiamo i permessi di scrittura (Permissions: users-modify) 
; perché in Program Files l'utente standard non può scrivere di default.
Source: "..\..\database.db"; DestDir: "{app}"; Flags: onlyifdoesntexist uninsneveruninstall skipifsourcedoesntexist; Permissions: users-modify

; === DOCUMENTAZIONE JULES ===
; Copia l'intera cartella .jules-docs (tutti i file)
Source: "..\..\.jules-docs\*"; DestDir: "{app}\.jules-docs"; Flags: ignoreversion recursesubdirs createallsubdirs skipifsourcedoesntexist

[Icons]
Name: "{autoprograms}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
; Avvia l'app dopo l'installazione
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#MyAppName}}"; Flags: nowait postinstall skipifsilent

[Code]
var
  ConfigPage: TInputQueryWizardPage;

procedure InitializeWizard;
begin
  ConfigPage := CreateInputQueryWizardPage(wpSelectTasks,
    'Configurazione Iniziale', 'Inserisci le impostazioni opzionali per l''applicazione',
    'Se lasciati vuoti, verranno mantenuti i valori predefiniti o esistenti.');

  ConfigPage.Add('Gemini API Key:', False);
  ConfigPage.Add('Google Cloud Project ID:', False);
  ConfigPage.Add('GCS Bucket Name:', False);
  ConfigPage.Add('SMTP Host:', False);
  ConfigPage.Add('SMTP Port:', False);
  ConfigPage.Add('SMTP User:', False);
  ConfigPage.Add('SMTP Password:', True);
  ConfigPage.Add('Email A (separati da virgola):', False);
  ConfigPage.Add('Email CC (separati da virgola):', False);
end;

procedure CurStepChanged(CurStep: TSetupStep);
var
  Lines: TArrayOfString;
  I: Integer;
  EnvPath: String;
  Val: String;
begin
  if CurStep = ssPostInstall then
  begin
    EnvPath := ExpandConstant('{app}\.env');

    // Carica il file .env (che è stato copiato da .env.example o preservato)
    if LoadStringsFromFile(EnvPath, Lines) then
    begin
      for I := 0 to GetArrayLength(Lines) - 1 do
      begin
        // Aggiorna solo se l'utente ha inserito un valore

        Val := ConfigPage.Values[0];
        if (Val <> '') and (Pos('GEMINI_API_KEY=', Lines[I]) = 1) then
          Lines[I] := 'GEMINI_API_KEY="' + Val + '"';

        Val := ConfigPage.Values[1];
        if (Val <> '') and (Pos('GOOGLE_CLOUD_PROJECT=', Lines[I]) = 1) then
          Lines[I] := 'GOOGLE_CLOUD_PROJECT="' + Val + '"';

        Val := ConfigPage.Values[2];
        if (Val <> '') and (Pos('GCS_BUCKET_NAME=', Lines[I]) = 1) then
          Lines[I] := 'GCS_BUCKET_NAME="' + Val + '"';

        Val := ConfigPage.Values[3];
        if (Val <> '') and (Pos('SMTP_HOST=', Lines[I]) = 1) then
          Lines[I] := 'SMTP_HOST="' + Val + '"';

        Val := ConfigPage.Values[4];
        if (Val <> '') and (Pos('SMTP_PORT=', Lines[I]) = 1) then
          Lines[I] := 'SMTP_PORT=' + Val;

        Val := ConfigPage.Values[5];
        if (Val <> '') and (Pos('SMTP_USER=', Lines[I]) = 1) then
          Lines[I] := 'SMTP_USER="' + Val + '"';

        Val := ConfigPage.Values[6];
        if (Val <> '') and (Pos('SMTP_PASSWORD=', Lines[I]) = 1) then
          Lines[I] := 'SMTP_PASSWORD="' + Val + '"';

        Val := ConfigPage.Values[7];
        if (Val <> '') and (Pos('EMAIL_RECIPIENTS_TO=', Lines[I]) = 1) then
          Lines[I] := 'EMAIL_RECIPIENTS_TO="' + Val + '"';

        Val := ConfigPage.Values[8];
        if (Val <> '') and (Pos('EMAIL_RECIPIENTS_CC=', Lines[I]) = 1) then
          Lines[I] := 'EMAIL_RECIPIENTS_CC="' + Val + '"';
      end;

      SaveStringsToFile(EnvPath, Lines, False);
    end;
  end;
end;
