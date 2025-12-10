; Script generato per Intelleo (Formazione Coemi)
; Compatibile con struttura PyInstaller OneDir

#define MyAppName "Intelleo"
#define MyAppPublisher "Giancarlo Allegretti"
#define MyAppExeName "Intelleo.exe"

; Default values if not defined via command line
#ifndef MyAppVersion
  #define MyAppVersion "2.0.0"
#endif
#ifndef BuildDir
  ; Fallback relativo se non passato da riga di comando
  ; UPDATED: Nuitka build path (was PyInstaller: ..\offusca\dist\Intelleo)
  #define BuildDir "..\..\dist\nuitka\Intelleo.dist"
#endif

[Setup]
; ID univoco per l'applicazione
AppId={{A1B2C3D4-E5F6-7890-1234-567890ABCDEF}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
; Installa in C:\Program Files\Intelleo
DefaultDirName={autopf}\{#MyAppName}
PrivilegesRequiredOverridesAllowed=dialog
ArchitecturesAllowed=x64
ArchitecturesInstallIn64BitMode=x64
MinVersion=10.0
DisableProgramGroupPage=yes

; === OUTPUT DIRECTORY ===
; Salva l'installer in formazione_coemi\dist\installer
OutputDir=..\..\dist\installer
OutputBaseFilename=Intelleo_Setup_v{#MyAppVersion}

Compression=lzma2/ultra64
SolidCompression=yes
WizardStyle=modern
WizardSizePercent=120
UninstallFilesDir={app}\Disinstalla
LicenseFile=EULA.rtf
; Immagini personalizzate
WizardImageFile=..\..\desktop_app\assets\installer_wizard.bmp
WizardSmallImageFile=..\..\desktop_app\assets\installer_small.bmp
; Icona del setup
SetupIconFile=..\..\desktop_app\icons\icon.ico
UninstallDisplayIcon={app}\{#MyAppExeName}

[Languages]
Name: "italian"; MessagesFile: "compiler:Languages\Italian.isl"

[Messages]
; === HUMBLE & REALISTIC COPYWRITING ===
WelcomeLabel1=Benvenuto in Intelleo
WelcomeLabel2=Stai per installare Intelleo sul tuo computer.%n%nSoluzione software per la gestione dei processi di conformità e sicurezza aziendale.%n%nIl programma installerà i componenti necessari per l'utilizzo della piattaforma.
ClickNext=Clicca su Avanti per continuare.
FinishedHeadingLabel=Installazione Completata
FinishedLabel=L'installazione di Intelleo è terminata correttamente.%n%nÈ possibile avviare l'applicazione utilizzando l'icona sul desktop o dal menu Start.%n%nClicca Fine per uscire.
StatusExtractFiles=Estrazione file in corso...
StatusInstalling=Installazione componenti...

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "startup"; Description: "Avvia Intelleo automaticamente all'avvio di Windows"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "cleancache"; Description: "Esegui pulizia della cache (Consigliato per aggiornamenti)"; GroupDescription: "Manutenzione:"; Flags: unchecked
Name: "contextpdf"; Description: "Aggiungi 'Analizza con Intelleo' al menu contestuale dei PDF"; GroupDescription: "Integrazione Esplora Risorse:"; Flags: unchecked
Name: "contextcsv"; Description: "Aggiungi 'Importa in Intelleo' al menu contestuale dei CSV"; GroupDescription: "Integrazione Esplora Risorse:"; Flags: unchecked

[Dirs]
; === CREAZIONE FORZATA CARTELLE ===
; Crea la cartella AppData durante l'installazione per evitare che il collegamento punti al nulla
Name: "{localappdata}\Intelleo"

[Registry]
; Avvio Automatico
Root: HKCU; Subkey: "Software\Microsoft\Windows\CurrentVersion\Run"; ValueType: string; ValueName: "{#MyAppName}"; ValueData: """{app}\{#MyAppExeName}"" --minimized"; Flags: uninsdeletevalue; Tasks: startup

; Menu contestuale "Analizza con Intelleo" (Cartelle)
Root: HKCR; Subkey: "Directory\shell\IntelleoAnalyze"; ValueType: string; ValueName: ""; ValueData: "Analizza con Intelleo"; Flags: uninsdeletekey
Root: HKCR; Subkey: "Directory\shell\IntelleoAnalyze"; ValueType: string; ValueName: "Icon"; ValueData: "{app}\{#MyAppExeName}"; Flags: uninsdeletekey
Root: HKCR; Subkey: "Directory\shell\IntelleoAnalyze\command"; ValueType: string; ValueName: ""; ValueData: """{app}\{#MyAppExeName}"" --analyze ""%1"""; Flags: uninsdeletekey

; Menu contestuale "Analizza con Intelleo" (PDF Singolo) - LEGATO A TASK
Root: HKCR; Subkey: "SystemFileAssociations\.pdf\shell\IntelleoAnalyze"; ValueType: string; ValueName: ""; ValueData: "Analizza con Intelleo"; Flags: uninsdeletekey; Tasks: contextpdf
Root: HKCR; Subkey: "SystemFileAssociations\.pdf\shell\IntelleoAnalyze"; ValueType: string; ValueName: "Icon"; ValueData: "{app}\{#MyAppExeName}"; Flags: uninsdeletekey; Tasks: contextpdf
Root: HKCR; Subkey: "SystemFileAssociations\.pdf\shell\IntelleoAnalyze\command"; ValueType: string; ValueName: ""; ValueData: """{app}\{#MyAppExeName}"" --analyze ""%1"""; Flags: uninsdeletekey; Tasks: contextpdf

; Menu contestuale "Importa Anagrafica" (CSV) - LEGATO A TASK
Root: HKCR; Subkey: "SystemFileAssociations\.csv\shell\IntelleoImport"; ValueType: string; ValueName: ""; ValueData: "Importa Anagrafica Dipendenti da Intelleo"; Flags: uninsdeletekey; Tasks: contextcsv
Root: HKCR; Subkey: "SystemFileAssociations\.csv\shell\IntelleoImport"; ValueType: string; ValueName: "Icon"; ValueData: "{app}\{#MyAppExeName}"; Flags: uninsdeletekey; Tasks: contextcsv
Root: HKCR; Subkey: "SystemFileAssociations\.csv\shell\IntelleoImport\command"; ValueType: string; ValueName: ""; ValueData: """{app}\{#MyAppExeName}"" --import-csv ""%1"""; Flags: uninsdeletekey; Tasks: contextcsv

[Files]
; === NUITKA BUILD OUTPUT ===
; Source: dist/nuitka/Intelleo.dist/* (or custom BuildDir)
Source: "{#BuildDir}\*"; DestDir: "{app}"; Excludes: "Intelleo_Setup_*.exe,Licenza,docs,*.log,*.tmp,__pycache__"; Flags: ignoreversion recursesubdirs createallsubdirs

; === LICENZA ===
Source: "{#BuildDir}\Licenza\*"; DestDir: "{app}\Licenza"; Flags: ignoreversion recursesubdirs createallsubdirs skipifsourcedoesntexist

; === ASSET GRAFICI ===
Source: "..\..\desktop_app\assets\*"; DestDir: "{app}\desktop_app\assets"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "..\..\desktop_app\icons\*"; DestDir: "{app}\desktop_app\icons"; Flags: ignoreversion recursesubdirs createallsubdirs

; === SLIDESHOW ===
Source: "..\..\desktop_app\assets\slide_*.bmp"; DestDir: "{tmp}"; Flags: dontcopy

[UninstallDelete]
; === PULIZIA AGGRESSIVA ===
Type: files; Name: "{app}\.env"
Type: files; Name: "{app}\database_documenti.db"
Type: files; Name: "{app}\database.db"
Type: files; Name: "{app}\scadenzario.db"
Type: files; Name: "{app}\pyarmor.rkey"
Type: files; Name: "{app}\*.log"
Type: filesandordirs; Name: "{app}\Licenza"
Type: files; Name: "{localappdata}\Intelleo\*.env"
Type: files; Name: "{localappdata}\Intelleo\*.db"
Type: files; Name: "{localappdata}\Intelleo\*.lock"
Type: files; Name: "{localappdata}\Intelleo\*.log"
Type: filesandordirs; Name: "{localappdata}\Intelleo"
Type: filesandordirs; Name: "{app}"

[Icons]
Name: "{autoprograms}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

; === SCORCIATOIE VISTE ===
Name: "{autoprograms}\{#MyAppName} - Dashboard"; Filename: "{app}\{#MyAppExeName}"; Parameters: "--view dashboard"; IconFilename: "{app}\{#MyAppExeName}"
Name: "{autoprograms}\{#MyAppName} - Scadenzario"; Filename: "{app}\{#MyAppExeName}"; Parameters: "--view scadenzario"; IconFilename: "{app}\{#MyAppExeName}"
Name: "{autoprograms}\{#MyAppName} - Convalida Dati"; Filename: "{app}\{#MyAppExeName}"; Parameters: "--view validation"; IconFilename: "{app}\{#MyAppExeName}"
Name: "{autoprograms}\{#MyAppName} - Importa Documenti"; Filename: "{app}\{#MyAppExeName}"; Parameters: "--view import"; IconFilename: "{app}\{#MyAppExeName}"
Name: "{app}\AppDataIntelleo"; Filename: "{win}\explorer.exe"; Parameters: """{localappdata}\Intelleo"""; IconFilename: "{win}\explorer.exe"

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#MyAppName}}"; Flags: nowait postinstall skipifsilent

[Code]
// API Import for Timers & Window Control
function SetTimer(hWnd: LongWord; nIDEvent, uElapse: LongWord; lpTimerFunc: LongWord): LongWord;
external 'SetTimer@user32.dll stdcall';

function KillTimer(hWnd: LongWord; nIDEvent: LongWord): BOOL;
external 'KillTimer@user32.dll stdcall';

function ShowWindow(hWnd: HWND; nCmdShow: Integer): BOOL;
external 'ShowWindow@user32.dll stdcall';

const
  SW_MAXIMIZE = 3;

var
  ConfigPage: TInputQueryWizardPage;
  TipsLabel: TNewStaticText;

  // Slideshow components
  SlideImage: TBitmapImage;
  SlideTimerID: LongWord;
  SlideIndex: Integer;

procedure TimerProc(H: LongWord; Msg: LongWord; IdEvent: LongWord; Time: LongWord);
var
  FileName: String;
begin
  if IdEvent = SlideTimerID then
  begin
    SlideIndex := (SlideIndex + 1) mod 6;
    FileName := 'slide_' + IntToStr(SlideIndex + 1) + '.bmp';
    SlideImage.Bitmap.LoadFromFile(ExpandConstant('{tmp}\' + FileName));
  end;
end;

procedure InitializeWizard;
var
  I: Integer;
begin
  // --- FULLSCREEN & RESIZABLE FIX ---
  WizardForm.BorderIcons := [biSystemMenu, biMinimize, biMaximize];
  WizardForm.BorderStyle := bsSizeable;
  ShowWindow(WizardForm.Handle, SW_MAXIMIZE);

  // --- PRE-EXTRACT SLIDES ---
  for I := 1 to 6 do
    ExtractTemporaryFile('slide_' + IntToStr(I) + '.bmp');

  // --- SINGLE CONFIG PAGE ---
  ConfigPage := CreateInputQueryPage(wpSelectTasks,
    'Configurazione Generale', 'Parametri Cloud e Notifiche',
    'Inserisci i parametri necessari per il funzionamento del software.');

  // 0-2: Cloud
  ConfigPage.Add('Gemini API Key:', False);
  ConfigPage.Add('Google Cloud Project ID:', False);
  ConfigPage.Add('GCS Bucket Name:', False);

  // 3-6: SMTP
  ConfigPage.Add('SMTP Host:', False);
  ConfigPage.Add('SMTP Port:', False);
  ConfigPage.Add('SMTP User:', False);
  ConfigPage.Add('SMTP Password:', True);

  // 7-8: Recipients
  ConfigPage.Add('Destinatari (A):', False);
  ConfigPage.Add('Destinatari in copia (CC):', False);

  // Optimize Logo Layout
  WizardForm.WizardSmallBitmapImage.Width := ScaleX(150);
  WizardForm.WizardSmallBitmapImage.Height := ScaleY(57);
  WizardForm.WizardSmallBitmapImage.Left := WizardForm.ClientWidth - ScaleX(160);
  WizardForm.WizardSmallBitmapImage.Top := ScaleY(5);

  // Tips Label (Italian & Elegant)
  TipsLabel := TNewStaticText.Create(WizardForm);
  TipsLabel.Parent := WizardForm.InstallingPage;
  TipsLabel.Visible := False;
  TipsLabel.WordWrap := True;
  TipsLabel.Caption := 'Inizializzazione del sistema in corso...' + #13#10 + #13#10 +
                       '- Attivazione motore di elaborazione...' + #13#10 +
                       '- Configurazione database locale crittografato...' + #13#10 +
                       '- Predisposizione modulo notifiche...' + #13#10 +
                       '- Verifica integrità componenti...' + #13#10 +
                       '- Preparazione ambiente utente...' + #13#10 + #13#10 +
                       'Attendere prego. Stiamo approntando il tuo ambiente di lavoro.';
  TipsLabel.Font.Style := [fsItalic];
  TipsLabel.Font.Color := clWindowText;
  TipsLabel.Font.Name := 'Segoe UI';
  TipsLabel.Font.Size := 12;

  // Initialize Slideshow Image
  SlideImage := TBitmapImage.Create(WizardForm);
  SlideImage.Parent := WizardForm.InstallingPage;
  SlideImage.Visible := False;
  SlideImage.Stretch := True;
  SlideImage.Center := True;
  SlideImage.Bitmap.LoadFromFile(ExpandConstant('{tmp}\slide_1.bmp'));
  SlideIndex := 0;
end;

procedure CurPageChanged(CurPageID: Integer);
var
  HalfWidth: Integer;
begin
  if CurPageID = wpInstalling then
  begin
    HalfWidth := WizardForm.InstallingPage.ClientWidth div 2;

    // LEFT COLUMN
    WizardForm.StatusLabel.Left := ScaleX(40);
    WizardForm.StatusLabel.Width := HalfWidth - ScaleX(80);
    WizardForm.StatusLabel.Font.Size := 10;

    WizardForm.FileNameLabel.Left := ScaleX(40);
    WizardForm.FileNameLabel.Width := HalfWidth - ScaleX(80);

    WizardForm.ProgressGauge.Left := ScaleX(40);
    WizardForm.ProgressGauge.Width := HalfWidth - ScaleX(80);
    WizardForm.ProgressGauge.Height := ScaleY(25);

    TipsLabel.Visible := True;
    TipsLabel.Left := ScaleX(40);
    TipsLabel.Width := HalfWidth - ScaleX(80);
    TipsLabel.Top := WizardForm.ProgressGauge.Top + WizardForm.ProgressGauge.Height + ScaleY(40);

    // RIGHT COLUMN: Slideshow
    SlideImage.Visible := True;
    SlideImage.Left := HalfWidth;
    SlideImage.Top := ScaleY(20);
    SlideImage.Width := HalfWidth - ScaleX(40);
    SlideImage.Height := WizardForm.InstallingPage.ClientHeight - ScaleY(40);

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
  if CurStep = ssInstall then
  begin
     if WizardIsTaskSelected('cleancache') then
     begin
        DelTree(ExpandConstant('{localappdata}\Intelleo\cache'), True, True, True);
     end;
  end;

  if CurStep = ssPostInstall then
  begin
    AppDataDir := ExpandConstant('{localappdata}\Intelleo');
    if not DirExists(AppDataDir) then ForceDirectories(AppDataDir);
    
    // Show post-install message
    MsgBox('Installazione completata!' + #13#10 + #13#10 +
           'Al primo avvio, Intelleo potrebbe richiedere la licenza.' + #13#10 +
           'Seguire le istruzioni a schermo.' + #13#10 + #13#10 +
           'Versione: {#MyAppVersion} (Nuitka Build)', 
           mbInformation, MB_OK);

    EnvPath := AppDataDir + '\.env';

    if not LoadStringsFromFile(EnvPath, Lines) then
      SetArrayLength(Lines, 0);

    // Read from SINGLE ConfigPage (Indices 0-8)
    Val := ConfigPage.Values[0]; if Val <> '' then UpdateEnvVar(Lines, 'GEMINI_API_KEY', '"' + Val + '"');
    Val := ConfigPage.Values[1]; if Val <> '' then UpdateEnvVar(Lines, 'GOOGLE_CLOUD_PROJECT', '"' + Val + '"');
    Val := ConfigPage.Values[2]; if Val <> '' then UpdateEnvVar(Lines, 'GCS_BUCKET_NAME', '"' + Val + '"');

    Val := ConfigPage.Values[3]; if Val <> '' then UpdateEnvVar(Lines, 'SMTP_HOST', '"' + Val + '"');
    Val := ConfigPage.Values[4]; if Val <> '' then UpdateEnvVar(Lines, 'SMTP_PORT', Val);
    Val := ConfigPage.Values[5]; if Val <> '' then UpdateEnvVar(Lines, 'SMTP_USER', '"' + Val + '"');
    Val := ConfigPage.Values[6]; if Val <> '' then UpdateEnvVar(Lines, 'SMTP_PASSWORD', '"' + Val + '"');

    Val := ConfigPage.Values[7]; if Val <> '' then UpdateEnvVar(Lines, 'EMAIL_RECIPIENTS_TO', '"' + Val + '"');
    Val := ConfigPage.Values[8]; if Val <> '' then UpdateEnvVar(Lines, 'EMAIL_RECIPIENTS_CC', '"' + Val + '"');

    SaveStringsToFile(EnvPath, Lines, False);
  end;
end;
