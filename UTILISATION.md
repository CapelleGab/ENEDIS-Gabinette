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

- 📈 Statistiques générales avec moyennes pondérées par nombre d'employés
- 🏢 Analyse des équipes avec conversion automatique heures/jours
- 📋 Répartition détaillée par équipe avec moyennes pondérées intégrées
- 🏆 TOP consolidé en fin : classements astreinte, TIP et 3x8
- ⏰ Détails spécifiques 3x8 (postes, absences) avec moyennes pondérées

#### 💾 Export Excel (données complètes)

1. **Cliquez** "💾 Exporter vers Excel"
2. **Choisissez** l'emplacement (Documents recommandé)
3. **Nommez** le fichier (ex: `Analyse_PMT_Mai2025.xlsx`)
4. **Enregistrez**

## 📊 Résultats

### Affichage dans l'app

**Équipes d'astreinte :**

- 📈 Statistiques générales avec moyennes pondérées (heures et jours)
- 🏢 Meilleure équipe avec conversion heures/jours
- 📋 Répartition par équipe avec moyennes pondérées intégrées

**Équipes TIP (hors astreinte) :**

- 📈 Statistiques générales TIP avec moyennes pondérées
- 📋 Répartition par équipe TIP avec moyennes pondérées intégrées

**Équipes 3x8 :**

- 📅 Statistiques de présence détaillées
- ⏰ Répartition des postes (matin/après-midi/nuit)
- 📋 Moyennes par équipe avec moyennes pondérées en jours travaillés

**🏆 TOP consolidé (en fin de résumé) :**

- Top 5 employés astreinte (par heures travaillées)
- Top 3 employés TIP (par heures travaillées)
- Top employés 3x8 (par jours travaillés avec détails postes)

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
