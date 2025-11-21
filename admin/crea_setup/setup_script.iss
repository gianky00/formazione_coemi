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
WizardResizable=yes
WizardSizePercent=120
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
  ConfigPage: TWizardPage;
  ScrollBox: TScrollBox;
  ConfigPanel: TPanel;
  Edits: array of TNewEdit;

procedure CreateScrollableConfigPage;
var
  Fields: array of String;
  i, TopPos: Integer;
  Lbl: TNewStaticText;
  Ed: TNewEdit;
begin
  ConfigPage := CreateCustomPage(wpSelectTasks, 'Configurazione Iniziale', 'Inserisci le impostazioni opzionali per l''applicazione (Scorri per vedere tutto)');

  ScrollBox := TScrollBox.Create(ConfigPage);
  ScrollBox.Parent := ConfigPage.Surface;
  ScrollBox.Align := alClient;

  ConfigPanel := TPanel.Create(ConfigPage);
  ConfigPanel.Parent := ScrollBox;
  ConfigPanel.Align := alTop;
  ConfigPanel.BevelOuter := bvNone;
  ConfigPanel.Color := clWindow;

  SetArrayLength(Fields, 9);
  Fields[0] := 'Gemini API Key:';
  Fields[1] := 'Google Cloud Project ID:';
  Fields[2] := 'GCS Bucket Name:';
  Fields[3] := 'SMTP Host:';
  Fields[4] := 'SMTP Port:';
  Fields[5] := 'SMTP User:';
  Fields[6] := 'SMTP Password:';
  Fields[7] := 'Email A (separati da virgola):';
  Fields[8] := 'Email CC (separati da virgola):';

  SetArrayLength(Edits, 9);

  TopPos := 0;
  for i := 0 to 8 do
  begin
    Lbl := TNewStaticText.Create(ConfigPage);
    Lbl.Parent := ConfigPanel;
    Lbl.Caption := Fields[i];
    Lbl.Left := 0;
    Lbl.Top := TopPos;

    Ed := TNewEdit.Create(ConfigPage);
    Ed.Parent := ConfigPanel;
    Ed.Top := TopPos + Lbl.Height + ScaleY(4);
    Ed.Width := ConfigPage.SurfaceWidth - ScaleX(30);
    Ed.Text := '';

    if i = 6 then Ed.PasswordChar := '*';

    Edits[i] := Ed;

    TopPos := Ed.Top + Ed.Height + ScaleY(12);
  end;

  ConfigPanel.Height := TopPos;
end;

procedure InitializeWizard;
var
  TipsLabel: TNewStaticText;
begin
  CreateScrollableConfigPage;

  // Ingrandisci il logo in alto a destra
  WizardForm.WizardSmallBitmapImage.Width := ScaleX(110);
  WizardForm.WizardSmallBitmapImage.Left := WizardForm.ClientWidth - ScaleX(110);

  // Suggerimenti Professionali durante l'installazione
  TipsLabel := TNewStaticText.Create(WizardForm);
  TipsLabel.Parent := WizardForm.InstallingPage;
  TipsLabel.Caption := 'Funzionalit' + #224 + ' Professionali:' + #13#10 + #13#10 +
                       '- Analisi Documentale AI Gemini Pro' + #13#10 +
                       '- Scadenzario Intelligente e Predittivo' + #13#10 +
                       '- Notifiche Automatiche via Email' + #13#10 +
                       '- Gestione Sicura dei Dati Aziendali';
  TipsLabel.Top := WizardForm.ProgressGauge.Top + WizardForm.ProgressGauge.Height + ScaleY(20);
  TipsLabel.Left := 0;
  TipsLabel.Width := WizardForm.InstallingPage.SurfaceWidth;
  TipsLabel.Font.Style := [fsBold, fsItalic];
  TipsLabel.Font.Color := clWindowText;
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

    if LoadStringsFromFile(EnvPath, Lines) then
    begin
      for I := 0 to GetArrayLength(Lines) - 1 do
      begin
        Val := Edits[0].Text;
        if (Val <> '') and (Pos('GEMINI_API_KEY=', Lines[I]) = 1) then Lines[I] := 'GEMINI_API_KEY="' + Val + '"';

        Val := Edits[1].Text;
        if (Val <> '') and (Pos('GOOGLE_CLOUD_PROJECT=', Lines[I]) = 1) then Lines[I] := 'GOOGLE_CLOUD_PROJECT="' + Val + '"';

        Val := Edits[2].Text;
        if (Val <> '') and (Pos('GCS_BUCKET_NAME=', Lines[I]) = 1) then Lines[I] := 'GCS_BUCKET_NAME="' + Val + '"';

        Val := Edits[3].Text;
        if (Val <> '') and (Pos('SMTP_HOST=', Lines[I]) = 1) then Lines[I] := 'SMTP_HOST="' + Val + '"';

        Val := Edits[4].Text;
        if (Val <> '') and (Pos('SMTP_PORT=', Lines[I]) = 1) then Lines[I] := 'SMTP_PORT=' + Val;

        Val := Edits[5].Text;
        if (Val <> '') and (Pos('SMTP_USER=', Lines[I]) = 1) then Lines[I] := 'SMTP_USER="' + Val + '"';

        Val := Edits[6].Text;
        if (Val <> '') and (Pos('SMTP_PASSWORD=', Lines[I]) = 1) then Lines[I] := 'SMTP_PASSWORD="' + Val + '"';

        Val := Edits[7].Text;
        if (Val <> '') and (Pos('EMAIL_RECIPIENTS_TO=', Lines[I]) = 1) then Lines[I] := 'EMAIL_RECIPIENTS_TO="' + Val + '"';

        Val := Edits[8].Text;
        if (Val <> '') and (Pos('EMAIL_RECIPIENTS_CC=', Lines[I]) = 1) then Lines[I] := 'EMAIL_RECIPIENTS_CC="' + Val + '"';
      end;

      SaveStringsToFile(EnvPath, Lines, False);
    end;
  end;
end;
