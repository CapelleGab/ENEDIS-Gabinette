# 📊 PMT Analytics - Guide Utilisateur

## 🎯 Présentation

**PMT Analytics** analyse automatiquement les fichiers CSV de planning journalier Enedis et génère des statistiques détaillées sur la présence et les heures travaillées des employés.

## 🚀 Installation

### macOS

1. Téléchargez `PMTAnalytics_v1.0.0_macOS.zip`
2. Décompressez et lancez `PMTAnalytics.app`
3. Si macOS bloque l'app : Clic droit → "Ouvrir" → Confirmer

### Windows

1. Téléchargez `PMTAnalytics_v1.0.0_Windows.zip`
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

### 3. Export Excel

1. **Cliquez** "💾 Exporter vers Excel"
2. **Choisissez** l'emplacement (Documents recommandé)
3. **Nommez** le fichier (ex: `Analyse_PMT_Mai2025.xlsx`)
4. **Enregistrez**

## 📊 Résultats

### Affichage dans l'app

- 📈 Statistiques générales
- 🏆 Top 5 employés par heures
- 🏢 Meilleure équipe
- 📋 Répartition par équipe

### Fichier Excel (2 feuilles)

**Feuille 1 - Statistiques Employés :**

- Nom, Prénom, Équipe
- Jours présents/absents
- Heures travaillées
- Taux de présence
- Moyenne heures/jour

**Feuille 2 - Moyennes par Équipe :**

- Stats moyennes par équipe
- Nombre d'employés
- Comparaisons

## ⚙️ Équipes analysées

- PV IT ASTREINTE
- PV B ASTREINTE
- PV G ASTREINTE
- PV PE ASTREINTE

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

**Version** : v1.0.0  
**Dernière mise à jour** : Mai 2025  
**Usage** : Interne Enedis uniquement
