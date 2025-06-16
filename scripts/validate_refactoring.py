#!/usr/bin/env python3
"""
Script de validation du refactoring PMT Analytics.
Vérifie que toutes les fonctions de l'ancienne API sont toujours disponibles.

Author: CAPELLE Gabin
Version: 2.0.0
"""

import sys
import importlib
from pathlib import Path

# Ajouter le répertoire racine au path
root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))


def test_imports():
    """Test que tous les imports de l'ancienne API fonctionnent."""
    print("🔍 Test des imports de compatibilité...")

    try:
        # Test config
        from config import (
            ANNEE, FICHIER_CSV, FICHIER_EXCEL,
            CODES_EQUIPES_ASTREINTE, CODES_EQUIPES_HORS_ASTREINTE,
            JOURS_WEEKEND, HORAIRE_DEBUT_REFERENCE, HORAIRE_FIN_REFERENCE,
            CSV_ENCODING, CSV_SEPARATOR, COLONNES_FINALES, NOMS_FEUILLES
        )
        print("✅ Config - imports OK")

        # Test data_loader
        from src.utils.data_loader import (
            charger_donnees_csv, preparer_donnees, preparer_donnees_tip,
            preparer_donnees_3x8, supprimer_doublons
        )
        print("✅ Data loader - imports OK")

        # Test calculateurs
        from src.utils.calculateurs import (
            calculer_heures_travaillees, calculer_jours_travailles,
            calculer_statistiques_employes, calculer_moyennes_equipe
        )
        print("✅ Calculateurs - imports OK")

        # Test utils package
        from src.utils import (
            charger_donnees_csv, preparer_donnees, calculer_statistiques_employes,
            calculer_moyennes_equipe, formater_donnees_finales, sauvegarder_excel
        )
        print("✅ Utils package - imports OK")

        return True

    except ImportError as e:
        print(f"❌ Erreur d'import: {e}")
        return False


def test_new_features():
    """Test que les nouvelles fonctionnalités sont disponibles."""
    print("\n🔍 Test des nouvelles fonctionnalités...")

    try:
        # Test nouvelles classes
        from src.utils.data_loader import DataLoader
        from src.utils.calculateurs import StatisticsCalculator, WorkHoursCalculator
        from src.utils.logger import PMTLogger
        from src.utils.exceptions import PMTAnalyticsError, DataValidationError

        # Test instances
        loader = DataLoader()
        calculator = StatisticsCalculator()
        logger = PMTLogger()

        print("✅ Nouvelles classes - OK")

        # Test nouvelle config
        from config import config
        assert hasattr(config, 'files')
        assert hasattr(config, 'teams')
        assert hasattr(config, 'time')
        assert hasattr(config, 'columns')

        print("✅ Nouvelle configuration - OK")

        return True

    except Exception as e:
        print(f"❌ Erreur nouvelles fonctionnalités: {e}")
        return False


def test_functionality():
    """Test basique de fonctionnalité."""
    print("\n🔍 Test de fonctionnalité basique...")

    try:
        import pandas as pd
        from src.utils.data_loader import DataLoader
        from src.utils.calculateurs import WorkHoursCalculator

        # Test DataLoader
        loader = DataLoader()

        # Test WorkHoursCalculator
        calculator = WorkHoursCalculator()
        test_row = pd.Series({
            'Code': '80TH',
            'Valeur': '',
            'Dés. unité': ''
        })

        result = calculator.calculate_hours_worked(test_row)
        assert result.hours_worked == 8.0
        assert result.is_full_day == True

        print("✅ Tests fonctionnels - OK")
        return True

    except Exception as e:
        print(f"❌ Erreur test fonctionnel: {e}")
        return False


def test_config_compatibility():
    """Test de compatibilité de la configuration."""
    print("\n🔍 Test de compatibilité configuration...")

    try:
        # Test ancienne API
        from config import CODES_EQUIPES_ASTREINTE, FICHIER_CSV

        # Test nouvelle API
        from config import config

        # Vérifier équivalence
        assert CODES_EQUIPES_ASTREINTE == config.teams.astreinte_teams
        assert FICHIER_CSV == config.files.csv_filename

        print("✅ Compatibilité configuration - OK")
        return True

    except Exception as e:
        print(f"❌ Erreur compatibilité config: {e}")
        return False


def main():
    """Fonction principale de validation."""
    print("🚀 Validation du refactoring PMT Analytics v2.0")
    print("=" * 50)

    tests = [
        test_imports,
        test_new_features,
        test_functionality,
        test_config_compatibility
    ]

    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"❌ Erreur inattendue dans {test.__name__}: {e}")
            results.append(False)

    print("\n" + "=" * 50)
    print("📊 Résultats de validation:")

    success_count = sum(results)
    total_count = len(results)

    if success_count == total_count:
        print(f"✅ Tous les tests réussis ({success_count}/{total_count})")
        print("🎉 Le refactoring est compatible!")
        return 0
    else:
        print(f"❌ {total_count - success_count} test(s) échoué(s) sur {total_count}")
        print("⚠️  Des problèmes de compatibilité ont été détectés")
        return 1


if __name__ == "__main__":
    sys.exit(main())
