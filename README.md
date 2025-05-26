# 📊 Analyse des Statistiques PMT (Planning de Maintenance Technique)

Ce projet analyse les données de planning journalier pour calculer les statistiques de présence et d'heures travaillées par employé et par équipe.

## 🎯 Objectif

Traiter les fichiers CSV de planning journalier pour générer des statistiques détaillées sur :

- Les heures travaillées par employé
- Les jours de présence et d'absence
- Les moyennes par équipe
- L'analyse des codes d'absence

## 📋 Prérequis

- Python 3.7+
- Pandas
- NumPy
- OpenPyXL

## 🚀 Installation

1. Clonez le projet ou téléchargez les fichiers
2. Créez un environnement virtuel :

```bash
python -m venv .venv
source .venv/bin/activate  # Sur macOS/Linux
# ou
.venv\Scripts\activate     # Sur Windows
```

3. Installez les dépendances :

```bash
pip install pandas numpy openpyxl
```

## 📁 Structure du projet

```
StatistiquePMT/
├── main_new.py                # Script principal d'analyse (nouvelle architecture)
├── main.py                    # Script principal d'analyse (ancienne version)
├── config.py                  # Configuration centralisée
├── utils/                     # Modules utilitaires
│   ├── __init__.py           # Package utils
│   ├── data_loader.py        # Chargement des données
│   ├── horaires.py           # Gestion des horaires
│   ├── filtres.py            # Filtrage des données
│   ├── calculateurs.py       # Calculs statistiques
│   ├── formatters.py         # Formatage des données
│   ├── excel_writer.py       # Sauvegarde Excel
│   └── reporter.py           # Génération de rapports
├── requirements.txt           # Dépendances Python
├── Planning_journalier_2024.csv  # Fichier source (à fournir)
├── Statistiques_PMT_2024.xlsx    # Fichier de résultats généré
├── LICENSE                    # Licence propriétaire Enedis
└── README.md                  # Ce fichier
```

## 🏃‍♂️ Utilisation

### Nouvelle architecture (recommandée)

```bash
.venv/bin/python main.py
```

### Ancienne version (monolithique)

```bash
.venv/bin/python old/main.py
```

### Configuration

Modifiez le fichier `config.py` pour ajuster les paramètres :

```python
ANNEE = '2024'
CODES_EQUIPES = ['PV IT ASTREINTE', 'PV B ASTREINTE', ...]
HORAIRE_DEBUT_REFERENCE = '07:30:00'
HORAIRE_FIN_REFERENCE = '16:15:00'
```

## 📊 Logique de calcul

### Heures travaillées

