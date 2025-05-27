#!/usr/bin/env python3
"""
Script universel pour créer des exécutables PMT Analytics.
Supporte macOS et Windows avec détection automatique de plateforme.

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
    dependencies = ['Pillow', 'pyinstaller']
    
    for dep in dependencies:
        try:
            if dep == 'Pillow':
                import PIL
            else:
                __import__(dep.lower().replace('-', '_'))
            print(f"✅ {dep} déjà installé")
        except ImportError:
            print(f"📦 Installation de {dep}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", dep])
            print(f"✅ {dep} installé")

def get_icon_path(platform_type):
    """Récupère le chemin de l'icône selon la plateforme."""
    if platform_type == 'windows':
        ico_path = "assets/pmtIcon.ico"
    else:
        ico_path = "assets/pmtIcon.ico"  # macOS peut aussi utiliser .ico
    
    if os.path.exists(ico_path):
        print(f"✅ Icône trouvée : {ico_path}")
        return ico_path
    else:
        print("⚠️ Fichier d'icône non trouvé, création sans icône")
        return None

def create_spec_file_macos(icon_path=None):
    """Crée un fichier .spec optimisé pour macOS."""
    if icon_path:
        icon_line = f"    icon='../{icon_path}',"
        print(f"🎨 Icône configurée : {icon_path}")
    else:
        icon_line = "    icon=None,"
        print("📝 Aucune icône configurée")
    
    spec_content = '''# -*- mode: python ; coding: utf-8 -*-

import os
import sys
from pathlib import Path

# Chemin du projet
project_path = os.path.dirname(os.path.abspath(SPEC))

a = Analysis(
    ['../gui_interface.py'],
    pathex=[
        project_path,
        os.path.join(project_path, '..'),
        os.path.join(project_path, '..', 'utils'),
    ],
    binaries=[],
    datas=[
        ('../utils', 'utils'),
        ('../config.py', '.'),
        ('../assets', 'assets'),
    ],
    hiddenimports=[
        # Modules Python standard
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
        
        # Modules du projet
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
        
        # Modules pandas/numpy cachés souvent oubliés
        'pandas._libs.tslibs.timedeltas',
        'pandas._libs.tslibs.np_datetime',
        'pandas._libs.tslibs.nattype',
        'pandas._libs.properties',
        'numpy.random.common',
        'numpy.random.bounded_integers',
        'numpy.random.entropy',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)

# Ajouter explicitement tous les modules utils
for module_name in [
    'utils.data_loader',
    'utils.data_processor', 
    'utils.statistics',
    'utils.excel_writer',
    'utils.reporter',
    'utils.calculateurs',
    'utils.formatters',
    'utils.filtres',
    'utils.horaires'
]:
    if module_name not in a.hiddenimports:
        a.hiddenimports.append(module_name)

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
''' + icon_line + '''
    bundle_identifier='com.enedis.pmtanalytics',
    info_plist={
        'NSPrincipalClass': 'NSApplication',
        'NSAppleScriptEnabled': False,
        'CFBundleDocumentTypes': [
            {
                'CFBundleTypeName': 'CSV Files',
                'CFBundleTypeExtensions': ['csv'],
                'CFBundleTypeRole': 'Viewer'
            }
        ]
    },
)
'''
    
    with open('scripts/PMTAnalytics_macOS.spec', 'w', encoding='utf-8') as f:
        f.write(spec_content)
    
    print("✅ Fichier .spec macOS créé")

def create_spec_file_windows(icon_path=None):
    """Crée un fichier .spec optimisé pour Windows."""
    if icon_path:
        icon_line = f"    icon='../{icon_path}',"
        print(f"🎨 Icône configurée : {icon_path}")
    else:
        icon_line = "    icon=None,"
        print("📝 Aucune icône configurée")
    
    spec_content = '''# -*- mode: python ; coding: utf-8 -*-

import os
import sys
from pathlib import Path

# Chemin du projet
project_path = os.path.dirname(os.path.abspath(SPEC))

a = Analysis(
    ['../gui_interface.py'],
    pathex=[
        project_path,
        os.path.join(project_path, '..'),
        os.path.join(project_path, '..', 'utils'),
    ],
    binaries=[],
    datas=[
        ('../utils', 'utils'),
        ('../config.py', '.'),
        ('../assets', 'assets'),
    ],
    hiddenimports=[
        # Modules Python standard
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
        
        # Modules du projet
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
        
        # Modules pandas/numpy cachés souvent oubliés
        'pandas._libs.tslibs.timedeltas',
        'pandas._libs.tslibs.np_datetime',
        'pandas._libs.tslibs.nattype',
        'pandas._libs.properties',
        'numpy.random.common',
        'numpy.random.bounded_integers',
        'numpy.random.entropy',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)

# Ajouter explicitement tous les modules utils
for module_name in [
    'utils.data_loader',
    'utils.data_processor', 
    'utils.statistics',
    'utils.excel_writer',
    'utils.reporter',
    'utils.calculateurs',
    'utils.formatters',
    'utils.filtres',
    'utils.horaires'
]:
    if module_name not in a.hiddenimports:
        a.hiddenimports.append(module_name)

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
    console=False,  # Interface graphique sur Windows
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
''' + icon_line + '''
)
'''
    
    with open('scripts/PMTAnalytics_Windows.spec', 'w', encoding='utf-8') as f:
        f.write(spec_content)
    
    print("✅ Fichier .spec Windows créé")

