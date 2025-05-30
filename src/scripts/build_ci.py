#!/usr/bin/env python3
"""
Script de build automatisé pour GitHub Actions.
Détecte automatiquement la plateforme et compile l'exécutable correspondant.

author : CAPELLE Gabin
"""

import subprocess
import sys
import os
import platform
from pathlib import Path

def detect_platform():
    """Détecte la plateforme actuelle."""
    system = platform.system().lower()
    if system == 'darwin':
        return 'macos'
    elif system == 'windows':
        return 'windows'
    elif system == 'linux':
        return 'linux'
    else:
        return 'unknown'

def install_dependencies():
    """Installe les dépendances nécessaires."""
    print("[DEPS] Installation des dépendances...")
    
    # Installer PyInstaller
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
        print("[OK] PyInstaller installé")
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Erreur installation PyInstaller : {e}")
        return False
    
    return True

def get_icon_path():
    """Récupère le chemin de l'icône."""
    ico_path = "assets/pmtIcon.ico"
    
    if os.path.exists(ico_path):
        print(f"[OK] Icône trouvée : {ico_path}")
        return ico_path
    else:
        print("[WARNING] Fichier d'icône non trouvé, création sans icône")
        return None

def create_spec_file_macos(icon_path=None):
    """Crée un fichier .spec optimisé pour macOS."""
    if icon_path:
        icon_line = f"    icon='{icon_path}',"
    else:
        icon_line = "    icon=None,"
    
    spec_content = f'''# -*- mode: python ; coding: utf-8 -*-

import os
import sys
from pathlib import Path

a = Analysis(
    ['main.py'],
    pathex=['.'],
    binaries=[],
    datas=[
        ('src/utils', 'src/utils'),
        ('src/gui', 'src/gui'),
        ('config.py', '.'),
        ('assets', 'assets'),
    ],
    hiddenimports=[
        'pandas',
        'numpy',
        'openpyxl',
        'tkinter',
        'tkinter.ttk',
        'tkinter.filedialog',
        'tkinter.messagebox',
        'tkinter.scrolledtext',
        'threading',
        'queue',
        'datetime',
        'pathlib',
        'csv',
        'json',
        'os',
        'sys',
        'config',
        'src',
        'src.utils',
        'src.gui',
        'src.gui.interface',
        'src.gui.processing',
        'src.gui.export',
        'src.gui.helpers',
        'src.utils.data_loader',
        'src.utils.calculateurs',
        'src.utils.formatters',
        'src.utils.filtres',
        'src.utils.horaires',
        'src.utils.excel_writer',
        'src.utils.calculateurs_3x8',
        'src.utils.remover',
        'pandas._libs.tslibs.timedeltas',
        'pandas._libs.tslibs.np_datetime',
        'pandas._libs.tslibs.nattype',
        'pandas._libs.properties',
        'numpy.random.common',
        'numpy.random.bounded_integers',
        'numpy.random.entropy',
    ],
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=None)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='PMTAnalytics',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

app = BUNDLE(
    exe,
    name='PMTAnalytics.app',
{icon_line}
    bundle_identifier='com.enedis.pmtanalytics',
    info_plist={{
        'NSPrincipalClass': 'NSApplication',
        'NSAppleScriptEnabled': False,
        'CFBundleDocumentTypes': [
            {{
                'CFBundleTypeName': 'CSV Files',
                'CFBundleTypeExtensions': ['csv'],
                'CFBundleTypeRole': 'Viewer'
            }}
        ]
    }},
)
'''
    
    with open('PMTAnalytics_macOS.spec', 'w', encoding='utf-8') as f:
        f.write(spec_content)
    
    print("[OK] Fichier .spec macOS créé")
    return 'PMTAnalytics_macOS.spec'

