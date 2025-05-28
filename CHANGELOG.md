# 🎉 PMT Analytics - Changelog

## Version 1.2.1 - Amélioration du traitement des équipes d'astreinte

### 🔧 Améliorations

- **Équipes d'astreinte** : Inclusion des jours d'astreinte (avec "I") dans les calculs
- **Filtrage spécialisé** : Nouvelle fonction `appliquer_filtres_astreinte()` pour les équipes d'astreinte
- **Comportement différencié** :
  - Équipes d'astreinte : Comptent TOUS les jours (avec et sans "I")
  - Équipes PIT : Continuent d'exclure les jours d'astreinte (inchangé)
  - Équipes 3x8 : Comportement inchangé

### 🛠️ Technique

- Nouveau filtre `appliquer_filtres_astreinte()` dans `src/utils/filtres.py`
- Modification du traitement dans `src/gui/processing.py`
- Messages de log explicites sur l'inclusion des jours d'astreinte

---

## Version 1.2.0 - Support des équipes 3x8

### 🆕 Nouvelles fonctionnalités

- **Équipes 3x8** : Détection automatique des horaires 3x8 (Matin 7h30-15h30, Après-midi 15h30-23h30, Nuit 23h30-7h30)
- **Séparation complète** : Les employés 3x8 sont exclus des statistiques PIT
- **Absences partielles** : Calcul précis basé sur la colonne Valeur (si Valeur < 8, fraction travaillée = (8-Valeur)/8)
- **Export Excel** : 6 feuilles (Astreinte + PIT + 3x8)

### 🛠️ Technique

- Nouveau module `calculateurs_3x8.py`
- Statistiques spécialisées pour les postes 3x8
- Distinction absences complètes/partielles

---

## Version 1.1.0 - Support des équipes PIT

### 🆕 Nouvelles fonctionnalités

- **Équipes PIT** : Analyse des 6 équipes hors astreinte
- **Export Excel** : 4 feuilles (Astreinte + PIT)

### 📈 Équipes supportées

**Astreinte (4) :** PV IT ASTREINTE, PV B ASTREINTE, PV G ASTREINTE, PV PE ASTREINTE

**PIT (6) :** PV B SANS ASTREINTE, PV B TERRAIN, PV IT SANS ASTREINTE, PF IT TERRAIN, PV G SANS ASTREINTE, PV PE SANS ASTREINTE

---

## Version 1.0.0 - Première version stable

- 📊 Analyse automatique des fichiers CSV
- 📈 Statistiques par employé et équipe
- 💾 Export Excel formaté
- 🖥️ Interface graphique

**Développé par** : CAPELLE Gabin - Enedis
