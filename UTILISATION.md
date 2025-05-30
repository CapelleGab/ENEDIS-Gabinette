# 📊 PMT Analytics - Guide Utilisateur

## 🎯 Présentation

**PMT Analytics** analyse automatiquement les fichiers CSV de planning journalier Enedis et génère des statistiques détaillées sur la présence et les heures travaillées des employés pour les équipes d'astreinte, TIP (hors astreinte) et 3x8.

## 🚀 Installation

### macOS

1. Téléchargez `PMTAnalytics_v2.0.0_macOS.zip`
2. Décompressez et lancez `PMTAnalytics.app`
3. Si macOS bloque l'app : Clic droit → "Ouvrir" → Confirmer

### Windows

1. Téléchargez `PMTAnalytics_v2.0.0_Windows.zip`
2. Décompressez et lancez `PMTAnalytics.exe`

## 📋 Utilisation

### 1. Préparation du fichier CSV

- Format : `Planning_journalier_YYYY.csv`
- Encodage : Latin1 (ISO-8859-1)
- Séparateur : Point-virgule (;)
- Doit contenir les colonnes standard Enedis

### 2. Analyse

1. **Lancez** PMT Analytics
2. **Cliquez** "🔍 Sélectionner le fichier CSV"
3. **Choisissez** votre fichier de planning
4. **Cliquez** "🚀 Lancer l'analyse"
5. **Consultez** les résultats affichés

### 3. Export des résultats

#### 📄 Export du résumé (NOUVEAU v2.0.0)

1. **Cliquez** "📄 Exporter le résumé"
2. **Choisissez** l'emplacement (Documents recommandé)
3. **Nommez** le fichier (ex: `Resume_PMT_Mai2025.txt`)
4. **Enregistrez**

Le fichier texte contiendra :

- 📈 Statistiques générales
- 🏆 Top employés par catégorie
- 📋 Répartition par équipe
- 📊 Détails spécifiques 3x8 (postes, absences)

#### 💾 Export Excel (données complètes)

1. **Cliquez** "💾 Exporter vers Excel"
2. **Choisissez** l'emplacement (Documents recommandé)
3. **Nommez** le fichier (ex: `Analyse_PMT_Mai2025.xlsx`)
4. **Enregistrez**

## 📊 Résultats

### Affichage dans l'app

**Équipes d'astreinte :**

- 📈 Statistiques générales
- 🏆 Top 5 employés par heures
- 🏢 Meilleure équipe
- 📋 Répartition par équipe

**Équipes TIP (hors astreinte) :**

- 📈 Statistiques générales TIP
- 🏆 Top 3 employés TIP par heures
- 📋 Répartition par équipe TIP

**Équipes 3x8 :**

- 📅 Statistiques de présence
- ⏰ Répartition des postes (matin/après-midi/nuit)
- 🏆 Top employés par jours travaillés
- 📋 Moyennes par équipe

### Fichier Excel (6 feuilles)

**ASTREINTE_STATS - Statistiques Employés (astreinte) :**

- Nom, Prénom, Équipe
- Jours présents/absents
- Heures travaillées
- Taux de présence
- Moyenne heures/jour

**ASTREINTE_EQUIPE_MOYENNES - Moyennes par Équipe (astreinte) :**

- Stats moyennes par équipe
- Nombre d'employés
- Comparaisons

**TIP_STATS - Statistiques Employés (hors astreinte) :**

- Mêmes colonnes que pour l'astreinte
- Équipes TIP uniquement

**TIP_EQUIPE_MOYENNES - Moyennes par Équipe (hors astreinte) :**

- Stats moyennes par équipe TIP
- Nombre d'employés TIP
- Comparaisons TIP

**3x8_STATS - Statistiques Employés (3x8) :**

- Jours travaillés, absences partielles
- Nombre de postes par type (matin/après-midi/nuit)
- Total jours d'absence

**3x8_EQUIPES_MOYENNES - Moyennes par Équipe (3x8) :**

- Moyennes par équipe 3x8
- Totaux des postes par équipe

## ⚙️ Équipes analysées

**Équipes d'astreinte (4) :**

- PV IT ASTREINTE, PV B ASTREINTE, PV G ASTREINTE, PV PE ASTREINTE

**Équipes TIP - Hors astreinte (6) :**

- PV B SANS ASTREINTE, PV B TERRAIN, PV IT SANS ASTREINTE
- PF IT TERRAIN, PV G SANS ASTREINTE, PV PE SANS ASTREINTE

**Équipes 3x8 :**

- Détection automatique des horaires 3x8
- Matin : 7h30-15h30
- Après-midi : 15h30-23h30
- Nuit : 23h30-7h30

## 🔧 Filtrage automatique (v2.0.0)

L'application supprime automatiquement les employés avec des données insuffisantes :

- **Astreinte** : < 50 jours présents complets
- **TIP** : < 55 jours présents complets
- **3x8** : Pas de filtrage appliqué

## 🔧 Paramètres

- **Horaires** : 07h30 - 16h15
- **Jours exclus** : Weekend
- **Année** : 2025
- **Encodage** : Latin1

## ❓ Problèmes courants

| Problème                  | Solution                          |
| ------------------------- | --------------------------------- |
| Fichier non trouvé        | Vérifiez le chemin et l'existence |
| Permissions insuffisantes | Sauvegardez dans Documents        |
| Colonnes manquantes       | Vérifiez le format CSV Enedis     |
| App bloquée (macOS)       | Clic droit → Ouvrir               |

## 📞 Support

- 📖 **Documentation** : Ce guide
- 🐛 **Bugs** : [GitHub Issues](https://github.com/CapelleGab/ENEDIS-charge-pmt/issues)
- 📧 **Contact** : CAPELLE Gabin - Enedis

---

**Version** : v2.0.0  
**Dernière mise à jour** : Janvier 2025  
**Usage** : Interne Enedis uniquement
