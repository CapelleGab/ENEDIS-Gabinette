"""
Script de setup pour PMT Analytics
"""

import subprocess
import sys
from pathlib import Path


def install_requirements():
    """Installe les dépendances requises"""
    print("Installation des dépendances...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dépendances installées avec succès")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Erreur lors de l'installation des dépendances: {e}")
        return False


def run_tests():
    """Lance les tests unitaires"""
    print("\nLancement des tests...")
    try:
        subprocess.check_call([sys.executable, "-m", "unittest", "discover", "-s", "tests", "-v"])
        print("✅ Tous les tests sont passés")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Certains tests ont échoué: {e}")
        return False


def create_directories():
    """Crée les répertoires nécessaires"""
    print("Création des répertoires...")
    directories = [
        "data/input",
        "data/output",
        "data/samples",
        "logs"
    ]

    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"✅ Répertoire créé: {directory}")


def main():
    """Fonction principale de setup"""
    print("=" * 50)
    print("SETUP LA GABINETTE")
    print("=" * 50)

    # Créer les répertoires
    create_directories()

    # Installer les dépendances
    if not install_requirements():
        print("❌ Setup échoué lors de l'installation des dépendances")
        sys.exit(1)

    # Lancer les tests
    if not run_tests():
        print("⚠️  Setup terminé mais certains tests ont échoué")
        print("L'application peut fonctionner mais il pourrait y avoir des problèmes")

    print("\n" + "=" * 50)
    print("✅ SETUP TERMINÉ AVEC SUCCÈS")
    print("=" * 50)
    print("\nPour lancer l'application:")
    print("  python run.py")
    print("\nOu directement:")
    print("  python src/main.py")
    print("\nFichier d'exemple disponible:")
    print("  data/samples/exemple_pmt.csv")


if __name__ == "__main__":
    main()
