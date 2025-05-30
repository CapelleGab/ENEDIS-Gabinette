# 🎉 PMT Analytics - Changelog

## Version 2.0.0 - Export du résumé et améliorations majeures

### 🆕 Nouvelles fonctionnalités

- **📄 Export du résumé** : Nouveau bouton "Exporter le résumé" pour sauvegarder l'analyse en fichier texte (.txt)
- **🔧 Filtrage des données** : Suppression automatique des employés avec données insuffisantes
  - Astreinte : < 50 jours présents complets
  - TIP : < 55 jours présents complets
  - 3x8 : Pas de filtrage pour le moment
- **📊 Terminologie mise à jour** : Changement de "PIT" vers "TIP" dans toute l'application

### 🛠️ Améliorations techniques

- **🔨 Build optimisé** : Configuration PyInstaller améliorée avec icônes pour Windows et macOS
- **📦 Modules intégrés** : Ajout des modules `calculateurs_3x8` et `remover` dans la configuration de build
- **🐛 Corrections** :
  - Suppression des messages de debug en console
  - Correction du paramètre `initialfile` dans les dialogues d'export
  - Suppression de la colonne `Jours_Absents_Complets` des statistiques 3x8

### 📋 Interface utilisateur

- **🎨 Nouveau bouton** : "📄 Exporter le résumé" à côté du bouton Excel
- **💾 Export flexible** : Choix du format (Excel pour données détaillées, Texte pour résumé)
- **📊 Affichage amélioré** : Résumé plus structuré et lisible

### 📈 Améliorations du résumé

- **🧮 Moyennes pondérées** : Calcul automatique des moyennes pondérées par nombre d'employés
  - Astreinte : Moyenne pondérée des 4 agences avec conversion heures/jours
  - TIP : Moyenne pondérée des équipes TIP avec conversion heures/jours
  - 3x8 : Moyenne pondérée des équipes 3x8 en jours travaillés
- **📊 Affichage optimisé** :
  - Conversion automatique heures → jours (÷8) affichée entre parenthèses
  - Réorganisation : statistiques générales → équipes → TOP regroupés en fin
  - Suppression des sections techniques (fichier source, export)
- **🏆 TOP consolidé** : Tous les classements regroupés à la fin du résumé
  - TOP 5 employés astreinte (par heures)
  - TOP 3 employés TIP (par heures)
  - TOP employés 3x8 (par jours travaillés)

### 🔧 Configuration

- **⚙️ Nouveau module** : `src/utils/remover.py` pour le filtrage des données
- **📝 Renommage** : Toutes les références "PIT" → "TIP" (feuilles Excel, variables, messages)
- **🏗️ Build CI** : Script de build automatisé amélioré pour GitHub Actions

---

**Développé par** : CAPELLE Gabin - Enedis
