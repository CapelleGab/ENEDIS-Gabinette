# Système de Classification des Employés - PMT Analytics

## Vue d'ensemble

Le système de classification des employés a été implémenté avec succès dans PMT Analytics. Il permet de classifier automatiquement les employés en 4 catégories selon les règles métier spécifiées et d'exporter les résultats dans un fichier Excel avec une feuille par catégorie.

## Les 4 Catégories d'Employés

### 1. ASTREINTES 🚨
**Critères d'identification :**
- Équipe dans : `PV IT ASTREINTE`, `PV B ASTREINTE`, `PV G ASTREINTE`, `PV PE ASTREINTE`

**Règles métier appliquées :**
- ✅ Inclut les jours d'astreinte (colonne 'Astreinte' = 'I')
- ❌ Exclut les weekends (Samedi/Dimanche) sauf si en astreinte
- ❌ Exclut les jours fériés (colonne 'Jour férié' = 'X')
- 📋 Horaires acceptés : 'J' OU n'importe quel code si 'Astreinte' = 'I'

### 2. TIPS 🔧
**Critères d'identification :**
- Équipe dans : `PV B SANS ASTREINTE`, `PV B TERRAIN`, `PV IT SANS ASTREINTE`, `PF IT TERRAIN`, `PV G SANS ASTREINTE`, `PV G CLI/TRAVAUX`, `PV G POLE RIP`, `PV PE SANS ASTREINTE`, `PF PE TERRAIN`
- ET ne travaille PAS en horaires 3x8

**Règles métier appliquées :**
- ❌ Exclut les jours d'astreinte (colonne 'Astreinte' = 'I')
- ❌ Exclut les jours fériés (colonne 'Jour férié' = 'X')
- 📋 Horaires acceptés : Uniquement 'J'

### 3. 3X8 🕐
**Critères d'identification :**
- Équipe TIP (voir liste ci-dessus)
- ET travaille en horaires 3x8 détectés automatiquement

**Horaires 3x8 détectés :**
- Poste du matin : 07:30:00 - 15:30:00
- Poste d'après-midi : 15:30:00 - 23:30:00
- Poste de nuit : 23:30:00 - 07:30:00

**Règles métier appliquées :**
- ✅ Inclut les weekends et jours fériés (service continu)
- ❌ Exclut uniquement les jours d'astreinte (colonne 'Astreinte' = 'I')
- 📋 Horaires acceptés : Tous les horaires 3x8 détectés

### 4. AUTRES 👤
**Critères d'identification :**
- Employés de DR PARIS qui ne sont ni astreigneurs, ni TIP, ni 3x8

**Règles métier appliquées :**
- ❌ Exclut les jours d'astreinte (colonne 'Astreinte' = 'I')
- ❌ Exclut les jours fériés (colonne 'Jour férié' = 'X')

## Répartition par Agence

Le système détecte automatiquement l'agence de chaque employé basé sur son équipe :
- **Italie** : équipes contenant "IT"
- **Grenelle** : équipes contenant "G"
- **Batignolles** : équipes contenant "B"
- **Paris Est** : équipes contenant "PE"
- **Autres** : toutes les autres équipes

## Format d'Export Excel

### Structure du fichier
- **4 feuilles principales** : ASTREINTES, TIPS, 3X8, AUTRES
- **1 feuille de résumé** : RESUME avec statistiques globales

### Contenu de chaque feuille
Chaque feuille contient **une ligne par employé unique** avec les colonnes suivantes :
1. **NNI** : Numéro d'identification de l'employé
2. **Équipe** : Libellé de l'équipe
3. **Nom** : Nom de famille
4. **Prénom** : Prénom
5. **Agence** : Agence déterminée automatiquement

### Formatage visuel
- **Couleurs par catégorie** :
  - ASTREINTES : Rouge (#E74C3C)
  - TIPS : Bleu (#3498DB)
  - 3X8 : Orange (#F39C12)
  - AUTRES : Vert (#27AE60)
  - RESUME : Violet (#8E44AD)

## Interface Utilisateur

### Nouvel onglet "Classifications"
- **Résumé des classifications** : Statistiques générales et par agence
- **Détails par catégorie** : Onglets séparés pour chaque catégorie
- **Vue employés** : Liste des employés avec NNI, Nom, Prénom, Équipe, Agence

### Export automatique
- Le bouton "Exporter Excel" génère automatiquement le fichier avec les 4 feuilles
- Nom de fichier : `export_pmt_categories_YYYYMMDD_HHMMSS.xlsx`

## Architecture Technique

### Nouveaux composants créés
1. **`EmployeeClassifier`** (`src/services/employee_classifier.py`)
   - Classification automatique des employés
   - Application des règles métier
   - Détection des horaires 3x8

2. **Export amélioré** (`src/services/export_service.py`)
   - Génération des 4 feuilles par catégorie
   - Formatage visuel différencié
   - Résumé des statistiques

3. **Interface enrichie** (`src/ui/main_window.py`)
   - Nouvel onglet Classifications
   - Affichage des résultats par catégorie
   - Intégration avec le système d'export

### Intégration
- Le système est entièrement intégré dans l'application existante
- Aucune modification des données sources requise
- Compatible avec tous les fichiers CSV existants

## Utilisation

1. **Charger un fichier CSV** via le bouton "Ouvrir CSV"
2. **Consulter les classifications** dans l'onglet "Classifications"
3. **Exporter les résultats** via le bouton "Exporter Excel"
4. **Analyser les données** dans le fichier Excel généré

## Exemple de Résultats

Avec le fichier de test fourni :
- **ASTREINTES** : 3 employés (Martin, Dupont, Leroy)
- **TIPS** : 2 employés (Bernard, Robert)
- **3X8** : 1 employé (Moreau)
- **AUTRES** : 1 employé (Simon)

**Total** : 7 employés uniques classifiés automatiquement

---

*Système développé selon les spécifications métier pour la DR PARIS* 