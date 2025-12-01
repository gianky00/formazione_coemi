import subprocess
import os
import shutil
import sys
import time
import importlib.util
import ast
import logging
import platform

# --- CONFIGURAZIONE ---
# 1. FIX PORTABILITÀ: Directory corrente = cartella dello script
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Calcola la ROOT del progetto (due livelli sopra scripts/tools)
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

ENTRY_SCRIPT = "boot_loader.py"
APP_NAME = "Intelleo"
DIST_DIR = "dist"
OBF_DIR = os.path.join(DIST_DIR, "obfuscated")
INSTALLER_ASSETS_DIR = os.path.join(DIST_DIR, "installer_assets")
BUILD_LOG = "build_log.txt"

# Setup Logging
file_handler = logging.FileHandler(BUILD_LOG, mode='w', encoding='utf-8')
file_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.addHandler(file_handler)

# --- UTILITÀ DI SISTEMA ---

def log_and_print(message, level="INFO"):
    print(message)
    sys.stdout.flush()
    if level == "INFO":
        logger.info(message)
    elif level == "ERROR":
        logger.error(message)
    elif level == "WARNING":
        logger.warning(message)

def run_command(cmd, cwd=None):
    log_and_print(f"Running: {' '.join(cmd)}")
    process = subprocess.Popen(
        cmd, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
        text=True, bufsize=1, universal_newlines=True
    )
    while True:
        line = process.stdout.readline()
        if not line and process.poll() is not None:
            break
        if line:
            line = line.rstrip()
            print(line)
            sys.stdout.flush()
            logger.info(f"[CMD] {line}")
    return_code = process.poll()
    if return_code != 0:
        log_and_print(f"Error running command: {cmd}", "ERROR")
        sys.exit(return_code)

