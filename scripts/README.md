# 📦 Scripts de Création d'Exécutable

Ce dossier contient les scripts pour créer des exécutables de l'application StatistiquesPMT.

## 🎯 Scripts Disponibles

### 🍎 macOS

- **`creer_exe_macos.py`** ⭐ **RECOMMANDÉ** ✨ **CORRIGÉ**
  - Script corrigé qui résout les erreurs de modules manquants
  - Configuration PyInstaller optimisée avec mode "One File"
  - Inclut automatiquement tous les modules utils
  - Gestion des chemins corrigée
  - Usage : `python scripts/creer_exe_macos.py`

### 🪟 Windows

- **`creer_exe_windows.py`** ⭐ **RECOMMANDÉ**
  - Script corrigé avec configuration PyInstaller optimisée
  - Crée un exécutable .exe autonome
  - Usage : `python scripts/creer_exe_windows.py`

### 🌐 Multiplateforme (Interface graphique)

- **`creer_executable_simple.py`**
  - Lance auto-py-to-exe avec interface web
  - Configuration manuelle requise
  - Usage : `python scripts/creer_executable_simple.py`

### 🐧 Linux/Unix

- **`creer_exe.sh`**
  - Script shell pour systèmes Unix
  - Lance auto-py-to-exe
  - Usage : `./scripts/creer_exe.sh`

## 🚀 Utilisation Recommandée

### Pour macOS :

```bash
# Depuis la racine du projet
python scripts/creer_exe_macos.py
```

### Pour Windows :

```bash
# Depuis la racine du projet
python scripts/creer_exe_windows.py
```

## ⚙️ Configuration Automatique

Les scripts corrigés (`creer_exe_macos.py` et `creer_exe_windows.py`) incluent automatiquement :

✅ **Modules Python requis :**

- pandas, numpy, openpyxl
- tkinter et ses sous-modules
- Tous les modules utils
- config.py

✅ **Fichiers de données :**

- Dossier `utils/` complet
- Fichier `config.py`

✅ **Configuration optimisée :**

- Mode fenêtré (pas de console)
- Compression UPX
- Gestion des dépendances

## 📁 Résultats

Après exécution, vous trouverez :

### macOS :

- `dist/StatistiquesPMT.app` - Application macOS
- `scripts/lancer_app.sh` - Script de test

### Windows :

- `dist/StatistiquesPMT.exe` - Exécutable Windows
- `scripts/lancer_exe.bat` - Script de test
- `dist/README.txt` - Instructions utilisateur

## 🐛 Dépannage

### Erreur "Module not found" dans l'exécutable

➡️ Utilisez les scripts corrigés (`creer_exe_macos.py` ou `creer_exe_windows.py`)

### Erreur d'icône sur macOS

➡️ Les scripts corrigés n'utilisent pas d'icône (évite les erreurs)

### Exécutable trop volumineux

➡️ Normal (50-150 MB) car il inclut Python et toutes les dépendances

### L'application ne se lance pas

➡️ Testez d'abord en mode développement : `python gui_interface.py`

## 📋 Prérequis

- Python 3.8+
- Environnement virtuel activé
- Dépendances installées : `pip install -r requirements.txt`

## 🎉 Distribution

### macOS :

1. Compressez `dist/StatistiquesPMT.app` en ZIP
2. Les utilisateurs décompressent et double-cliquent sur l'app

### Windows :

1. Compressez `dist/StatistiquesPMT.exe` en ZIP
2. Les utilisateurs décompressent et double-cliquent sur l'exe

---

**Auteur :** CAPELLE Gabin  
**Version :** 2.0  
**Dernière mise à jour :** 2025
