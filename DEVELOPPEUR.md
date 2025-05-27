# 🛠️ PMT Analytics - Guide Développeur

## 📋 Vue d'ensemble

**PMT Analytics** est une application Python avec interface Tkinter pour l'analyse des plannings PMT d'Enedis. Architecture modulaire avec support des équipes d'astreinte et PIT, build automatisé via GitHub Actions.

## 🏗️ Architecture

```
StatistiquePMT/
├── main.py                # Point d'entrée principal
├── src/                   # Code source
│   ├── gui/               # Interface graphique modulaire
│   │   ├── interface.py   # Interface utilisateur
│   │   ├── processing.py  # Traitement des données
│   │   ├── export.py      # Gestion export Excel
│   │   └── helpers.py     # Fonctions utilitaires
│   ├── utils/             # Modules métier
│   │   ├── data_loader.py # Chargement CSV
│   │   ├── calculateurs.py # Calculs statistiques
│   │   ├── excel_writer.py # Export Excel
│   │   ├── filtres.py     # Filtrage données
│   │   └── formatters.py  # Formatage résultats
│   └── scripts/           # Build et CI/CD
│       └── build_ci.py    # Build automatisé
├── assets/                # Ressources
│   └── pmtIcon.ico        # Icône application
└── .github/workflows/     # GitHub Actions
    └── build-executables.yml
```

## 🚀 Setup développement

```bash
# Clone et setup
git clone https://github.com/CapelleGab/ENEDIS-charge-pmt.git
cd StatistiquePMT

# Environnement virtuel
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# .venv\Scripts\activate   # Windows

# Dépendances
pip install -r requirements.txt

# Lancement interface graphique
python main.py
```

## 📦 Dépendances

| Package       | Version  | Usage                    |
| ------------- | -------- | ------------------------ |
| `pandas`      | ^2.0.0   | Manipulation données CSV |
| `openpyxl`    | ^3.1.0   | Export Excel             |
| `tkinter`     | Built-in | Interface graphique      |
| `pyinstaller` | ^6.0.0   | Build exécutables        |

## 🔧 Configuration

### `config.py`

```python
ANNEE = '2025'
CODES_EQUIPES_ASTREINTE = ['PV IT ASTREINTE', 'PV B ASTREINTE', ...]
CODES_EQUIPES_HORS_ASTREINTE = ['PV B SANS ASTREINTE', 'PV B TERRAIN', ...]
HORAIRE_DEBUT_REFERENCE = '07:30:00'
CSV_ENCODING = 'latin1'
```

### Personnalisation équipes

```python
# Équipes d'astreinte
CODES_EQUIPES_ASTREINTE = [
    'NOUVELLE_EQUIPE_ASTREINTE',
    'AUTRE_EQUIPE_ASTREINTE'
]

# Équipes PIT (hors astreinte)
CODES_EQUIPES_HORS_ASTREINTE = [
    'NOUVELLE_EQUIPE_PIT',
    'AUTRE_EQUIPE_PIT'
]
```

## 🔄 Flux de données

```
CSV → data_loader → filtres → calculateurs → formatters → excel_writer
                 ↓
            [Astreinte + PIT en parallèle]
```

1. **Chargement** : `data_loader.charger_donnees_csv()`
2. **Filtrage** : `filtres.appliquer_filtres_base()`
3. **Séparation** : `preparer_donnees()` + `preparer_donnees_pit()`
4. **Calculs** : `calculateurs.calculer_statistiques_employes()` (x2)
5. **Export** : `excel_writer.sauvegarder_excel()` (4 feuilles)

## 🏗️ Build et déploiement

### Build local

```bash
# Build pour la plateforme actuelle
python src/scripts/build_ci.py

# Résultat dans dist/
# macOS: PMTAnalytics.app
# Windows: PMTAnalytics.exe
```

### GitHub Actions

- **Déclenchement** : Push de tags `v*`
- **Plateformes** : Windows + macOS en parallèle
- **Artifacts** : Archives ZIP avec README
- **Release** : Automatique avec CHANGELOG.md

### Workflow release

```bash
git tag v1.0.1
git push origin v1.0.1
# → Build automatique + release GitHub
```

## 🧪 Tests et qualité

### Tests manuels

```bash
python test_export.py
```

### Conventions

- **PEP 8** pour le style
- **Docstrings** pour fonctions publiques
- **Type hints** recommandés
- **Gestion d'erreurs** explicite

### Exemple fonction

```python
def calculer_statistiques_employes(df_filtre: pd.DataFrame) -> pd.DataFrame:
    """
    Calcule les statistiques détaillées pour chaque employé.

    Args:
        df_filtre: DataFrame filtré des données

    Returns:
        DataFrame avec statistiques par employé

    Raises:
        ValueError: Si DataFrame vide
    """
```

## 🐛 Debug et logs

### Activation logs

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Erreurs courantes

| Erreur               | Cause               | Solution               |
| -------------------- | ------------------- | ---------------------- |
| `FileNotFoundError`  | CSV manquant        | Vérifier chemin        |
| `UnicodeDecodeError` | Mauvais encodage    | Forcer `latin1`        |
| `KeyError`           | Colonne manquante   | Valider format CSV     |
| `PermissionError`    | Droits insuffisants | Changer dossier export |

## 📈 Performance

### Temps typiques

- **1K lignes** : ~2-3s
- **10K lignes** : ~5-10s
- **Export Excel** : ~1-2s

### Optimisations possibles

- `pandas.read_csv()` avec `chunksize`
- Cache calculs intermédiaires
- Parallélisation `multiprocessing`

## 🔄 Workflow Git

### Branches

- `main` : Version stable
- `develop` : Développement
- `feature/nom` : Nouvelles fonctionnalités
- `hotfix/nom` : Corrections urgentes

### Commits

```bash
git commit -m "🐛 Fix: Correction export Excel"
git commit -m "✨ Feat: Support équipes personnalisées"
git commit -m "📚 Docs: Mise à jour README"
```

## 🤝 Contribution

1. **Fork** le repository
2. **Créer** branche feature
3. **Développer** avec tests
4. **Commit** avec messages clairs
5. **Pull Request** vers develop

### Checklist PR

- [ ] Code testé manuellement
- [ ] Docstrings ajoutées
- [ ] Pas de hardcoding
- [ ] Gestion d'erreurs
- [ ] Performance acceptable

## 📚 Ressources

- [Pandas Docs](https://pandas.pydata.org/docs/)
- [Tkinter Tutorial](https://docs.python.org/3/library/tkinter.html)
- [PyInstaller Manual](https://pyinstaller.readthedocs.io/)
- [GitHub Actions Docs](https://docs.github.com/en/actions)

## 📞 Support

- 🐛 **Issues** : [GitHub Issues](https://github.com/CapelleGab/ENEDIS-charge-pmt/issues)
- 📧 **Contact** : CAPELLE Gabin - Enedis
- 📖 **Wiki** : [GitHub Wiki](https://github.com/CapelleGab/ENEDIS-charge-pmt/wiki)

---

**Version** : v1.1.0  
**Dernière mise à jour** : Mai 2025  
**Auteur** : CAPELLE Gabin - Enedis  
**License** : Usage interne Enedis uniquement