def create_spec_file_windows(icon_path=None):
    """Crée un fichier .spec optimisé pour Windows."""
    
    # Gérer l'icône correctement
    if icon_path:
        icon_line = f"    icon='{icon_path}',"
    else:
        icon_line = "    icon=None,"
    
    spec_content = f'''# -*- mode: python ; coding: utf-8 -*-

import os
import sys
from pathlib import Path

a = Analysis(
    ['main.py'],
    pathex=['.'],
    binaries=[],
    datas=[
        ('src/utils', 'src/utils'),
        ('src/gui', 'src/gui'),
        ('config.py', '.'),
        ('assets', 'assets'),
    ],
    hiddenimports=[
        'pandas',
        'numpy',
        'openpyxl',
        'tkinter',
        'tkinter.ttk',
        'tkinter.filedialog',
        'tkinter.messagebox',
        'tkinter.scrolledtext',
        'threading',
        'queue',
        'datetime',
        'pathlib',
        'csv',
        'json',
        'os',
        'sys',
        'config',
        'src',
        'src.utils',
        'src.gui',
        'src.gui.interface',
        'src.gui.processing',
        'src.gui.export',
        'src.gui.helpers',
        'src.utils.data_loader',
        'src.utils.calculateurs',
        'src.utils.formatters',
        'src.utils.filtres',
        'src.utils.horaires',
        'src.utils.excel_writer',
        'pandas._libs.tslibs.timedeltas',
        'src.utils.calculateurs_3x8',
        'src.utils.remover',
        'pandas._libs.tslibs.np_datetime',
        'pandas._libs.tslibs.nattype',
        'pandas._libs.properties',
        'numpy.random.common',
        'numpy.random.bounded_integers',
        'numpy.random.entropy',
    ],
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=None)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='PMTAnalytics',
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
{icon_line}
)
'''
    
    with open('PMTAnalytics_Windows.spec', 'w', encoding='utf-8') as f:
        f.write(spec_content)
    
    print("[OK] Fichier .spec Windows créé")
    return 'PMTAnalytics_Windows.spec'

def build_executable(platform_type, spec_file):
    """Construit l'exécutable avec PyInstaller."""
    print(f"[BUILD] Construction de l'exécutable {platform_type}...")
    
    try:
        # Nettoyer les anciens builds
        for folder in ['build', 'dist']:
            if os.path.exists(folder):
                import shutil
                shutil.rmtree(folder)
                print(f"[CLEAN] Dossier {folder} nettoyé")
        
        # Construire avec le fichier .spec
        cmd = [sys.executable, "-m", "PyInstaller", "--clean", spec_file]
        
        print(f"[PYINSTALLER] Lancement de PyInstaller...")
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"[SUCCESS] Exécutable {platform_type} créé avec succès !")
            return True
        else:
            print(f"[ERROR] Erreur lors de la construction :")
            print(result.stderr)
            return False
            
    except Exception as e:
        print(f"[ERROR] Erreur inattendue : {e}")
        return False

def get_folder_size(folder_path):
    """Calcule la taille d'un dossier en MB."""
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(folder_path):
        for filename in filenames:
            filepath = os.path.join(dirpath, filename)
            if os.path.exists(filepath):
                total_size += os.path.getsize(filepath)
    return total_size / (1024 * 1024)

def verify_build(platform_type):
    """Vérifie que l'exécutable a été créé correctement."""
    if platform_type == 'macos':
        exe_path = Path("dist/PMTAnalytics.app")
        if exe_path.exists():
            size_mb = get_folder_size(exe_path)
            print(f"[INFO] Application créée : {exe_path}")
            print(f"[INFO] Taille : {size_mb:.1f} MB")
            return True
    elif platform_type == 'windows':
        exe_path = Path("dist/PMTAnalytics.exe")
        if exe_path.exists():
            size_mb = exe_path.stat().st_size / (1024 * 1024)
            print(f"[INFO] Exécutable créé : {exe_path}")
            print(f"[INFO] Taille : {size_mb:.1f} MB")
            return True
    
    print(f"[ERROR] Exécutable {platform_type} non trouvé")
    return False

def main():
    """Fonction principale."""
    current_platform = detect_platform()
    
    print("[START] BUILD AUTOMATISE PMT ANALYTICS")
    print("=" * 50)
    print(f"Plateforme détectée : {current_platform}")
    print()
    
    # Vérifier qu'on est dans le bon répertoire
    if not os.path.exists('main.py'):
        print("[ERROR] Erreur : main.py non trouvé")
        return False
    
    # Installer les dépendances
    if not install_dependencies():
        return False
    
    # Récupérer l'icône
    print("[ICON] Vérification de l'icône...")
    icon_path = get_icon_path()
    
    # Créer le fichier .spec selon la plateforme
    print("[CONFIG] Création de la configuration...")
    if current_platform == 'macos':
        spec_file = create_spec_file_macos(icon_path)
    elif current_platform == 'windows':
        spec_file = create_spec_file_windows(icon_path)
    else:
        print(f"[ERROR] Plateforme {current_platform} non supportée")
        return False
    
    # Construire l'exécutable
    if build_executable(current_platform, spec_file):
        if verify_build(current_platform):
            print(f"\n[SUCCESS] BUILD {current_platform.upper()} REUSSI !")
            return True
    
    print(f"\n[ERROR] BUILD {current_platform.upper()} ECHOUE")
    return False

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n[ERROR] Erreur inattendue : {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1) 