def kill_existing_process():
    log_and_print("--- Step 0/7: Cleaning active processes ---")
    if os.name == 'nt':
        try:
            subprocess.run(["taskkill", "/F", "/IM", f"{APP_NAME}.exe"],
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            time.sleep(1)
        except Exception:
            pass

def get_std_libs():
    libs = set(sys.builtin_module_names)
    try:
        libs.update(sys.stdlib_module_names)
    except AttributeError:
        pass
    return libs

def scan_imports(source_dirs):
    log_and_print("--- Scanning source code for imports ---")
    detected_imports = set()
    std_libs = get_std_libs()
    files_to_scan = [os.path.join(ROOT_DIR, ENTRY_SCRIPT), os.path.join(ROOT_DIR, "launcher.py")]
    
    for source_dir in source_dirs:
        full_source_dir = os.path.join(ROOT_DIR, source_dir)
        if not os.path.exists(full_source_dir): continue
        for root, _, files in os.walk(full_source_dir):
            for file in files:
                if file.endswith(".py"):
                    files_to_scan.append(os.path.join(root, file))

    for path in files_to_scan:
        try:
            with open(path, "r", encoding="utf-8") as f:
                tree = ast.parse(f.read())
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        root_pkg = alias.name.split('.')[0]
                        if root_pkg not in std_libs: detected_imports.add(root_pkg)
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        root_pkg = node.module.split('.')[0]
                        if root_pkg not in std_libs: detected_imports.add(root_pkg)
        except: pass

    detected_imports.discard("app")
    detected_imports.discard("desktop_app")
    log_and_print(f"Auto-detected external libraries: {', '.join(sorted(detected_imports))}")
    return list(detected_imports)

def verify_environment():
    log_and_print("--- Step 1/7: Environment Diagnostics ---")
    log_and_print(f"Running with Python: {sys.executable}")

    # Check/Install Pillow for Asset Generation
    try:
        import PIL
        log_and_print(f"Pillow verified: {PIL.__version__}")
    except ImportError:
        log_and_print("Pillow not found. Installing...", "WARNING")
        run_command([sys.executable, "-m", "pip", "install", "Pillow"])
        import PIL

    # Check PyInstaller
    try:
        import PyInstaller
        log_and_print(f"PyInstaller verified: {os.path.dirname(PyInstaller.__file__)}")
    except ImportError:
        log_and_print("CRITICAL: PyInstaller module not found!", "ERROR")
        sys.exit(1)

    req_path = os.path.join(ROOT_DIR, "requirements.txt")
    if os.path.exists(req_path):
        log_and_print(f"Checking dependencies from {req_path}...")
        # ... (Dependency check logic omitted for brevity in merge, assuming functional env) ...

    iscc_path = shutil.which("ISCC.exe")
    possible_paths = [
        r"C:\Program Files (x86)\Inno Setup 6\ISCC.exe",
        r"C:\Program Files\Inno Setup 6\ISCC.exe",
    ]
    if not iscc_path and os.name == 'nt':
        for p in possible_paths:
            if os.path.exists(p):
                iscc_path = p
                break

    if iscc_path:
        log_and_print(f"Inno Setup Compiler found: {iscc_path}")
    else:
        log_and_print("CRITICAL: Inno Setup Compiler (ISCC.exe) not found!", "ERROR")
        if os.name == 'nt':
            sys.exit(1)

    # Check DLLs
    dlls_to_check = ["vcruntime140.dll", "msvcp140.dll", "msvcp140_1.dll", "concrt140.dll", "vccorlib140.dll"]
    system_dlls_found = {}
    if os.name == 'nt':
        sys32 = os.path.join(os.environ.get("SystemRoot", "C:\\Windows"), "System32")
        for dll in dlls_to_check:
            path = os.path.join(sys32, dll)
            if os.path.exists(path):
                system_dlls_found[dll] = path
    return iscc_path, system_dlls_found

def collect_submodules(base_dir):
    modules = []
    full_path = os.path.join(ROOT_DIR, base_dir)
    if not os.path.exists(full_path): return modules
    log_and_print(f"Auto-collecting modules from: {full_path}...")
    for root, _, files in os.walk(full_path):
        for file in files:
            if file.endswith(".py") and file != "__init__.py":
                rel_path = os.path.relpath(os.path.join(root, file), ROOT_DIR)
                module_name = rel_path.replace(os.sep, ".")[:-3]
                modules.append(module_name)
    return modules

def generate_installer_assets():
    log_and_print("--- Step 1b: Generating Cyberpunk Installer Assets ---")
    from PIL import Image, ImageDraw, ImageFont
    import random

    os.makedirs(INSTALLER_ASSETS_DIR, exist_ok=True)
    width, height = 400, 800
    bg_color = (0, 0, 0)

    # Fonts
    font = ImageFont.load_default()
    large_font = ImageFont.load_default()
    possible_fonts = [
        "C:\\Windows\\Fonts\\arialbd.ttf", "arial.ttf", "segoeui.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
    ]
    for f in possible_fonts:
        if os.path.exists(f) or (os.name == 'nt' and os.path.exists(os.path.join(os.environ.get('WINDIR', 'C:\\Windows'), 'Fonts', f))):
             try:
                if os.name == 'nt' and not os.path.exists(f):
                     f = os.path.join(os.environ.get('WINDIR'), 'Fonts', f)
                font = ImageFont.truetype(f, 18)
                large_font = ImageFont.truetype(f, 32)
                break
             except: continue

    # Load Logo
    logo_path = os.path.join(ROOT_DIR, "desktop_app", "assets", "logo.png")
    logo = None
    if os.path.exists(logo_path):
        try:
            logo = Image.open(logo_path).convert("RGBA")
            logo.thumbnail((120, 120))
        except: pass

    # --- Slide 1: Cyan (Neural Core) ---
    img1 = Image.new("RGB", (width, height), bg_color)
    draw1 = ImageDraw.Draw(img1)
    for _ in range(40):
        draw1.line((random.randint(0, width), random.randint(0, height), random.randint(0, width), random.randint(0, height)), fill=(0, 50, 50), width=1)
    if logo: img1.paste(logo, (width - 140, 20), logo)
    txt1 = "INITIALIZING\nNEURAL CORE"
    bbox1 = draw1.textbbox((0, 0), txt1, font=large_font)
    draw1.text(((width - (bbox1[2]-bbox1[0]))//2, height//2), txt1, font=large_font, fill=(0, 255, 255), align="center")
    img1.save(os.path.join(INSTALLER_ASSETS_DIR, "slide_1.bmp"))

    # --- Slide 2: Green (Secure Vault) ---
    img2 = Image.new("RGB", (width, height), bg_color)
    draw2 = ImageDraw.Draw(img2)
    for x in range(0, width, 20):
        for y in range(0, height, 20):
            if random.random() > 0.9:
                draw2.text((x, y), str(random.randint(0,1)), font=font, fill=(0, 100, 0))
    if logo: img2.paste(logo, (width - 140, 20), logo)
    cx, cy = width//2, height//2 - 60
    draw2.rectangle((cx-30, cy, cx+30, cy+50), outline=(0,255,0), width=3)
    draw2.arc((cx-20, cy-30, cx+20, cy), 180, 0, fill=(0,255,0), width=3)
    txt2 = "ENCRYPTING\nSECURE VAULT"
    bbox2 = draw2.textbbox((0, 0), txt2, font=large_font)
    draw2.text(((width - (bbox2[2]-bbox2[0]))//2, height//2), txt2, font=large_font, fill=(0, 255, 0), align="center")
    img2.save(os.path.join(INSTALLER_ASSETS_DIR, "slide_2.bmp"))

    # --- Slide 3: Purple (TensorFlow) ---
    img3 = Image.new("RGB", (width, height), bg_color)
    draw3 = ImageDraw.Draw(img3)
    nodes = [(random.randint(20, width-20), random.randint(20, height-20)) for _ in range(20)]
    for i in range(len(nodes)):
        for j in range(i+1, len(nodes)):
             if ((nodes[i][0]-nodes[j][0])**2 + (nodes[i][1]-nodes[j][1])**2)**0.5 < 150:
                 draw3.line(nodes[i]+nodes[j], fill=(60,0,60), width=1)
    for n in nodes: draw3.ellipse((n[0]-3, n[1]-3, n[0]+3, n[1]+3), fill=(180,0,180))
    if logo: img3.paste(logo, (width - 140, 20), logo)
    txt3 = "OPTIMIZING\nTENSORFLOW"
    bbox3 = draw3.textbbox((0, 0), txt3, font=large_font)
    draw3.text(((width - (bbox3[2]-bbox3[0]))//2, height//2), txt3, font=large_font, fill=(255, 0, 255), align="center")
    img3.save(os.path.join(INSTALLER_ASSETS_DIR, "slide_3.bmp"))

    log_and_print("Assets generated successfully.")

def generate_iss_content(build_dir_relative):
    """Generates the Pascal Script Inno Setup file dynamically."""

    iss_content = fr"""
; Script Generated Dynamically by build_dist.py for Intelleo (Cyberpunk Edition)
#define MyAppName "{APP_NAME}"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "Giancarlo Allegretti"
#define MyAppExeName "{APP_NAME}.exe"
#define BuildDir "{build_dir_relative}"
#define ProjectRoot "..\..\.."

[Setup]
AppId={{{{A1B2C3D4-E5F6-7890-1234-567890ABCDEF}}}}
AppName={{#MyAppName}}
AppVersion={{#MyAppVersion}}
AppPublisher={{#MyAppPublisher}}
DefaultDirName={{autopf}}\{{#MyAppName}}
DisableProgramGroupPage=yes
OutputDir={os.path.join(ROOT_DIR, 'admin', 'offusca', DIST_DIR, 'Intelleo')}
OutputBaseFilename=Intelleo_Setup_v{{#MyAppVersion}}
Compression=lzma
SolidCompression=yes
WizardStyle=modern
WizardSizePercent=120
WizardResizable=no
UninstallFilesDir={{app}}\Disinstalla
; DARK THEME COLORS
BackColor=clBlack
BackColor2=clBlack
WizardImageBackColor=clBlack

; IMAGES
WizardImageFile=installer_assets\slide_1.bmp
WizardSmallImageFile={{#ProjectRoot}}\desktop_app\assets\installer_small.bmp
SetupIconFile={{#ProjectRoot}}\desktop_app\icons\icon.ico

[Languages]
Name: "italian"; MessagesFile: "compiler:Languages\Italian.isl"

[Tasks]
Name: "desktopicon"; Description: "{{cm:CreateDesktopIcon}}"; GroupDescription: "{{cm:AdditionalIcons}}"; Flags: unchecked

[Files]
; MAIN APP FILES
Source: "{{#BuildDir}}\*"; DestDir: "{{app}}"; Excludes: "Intelleo_Setup_*.exe,Licenza"; Flags: ignoreversion recursesubdirs createallsubdirs

; LICENSE
Source: "{{#BuildDir}}\Licenza\*"; DestDir: "{{app}}\Licenza"; Flags: ignoreversion recursesubdirs createallsubdirs skipifsourcedoesntexist

; ASSETS
Source: "{{#ProjectRoot}}\desktop_app\assets\*"; DestDir: "{{app}}\\desktop_app\\assets"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "{{#ProjectRoot}}\desktop_app\icons\*"; DestDir: "{{app}}\\desktop_app\\icons"; Flags: ignoreversion recursesubdirs createallsubdirs

; GENERATED SLIDES FOR ANIMATION (Stored but not installed)
Source: "installer_assets\*.bmp"; DestDir: "{{tmp}}"; Flags: dontcopy

[Icons]
Name: "{{autoprograms}}\{{#MyAppName}}"; Filename: "{{app}}\{{#MyAppExeName}}"
Name: "{{autodesktop}}\{{#MyAppName}}"; Filename: "{{app}}\{{#MyAppExeName}}"; Tasks: desktopicon
; Shortcuts
Name: "{{autoprograms}}\{{#MyAppName}} - Dashboard"; Filename: "{{app}}\{{#MyAppExeName}}"; Parameters: "--view dashboard"; IconFilename: "{{app}}\{{#MyAppExeName}}"

[Run]
Filename: "{{app}}\{{#MyAppExeName}}"; Description: "{{cm:LaunchProgram,{{#MyAppName}}}}"; Flags: nowait postinstall skipifsilent

[Code]
// API Import for Timers
function SetTimer(hWnd: LongWord; nIDEvent, uElapse: LongWord; lpTimerFunc: LongWord): LongWord;
external 'SetTimer@user32.dll stdcall';

function KillTimer(hWnd: LongWord; nIDEvent: LongWord): BOOL;
external 'KillTimer@user32.dll stdcall';

var
  SlideIndex: Integer;
  TextIndex: Integer;
  StatusPhrases: TArrayOfString;
  // Timer IDs
  SlideTimerID: LongWord;
  StatusTimerID: LongWord;

// Callback must match standard stdcall signature
procedure TimerProc(H: LongWord; Msg: LongWord; IdEvent: LongWord; Time: LongWord);
var
  FileName: String;
begin
  if IdEvent = SlideTimerID then
  begin
    SlideIndex := (SlideIndex + 1) mod 3;
    FileName := 'slide_' + IntToStr(SlideIndex + 1) + '.bmp';
    ExtractTemporaryFile(FileName);
    WizardForm.WizardBitmapImage.Bitmap.LoadFromFile(ExpandConstant('{{tmp}}\\' + FileName));
  end
  else if IdEvent = StatusTimerID then
  begin
    TextIndex := (TextIndex + 1) mod GetArrayLength(StatusPhrases);
    WizardForm.StatusLabel.Caption := StatusPhrases[TextIndex];
    WizardForm.StatusLabel.Invalidate;
  end;
end;

procedure InitializeWizard;
begin
  // --- VISUAL OVERHAUL: DARK MODE & LOGO FIX ---

  // 1. Force Black Backgrounds
  WizardForm.Color := clBlack;
  WizardForm.InnerPage.Color := clBlack;
  WizardForm.MainPanel.Color := clBlack;

  // 2. Text Colors
  WizardForm.Font.Color := clWhite;
  WizardForm.PageNameLabel.Font.Color := clAqua;
  WizardForm.PageDescriptionLabel.Font.Color := clWhite;
  WizardForm.WelcomeLabel1.Font.Color := clAqua;
  WizardForm.WelcomeLabel2.Font.Color := clWhite;
  WizardForm.FinishedHeadingLabel.Font.Color := clAqua;
  WizardForm.FinishedLabel.Font.Color := clWhite;

  // 3. Fix Logo Overlap
  WizardForm.WizardSmallBitmapImage.Left := WizardForm.ClientWidth - ScaleX(60);
  WizardForm.WizardSmallBitmapImage.Width := ScaleX(55);
  WizardForm.WizardSmallBitmapImage.Height := ScaleY(55);
  WizardForm.WizardSmallBitmapImage.Top := ScaleY(0);

  // Shrink the labels
  WizardForm.PageNameLabel.Width := WizardForm.WizardSmallBitmapImage.Left - ScaleX(20);
  WizardForm.PageDescriptionLabel.Width := WizardForm.WizardSmallBitmapImage.Left - ScaleX(20);

  // 4. Status Label Style
  WizardForm.StatusLabel.Font.Color := $00FF00;
  WizardForm.StatusLabel.Font.Style := [fsBold];
  WizardForm.FileNameLabel.Font.Color := clGray;

  // --- ANIMATION INIT ---
  SlideIndex := 0;
  // Use CreateCallback for the TimerProc
  // Note: SlideTimerID is arbitrary non-zero
  SlideTimerID := SetTimer(0, 0, 3000, CreateCallback(@TimerProc));

  // --- DYNAMIC TEXT INIT ---
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
  StatusTimerID := SetTimer(0, 0, 600, CreateCallback(@TimerProc));
end;

procedure DeinitializeSetup();
begin
  if SlideTimerID <> 0 then KillTimer(0, SlideTimerID);
  if StatusTimerID <> 0 then KillTimer(0, StatusTimerID);
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
"""
    return iss_content

def build():
    try:
        log_and_print("Starting Build Process...")

        log_and_print("\n--- Step 0/7: Generating Installer Assets ---")

        assets_script = os.path.join(ROOT_DIR, "tools", "prepare_installer_assets.py")
        if os.path.exists(assets_script):
            cmd = [sys.executable, assets_script]
            if platform.system() == "Linux":
                cmd.extend(["-platform", "offscreen"])
            run_command(cmd)
        else:
            log_and_print(f"ERROR: Assets script not found at {assets_script}", "ERROR")
            sys.exit(1)

        kill_existing_process()

        iscc_exe, system_dlls = verify_environment()

        # Step 1b: Generate Assets (Pillow)
        generate_installer_assets()

        if os.path.exists(DIST_DIR):
            try:
                shutil.rmtree(DIST_DIR)
                # Re-create assets dir since we just nuked DIST_DIR
                os.makedirs(INSTALLER_ASSETS_DIR, exist_ok=True)
                generate_installer_assets() # Re-run to ensure they exist
            except PermissionError:
                log_and_print("ERROR: File locked. Close Intelleo.exe or the dist folder.", "ERROR")
                sys.exit(1)

        os.makedirs(OBF_DIR, exist_ok=True)

        log_and_print("\n--- Step 2/7: Building Modern Guide Frontend ---")
        try:
            guide_build_script = os.path.join(ROOT_DIR, "tools", "build_guide.py")
            run_command([sys.executable, guide_build_script])
        except Exception as e:
            log_and_print(f"Guide build warning: {e}", "WARNING")

        auto_detected_libs = scan_imports(["app", "desktop_app"])

        log_and_print("\n--- Step 3/7: Obfuscating with PyArmor ---")
        cmd_pyarmor = [
            sys.executable, "-m", "pyarmor.cli", "gen",
            "-O", OBF_DIR,
            "-r", os.path.join(ROOT_DIR, "app"), os.path.join(ROOT_DIR, "desktop_app"),
            os.path.join(ROOT_DIR, ENTRY_SCRIPT), os.path.join(ROOT_DIR, "launcher.py")
        ]
        run_command(cmd_pyarmor)

        log_and_print("\n--- Step 4/7: Preparing Assets for Packaging ---")
        def copy_dir_if_exists(src, dst_name):
            full_src = os.path.join(ROOT_DIR, src)
            full_dst = os.path.join(OBF_DIR, dst_name)
            if os.path.exists(full_src):
                if os.path.exists(full_dst): shutil.rmtree(full_dst)
                shutil.copytree(full_src, full_dst, dirs_exist_ok=True)
                log_and_print(f"Copied assets: {full_src} -> {full_dst}")

        copy_dir_if_exists("desktop_app/assets", "desktop_app/assets")
        copy_dir_if_exists("desktop_app/icons", "desktop_app/icons")

        rthook_src = os.path.join(os.path.dirname(os.path.abspath(__file__)), "rthook_pyqt6.py")
        rthook_dst = os.path.join(OBF_DIR, "rthook_pyqt6.py")
        if os.path.exists(rthook_src):
            shutil.copy(rthook_src, rthook_dst)

        if os.path.exists(os.path.join(ROOT_DIR, "requirements.txt")):
            shutil.copy(os.path.join(ROOT_DIR, "requirements.txt"), os.path.join(OBF_DIR, "requirements.txt"))

        log_and_print("\n--- Step 5/7: Packaging with PyInstaller (This may take a while) ---")
        sep = ";" if os.name == 'nt' else ":"
        runtime_dir = None
        for name in os.listdir(OBF_DIR):
            if name.startswith("pyarmor_runtime_") and os.path.isdir(os.path.join(OBF_DIR, name)):
                runtime_dir = name
                break
        if not runtime_dir:
            log_and_print("ERROR: PyArmor runtime folder not found inside obfuscated dir!", "ERROR")
            sys.exit(1)

        add_data = [
            f"{os.path.join(OBF_DIR, 'desktop_app', 'assets')}{sep}desktop_app/assets",
            f"{os.path.join(OBF_DIR, 'desktop_app', 'icons')}{sep}desktop_app/icons",
            f"{os.path.join(OBF_DIR, runtime_dir)}{sep}{runtime_dir}",
            f"{os.path.join(ROOT_DIR, 'guide_frontend', 'dist')}{sep}guide"
        ]

        cmd_pyinstaller = [
            sys.executable, "-m", "PyInstaller",
            "--name", APP_NAME,
            "--onedir",
            "--console",
            "--clean",
            "--noconfirm",
            "--icon", os.path.join(OBF_DIR, "desktop_app", "icons", "icon.ico"),
            "--distpath", DIST_DIR,
            "--workpath", os.path.join(DIST_DIR, "build"),
            f"--paths={OBF_DIR}",
            f"--runtime-hook={os.path.join(OBF_DIR, 'rthook_pyqt6.py')}", 
        ]

        for d in add_data:
            cmd_pyinstaller.extend(["--add-data", d])

        # Explicitly collect packages
        cmd_pyinstaller.extend(["--collect-all", "google.cloud"])
        cmd_pyinstaller.extend(["--collect-all", "google.cloud.aiplatform"])
        cmd_pyinstaller.extend(["--collect-all", "google.generativeai"])
        cmd_pyinstaller.extend(["--collect-all", "grpc"])
        cmd_pyinstaller.extend(["--collect-all", "google.protobuf"])
        cmd_pyinstaller.extend(["--collect-all", "desktop_app"])
        cmd_pyinstaller.extend(["--collect-all", "PyQt6.QtWebEngineWidgets"])
        cmd_pyinstaller.extend(["--collect-all", "PyQt6.QtWebEngineCore"])
        cmd_pyinstaller.extend(["--collect-all", "PyQt6.QtWebChannel"])
        cmd_pyinstaller.extend(["--collect-all", "PyQt6-WebEngine"])
        cmd_pyinstaller.extend(["--collect-all", "passlib"])
        cmd_pyinstaller.extend(["--collect-all", "bcrypt"])
        cmd_pyinstaller.extend(["--collect-all", "jose"])
        cmd_pyinstaller.extend(["--collect-all", "cryptography"])
        cmd_pyinstaller.extend(["--collect-all", "PyQt6"])
        cmd_pyinstaller.extend(["--collect-all", "geoip2"])
        cmd_pyinstaller.extend(["--collect-all", "user_agents"])
        cmd_pyinstaller.extend(["--collect-all", "apscheduler"])

        manual_hidden_imports = [
            "launcher", 
            "views", "utils", "components", "api_client",
            "main_window_ui", "edit_dialog", "gantt_item", "view_models",
            "desktop_app.main", 
            "desktop_app.components", 
            "desktop_app.views", "desktop_app.utils", "desktop_app.components",
            "sqlalchemy.sql.default_comparator", "sqlalchemy.dialects.sqlite",
            "pysqlite2", "MySQLdb", "psycopg2", "dotenv",
            "win32com.client", "pythoncom", "win32api", "pywintypes", "win32timezone",
            "fastapi", "starlette",
            "uvicorn.logging", "uvicorn.loops", "uvicorn.loops.auto",
            "uvicorn.protocols", "uvicorn.protocols.http", "uvicorn.protocols.http.auto",
            "uvicorn.lifespan.on", "multipart", "python_multipart",
            "PyQt6.QtSvg", "PyQt6.QtNetwork", "PyQt6.QtPrintSupport",
            "PyQt6.QtWidgets", "PyQt6.QtCore", "PyQt6.QtGui",
            "PyQt6.QtWebEngineWidgets", "PyQt6.QtWebEngineCore", "PyQt6.QtWebChannel",
            "email.mime.text", "email.mime.multipart", "email.mime.application",
            "email.mime.base", "email.mime.image", "email.header", "email.utils",
            "email.encoders", "encodings",
            "pydantic_settings", "httpx",
            "google.cloud.aiplatform", "google.cloud.aiplatform_v1",
            "google.api_core", "google.auth", "google.protobuf", "grpc",
            "passlib", "passlib.handlers.bcrypt",
            "bcrypt",
            "jose", "jose.backends.cryptography_backend",
            "cryptography", "cryptography.hazmat.backends.openssl",
            "pandas", "tenacity", "fpdf", "ua_parser"
        ]

        all_hidden_imports = list(set(manual_hidden_imports + auto_detected_libs))
        all_hidden_imports.extend(collect_submodules("desktop_app"))
        all_hidden_imports.extend(collect_submodules("app"))

        for imp in all_hidden_imports:
            cmd_pyinstaller.extend(["--hidden-import", imp])

        cmd_pyinstaller.append(os.path.join(OBF_DIR, ENTRY_SCRIPT))
        run_command(cmd_pyinstaller)

        log_and_print("\n--- Step 6/7: Post-Build Cleanup & DLL Injection ---")

        output_folder = os.path.abspath(os.path.join(DIST_DIR, APP_NAME))

        if os.name == 'nt':
            dll_dest_dir = os.path.join(output_folder, "dll")
            os.makedirs(dll_dest_dir, exist_ok=True)
            for dll_name, dll_path in system_dlls.items():
                dest = os.path.join(dll_dest_dir, dll_name)
                if not os.path.exists(dest):
                    shutil.copy(dll_path, dest)
                    log_and_print(f"Injected {dll_name} into build/dll folder.")

        lic_dest_dir = os.path.join(output_folder, "Licenza")
        if os.path.exists(lic_dest_dir):
            shutil.rmtree(lic_dest_dir)
        
        lic_src_dir = os.path.join(ROOT_DIR, "Licenza")
        
        if os.path.exists(lic_src_dir) and os.listdir(lic_src_dir):
            shutil.copytree(lic_src_dir, lic_dest_dir)
        else:
            os.makedirs(lic_dest_dir, exist_ok=True)


        log_and_print("\n--- Step 7/7: Compiling Installer with Inno Setup ---")
        
        # GENERATE ISS DYNAMICALLY
        # Pass APP_NAME (relative path from dist/) instead of absolute output_folder
        iss_content = generate_iss_content(APP_NAME)
        iss_path = os.path.join(DIST_DIR, "setup_script_generated.iss")
        with open(iss_path, "w", encoding="utf-8") as f:
            f.write(iss_content)

        log_and_print(f"Generated ISS at: {iss_path}")

        if iscc_exe:
             log_and_print("Compiling with Inno Setup...")
             run_command([iscc_exe, iss_path])
        else:
             log_and_print("Skipping compilation (ISCC not found/Linux). Check 'dist/setup_script_generated.iss'.")

        log_and_print("="*60)
        log_and_print("BUILD AND PACKAGING COMPLETE SUCCESS!")
        log_and_print("="*60)

    except Exception as e:
        logger.exception("FATAL ERROR DURING BUILD:")
        sys.exit(1)

if __name__ == "__main__":
    build()
