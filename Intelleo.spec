# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_all

datas = [('desktop_app/assets', 'desktop_app/assets'), ('desktop_app/icons', 'desktop_app/icons'), ('dist\\obfuscated\\pyarmor_runtime_009329', 'pyarmor_runtime_009329')]
binaries = []
hiddenimports = ['sqlalchemy.sql.default_comparator', 'google', 'httpx', 'dotenv', 'PyQt6.QtWidgets', 'PyQt6.QtPrintSupport', 'PyQt6.QtNetwork', 'google.cloud.aiplatform', 'apscheduler', 'uvicorn', 'email.encoders', 'pandas', 'api_client', 'starlette', 'PyQt6.QtGui', 'apscheduler.triggers.cron', 'email.mime.multipart', 'uvicorn.lifespan.on', 'dateutil', 'python_multipart', 'pandas._libs.tslibs.base', 'psycopg2', 'google.auth', 'email.mime.base', 'view_models', 'sqlalchemy', 'edit_dialog', 'fpdf', 'uvicorn.loops.auto', 'apscheduler.triggers.interval', 'PyQt6', 'grpc', 'playwright.sync_api', 'uvicorn.protocols.http.auto', 'pydantic', 'google.cloud.aiplatform.gapic', 'google.protobuf', 'requests', 'PyQt6.QtCore', 'google.cloud.aiplatform_v1', 'google.api_core', 'pyarmor_runtime', 'gantt_item', 'MySQLdb', 'main_window_ui', 'email.mime.application', 'pydantic_settings', 'pysqlite2', 'email.header', 'email.mime.text', 'PyQt6.QtSvg', 'multipart', 'email.mime.image', 'fastapi', 'email.utils', 'desktop_app.api_client', 'desktop_app.main', 'desktop_app.main_window_ui', 'desktop_app.views.config_view', 'desktop_app.views.contact_dialog', 'desktop_app.views.dashboard_view', 'desktop_app.views.edit_dialog', 'desktop_app.views.gantt_item', 'desktop_app.views.guide_dialog', 'desktop_app.views.import_view', 'desktop_app.views.scadenzario_view', 'desktop_app.views.validation_view', 'desktop_app.view_models.dashboard_view_model', 'app.main', 'app.api.main', 'app.api.routers.notifications', 'app.api.routers.tuning', 'app.core.config', 'app.core.constants', 'app.db.models', 'app.db.seeding', 'app.db.session', 'app.schemas.schemas', 'app.services.ai_extraction', 'app.services.ai_tuning', 'app.services.certificate_logic', 'app.services.matcher', 'app.services.notification_service']
tmp_ret = collect_all('google.cloud')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_all('google.cloud.aiplatform')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_all('google_cloud_aiplatform')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_all('google.generativeai')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_all('playwright')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_all('grpc')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_all('proto')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_all('google.protobuf')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]


a = Analysis(
    ['dist\\obfuscated\\launcher.py'],
    pathex=['dist\\obfuscated'],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='Intelleo',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
