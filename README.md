# 📊 PMT Analytics v2.0.0

> **Analyse automatique des plannings journaliers Enedis**

PMT Analytics est une application desktop qui analyse les fichiers CSV de planning journalier Enedis et génère des statistiques détaillées pour les équipes d'astreinte, TIP (hors astreinte) et 3x8.

## 🚀 Fonctionnalités

### ✨ Nouveau dans v2.0.0

- **📄 Export du résumé** : Sauvegarde du résumé d'analyse en fichier texte
- **🔧 Filtrage automatique** : Suppression des employés avec données insuffisantes
- **📊 Terminologie TIP** : Changement de "PIT" vers "TIP" dans toute l'application
- **🔨 Build optimisé** : Configuration améliorée avec icônes Windows/macOS
- **🧮 Moyennes pondérées** : Calcul automatique des moyennes par nombre d'employés
- **📈 Résumé optimisé** : Affichage restructuré avec conversion heures/jours et TOP consolidés

### 📈 Analyses supportées

- **Équipes d'astreinte** (4 équipes) : Analyse complète avec jours d'astreinte
- **Équipes TIP** (6 équipes) : Équipes hors astreinte
- **Équipes 3x8** : Détection automatique des horaires en 3 postes

### 💾 Exports disponibles

- **Excel** : 6 feuilles avec données complètes par employé et équipe
- **Texte** : Résumé structuré de l'analyse

## 🛠️ Installation

### Prérequis

- **macOS** : 10.14+ (Mojave ou plus récent)
- **Windows** : 10/11 (64-bit)

### Téléchargement

1. Rendez-vous sur la [page des releases](https://github.com/CapelleGab/ENEDIS-charge-pmt/releases)
2. Téléchargez la version correspondant à votre OS :
   - `PMTAnalytics_v2.0.0_macOS.zip`
   - `PMTAnalytics_v2.0.0_Windows.zip`
3. Décompressez et lancez l'application

### Première utilisation

- **macOS** : Si l'app est bloquée → Clic droit → "Ouvrir" → Confirmer
- **Windows** : Exécuter en tant qu'administrateur si nécessaire

## 📋 Guide d'utilisation

### 1. Préparation des données

Votre fichier CSV doit respecter le format Enedis standard :

- **Format** : `Planning_journalier_YYYY.csv`
- **Encodage** : Latin1 (ISO-8859-1)
- **Séparateur** : Point-virgule (;)

### 2. Analyse

1. **Sélectionner** le fichier CSV
2. **Lancer** l'analyse
3. **Consulter** le résumé affiché
4. **Exporter** les résultats

### 3. Résultats

#### Affichage temps réel

- **📈 Statistiques générales** : Moyennes pondérées par nombre d'employés avec conversion heures/jours
- **🏢 Analyse par équipe** : Répartition détaillée avec moyennes pondérées intégrées
- **🏆 TOP consolidé** : Classements regroupés en fin de résumé (astreinte, TIP, 3x8)
- **⏰ Détails 3x8** : Répartition des postes matin/après-midi/nuit

#### Export Excel (6 feuilles)

- `ASTREINTE_STATS` / `ASTREINTE_EQUIPE_MOYENNES`
- `TIP_STATS` / `TIP_EQUIPE_MOYENNES`
- `3x8_STATS` / `3x8_EQUIPES_MOYENNES`

#### Export Texte

- Résumé complet de l'analyse
- Format lisible et structuré

## ⚙️ Configuration

### Équipes analysées

**Astreinte (4)** :

- PV IT ASTREINTE, PV B ASTREINTE, PV G ASTREINTE, PV PE ASTREINTE

**TIP - Hors astreinte (6)** :

- PV B SANS ASTREINTE, PV B TERRAIN, PV IT SANS ASTREINTE
- PF IT TERRAIN, PV G SANS ASTREINTE, PV PE SANS ASTREINTE

**3x8** :

- Détection automatique des horaires
- Matin : 7h30-15h30 / Après-midi : 15h30-23h30 / Nuit : 23h30-7h30

### Filtrage automatique

- **Astreinte** : < 50 jours présents complets → Supprimé
- **TIP** : < 55 jours présents complets → Supprimé
- **3x8** : Pas de filtrage appliqué

## 🔧 Développement

### Structure du projet

```
PMTAnalytics/
├── src/
│   ├── gui/           # Interface utilisateur
│   ├── utils/         # Utilitaires de traitement
│   └── scripts/       # Scripts de build
├── assets/            # Ressources (icônes)
├── config.py          # Configuration
└── main.py           # Point d'entrée
```

### Build local

```bash
# Installation des dépendances
pip install -r requirements.txt

# Lancement en développement
python main.py

# Build avec PyInstaller
python src/scripts/build_ci.py
```

### Technologies utilisées

- **Python 3.12+**
- **Tkinter** : Interface graphique
- **Pandas** : Traitement des données
- **OpenPyXL** : Export Excel
- **PyInstaller** : Packaging

## 📞 Support

- **Documentation** : [UTILISATION.md](UTILISATION.md)
- **Changelog** : [CHANGELOG.md](CHANGELOG.md)
- **Issues** : [GitHub Issues](https://github.com/CapelleGab/ENEDIS-charge-pmt/issues)

## 📄 Licence

Usage interne Enedis uniquement.

---

**Développé par** : CAPELLE Gabin - Enedis  
**Version** : 2.0.0  
**Dernière mise à jour** : Mai 2025
