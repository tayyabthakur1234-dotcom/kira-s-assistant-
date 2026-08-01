# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller Spec File for KIRA AI Operating System Engine (Phase 12)
Bundles FastAPI backend, Open Interpreter, Vision, Voice, Memory, Router,
Developer Engine, and Enterprise Platform into a standalone Windows EXE.
"""

block_cipher = None

a = Analysis(
    ['api/main.py'],
    pathex=['.'],
    binaries=[],
    datas=[
        ('config', 'config'),
        ('plugins', 'plugins'),
        ('developer', 'developer'),
        ('production', 'production'),
        ('first_run_config.json', '.'),
    ],
    hiddenimports=[
        'uvicorn',
        'fastapi',
        'pydantic',
        'httpx',
        'psutil',
        'cv2',
        'numpy',
        'PIL',
        'pyautogui',
        'speech_recognition',
        'edge_tts',
        'google.genai',
        'chromadb',
        'sqlite3',
        'developer.code_analyzer',
        'developer.code_generator',
        'developer.debugger',
        'developer.testing_engine',
        'developer.git_manager',
        'developer.github_manager',
        'developer.docker_manager',
        'developer.vscode_manager',
        'developer.doc_generator',
        'developer.pair_programming',
        'developer.security_scanner',
        'developer.project_manager',
        'production.installer',
        'production.first_run_wizard',
        'production.background_service',
        'production.auto_updater',
        'production.crash_recovery',
        'production.security_vault',
        'production.backup_restore',
        'production.diagnostics',
        'production.telemetry_logging',
        'production.system_modes',
        'production.enterprise_platform'
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='KIRA_AI_OS_Engine',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='public/icon.ico' if False else None
)
