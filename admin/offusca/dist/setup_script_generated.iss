; Script Generated Dynamically by build_dist.py for Intelleo (Cyberpunk Edition)
#define MyAppName "Intelleo"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "Giancarlo Allegretti"
#define MyAppExeName "Intelleo.exe"

; --- CONFIGURAZIONE PERCORSI DINAMICI ---
; SourcePath è la cartella dove si trova questo script .iss (...\admin\offusca\dist)
#define ScriptDir SourcePath

; Immagini Slide: Si trovano in ...\dist\installer_assets
#define InstallerAssetsDir ScriptDir + "installer_assets"

; Applicazione Compilata: Si trova in ...\dist\Intelleo
#define AppBuildDir ScriptDir + "Intelleo"

; Risorse Esterne: Risaliamo di 3 livelli (dist -> offusca -> admin -> formazione_coemi) per arrivare a desktop_app
#define ProjectRoot ScriptDir + "..\..\..\"
#define DesktopAppDir ProjectRoot + "desktop_app"

[Setup]
AppId={{A1B2C3D4-E5F6-7890-1234-567890ABCDEF}}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={autopf}\{#MyAppName}
DisableProgramGroupPage=yes
; Output nella stessa cartella dello script
OutputDir={#ScriptDir}
OutputBaseFilename=Intelleo_Setup_v{#MyAppVersion}
Compression=lzma
SolidCompression=yes
WizardStyle=modern
WizardSizePercent=120
WizardResizable=no
UninstallFilesDir={app}\Disinstalla
; DARK THEME COLORS
BackColor=clBlack
BackColor2=clBlack
WizardImageBackColor=clBlack

; IMAGES
WizardImageFile={#InstallerAssetsDir}\slide_1.bmp
WizardSmallImageFile={#DesktopAppDir}\assets\installer_small.bmp
SetupIconFile={#DesktopAppDir}\icons\icon.ico

[Languages]
Name: "italian"; MessagesFile: "compiler:Languages\Italian.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
; MAIN APP FILES
Source: "{#AppBuildDir}\*"; DestDir: "{app}"; Excludes: "Intelleo_Setup_*.exe,Licenza"; Flags: ignoreversion recursesubdirs createallsubdirs

; LICENSE
Source: "{#AppBuildDir}\Licenza\*"; DestDir: "{app}\Licenza"; Flags: ignoreversion recursesubdirs createallsubdirs skipifsourcedoesntexist

; ASSETS
Source: "{#DesktopAppDir}\assets\*"; DestDir: "{app}\desktop_app\assets"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "{#DesktopAppDir}\icons\*"; DestDir: "{app}\desktop_app\icons"; Flags: ignoreversion recursesubdirs createallsubdirs

; SLIDES (Vengono estratte in TMP per l'animazione)
Source: "{#InstallerAssetsDir}\*.bmp"; DestDir: "{tmp}"; Flags: dontcopy

[Icons]
Name: "{autoprograms}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon
; Shortcuts
Name: "{autoprograms}\{#MyAppName} - Dashboard"; Filename: "{app}\{#MyAppExeName}"; Parameters: "--view dashboard"; IconFilename: "{app}\{#MyAppExeName}"

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#MyAppName}}"; Flags: nowait postinstall skipifsilent

[Code]
// --- IMPORTAZIONE API WINDOWS PER I TIMER ---
function SetTimer(hWnd: longword; nIDEvent, uElapse: longword; lpTimerFunc: longword): longword; external 'SetTimer@user32.dll stdcall';
function KillTimer(hWnd: longword; nIDEvent: longword): BOOL; external 'KillTimer@user32.dll stdcall';

var
  SlideTimerID: LongWord;
  StatusTimerID: LongWord;
  SlideIndex: Integer;
  TextIndex: Integer;
  StatusPhrases: TArrayOfString;

// --- CALLBACK TIMER SLIDES (Ogni 3 secondi) ---
procedure SlideTimerProc(h: LongWord; msg: LongWord; idevent: LongWord; dwTime: LongWord);
var
  FileName: String;
  FullTmpPath: String;
begin
  try
    // Cicla l'indice tra 0 e 2 (3 slide)
    SlideIndex := (SlideIndex + 1) mod 3;
    // Costruisce il nome file (slide_1.bmp, slide_2.bmp, slide_3.bmp)
    FileName := 'slide_' + IntToStr(SlideIndex + 1) + '.bmp';
    FullTmpPath := ExpandConstant('{tmp}\' + FileName);

    // Controlla se il file esiste (dovrebbe essere stato estratto in InitializeWizard)
    if FileExists(FullTmpPath) then
    begin
      WizardForm.WizardBitmapImage.Bitmap.LoadFromFile(FullTmpPath);
    end;
  except
    // Gestione silenziosa errori per non bloccare l'installer
  end;
end;

// --- CALLBACK TIMER TESTO (Ogni 0.6 secondi) ---
procedure StatusTimerProc(h: LongWord; msg: LongWord; idevent: LongWord; dwTime: LongWord);
begin
  try
    TextIndex := (TextIndex + 1) mod GetArrayLength(StatusPhrases);
    WizardForm.StatusLabel.Caption := StatusPhrases[TextIndex];
  except
  end;
end;

procedure InitializeWizard;
var
  i: Integer;
begin
  // --- VISUAL OVERHAUL: DARK MODE & LOGO FIX ---
  WizardForm.Color := clBlack;
  WizardForm.InnerPage.Color := clBlack;
  WizardForm.MainPanel.Color := clBlack;
  WizardForm.Font.Color := clWhite;

  // Colori etichette
  WizardForm.PageNameLabel.Font.Color := clAqua;
  WizardForm.PageDescriptionLabel.Font.Color := clWhite;
  WizardForm.WelcomeLabel1.Font.Color := clAqua;
  WizardForm.WelcomeLabel2.Font.Color := clWhite;
  WizardForm.FinishedHeadingLabel.Font.Color := clAqua;
  WizardForm.FinishedLabel.Font.Color := clWhite;

  // Fix Logo Overlap
  WizardForm.WizardSmallBitmapImage.Left := WizardForm.ClientWidth - ScaleX(60);
  WizardForm.WizardSmallBitmapImage.Width := ScaleX(55);
  WizardForm.WizardSmallBitmapImage.Height := ScaleY(55);
  WizardForm.WizardSmallBitmapImage.Top := ScaleY(0);
  WizardForm.PageNameLabel.Width := WizardForm.WizardSmallBitmapImage.Left - ScaleX(20);
  WizardForm.PageDescriptionLabel.Width := WizardForm.WizardSmallBitmapImage.Left - ScaleX(20);

  // Status Label Style (Terminale Hacker)
  WizardForm.StatusLabel.Font.Color := $00FF00;
  WizardForm.StatusLabel.Font.Style := [fsBold];
  WizardForm.FileNameLabel.Font.Color := clGray;

  // --- PREPARAZIONE ANIMAZIONE ---
  // Estrai tutte le slide ora per evitare lag durante il timer
  for i := 1 to 3 do
    ExtractTemporaryFile('slide_' + IntToStr(i) + '.bmp');

  SlideIndex := 0;
  // Avvia Timer Slide (3000ms = 3s)
  SlideTimerID := SetTimer(0, 0, 3000, CreateCallback(@SlideTimerProc));

  // --- PREPARAZIONE TESTO DINAMICO ---
  SetArrayLength(StatusPhrases, 10);
  StatusPhrases[0] := 'Initializing Neural Core...';
  StatusPhrases[1] := 'Optimizing Tensor Flow...';
  StatusPhrases[2] := 'Encrypting Local Database (AES-256)...';
  StatusPhrases[3] := 'Calibrating Optical Recognition...';
  StatusPhrases[4] := 'Establishing Secure Environment...';
  StatusPhrases[5] := 'Injecting Dependencies...';
  StatusPhrases[6] := 'Compiling Neural Weights...';
  StatusPhrases[7] := 'Verifying Integrity Checksums...';
  StatusPhrases[8] := 'Allocating Memory Blocks...';
  StatusPhrases[9] := 'System Ready.';

  TextIndex := 0;
  // Avvia Timer Testo (600ms)
  StatusTimerID := SetTimer(0, 0, 600, CreateCallback(@StatusTimerProc));
end;

procedure CurPageChanged(CurPageID: Integer);
begin
  if CurPageID = wpInstalling then
  begin
      WizardForm.WizardBitmapImage.Parent := WizardForm.InnerPage;
      WizardForm.WizardBitmapImage.Left := WizardForm.InnerPage.Width - WizardForm.WizardBitmapImage.Width;
      WizardForm.WizardBitmapImage.Visible := True;
      WizardForm.WizardBitmapImage.BringToFront;
  end;
end;

procedure DeinitializeSetup();
begin
  // --- PULIZIA ---
  // È fondamentale uccidere i timer alla chiusura per evitare crash
  if SlideTimerID <> 0 then KillTimer(0, SlideTimerID);
  if StatusTimerID <> 0 then KillTimer(0, StatusTimerID);
end;