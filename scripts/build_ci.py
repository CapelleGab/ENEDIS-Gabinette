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
    print("📦 Installation des dépendances...")
    
    # Installer PyInstaller
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
        print("✅ PyInstaller installé")
    except subprocess.CalledProcessError as e:
        print(f"❌ Erreur installation PyInstaller : {e}")
        return False
    
    return True

def get_icon_path():
    """Récupère le chemin de l'icône."""
    ico_path = "assets/pmtIcon.ico"
    
    if os.path.exists(ico_path):
        print(f"✅ Icône trouvée : {ico_path}")
        return ico_path
    else:
        print("⚠️ Fichier d'icône non trouvé, création sans icône")
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
    ['gui_interface.py'],
    pathex=['.'],
    binaries=[],
    datas=[
        ('utils', 'utils'),
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
        'utils',
        'utils.data_loader',
        'utils.data_processor',
        'utils.statistics',
        'utils.excel_writer',
        'utils.reporter',
        'utils.calculateurs',
        'utils.formatters',
        'utils.filtres',
        'utils.horaires',
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
    
    print("✅ Fichier .spec macOS créé")
    return 'PMTAnalytics_macOS.spec'

def create_spec_file_windows(icon_path=None):
    """Crée un fichier .spec optimisé pour Windows."""
    if icon_path:
        icon_line = f"    icon='{icon_path}',"
    else:
        icon_line = "    icon=None,"
    
    spec_content = f'''# -*- mode: python ; coding: utf-8 -*-

import os
import sys
from pathlib import Path

a = Analysis(
    ['gui_interface.py'],
    pathex=['.'],
    binaries=[],
    datas=[
        ('utils', 'utils'),
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
        'utils',
        'utils.data_loader',
        'utils.data_processor',
        'utils.statistics',
        'utils.excel_writer',
        'utils.reporter',
        'utils.calculateurs',
        'utils.formatters',
        'utils.filtres',
        'utils.horaires',
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
    
    print("✅ Fichier .spec Windows créé")
    return 'PMTAnalytics_Windows.spec'

def build_executable(platform_type, spec_file):
    """Construit l'exécutable avec PyInstaller."""
    print(f"🔨 Construction de l'exécutable {platform_type}...")
    
    try:
        # Nettoyer les anciens builds
        for folder in ['build', 'dist']:
            if os.path.exists(folder):
                import shutil
                shutil.rmtree(folder)
                print(f"🧹 Dossier {folder} nettoyé")
        
        # Construire avec le fichier .spec
        cmd = [sys.executable, "-m", "PyInstaller", "--clean", spec_file]
        
        print(f"🚀 Lancement de PyInstaller...")
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"✅ Exécutable {platform_type} créé avec succès !")
            return True
        else:
            print(f"❌ Erreur lors de la construction :")
            print(result.stderr)
            return False
            
    except Exception as e:
        print(f"❌ Erreur inattendue : {e}")
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
            print(f"📁 Application créée : {exe_path}")
            print(f"📏 Taille : {size_mb:.1f} MB")
            return True
    elif platform_type == 'windows':
        exe_path = Path("dist/PMTAnalytics.exe")
        if exe_path.exists():
            size_mb = exe_path.stat().st_size / (1024 * 1024)
            print(f"📁 Exécutable créé : {exe_path}")
            print(f"📏 Taille : {size_mb:.1f} MB")
            return True
    
    print(f"❌ Exécutable {platform_type} non trouvé")
    return False

def main():
    """Fonction principale."""
    current_platform = detect_platform()
    
    print("🚀 BUILD AUTOMATISÉ PMT ANALYTICS")
    print("=" * 50)
    print(f"Plateforme détectée : {current_platform}")
    print()
    
    # Vérifier qu'on est dans le bon répertoire
    if not os.path.exists('gui_interface.py'):
        print("❌ Erreur : gui_interface.py non trouvé")
        return False
    
    # Installer les dépendances
    if not install_dependencies():
        return False
    
    # Récupérer l'icône
    print("🎨 Vérification de l'icône...")
    icon_path = get_icon_path()
    
    # Créer le fichier .spec selon la plateforme
    print("⚙️ Création de la configuration...")
    if current_platform == 'macos':
        spec_file = create_spec_file_macos(icon_path)
    elif current_platform == 'windows':
        spec_file = create_spec_file_windows(icon_path)
    else:
        print(f"❌ Plateforme {current_platform} non supportée")
        return False
    
    # Construire l'exécutable
    if build_executable(current_platform, spec_file):
        if verify_build(current_platform):
            print(f"\n🎉 BUILD {current_platform.upper()} RÉUSSI !")
            return True
    
    print(f"\n❌ BUILD {current_platform.upper()} ÉCHOUÉ")
    return False

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Erreur inattendue : {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1) 