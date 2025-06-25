# La Gabinette - Application de Traitement de Données

## Description

Application de bureau Python pour le traitement et l'analyse de fichiers CSV spécifiques avec une interface graphique moderne.

## Architecture

### Structure du Projet

```
GABINETTE/
├── src/
│   ├── __init__.py
│   ├── main.py                 # Point d'entrée principal
│   ├── config/
│   │   ├── __init__.py
│   │   └── settings.py         # Configuration globale
│   ├── models/
│   │   ├── __init__.py
│   │   ├── data_model.py       # Modèles de données
│   │   └── csv_schema.py       # Schéma CSV spécifique
│   ├── services/
│   │   ├── __init__.py
│   │   ├── csv_processor.py    # Traitement des fichiers CSV
│   │   ├── data_validator.py   # Validation des données
│   │   └── export_service.py   # Services d'export
│   ├── ui/
│   │   ├── __init__.py
│   │   ├── main_window.py      # Fenêtre principale
│   │   ├── components/         # Composants UI réutilisables
│   │   └── styles/            # Styles et thèmes
│   ├── scripts/              # Scripts de build et CI/CD
│   └── utils/
│       ├── __init__.py
│       ├── logger.py          # Système de logging
│       └── helpers.py         # Fonctions utilitaires
├── tests/
├── data/
│   ├── input/                 # Fichiers d'entrée
│   ├── output/               # Fichiers de sortie
│   └── samples/              # Exemples de fichiers
├── requirements.txt
└── README.md
```

## Installation

1. Cloner le projet
2. Créer un environnement virtuel : `python -m venv .venv`
3. Activer l'environnement : `source .venv/bin/activate` (Linux/Mac) ou `.venv\Scripts\activate` (Windows)
4. Installer les dépendances : `pip install -r requirements.txt`

## Utilisation

### Lancement de l'application

```bash
# Depuis la racine du projet
python run.py

# Ou directement
python src/main.py
```

### Build d'exécutables

Le projet inclut un système de build automatique pour créer des exécutables natifs.

> **Note :** Les scripts de build sont situés dans `src/scripts/` et le système de build local/CI est aligné sur le modèle StatistiquePMT (multi-plateforme, PyInstaller, GitHub Actions).

#### Validation du système de build

```bash
python src/scripts/validate_build.py
```

#### Compilation locale

```bash
python src/scripts/build_ci.py
```

#### Build automatique via GitHub Actions

```bash
# Créer un tag de version
git tag v1.0.0
git push origin v1.0.0
```

Voir [docs/GITHUB_ACTIONS.md](docs/GITHUB_ACTIONS.md) pour plus de détails.

## Fonctionnalités

- Import de fichiers CSV avec validation du schéma
- Interface graphique moderne avec ttkbootstrap
- Traitement et analyse des données
- Export vers différents formats
- Logging complet des opérations
- Architecture modulaire et extensible

## Format CSV Supporté

Le fichier CSV doit contenir exactement ces colonnes (séparées par "|") :

- UM | UM (Lib) | DUM | DUM (Lib) | SDUM | FSDUM | Dom. | Dom.(Lib) | SDOM | SDOM.(Lib) | Equipe | Equipe (Lib.) | NNI | Nom | Prénom | Jour | Désignation jour | Jour férié | Fin cycle | Astreinte | Astr. Occas. | HT | De | à | De | à | HTM | De | à | De | à | HE | De | à | De | à | Code | Désignation code | Valeur | Dés. Unité | Heure début | Heure fin

> **Note :** Le build CI/CD nécessite le workflow GitHub Actions dans `.github/workflows/build-executables.yml`.

## CI/CD & Builds multiplateformes

### Génération locale d'un exécutable

1. Installez les dépendances :
   ```bash
   pip install -r requirements.txt
   pip install pyinstaller
   ```
2. Générez l'exécutable :
   ```bash
   pyinstaller --noconfirm --onefile --windowed --name "Gabinette" --icon "assets/logo/gabinette-logo.ico" run.py
   ```
   L'exécutable sera dans le dossier `dist/`.

### Pipeline GitHub Actions

- À chaque **push de tag** (`git tag vX.Y.Z && git push origin vX.Y.Z`), la pipeline :
  - Build l'app sur Windows, macOS, Linux (via PyInstaller)
  - Archive les exécutables en artefacts
  - Crée une Release GitHub avec les exécutables

#### Tester la pipeline
1. Créez un tag :
   ```bash
   git tag v1.0.0
   git push origin v1.0.0
   ```
2. Rendez-vous sur l'onglet "Actions" de GitHub pour suivre le build.
3. Les exécutables sont disponibles dans la Release GitHub générée.

### Signature des builds
- La pipeline prévoit un emplacement pour la signature automatique (à compléter selon vos certificats et OS).
- Pour Windows : utilisez `signtool` ou `osslsigncode`.
- Pour macOS : utilisez `codesign`.
- Pour Linux : signature GPG possible.

---

**Astuce :** Pour tester un build local, supprimez le dossier `build/` et `dist/` avant de relancer PyInstaller si besoin.
