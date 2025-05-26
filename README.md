# 📊 Statistiques PMT - Analyse des Plannings Enedis

> **Application d'analyse des statistiques de Planning de Maintenance Technique (PMT) pour Enedis**

## 🎯 Qu'est-ce que c'est ?

Cette application analyse automatiquement vos fichiers CSV de planning journalier et génère :

- ✅ **Statistiques détaillées** par employé (heures travaillées, absences, etc.)
- ✅ **Moyennes par équipe** pour comparer les performances
- ✅ **Résumé complet** avec top employés et meilleures équipes
- ✅ **Export Excel** pour partager les résultats

---

# 👥 UTILISATION (Pour les employés Enedis)

## 🚀 Installation Ultra Simple

### Étape 1 : Télécharger l'application

1. Récupérez le fichier `StatistiquesPMT.exe` auprès de votre administrateur
2. Placez-le dans un dossier de votre choix (ex: `C:\StatistiquePMT\`)
3. **C'est tout !** Aucune installation requise

### Étape 2 : Utilisation

1. **Double-cliquez** sur `StatistiquesPMT.exe`
2. L'interface graphique s'ouvre automatiquement

## 🖥️ Mode Interface Graphique (Recommandé)

**Utilisation simple :**

1. Cliquez sur "🔍 Sélectionner le fichier CSV"
2. Choisissez votre fichier de planning journalier
3. Cliquez sur "🚀 Lancer l'analyse"
4. Consultez le résumé dans le journal d'exécution
5. Utilisez "💾 Exporter vers Excel" pour sauvegarder

**Avantages :**

- ✅ Interface intuitive avec boutons
- ✅ Résumé affiché en temps réel
- ✅ Export Excel en un clic
- ✅ Aide intégrée

## 📊 Format des Données d'Entrée

Votre fichier CSV doit contenir au minimum ces colonnes :

- `Nom` : Nom de famille
- `Prénom` : Prénom
- `Équipe` : Code équipe
- `Date` : Date au format YYYY-MM-DD
- `Code_Présence` : Code de présence/absence
- `Heure_Début` : Heure de début (optionnel)
- `Heure_Fin` : Heure de fin (optionnel)

## 📈 Résultats Générés

### Dans l'interface

- **Journal d'exécution** : Résumé complet avec statistiques
- **Top 5 employés** par heures travaillées
- **Meilleure équipe** par performance
- **Répartition par équipe** détaillée

### Fichier Excel exporté

- **Feuille "Statistiques_Employés"** : Détail par personne
- **Feuille "Moyennes_Équipes"** : Résumé par équipe

## 🆘 Support Utilisateur

### Problèmes Courants

**❌ "L'application ne se lance pas"**

- Vérifiez que vous avez les droits d'exécution
- Contactez votre administrateur IT

**❌ "Erreur lors du chargement CSV"**

- Vérifiez que votre fichier CSV contient les bonnes colonnes
- Assurez-vous que le fichier n'est pas ouvert dans Excel

**❌ "Résultats incohérents"**

- Vérifiez le format des dates dans votre CSV
- Contactez l'équipe de développement

### Contact Support

- **Support technique** : CAPELLE Gabin
- **Version** : 2.0
- **Dernière mise à jour** : 2025

---

# 🛠️ DÉVELOPPEMENT (Pour les développeurs)

## 📋 Prérequis Développement

- Python 3.8+
- Git (optionnel)
- Éditeur de code (VS Code, PyCharm, etc.)

## 🚀 Installation Environnement de Développement

### Étape 1 : Cloner le projet

```bash
git clone <url-du-projet>
cd StatistiquePMT
```

### Étape 2 : Créer l'environnement virtuel

```bash
# Créer l'environnement virtuel
python -m venv .venv

# Activer l'environnement virtuel
# Sur Windows :
.venv\Scripts\activate
# Sur Mac/Linux :
source .venv/bin/activate

# Installer les dépendances
pip install -r requirements.txt
```

## 🖥️ Modes de Développement

### Mode Interface Graphique

```bash
# Activer l'environnement virtuel
.venv\Scripts\activate

# Lancer l'interface graphique
python gui_interface.py
```

### Mode Console/Script

```bash
# Activer l'environnement virtuel
.venv\Scripts\activate

# Lancer l'analyse en mode script
python main.py
```

### Mode Debug

```bash
# Avec logs détaillés
python gui_interface.py --debug

# Avec profiling
python main.py --profile
```

## 📁 Structure du Projet

```
StatistiquePMT/
├── 📄 gui_interface.py          # Interface graphique principale
├── 📄 main.py                   # Script en ligne de commande
├── 📄 config.py                 # Configuration des paramètres
├── 📁 utils/                    # Fonctions métier
│   ├── 📄 __init__.py           # Package utils
│   ├── 📄 data_loader.py        # Chargement des données
│   ├── 📄 data_processor.py     # Traitement des données
│   ├── 📄 statistics.py         # Calculs statistiques
│   ├── 📄 excel_exporter.py     # Export Excel
│   └── 📄 reporter.py           # Génération de rapports
├── 📄 requirements.txt          # Dépendances Python
├── 📁 .venv/                    # Environnement virtuel
├── 📁 tests/                    # Tests unitaires
├── 📄 .gitignore               # Fichiers ignorés par Git
└── 📄 README.md                 # Ce fichier
```

## 🔧 Dépendances

```
pandas>=1.5.0      # Manipulation des données
openpyxl>=3.0.0    # Export Excel
```

### Dépendances de développement

```bash
# Installer les dépendances de dev
pip install pytest black flake8 mypy

# Ou via requirements-dev.txt
pip install -r requirements-dev.txt
```

## ⚙️ Configuration

Le fichier `config.py` contient tous les paramètres :

```python
# Horaires de travail
HEURE_DEBUT_MATIN = 8
HEURE_FIN_MATIN = 12
HEURE_DEBUT_APRES_MIDI = 13
HEURE_FIN_APRES_MIDI = 17

# Équipes à analyser
EQUIPES_INCLUSES = ['EQ1', 'EQ2', 'EQ3']

# Codes de présence à ignorer
CODES_A_IGNORER = ['CONG', 'MALA', 'FORM']

# Fichiers par défaut
FICHIER_CSV = 'Planning_journalier_2024.csv'
FICHIER_EXCEL = 'Statistiques_PMT_2024.xlsx'
```

## 🏗️ Créer l'Exécutable

### Méthode Simple (Recommandée)

```bash
# Activer l'environnement virtuel windows
.venv\Scripts\activate

# Activer l'environnement virtuel mac
. .venv\bin\activate

# Installer auto-py-to-exe
pip install auto-py-to-exe

# Lancer l'interface de création
python -m auto_py_to_exe
```

**Configuration dans auto-py-to-exe :**

1. **Script Location** : `gui_interface.py`
2. **Onefile** : ✅ Coché
3. **Console Window** : ❌ Décoché
4. **Additional Files** : Ajouter `utils/` et `config.py`
5. **Icon** : Optionnel (fichier .ico)

### Méthode PyInstaller (Avancée)

```bash
# Installation
pip install pyinstaller

# Création de l'exécutable
pyinstaller --onefile --windowed --add-data "utils;utils" --add-data "config.py;." gui_interface.py

# Renommer l'exécutable
mv dist/gui_interface.exe dist/StatistiquesPMT.exe
```

## 🧪 Tests

```bash
# Lancer tous les tests
pytest

# Tests avec couverture
pytest --cov=utils

# Tests spécifiques
pytest tests/test_data_loader.py
```

## 📝 Contribution

### Workflow de développement

1. Créer une branche : `git checkout -b feature/nouvelle-fonctionnalite`
2. Développer et tester
3. Formater le code : `black .`
4. Vérifier la qualité : `flake8`
5. Committer : `git commit -m "feat: nouvelle fonctionnalité"`
6. Pousser : `git push origin feature/nouvelle-fonctionnalite`
7. Créer une Pull Request

### Standards de code

- **Formatage** : Black
- **Linting** : Flake8
- **Type hints** : MyPy
- **Tests** : Pytest
- **Documentation** : Docstrings Google Style

## 🐛 Debug et Logs

### Activer les logs détaillés

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Fichiers de log

- `logs/application.log` : Logs généraux
- `logs/errors.log` : Erreurs uniquement
- `logs/performance.log` : Métriques de performance

## 📄 Licence

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.

---

## 🎉 Démarrage Rapide

### Pour les utilisateurs

1. **Récupérer** `StatistiquesPMT.exe`
2. **Double-cliquer** dessus
3. **Sélectionner** votre fichier CSV
4. **Profiter** des résultats ! 🚀

### Pour les développeurs

1. **Cloner** le projet
2. **Créer** l'environnement : `python -m venv .venv`
3. **Activer** : `.venv\Scripts\activate`
4. **Installer** : `pip install -r requirements.txt`
5. **Développer** ! 🛠️
