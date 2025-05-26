# 📊 PMT Analytics - Guide Utilisateur

## 🎯 Qu'est-ce que PMT Analytics ?

**PMT Analytics** est une application d'analyse des plannings de maintenance technique (PMT) d'Enedis. Elle permet d'analyser automatiquement les fichiers CSV de planning journalier et de générer des statistiques détaillées sur la présence et les heures travaillées des employés.

## ✨ Fonctionnalités

- 📈 **Analyse automatique** des fichiers CSV de planning
- 📊 **Statistiques détaillées** par employé et par équipe
- 💾 **Export Excel** avec tableaux formatés
- 🖥️ **Interface graphique** simple et intuitive
- 🔍 **Résumé visuel** des résultats dans l'application

## 🚀 Installation et Lancement

### Option 1 : Application macOS (Recommandée)

1. Téléchargez le fichier `PMTAnalytics.app`
2. Décompressez l'archive si nécessaire
3. Double-cliquez sur `PMTAnalytics.app` pour lancer l'application

### Option 2 : Version Python

1. Assurez-vous d'avoir Python 3.8+ installé
2. Téléchargez les fichiers du projet
3. Ouvrez un terminal dans le dossier du projet
4. Installez les dépendances : `pip install -r requirements.txt`
5. Lancez l'application : `python gui_interface.py`

## 📋 Guide d'utilisation

### 1. Préparation du fichier CSV

- Votre fichier CSV doit contenir les colonnes de planning journalier Enedis
- Format attendu : `Planning_journalier_YYYY.csv`
- Encodage : Latin1 (ISO-8859-1)
- Séparateur : Point-virgule (;)

### 2. Analyse des données

1. **Lancez PMT Analytics**
2. **Cliquez sur "🔍 Sélectionner le fichier CSV"**
3. **Choisissez votre fichier** de planning journalier
4. **Cliquez sur "🚀 Lancer l'analyse"**
5. **Attendez** que le traitement se termine (quelques secondes)

### 3. Consultation des résultats

L'application affiche automatiquement :

- 📈 **Statistiques générales** (nombre d'employés, moyennes)
- 🏆 **Top 5 des employés** par heures travaillées
- 🏢 **Meilleure équipe** par performance
- 📋 **Répartition par équipe** détaillée

### 4. Export des résultats

1. **Cliquez sur "💾 Exporter vers Excel"**
2. **Choisissez l'emplacement** de sauvegarde (Documents recommandé)
3. **Donnez un nom** au fichier (ex: `Analyse_PMT_Janvier2024.xlsx`)
4. **Cliquez sur "Enregistrer"**

## 📊 Contenu du fichier Excel

Le fichier Excel généré contient **2 feuilles** :

### Feuille 1 : "Statistiques_Employés"

- Nom, Prénom, Équipe
- Jours présents complets et partiels
- Total jours et heures travaillés
- Jours d'absence et heures d'absence
- Taux de présence sur 365 jours
- Moyenne d'heures par jour présent

### Feuille 2 : "Moyennes*par*Équipe"

- Statistiques moyennes par équipe
- Nombre d'employés par équipe
- Comparaison des performances

## ⚙️ Équipes analysées

L'application analyse automatiquement ces équipes :

- **PV IT ASTREINTE**
- **PV B ASTREINTE**
- **PV G ASTREINTE**
- **PV PE ASTREINTE**

## 🔧 Paramètres par défaut

- **Horaires de référence** : 07h30 - 16h15
- **Jours exclus** : Samedi et Dimanche
- **Année d'analyse** : 2024
- **Encodage CSV** : Latin1

## ❓ Résolution des problèmes

### Erreur "Fichier non trouvé"

- Vérifiez que le fichier CSV existe
- Assurez-vous que le chemin ne contient pas de caractères spéciaux

### Erreur "Permissions insuffisantes"

- Essayez de sauvegarder dans votre dossier Documents
- Vérifiez que vous avez les droits d'écriture dans le dossier choisi

### Erreur "Colonnes manquantes"

- Vérifiez que votre CSV contient toutes les colonnes requises
- Assurez-vous que le format correspond au planning journalier Enedis

### L'application ne se lance pas (macOS)

- Clic droit sur l'app → "Ouvrir" → Confirmer l'ouverture
- Vérifiez les paramètres de sécurité dans Préférences Système

## 📞 Support

Pour toute question ou problème :

- Consultez d'abord ce guide
- Vérifiez que votre fichier CSV est au bon format
- Contactez l'équipe de développement si le problème persiste

## 📝 Notes importantes

- ⚠️ **Confidentialité** : Ne partagez jamais vos fichiers CSV en dehors d'Enedis
- 💾 **Sauvegarde** : Conservez toujours une copie de vos fichiers originaux
- 🔄 **Mise à jour** : Utilisez toujours la dernière version de l'application

---

**Version** : 2.0  
**Dernière mise à jour** : Décembre 2024  
**Auteur** : CAPELLE Gabin - Enedis
