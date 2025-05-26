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
├── main.py                    # Script principal d'analyse
├── csv_converter.py           # Utilitaire de conversion CSV vers XLSX
├── Planning_journalier_2024.csv  # Fichier source (à fournir)
├── Statistiques_PMT_2024.xlsx    # Fichier de résultats généré
└── README.md                  # Ce fichier
```

## 🔧 Configuration

### Paramètres modifiables dans `main.py` :

```python
# Année à traiter
ANNEE = '2024'

# Équipes à analyser
CODES_EQUIPES = ['PV IT ASTREINTE', 'PV B ASTREINTE', 'PV G ASTREINTE', 'PV PE ASTREINTE']

# Horaires de référence pour le filtrage
HORAIRE_DEBUT_REFERENCE = '07:30:00'
HORAIRE_FIN_REFERENCE = '16:15:00'
```

## 🏃‍♂️ Utilisation

### Analyse principale

```bash
python main.py
```

### Conversion CSV vers XLSX (optionnel / A FIX)

```bash
python csv_converter.py
```

## 📊 Logique de calcul

### Heures travaillées

- **Code avec valeur** : `8h - valeur = heures travaillées`
- **Code sans valeur** : `0h travaillées` (8h d'absence complète)
- **Pas de code** : `8h travaillées` (journée complète)

### Filtres appliqués

1. ✅ Suppression des week-ends (Samedi, Dimanche)
2. ✅ Suppression des jours fériés
3. ✅ Suppression des jours d'astreinte
4. ✅ Conservation uniquement des horaires 'J'
5. ✅ Filtrage sur les horaires de référence :
   - `07:30:00 à 16:15:00` (continu)
   - `07:30:00 à 12:00:00 + 12:45:00 à 16:15:00` (avec pause)

## 📈 Résultats générés

### Fichier Excel avec 3 feuilles :

#### 1. **Statistiques_Employés**

| Colonne                         | Description                                |
| ------------------------------- | ------------------------------------------ |
| Nom                             | Nom de l'employé                           |
| Prénom                          | Prénom de l'employé                        |
| Équipe                          | Équipe d'appartenance                      |
| Jours_Présents                  | Nombre de jours où l'employé était présent |
| Total_Heures_Travaillées        | Somme totale des heures travaillées        |
| Jours_Complets                  | Nombre de jours avec 8h complètes          |
| Jours_Absents                   | Nombre de jours d'absence complète         |
| Total_Heures_Absence            | Somme totale des heures d'absence          |
| Présence\_%_365j                | Pourcentage de présence sur 365 jours      |
| Moyenne_Heures_Par_Jour_Présent | Moyenne d'heures par jour présent          |

#### 2. **Moyennes*par*Équipe**

Moyennes calculées par équipe pour tous les indicateurs.

#### 3. **Analyse_Codes**

Analyse détaillée des codes utilisés par employé.

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
Moyenne jours présents par employé: 145.1 jours
Moyenne heures totales par employé: 571.1 heures
Moyenne jours complets (8h) par employé: 71.4 jours
Moyenne jours absents par employé: 73.7 jours

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

## 📝 Notes techniques

- **Encodage** : `latin1` pour la lecture des fichiers CSV
- **Séparateur** : `;` (point-virgule)
- **Format de sortie** : Excel (.xlsx)
- **Gestion des doublons** : Suppression automatique par employé/jour

## 🤝 Contribution

Pour contribuer au projet :

1. Forkez le repository
2. Créez une branche pour votre fonctionnalité
3. Committez vos changements
4. Poussez vers la branche
5. Ouvrez une Pull Request

## 📄 Licence

Ce projet est destiné à un usage interne pour l'analyse des données PMT.

---

**Auteur** : Développé pour l'analyse des statistiques PMT Enedis  
**Version** : 1.0  
**Dernière mise à jour** : 2024
