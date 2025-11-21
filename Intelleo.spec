# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_all

datas = [('desktop_app/assets', 'desktop_app/assets'), ('desktop_app/icons', 'desktop_app/icons'), ('dist\\obfuscated\\pyarmor_runtime_009329', 'pyarmor_runtime_009329')]
binaries = []
hiddenimports = ['PyQt6', 'api_client', 'email.mime.multipart', 'pandas', 'apscheduler.triggers.interval', 'edit_dialog', 'MySQLdb', 'email.header', 'fpdf', 'uvicorn', 'gantt_item', 'uvicorn.protocols.http.auto', 'PyQt6.QtCore', 'PyQt6.QtPrintSupport', 'pydantic_settings', 'dateutil', 'apscheduler', 'sqlalchemy', 'email.mime.application', 'email.encoders', 'multipart', 'psycopg2', 'uvicorn.loops.auto', 'PyQt6.QtGui', 'view_models', 'main_window_ui', 'python_multipart', 'uvicorn.lifespan.on', 'httpx', 'google.protobuf', 'grpc', 'PyQt6.QtNetwork', 'google.cloud.aiplatform.gapic', 'pandas._libs.tslibs.base', 'requests', 'google.api_core', 'google', 'fastapi', 'dotenv', 'pyarmor_runtime', 'email.mime.base', 'email.mime.image', 'google.cloud.aiplatform', 'playwright.sync_api', 'pydantic', 'email.utils', 'apscheduler.triggers.cron', 'starlette', 'PyQt6.QtWidgets', 'google.auth', 'pysqlite2', 'google.cloud.aiplatform_v1', 'email.mime.text', 'sqlalchemy.sql.default_comparator', 'PyQt6.QtSvg', 'desktop_app.api_client', 'desktop_app.main', 'desktop_app.main_window_ui', 'desktop_app.views.config_view', 'desktop_app.views.contact_dialog', 'desktop_app.views.dashboard_view', 'desktop_app.views.edit_dialog', 'desktop_app.views.gantt_item', 'desktop_app.views.guide_dialog', 'desktop_app.views.import_view', 'desktop_app.views.scadenzario_view', 'desktop_app.views.validation_view', 'desktop_app.view_models.dashboard_view_model', 'app.main', 'app.api.main', 'app.api.routers.notifications', 'app.api.routers.tuning', 'app.core.config', 'app.core.constants', 'app.db.models', 'app.db.seeding', 'app.db.session', 'app.schemas.schemas', 'app.services.ai_extraction', 'app.services.ai_tuning', 'app.services.certificate_logic', 'app.services.matcher', 'app.services.notification_service']
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