def build_executable(platform_type):
    """Construit l'exécutable avec PyInstaller."""
    if platform_type == 'macos':
        spec_file = 'scripts/PMTAnalytics_macOS.spec'
        print("🔨 Construction de l'exécutable macOS...")
    elif platform_type == 'windows':
        spec_file = 'scripts/PMTAnalytics_Windows.spec'
        print("🔨 Construction de l'exécutable Windows...")
    else:
        print(f"❌ Plateforme {platform_type} non supportée")
        return False
    
    try:
        # Nettoyer les anciens builds
        for folder in ['build', f'dist_{platform_type}']:
            if os.path.exists(folder):
                import shutil
                shutil.rmtree(folder)
                print(f"🧹 Dossier {folder} nettoyé")
        
        # Construire avec le fichier .spec
        cmd = [
            sys.executable, "-m", "PyInstaller",
            "--clean",
            "--distpath", f"dist_{platform_type}",
            spec_file
        ]
        
        print(f"🚀 Lancement de PyInstaller pour {platform_type}...")
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"✅ Exécutable {platform_type} créé avec succès !")
            
            # Vérifier que l'exécutable existe
            if platform_type == 'macos':
                exe_path = Path(f"dist_{platform_type}/PMTAnalytics.app")
                if exe_path.exists():
                    size_mb = get_folder_size(exe_path)
                    print(f"📁 Application créée : {exe_path}")
                    print(f"📏 Taille : {size_mb:.1f} MB")
                    return True
            elif platform_type == 'windows':
                exe_path = Path(f"dist_{platform_type}/PMTAnalytics.exe")
                if exe_path.exists():
                    size_mb = exe_path.stat().st_size / (1024 * 1024)
                    print(f"📁 Exécutable créé : {exe_path}")
                    print(f"📏 Taille : {size_mb:.1f} MB")
                    return True
            
            print(f"❌ L'exécutable {platform_type} n'a pas été trouvé")
            return False
        else:
            print(f"❌ Erreur lors de la construction {platform_type} :")
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

def create_launcher_scripts(platforms_built):
    """Crée des scripts de lancement pour les plateformes construites."""
    current_platform = detect_platform()
    
    if 'macos' in platforms_built:
        launcher_content = '''#!/bin/bash
echo "🚀 Lancement de PMT Analytics (macOS)..."
open dist_macos/PMTAnalytics.app
'''
        with open('scripts/lancer_app_macos.sh', 'w') as f:
            f.write(launcher_content)
        os.chmod('scripts/lancer_app_macos.sh', 0o755)
        print("✅ Script de lancement macOS créé : scripts/lancer_app_macos.sh")
    
    if 'windows' in platforms_built:
        launcher_content = '''@echo off
echo 🚀 Lancement de PMT Analytics (Windows)...
start dist_windows\\PMTAnalytics.exe
'''
        with open('scripts/lancer_app_windows.bat', 'w') as f:
            f.write(launcher_content)
        print("✅ Script de lancement Windows créé : scripts/lancer_app_windows.bat")

def show_menu():
    """Affiche le menu de sélection des plateformes."""
    current_platform = detect_platform()
    
    print("🎯 SÉLECTION DES PLATEFORMES")
    print("=" * 40)
    print(f"Plateforme actuelle : {current_platform}")
    print()
    print("1. Créer pour la plateforme actuelle uniquement")
    print("2. Créer pour macOS uniquement")
    print("3. Créer pour Windows uniquement")
    print("4. Créer pour macOS ET Windows")
    print("5. Quitter")
    print()
    
    while True:
        try:
            choice = input("Votre choix (1-5) : ").strip()
            if choice in ['1', '2', '3', '4', '5']:
                return choice
            else:
                print("❌ Choix invalide. Veuillez entrer 1, 2, 3, 4 ou 5.")
        except KeyboardInterrupt:
            print("\n❌ Opération annulée")
            return '5'

