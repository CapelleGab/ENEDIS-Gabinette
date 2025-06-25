#!/usr/bin/env python3
"""
Script de lancement de PMT Analytics
"""

import sys
import os
from pathlib import Path

def main():
    """Lance l'application PMT Analytics"""
    # Détecter si nous sommes dans un environnement PyInstaller
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        # Nous sommes dans un exécutable PyInstaller
        # Le code est déjà dans le bon répertoire
        print("Lancement depuis l'exécutable PyInstaller...")
        try:
            from src.main import main as app_main
            app_main()
        except Exception as e:
            print(f"Erreur lors du lancement de l'application: {e}")
            import traceback
            traceback.print_exc()
    else:
        # Nous sommes en mode développement
        print("Lancement en mode développement...")
        # Obtenir le répertoire racine du projet
        project_root = Path(__file__).parent
        src_path = project_root / "src"

        # Ajouter le répertoire src au PYTHONPATH
        sys.path.insert(0, str(src_path))

        # Changer le répertoire de travail vers src pour les imports relatifs
        original_cwd = os.getcwd()
        
        try:
            os.chdir(src_path)
            from src.main import main as app_main
            app_main()
        except Exception as e:
            print(f"Erreur lors du lancement de l'application: {e}")
            print("Vérifiez que toutes les dépendances sont installées:")
            print("  source .venv/bin/activate")
            print("  pip install -r requirements.txt")
            import traceback
            traceback.print_exc()
        finally:
            # Restaurer le répertoire de travail original
            os.chdir(original_cwd)

if __name__ == "__main__":
    main()

