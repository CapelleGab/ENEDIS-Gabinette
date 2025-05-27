# 📁 Scripts PMT Analytics

Ce dossier contient les scripts de build et d'automatisation pour PMT Analytics.

## 🚀 Scripts disponibles

### `build_ci.py` - Build automatisé

Script optimisé pour GitHub Actions qui :

- Détecte automatiquement la plateforme (Windows/macOS)
- Installe les dépendances nécessaires
- Compile l'exécutable avec PyInstaller
- Vérifie la validité du build

**Usage :**

```bash
python scripts/build_ci.py
```

## 🔧 Méthodes de compilation

### 1. GitHub Actions (Recommandé)

- **Automatique** : Compilation sur push de tags
- **Multi-plateforme** : Windows et macOS en parallèle
- **Distribution** : Releases GitHub automatiques

Voir le guide complet : [`docs/GITHUB_ACTIONS.md`](../docs/GITHUB_ACTIONS.md)

### 2. Build local

Pour tester localement :

```bash
# Activer l'environnement virtuel
source .venv/bin/activate

# Compiler pour la plateforme actuelle
python scripts/build_ci.py
```

## 📋 Workflow recommandé

### Développement

```bash
git add .
git commit -m "Nouvelle fonctionnalité"
git push origin main
```

### Release

```bash
git tag v1.0.0
git push origin v1.0.0
# → Compilation automatique via GitHub Actions
```

## 🔗 Liens utiles

- [Guide GitHub Actions](../docs/GITHUB_ACTIONS.md)
- [Documentation PyInstaller](https://pyinstaller.readthedocs.io/)
- [Workflow GitHub Actions](../.github/workflows/build-executables.yml)

---

**Auteur :** CAPELLE Gabin  
**Version :** 3.0 - GitHub Actions  
**Dernière mise à jour :** 2025
