# Instructions de Build pour PMT Analytics

Ce document explique comment créer des exécutables pour Windows (.exe) et macOS Apple Silicon (.app) à partir du code source de PMT Analytics.

## Prérequis

- Python 3.9+ installé
- pip (gestionnaire de paquets Python)
- Environnement virtuel (recommandé)

## Installation des dépendances

Avant de créer les builds, assurez-vous que toutes les dépendances sont installées :

```bash
# Créer et activer un environnement virtuel (recommandé)
python -m venv .venv
source .venv/bin/activate  # Sur macOS/Linux
# ou
.venv\Scripts\activate     # Sur Windows

# Installer les dépendances
pip install -r requirements.txt
```

## Utilisation des scripts de build

Tous les scripts de build sont situés dans le dossier `/scripts`. Vous pouvez utiliser les scripts suivants selon votre système d'exploitation :

### Sur macOS / Linux

Utilisez le script shell `build_all.sh` :

```bash
# Rendre le script exécutable (uniquement la première fois)
chmod +x scripts/build_all.sh

# Afficher l'aide
./scripts/build_all.sh help

# Créer une application macOS (.app)
./scripts/build_all.sh macos

# Créer un fichier DMG (nécessite create-dmg)
./scripts/build_all.sh dmg

# Nettoyer les builds précédents
./scripts/build_all.sh clean

# Créer tous les formats disponibles sur la plateforme actuelle
./scripts/build_all.sh all
```

### Sur Windows

Utilisez le script batch `build_all.bat` :

```cmd
# Afficher l'aide
scripts\build_all.bat help

# Créer un exécutable Windows (.exe)
scripts\build_all.bat windows

# Créer un installateur Windows (nécessite NSIS)
scripts\build_all.bat installer

# Nettoyer les builds précédents
scripts\build_all.bat clean

# Créer tous les formats disponibles sur Windows
scripts\build_all.bat all
```

## Résultats

Les exécutables générés se trouvent dans le dossier `dist` :

- **Windows** : `dist/PMT_Analytics/PMT_Analytics.exe`
- **Windows Installer** : `dist/PMT_Analytics_Setup.exe`
- **macOS** : `dist/PMT_Analytics.app`
- **macOS DMG** : `dist/dmg/PMT_Analytics.dmg`

## Notes spécifiques par plateforme

### Windows

- L'icône utilisée est `assets/logo/gabinette-logo.ico`
- L'exécutable est créé avec une interface graphique (sans console)
- L'installateur est créé avec NSIS (nécessite l'installation de NSIS)

### macOS

- L'icône utilisée est `assets/logo/enedis.svg` (convertie automatiquement)
- L'application est compilée en Universal2 pour supporter Intel et Apple Silicon
- Le DMG nécessite l'installation de l'outil `create-dmg` (`brew install create-dmg`)

## Résolution des problèmes courants

### Dépendances manquantes

Si certaines dépendances ne sont pas correctement incluses dans le build :

1. Ajoutez-les à la liste `--hidden-import` dans le script `scripts/build.py`
2. Nettoyez les builds précédents avec `./scripts/build_all.sh clean` ou `scripts\build_all.bat clean`
3. Relancez le processus de build

### Problèmes d'icônes

- **Windows** : Assurez-vous que le fichier .ico est valide
- **macOS** : Si l'icône SVG n'est pas correctement convertie, créez manuellement un fichier .icns

### Cross-compilation

La compilation croisée (build Windows depuis macOS ou vice versa) nécessite des outils supplémentaires :

- Pour créer un .exe depuis macOS : Installez Wine
- Pour créer un .app depuis Windows : Non supporté nativement

## Personnalisation avancée

Pour personnaliser davantage le processus de build, modifiez les fichiers dans le dossier `scripts` :

- `build.py` : Script principal de build avec PyInstaller
- `create_dmg.py` : Script pour créer un DMG macOS
- `create_installer.nsi` : Script NSIS pour créer un installateur Windows
- `build_all.sh` / `build_all.bat` : Scripts d'aide pour faciliter le processus de build 