def main():
    """Fonction principale."""
    print("🚀 CRÉATEUR D'EXÉCUTABLES PMT ANALYTICS")
    print("=" * 60)
    print()
    
    # Détecter et se placer dans le bon répertoire
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)  # Remonter d'un niveau depuis scripts/
    
    # Vérifier si on trouve gui_interface.py dans le répertoire parent
    if os.path.exists(os.path.join(project_root, 'gui_interface.py')):
        os.chdir(project_root)
        print(f"✅ Répertoire de projet détecté : {project_root}")
    elif os.path.exists('gui_interface.py'):
        print("✅ Répertoire de projet détecté (déjà dans le bon dossier)")
    else:
        print("❌ Erreur : Impossible de trouver gui_interface.py")
        print("💡 Assurez-vous que le script est dans le dossier scripts/ du projet")
        return False
    
    # Afficher le menu
    choice = show_menu()
    
    if choice == '5':
        print("👋 Au revoir !")
        return True
    
    # Installer les dépendances
    print("\n📦 Vérification des dépendances...")
    install_dependencies()
    
    # Déterminer les plateformes à construire
    current_platform = detect_platform()
    platforms_to_build = []
    
    if choice == '1':
        if current_platform in ['macos', 'windows']:
            platforms_to_build = [current_platform]
        else:
            print(f"❌ Plateforme {current_platform} non supportée")
            return False
    elif choice == '2':
        platforms_to_build = ['macos']
    elif choice == '3':
        platforms_to_build = ['windows']
    elif choice == '4':
        platforms_to_build = ['macos', 'windows']
    
    print(f"\n🎯 Plateformes sélectionnées : {', '.join(platforms_to_build)}")
    
    # Avertissement pour cross-compilation
    if current_platform not in platforms_to_build:
        print("⚠️ ATTENTION : Cross-compilation détectée")
        print("La création d'exécutables pour d'autres plateformes peut ne pas fonctionner")
        response = input("Continuer quand même ? (o/n) : ")
        if response.lower() not in ['o', 'oui', 'y', 'yes']:
            print("❌ Opération annulée")
            return False
    
    platforms_built = []
    
    # Construire pour chaque plateforme
    for platform_type in platforms_to_build:
        print(f"\n🏗️ Construction pour {platform_type.upper()}")
        print("-" * 40)
        
        # Récupérer l'icône
        print("🎨 Vérification de l'icône...")
        icon_path = get_icon_path(platform_type)
        
        # Créer le fichier .spec
        print("⚙️ Création de la configuration...")
        if platform_type == 'macos':
            create_spec_file_macos(icon_path)
        elif platform_type == 'windows':
            create_spec_file_windows(icon_path)
        
        # Construire l'exécutable
        print("🔨 Construction de l'exécutable...")
        if build_executable(platform_type):
            platforms_built.append(platform_type)
            print(f"✅ {platform_type.upper()} terminé avec succès")
        else:
            print(f"❌ Échec pour {platform_type.upper()}")
    
    # Créer les scripts de lancement
    if platforms_built:
        print("\n📝 Création des scripts de lancement...")
        create_launcher_scripts(platforms_built)
        
        print("\n" + "=" * 60)
        print("🎉 SUCCÈS ! Exécutables créés")
        print("=" * 60)
        print()
        
        for platform_type in platforms_built:
            if platform_type == 'macos':
                print(f"📁 macOS : dist_macos/PMTAnalytics.app")
                print(f"🚀 Test : ./scripts/lancer_app_macos.sh")
            elif platform_type == 'windows':
                print(f"📁 Windows : dist_windows/PMTAnalytics.exe")
                print(f"🚀 Test : scripts/lancer_app_windows.bat")
        
        print()
        print("💡 Instructions de distribution :")
        print("1. Compressez les dossiers 'dist_*' en ZIP")
        print("2. Distribuez les ZIP aux utilisateurs correspondants")
        print()
        
        # Proposer de tester si on est sur la bonne plateforme
        current_platform = detect_platform()
        if current_platform in platforms_built:
            response = input(f"Voulez-vous tester l'application {current_platform} maintenant ? (o/n): ")
            if response.lower() in ['o', 'oui', 'y', 'yes']:
                if current_platform == 'macos':
                    subprocess.run(['open', 'dist_macos/PMTAnalytics.app'])
                elif current_platform == 'windows':
                    subprocess.run(['start', 'dist_windows/PMTAnalytics.exe'], shell=True)
        
        return True
    else:
        print("\n❌ Aucun exécutable créé avec succès")
        return False

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n❌ Opération annulée par l'utilisateur")
    except Exception as e:
        print(f"\n❌ Erreur inattendue : {e}")
        import traceback
        traceback.print_exc()
    finally:
        input("\nAppuyez sur Entrée pour fermer...") 