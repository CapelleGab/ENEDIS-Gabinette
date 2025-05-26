#!/usr/bin/env python3
"""
Script macOS corrigé pour créer un exécutable fonctionnel.
Configure automatiquement PyInstaller avec tous les modules nécessaires.

author : CAPELLE Gabin
"""

import subprocess
import sys
import os
from pathlib import Path

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

def get_icon_path():
    """Récupère le chemin de l'icône si elle existe."""
    ico_path = "assets/pmtIcon.ico"
    
    if os.path.exists(ico_path):
        print(f"✅ Icône trouvée : {ico_path}")
        return ico_path
    else:
        print("⚠️ Fichier d'icône non trouvé, création sans icône")
        return None

def create_spec_file(icon_path=None):
    """Crée un fichier .spec optimisé pour macOS."""
    # Préparer la ligne d'icône
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

# Ajouter explicitement tous les modules utils pour s'assurer qu'ils sont inclus
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
    
    print("✅ Fichier .spec créé avec configuration optimisée")

def build_executable():
    """Construit l'exécutable avec PyInstaller."""
    print("🔨 Construction de l'exécutable macOS...")
    
    try:
        # Nettoyer les anciens builds
        for folder in ['build', 'dist']:
            if os.path.exists(folder):
                import shutil
                shutil.rmtree(folder)
                print(f"🧹 Dossier {folder} nettoyé")
        
        # Construire avec le fichier .spec
        cmd = [
            sys.executable, "-m", "PyInstaller",
            "--clean",
            "scripts/PMTAnalytics_macOS.spec"
        ]
        
        print("🚀 Lancement de PyInstaller...")
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Exécutable créé avec succès !")
            
            # Vérifier que l'app existe
            app_path = Path("dist/PMTAnalytics.app")
            if app_path.exists():
                size_mb = get_folder_size(app_path)
                print(f"📁 Application créée : {app_path}")
                print(f"📏 Taille : {size_mb:.1f} MB")
                
                # Vérifier que les modules utils sont inclus dans l'app
                macos_path = app_path / "Contents" / "MacOS"
                if macos_path.exists():
                    print("✅ Structure de l'app correcte")
                    
                    # Chercher les fichiers utils
                    utils_found = False
                    for root, dirs, files in os.walk(macos_path):
                        if 'utils' in dirs or any('utils' in f for f in files):
                            utils_found = True
                            break
                    
                    if utils_found:
                        print("✅ Modules utils détectés dans l'app")
                    else:
                        print("⚠️ Modules utils non détectés - l'app pourrait ne pas fonctionner")
                
                return True
            else:
                print("❌ L'application .app n'a pas été trouvée")
                return False
        else:
            print("❌ Erreur lors de la construction :")
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

def create_launcher_script():
    """Crée un script de lancement pour tester l'app."""
    launcher_content = '''#!/bin/bash
echo "🚀 Lancement de PMT Analytics..."
open dist/PMTAnalytics.app
'''
    
    with open('scripts/lancer_app.sh', 'w') as f:
        f.write(launcher_content)
    
    os.chmod('scripts/lancer_app.sh', 0o755)
    print("✅ Script de lancement créé : scripts/lancer_app.sh")

def main():
    """Fonction principale."""
    print("🍎 CRÉATION D'EXÉCUTABLE MACOS ")
    print("=" * 60)
    print()
    
    # Vérifier qu'on est dans le bon répertoire
    if not os.path.exists('gui_interface.py'):
        print("❌ Erreur : Lancez ce script depuis la racine du projet")
        print("💡 Utilisez : python scripts/creer_exe_macos_fixe.py")
        return False
    
    print("✅ Répertoire de projet détecté")
    
    # Installer les dépendances
    print("\n📦 Vérification des dépendances...")
    install_dependencies()
    
    # Récupérer l'icône
    print("\n🎨 Vérification de l'icône...")
    icon_path = get_icon_path()
    
    # Créer le fichier .spec
    print("\n⚙️ Création de la configuration...")
    create_spec_file(icon_path)
    
    # Construire l'exécutable
    print("\n🏗️ Construction de l'exécutable...")
    if build_executable():
        create_launcher_script()
        
        print("\n" + "=" * 60)
        print("🎉 SUCCÈS ! Application macOS créée")
        print("=" * 60)
        print()
        print("📁 Emplacement : dist/PMTAnalytics.app")
        print("🚀 Test : ./scripts/lancer_app.sh")
        print()
        print("💡 Instructions de distribution :")
        print("1. Compressez le dossier 'dist' en ZIP")
        print("2. Distribuez le ZIP aux utilisateurs macOS")
        print("3. Ils décompressent et double-cliquent sur PMTAnalytics.app")
        print()
        
        # Proposer de tester
        response = input("Voulez-vous tester l'application maintenant ? (o/n): ")
        if response.lower() in ['o', 'oui', 'y', 'yes']:
            subprocess.run(['open', 'dist/PMTAnalytics.app'])
        
        return True
    else:
        print("\n❌ Échec de la création de l'exécutable")
        print("💡 Vérifiez les erreurs ci-dessus")
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