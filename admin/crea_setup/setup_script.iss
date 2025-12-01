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
  ; Fallback relativo se non passato da riga di comando
  #define BuildDir "..\offusca\dist\Intelleo"
#endif

[Setup]
; ID univoco per l'applicazione
AppId={{A1B2C3D4-E5F6-7890-1234-567890ABCDEF}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
; Installa in C:\Program Files\Intelleo
DefaultDirName={autopf}\{#MyAppName}
DisableProgramGroupPage=yes

; === OUTPUT DIRECTORY ===
; Salva l'installer in formazione_coemi\admin\crea_setup\dist\Intelleo
OutputDir=dist\Intelleo
OutputBaseFilename=Intelleo_Setup_v{#MyAppVersion}

Compression=lzma
SolidCompression=yes
WizardStyle=modern
WizardSizePercent=120
WizardResizable=yes
UninstallFilesDir={app}\Disinstalla
LicenseFile=EULA.rtf
; Immagini personalizzate
WizardImageFile=..\..\desktop_app\assets\installer_wizard.bmp
WizardSmallImageFile=..\..\desktop_app\assets\installer_small.bmp
; Icona del setup
SetupIconFile=..\..\desktop_app\icons\icon.ico

[Languages]
Name: "italian"; MessagesFile: "compiler:Languages\Italian.isl"

[Messages]
; === PREMIUM COPYWRITING ===
WelcomeLabel1=Benvenuto nella Suite Intelleo
WelcomeLabel2=Stai per installare Intelleo sul tuo computer.%n%nPredict. Validate. Automate.%nLa piattaforma definitiva per la gestione della sicurezza aziendale con Intelligenza Artificiale.%n%nPreparati a trasformare il modo in cui gestisci la conformità.
ClickNext=Clicca su Avanti per iniziare il viaggio verso la sicurezza intelligente.
FinishedHeadingLabel=Installazione Completata con Successo
FinishedLabel=Intelleo è stato installato correttamente ed è pronto all'uso.%n%nIl sistema è configurato per analizzare, validare e proteggere i tuoi dati aziendali con la potenza dell'IA.%n%nClicca Fine per avviare la Dashboard.

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Dirs]
; === CREAZIONE FORZATA CARTELLE ===
; Crea la cartella AppData durante l'installazione per evitare che il collegamento punti al nulla
Name: "{localappdata}\Intelleo"

[Registry]
; Menu contestuale "Analizza con Intelleo" (Cartelle)
Root: HKCR; Subkey: "Directory\shell\IntelleoAnalyze"; ValueType: string; ValueName: ""; ValueData: "Analizza con Intelleo"; Flags: uninsdeletekey
Root: HKCR; Subkey: "Directory\shell\IntelleoAnalyze"; ValueType: string; ValueName: "Icon"; ValueData: "{app}\{#MyAppExeName}"; Flags: uninsdeletekey
Root: HKCR; Subkey: "Directory\shell\IntelleoAnalyze\command"; ValueType: string; ValueName: ""; ValueData: """{app}\{#MyAppExeName}"" --analyze ""%1"""; Flags: uninsdeletekey

; Menu contestuale "Analizza con Intelleo" (PDF Singolo)
Root: HKCR; Subkey: "SystemFileAssociations\.pdf\shell\IntelleoAnalyze"; ValueType: string; ValueName: ""; ValueData: "Analizza con Intelleo"; Flags: uninsdeletekey
Root: HKCR; Subkey: "SystemFileAssociations\.pdf\shell\IntelleoAnalyze"; ValueType: string; ValueName: "Icon"; ValueData: "{app}\{#MyAppExeName}"; Flags: uninsdeletekey
Root: HKCR; Subkey: "SystemFileAssociations\.pdf\shell\IntelleoAnalyze\command"; ValueType: string; ValueName: ""; ValueData: """{app}\{#MyAppExeName}"" --analyze ""%1"""; Flags: uninsdeletekey

; Menu contestuale "Importa Anagrafica" (CSV)
Root: HKCR; Subkey: "SystemFileAssociations\.csv\shell\IntelleoImport"; ValueType: string; ValueName: ""; ValueData: "Importa Anagrafica Dipendenti da Intelleo"; Flags: uninsdeletekey
Root: HKCR; Subkey: "SystemFileAssociations\.csv\shell\IntelleoImport"; ValueType: string; ValueName: "Icon"; ValueData: "{app}\{#MyAppExeName}"; Flags: uninsdeletekey
Root: HKCR; Subkey: "SystemFileAssociations\.csv\shell\IntelleoImport\command"; ValueType: string; ValueName: ""; ValueData: """{app}\{#MyAppExeName}"" --import-csv ""%1"""; Flags: uninsdeletekey

[Files]
; === ESEGUIBILE E DIPENDENZE PYTHON ===
; Escludiamo la cartella Licenza qui per gestirla esplicitamente sotto
Source: "{#BuildDir}\*"; DestDir: "{app}"; Excludes: "Intelleo_Setup_*.exe,Licenza"; Flags: ignoreversion recursesubdirs createallsubdirs

; === LICENZA ===
; Copia la cartella Licenza preparata dallo script Python (che ora contiene la copia della cartella Licenza originale)
Source: "{#BuildDir}\Licenza\*"; DestDir: "{app}\Licenza"; Flags: ignoreversion recursesubdirs createallsubdirs skipifsourcedoesntexist

; === ASSET GRAFICI ===
Source: "..\..\desktop_app\assets\*"; DestDir: "{app}\desktop_app\assets"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "..\..\desktop_app\icons\*"; DestDir: "{app}\desktop_app\icons"; Flags: ignoreversion recursesubdirs createallsubdirs

; === SLIDESHOW ===
; Include slides but do not copy to {app}, only extract to {tmp} for installer display
Source: "..\..\desktop_app\assets\slide_*.bmp"; DestDir: "{tmp}"; Flags: dontcopy

; === DOCUMENTAZIONE JULES ===
Source: "..\..\docs\*"; DestDir: "{app}\docs"; Flags: ignoreversion recursesubdirs createallsubdirs skipifsourcedoesntexist

[UninstallDelete]
; === PULIZIA AGGRESSIVA ===
; Cancella file specifici
Type: files; Name: "{app}\.env"
Type: files; Name: "{app}\database_documenti.db"
Type: files; Name: "{app}\database.db"
Type: files; Name: "{app}\scadenzario.db"
Type: files; Name: "{app}\pyarmor.rkey"
Type: files; Name: "{app}\*.log"

; Cancella cartella Licenza
Type: filesandordirs; Name: "{app}\Licenza"

; Cancella dati utente in AppData
Type: files; Name: "{localappdata}\Intelleo\*.env"
Type: files; Name: "{localappdata}\Intelleo\*.db"
Type: files; Name: "{localappdata}\Intelleo\*.lock"
Type: files; Name: "{localappdata}\Intelleo\*.log"
; Rimuove intera cartella dati utente se vuoi pulizia totale (decommentare riga sotto se vuoi cancellare proprio tutto in appdata)
Type: filesandordirs; Name: "{localappdata}\Intelleo"

; Cancella l'intera cartella di installazione alla fine
Type: filesandordirs; Name: "{app}"

[Icons]
Name: "{autoprograms}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

; === SCORCIATOIE VISTE (Jumplist-like) ===
Name: "{autoprograms}\{#MyAppName} - Dashboard"; Filename: "{app}\{#MyAppExeName}"; Parameters: "--view dashboard"; IconFilename: "{app}\{#MyAppExeName}"
Name: "{autoprograms}\{#MyAppName} - Scadenzario"; Filename: "{app}\{#MyAppExeName}"; Parameters: "--view scadenzario"; IconFilename: "{app}\{#MyAppExeName}"
Name: "{autoprograms}\{#MyAppName} - Convalida Dati"; Filename: "{app}\{#MyAppExeName}"; Parameters: "--view validation"; IconFilename: "{app}\{#MyAppExeName}"
Name: "{autoprograms}\{#MyAppName} - Importa Documenti"; Filename: "{app}\{#MyAppExeName}"; Parameters: "--view import"; IconFilename: "{app}\{#MyAppExeName}"

; === COLLEGAMENTO DATI APPLICAZIONE FIXATO ===
; Apre esplora risorse nel percorso AppData. Parametri senza virgolette triple per evitare errori di parsing.
Name: "{app}\AppDataIntelleo"; Filename: "{win}\explorer.exe"; Parameters: """{localappdata}\Intelleo"""; IconFilename: "{win}\explorer.exe"

[Run]
; Avvia l'app dopo l'installazione
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#MyAppName}}"; Flags: nowait postinstall skipifsilent

[Code]
// API Import for Timers
function SetTimer(hWnd: LongWord; nIDEvent, uElapse: LongWord; lpTimerFunc: LongWord): LongWord;
external 'SetTimer@user32.dll stdcall';

function KillTimer(hWnd: LongWord; nIDEvent: LongWord): BOOL;
external 'KillTimer@user32.dll stdcall';

// API for Fullscreen
function ShowWindow(hWnd: HWND; nCmdShow: Integer): BOOL;
external 'ShowWindow@user32.dll stdcall';

const
  SW_MAXIMIZE = 3;

var
  ConfigPage1: TInputQueryWizardPage;
  ConfigPage2: TInputQueryWizardPage;
  ConfigPage3: TInputQueryWizardPage;
  TipsLabel: TNewStaticText;

  // Slideshow components
  SlideImage: TBitmapImage;
  SlideTimerID: LongWord;
  SlideIndex: Integer;

// Callback must match standard stdcall signature
procedure TimerProc(H: LongWord; Msg: LongWord; IdEvent: LongWord; Time: LongWord);
var
  FileName: String;
begin
  if IdEvent = SlideTimerID then
  begin
    SlideIndex := (SlideIndex + 1) mod 3;
    FileName := 'slide_' + IntToStr(SlideIndex + 1) + '.bmp';
    // Files are already extracted to {tmp} in InitializeWizard
    SlideImage.Bitmap.LoadFromFile(ExpandConstant('{tmp}\' + FileName));
  end;
end;

procedure InitializeWizard;
var
  I: Integer;
begin
  // --- FULLSCREEN MODE ---
  ShowWindow(WizardForm.Handle, SW_MAXIMIZE);

  // --- PRE-EXTRACT SLIDES (Performance Fix) ---
  for I := 1 to 3 do
    ExtractTemporaryFile('slide_' + IntToStr(I) + '.bmp');

  // Pagina 1: Impostazioni Cloud e AI
  ConfigPage1 := CreateInputQueryPage(wpSelectTasks,
    'Configurazione Cloud', 'Parametri AI & Cloud Integration',
    'Intelleo utilizza la potenza del Cloud per elaborare i documenti. Configura le chiavi di accesso.');

  ConfigPage1.Add('Gemini API Key:', False);
  ConfigPage1.Add('Google Cloud Project ID:', False);
  ConfigPage1.Add('GCS Bucket Name:', False);

  // Pagina 2: Impostazioni Email (SMTP Server)
  ConfigPage2 := CreateInputQueryPage(ConfigPage1.ID,
    'Configurazione Notifiche', 'Server SMTP (Posta in Uscita)',
    'Configura il server per l''invio automatico degli avvisi di scadenza.');

  ConfigPage2.Add('SMTP Host:', False);
  ConfigPage2.Add('SMTP Port:', False);
  ConfigPage2.Add('SMTP User:', False);
  ConfigPage2.Add('SMTP Password:', True);

  // Pagina 3: Destinatari Email
  ConfigPage3 := CreateInputQueryPage(ConfigPage2.ID,
    'Destinatari Avvisi', 'Canali di Comunicazione',
    'Definisci chi riceverà i report settimanali e gli alert critici.');

  ConfigPage3.Add('Destinatari (A):', False);
  ConfigPage3.Add('Destinatari in copia (CC):', False);

  // Ingrandisci il logo in alto a destra
  WizardForm.WizardSmallBitmapImage.Width := ScaleX(110);
  WizardForm.WizardSmallBitmapImage.Left := WizardForm.ClientWidth - ScaleX(110);

  // Suggerimenti Professionali
  TipsLabel := TNewStaticText.Create(WizardForm);
  TipsLabel.Parent := WizardForm.InstallingPage;
  TipsLabel.Visible := False;
  TipsLabel.WordWrap := True;
  TipsLabel.Caption := 'Intelleo System Initialization:' + #13#10 + #13#10 +
                       '- Attivazione Motore Neurale Gemini Pro...' + #13#10 +
                       '- Configurazione Database Crittografato AES-256...' + #13#10 +
                       '- Predisposizione Ambiente Scadenzario Intelligente...' + #13#10 +
                       '- Verifica Moduli di Notifica Automatica...' + #13#10 +
                       '- Inizializzazione Dashboard Interattiva...' + #13#10 + #13#10 +
                       'Attendere prego. Stiamo preparando il tuo ambiente di lavoro.';
  TipsLabel.Font.Style := [fsItalic];
  TipsLabel.Font.Color := clWindowText;

  // Initialize Slideshow Image (Hidden initially)
  SlideImage := TBitmapImage.Create(WizardForm);
  SlideImage.Parent := WizardForm.InstallingPage;
  SlideImage.Visible := False;
  SlideImage.Stretch := True;
  SlideImage.Center := True;
  // Load first image
  SlideImage.Bitmap.LoadFromFile(ExpandConstant('{tmp}\slide_1.bmp'));
  SlideIndex := 0;
end;

procedure CurPageChanged(CurPageID: Integer);
var
  InnerRect: TRect;
  HalfWidth: Integer;
begin
  if CurPageID = wpInstalling then
  begin
    // --- LAYOUT RECALCULATION for Fullscreen ---
    InnerRect := WizardForm.InstallingPage.ClientRect;
    HalfWidth := InnerRect.Right div 2;

    // LEFT COLUMN: Status, Progress, Tips
    WizardForm.StatusLabel.Left := ScaleX(40);
    WizardForm.StatusLabel.Width := HalfWidth - ScaleX(80);

    WizardForm.FileNameLabel.Left := ScaleX(40);
    WizardForm.FileNameLabel.Width := HalfWidth - ScaleX(80);

    WizardForm.ProgressGauge.Left := ScaleX(40);
    WizardForm.ProgressGauge.Width := HalfWidth - ScaleX(80);

    TipsLabel.Visible := True;
    TipsLabel.Left := ScaleX(40);
    TipsLabel.Width := HalfWidth - ScaleX(80);
    TipsLabel.Top := WizardForm.ProgressGauge.Top + WizardForm.ProgressGauge.Height + ScaleY(40);

    // RIGHT COLUMN: Slideshow
    SlideImage.Visible := True;
    SlideImage.Left := HalfWidth;
    SlideImage.Top := ScaleY(40); // Add some top margin
    SlideImage.Width := HalfWidth - ScaleX(40); // Margin on right
    SlideImage.Height := InnerRect.Bottom - ScaleY(80); // Margin bottom

    // START TIMER
    SlideTimerID := SetTimer(0, 0, 3000, CreateCallback(@TimerProc));
  end
  else
  begin
    TipsLabel.Visible := False;
    SlideImage.Visible := False;
    if SlideTimerID <> 0 then
    begin
        KillTimer(0, SlideTimerID);
        SlideTimerID := 0;
    end;
  end;
end;

procedure DeinitializeSetup();
begin
  if SlideTimerID <> 0 then KillTimer(0, SlideTimerID);
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

    if not LoadStringsFromFile(EnvPath, Lines) then
      SetArrayLength(Lines, 0);

    // Page 1 Values
    Val := ConfigPage1.Values[0]; if Val <> '' then UpdateEnvVar(Lines, 'GEMINI_API_KEY', '"' + Val + '"');
    Val := ConfigPage1.Values[1]; if Val <> '' then UpdateEnvVar(Lines, 'GOOGLE_CLOUD_PROJECT', '"' + Val + '"');
    Val := ConfigPage1.Values[2]; if Val <> '' then UpdateEnvVar(Lines, 'GCS_BUCKET_NAME', '"' + Val + '"');

    // Page 2 Values (Server)
    Val := ConfigPage2.Values[0]; if Val <> '' then UpdateEnvVar(Lines, 'SMTP_HOST', '"' + Val + '"');
    Val := ConfigPage2.Values[1]; if Val <> '' then UpdateEnvVar(Lines, 'SMTP_PORT', Val);
    Val := ConfigPage2.Values[2]; if Val <> '' then UpdateEnvVar(Lines, 'SMTP_USER', '"' + Val + '"');
    Val := ConfigPage2.Values[3]; if Val <> '' then UpdateEnvVar(Lines, 'SMTP_PASSWORD', '"' + Val + '"');

    // Page 3 Values (Recipients)
    Val := ConfigPage3.Values[0]; if Val <> '' then UpdateEnvVar(Lines, 'EMAIL_RECIPIENTS_TO', '"' + Val + '"');
    Val := ConfigPage3.Values[1]; if Val <> '' then UpdateEnvVar(Lines, 'EMAIL_RECIPIENTS_CC', '"' + Val + '"');

    SaveStringsToFile(EnvPath, Lines, False);
  end;
end;
