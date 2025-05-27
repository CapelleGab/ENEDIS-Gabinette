# 🚀 Guide GitHub Actions - PMT Analytics

## 📋 Vue d'ensemble

Ce guide explique comment utiliser GitHub Actions pour compiler automatiquement PMT Analytics sur Windows et macOS.

## 🎯 Fonctionnalités

### ✅ Compilation automatique

- **Windows** : Exécutable `.exe` natif
- **macOS** : Application `.app` native
- **Parallélisation** : Les deux builds se font en même temps

### ✅ Déclencheurs optimisés

- **Tags de release** : `git tag v1.0.0 && git push origin v1.0.0`
- **Manuel** : Bouton "Run workflow" sur GitHub
- **Sélectif** : Choisir Windows et/ou macOS

### ✅ Économie de minutes

- Cache des dépendances Python
- Compilation uniquement sur demande
- Optimisations PyInstaller

## 🚀 Utilisation

### 1. Création d'une release automatique

```bash
# Créer un tag de version
git tag v1.0.0

# Pousser le tag (déclenche la compilation)
git push origin v1.0.0
```

**Résultat :**

- Compilation automatique sur Windows et macOS
- Création d'une release GitHub avec les exécutables
- Téléchargement direct pour les utilisateurs

### 2. Compilation manuelle

1. Allez sur GitHub → Actions
2. Cliquez sur "Build PMT Analytics Executables"
3. Cliquez sur "Run workflow"
4. Choisissez les plateformes à compiler
5. Cliquez sur "Run workflow"

**Résultat :**

- Compilation des plateformes sélectionnées
- Artifacts téléchargeables (pas de release)

## 📊 Estimation des coûts

### Minutes GitHub Actions utilisées

```
Build typique :
├── Windows : 5 min réelles × 2 = 10 min facturées
├── macOS   : 5 min réelles × 10 = 50 min facturées
└── Total   : 60 minutes par release complète

Avec 2000 minutes gratuites :
└── ~33 releases complètes par mois
```

### Optimisations incluses

- **Cache pip** : -30% de temps d'installation
- **Compilation conditionnelle** : Pas de build sur chaque commit
- **Parallélisation** : Windows et macOS en même temps

## 🔧 Configuration avancée

### Variables d'environnement

Modifiez `.github/workflows/build-executables.yml` :

```yaml
env:
  PYTHON_VERSION: "3.12" # Version Python
  APP_NAME: "PMTAnalytics" # Nom de l'app
```

### Personnaliser les déclencheurs

```yaml
on:
  push:
    tags: ["v*"] # Tags v1.0.0, v2.1.0, etc.
    branches: ["main"] # Aussi sur push main (attention aux minutes)
  schedule:
    - cron: "0 2 * * 1" # Tous les lundis à 2h (build hebdo)
```

### Ajouter des tests

```yaml
- name: 🧪 Run tests
  run: |
    python -m pytest tests/
    python scripts/build_ci.py --dry-run
```

## 📁 Structure des artifacts

```
PMTAnalytics-Windows-v1.0.0.zip
├── PMTAnalytics.exe
└── README.txt

PMTAnalytics-macOS-v1.0.0.zip
├── PMTAnalytics.app/
└── README.txt
```

## 🐛 Dépannage

### Build qui échoue

1. **Vérifiez les logs** : GitHub Actions → Build échoué → Logs
2. **Dépendances manquantes** : Vérifiez `requirements.txt`
3. **Erreur PyInstaller** : Testez localement avec `python scripts/build_ci.py`

### Minutes épuisées

1. **Vérifiez l'usage** : Settings → Billing → Usage
2. **Optimisez** : Compilez moins souvent
3. **Alternative** : Utilisez le script local `scripts/creer_executables.py`

### Artifact non trouvé

1. **Vérifiez les conditions** : Le workflow s'est-il exécuté ?
2. **Permissions** : Vérifiez les permissions du repository
3. **Retention** : Les artifacts expirent après 30 jours

## 🎯 Workflow de développement recommandé

### Développement quotidien

```bash
git add .
git commit -m "Nouvelle fonctionnalité"
git push origin main
# Pas de compilation automatique
```

### Tests ponctuels

```bash
# GitHub → Actions → Run workflow
# Sélectionner une seule plateforme pour économiser
```

### Release officielle

```bash
git tag v1.2.0
git push origin v1.2.0
# Compilation automatique complète + release GitHub
```

## 📈 Monitoring

### Vérifier l'usage des minutes

1. GitHub → Settings → Billing
2. Voir "Actions minutes used"
3. Planifier en conséquence

### Optimiser les builds

- Utiliser le cache pip (déjà configuré)
- Compiler seulement sur les tags importants
- Tester localement avant de pousser

## 🔗 Liens utiles

- [Documentation GitHub Actions](https://docs.github.com/en/actions)
- [Tarification GitHub Actions](https://docs.github.com/en/billing/managing-billing-for-github-actions)
- [PyInstaller Documentation](https://pyinstaller.readthedocs.io/)

## 💡 Conseils

1. **Testez localement** avant de créer un tag
2. **Utilisez des tags sémantiques** : v1.0.0, v1.1.0, v2.0.0
3. **Documentez vos releases** dans le changelog
4. **Surveillez l'usage** des minutes GitHub Actions
