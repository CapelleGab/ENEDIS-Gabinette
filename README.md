# 📊 PMT Analytics

> **Application d'analyse des statistiques de Planning de Maintenance Technique (PMT) pour Enedis**

## 🎯 Présentation

**PMT Analytics** est une application Python avec interface graphique qui analyse automatiquement les fichiers CSV de planning journalier sur une année d'Enedis et génère des statistiques détaillées sur la présence et les heures travaillées des employés.

### ✨ Fonctionnalités principales

- 📈 **Analyse automatique** des fichiers CSV de planning journalier
- 📊 **Statistiques détaillées** par employé et par équipe
- 💾 **Export Excel** avec tableaux formatés et graphiques
- 🖥️ **Interface graphique** intuitive et moderne
- 🔍 **Résumé visuel** des résultats en temps réel

### 🏢 Équipes supportées

- PV IT ASTREINTE
- PV B ASTREINTE
- PV G ASTREINTE
- PV PE ASTREINTE

## 📚 Documentation

Choisissez le guide adapté à votre profil :

### 👥 Pour les utilisateurs

**[📖 Guide Utilisateur](UTILISATEUR.md)**

- Installation et lancement de l'application
- Guide d'utilisation pas à pas
- Résolution des problèmes courants
- Format des fichiers CSV attendus

### 🛠️ Pour les développeurs

**[⚙️ Guide Développeur](DEVELOPPEUR.md)**

- Configuration de l'environnement de développement
- Architecture du code et modules
- Création d'exécutables
- Contribution au projet

## 🚀 Démarrage rapide

### Utilisateurs

1. Téléchargez `PMTAnalytics.app` (macOS) ou `PMTAnalytics.exe` (Windows)
2. Lancez l'application
3. Sélectionnez votre fichier CSV de planning
4. Consultez les résultats et exportez vers Excel

### Développeurs

```bash
git clone <repository-url>
cd StatistiquePMT
python -m venv .venv
source .venv/bin/activate  # ou .venv\Scripts\activate sur Windows
pip install -r requirements.txt
python gui_interface.py
```

## 📋 Informations techniques

- **Langage** : Python 3.8+
- **Interface** : Tkinter
- **Dépendances** : pandas, openpyxl
- **Plateformes** : Windows, macOS, Linux
- **Version actuelle** : 2.0

## 👨‍💻 Auteur

**CAPELLE Gabin** - Enedis  
_Équipe Maintenance Technique_

---

📝 **Note** : Cette application est destinée à un usage interne Enedis uniquement.