- **Code avec valeur** : `8h - valeur = heures travaillées` (jour partiel)
- **Code sans valeur** : `0h travaillées` (8h d'absence complète)
- **Pas de code** : `8h travaillées` (journée complète)

### Types de jours

- **Jours complets** : 8h exactement travaillées
- **Jours partiels** : Code d'absence avec valeur > 0 (ex: Code="FP", Valeur=7.0 → 1h travaillée)
- **Jours absents** : 0h travaillées (absence complète)

### Gestion du format français

Le script gère automatiquement la conversion des décimales au format français :

- `'0,500'` → `0.5` (30 minutes)
- `'4,500'` → `4.5` (4h30)
- `'8,000'` → `8.0` (8h complètes)

### Filtres appliqués

1. ✅ Suppression des week-ends (Samedi, Dimanche)
2. ✅ Suppression des jours fériés
3. ✅ Suppression des jours d'astreinte
4. ✅ Conservation uniquement des horaires 'J'
5. ✅ Filtrage sur les horaires de référence :
   - `07:30:00 à 16:15:00` (continu)
   - `07:30:00 à 12:00:00 + 12:45:00 à 16:15:00` (avec pause)

## 📈 Résultats générés

### Fichier Excel avec 2 feuilles :

#### 1. **Statistiques_Employés**

| Colonne                         | Description                                       |
| ------------------------------- | ------------------------------------------------- |
| Nom                             | Nom de l'employé                                  |
| Prénom                          | Prénom de l'employé                               |
| Équipe                          | Équipe d'appartenance                             |
| Jours_Présents_Complets         | Nombre de jours avec 8h complètes                 |
| Jours_Partiels                  | Nombre de jours avec temps partiel                |
| Total_Jours_Travaillés          | Somme des jours complets + partiels (en fraction) |
| Total_Heures_Travaillées        | Somme totale des heures travaillées               |
| Jours_Complets                  | Nombre de jours avec 8h exactement                |
| Jours_Absents                   | Nombre de jours d'absence complète                |
| Total_Heures_Absence            | Somme totale des heures d'absence                 |
| Présence\_%_365j                | Pourcentage de présence sur 365 jours             |
| Moyenne_Heures_Par_Jour_Présent | Moyenne d'heures par jour présent                 |

#### 2. **Moyennes*par*Équipe**

Moyennes calculées par équipe pour tous les indicateurs.

## 📋 Exemple de sortie console

```
Traitement des statistiques PMT pour l'année 2024
Chargement des données depuis le fichier CSV...
Données chargées : 170558 lignes, 44 colonnes

Application des filtres de base...
Après suppression week-ends: 32822 lignes
Après suppression jours fériés: 31562 lignes
Après suppression astreintes: 23744 lignes
Après filtrage horaires 'J': 19227 lignes
Après filtrage horaires 07:30:00-16:15:00: 18721 lignes

Nombre d'employés analysés: 129
Moyenne jours présents par employé: 71.4 jours
Moyenne jours partiels par employé: 73.7 jours
Moyenne total jours travaillés par employé: 82.8 jours
Moyenne heures totales par employé: 662.3 heures
Moyenne jours complets (8h) par employé: 71.4 jours
Moyenne jours absents par employé: 54.0 jours

Fichier généré: Statistiques_PMT_2024.xlsx
```

## 🔍 Codes d'absence traités

Le script traite tous les codes présents dans les données, notamment :

- **Codes vides** (' ') : Journées complètes
- **Codes numériques** (21, 10, 41, 52, etc.) : Absences avec calcul
- **Codes alphabétiques** (J4, FP, D, etc.) : Divers types d'absence

## 🛠️ Fonctionnalités avancées

### Classe CSVToXLSXConverter

Utilitaire pour convertir les fichiers CSV en format Excel :

```python
from csv_converter import CSVToXLSXConverter

converter = CSVToXLSXConverter(encoding='latin1', separator=';')
result = converter.convert_file('fichier.csv', 'fichier.xlsx')
```

### Analyse des horaires

Le script analyse automatiquement les horaires disponibles dans les données et affiche un diagnostic des plages horaires trouvées.

## 🐛 Dépannage

### Erreurs courantes

1. **Fichier CSV introuvable**

   ```
   ERREUR : Le fichier CSV 'Planning_journalier_2024.csv' n'existe pas.
   ```

   → Vérifiez que le fichier CSV est présent dans le répertoire

2. **Problème d'encodage**
   → Le script utilise l'encodage `latin1` par défaut

3. **Colonnes manquantes**
   → Vérifiez que le fichier CSV contient toutes les colonnes requises

4. **Jours partiels à 0**
   → Problème résolu : Le script gère maintenant automatiquement la conversion du format français des décimales (virgule → point)

### Corrections récentes

- ✅ **v1.1** : Correction détection jours partiels - format français des décimales
- ✅ Gestion automatique de la conversion `'0,500'` → `0.5`
- ✅ Suppression du code de debug devenu inutile
- ✅ Optimisation de la logique de calcul des statistiques

## 📝 Notes techniques

- **Encodage** : `latin1` pour la lecture des fichiers CSV
- **Séparateur** : `;` (point-virgule)
- **Format de sortie** : Excel (.xlsx)
- **Gestion des doublons** : Suppression automatique par employé/jour
- **Format décimal** : Conversion automatique du format français (virgule) vers format anglais (point)
- **Détection jours partiels** : Code d'absence + Valeur > 0 = Jour partiel

## 🤝 Contribution

Pour contribuer au projet :

1. Forkez le repository
2. Créez une branche pour votre fonctionnalité
3. Committez vos changements
4. Poussez vers la branche
5. Ouvrez une Pull Request

## 📄 Licence

Ce projet est sous licence propriétaire Enedis. Voir le fichier [LICENSE](LICENSE) pour plus de détails.

**Usage autorisé** : Exclusivement pour les besoins internes d'Enedis  
**Confidentialité** : Ce projet contient des données et processus métier confidentiels  
**Restrictions** : Toute distribution ou utilisation externe est interdite

---

**Auteur** : Développé pour l'analyse des statistiques PMT Enedis  
**Version** : 1.1  
**Dernière mise à jour** : MAI 2025

### Historique des versions

- **v1.1** (Décembre 2024) : Correction détection jours partiels + gestion format français
- **v1.0** (2024) : Version initiale
