# PMT Analytics - Livraison

## 📦 Application livrée

**PMT Analytics** est une application de bureau Python avec une architecture maintenable et scalable pour traiter des fichiers CSV spécifiques selon vos contraintes.

## ✅ Fonctionnalités implémentées

### 🏗️ Architecture

- **Structure modulaire** : Séparation claire des responsabilités
- **Configuration centralisée** : Paramètres dans `src/config/settings.py`
- **Logging complet** : Traçabilité de toutes les opérations
- **Gestion d'erreurs robuste** : Validation et récupération d'erreurs
- **Tests unitaires** : Framework de tests pour la maintenance

### 📊 Traitement des données

- **Import CSV spécialisé** :
  - Séparateur : Point-virgule (`;`)
  - Encodage : Latin1 (ISO-8859-1)
  - 42 colonnes exactes selon votre spécification
- **Validation automatique** : Vérification de la structure et des données
- **Statistiques** : Calcul automatique des métriques importantes
- **Filtrage avancé** : Par équipe, nom, date, etc.

### 🖥️ Interface utilisateur

- **Interface moderne** : Utilisation de ttkbootstrap pour un design professionnel
- **Navigation par onglets** :
  - Données : Visualisation des enregistrements
  - Filtres : Outils de recherche et filtrage
  - Statistiques : Métriques et analyses
  - Validations : Erreurs et avertissements
- **Chargement asynchrone** : Interface réactive pendant le traitement
- **Feedback utilisateur** : Messages d'état et barres de progression

### 📤 Export et rapports

- **Formats multiples** : Excel (.xlsx), CSV, JSON
- **Rapports automatisés** : Génération de rapports complets
- **Données filtrées** : Export des résultats de recherche
- **Formatage professionnel** : Mise en forme Excel avec styles

## 🔧 Configuration spécifique

### Format CSV supporté

```
UM;UM (Lib);DUM;DUM (Lib);SDUM;FSDUM;Dom.;Dom.(Lib);SDOM;SDOM.(Lib);
Equipe;Equipe (Lib.);NNI;Nom;Prénom;Jour;Désignation jour;Jour férié;
Fin cycle;Astreinte;Astr. Occas.;HT;De;à;De;à;HTM;De;à;De;à;
HE;De;à;De;à;Code;Désignation code;Valeur;Dés. Unité;Heure début;Heure fin
```

### Valeurs validées

- **UM (Lib)** : "DR PARIS"
- **Equipe (Lib.)** : "PV IT ASTREINTE"
- **Désignation jour** : Lundi, Mardi, Mercredi, Jeudi, Vendredi, Samedi, Dimanche
- **Jour férié** : "X" ou vide
- **Astreinte** : "I" ou vide
- **HT** : "J" ou vide
- **Code** : "D"
- **Dés. Unité** : "Heure(s)", "Jour(s)"

## 📁 Structure du projet

```
PMTAnalytics/
├── src/                    # Code source principal
│   ├── config/            # Configuration
│   ├── models/            # Modèles de données
│   ├── services/          # Services métier
│   ├── ui/               # Interface utilisateur
│   ├── utils/            # Utilitaires
│   └── main.py           # Point d'entrée principal
├── data/                  # Données
│   ├── input/            # Fichiers d'entrée
│   ├── output/           # Fichiers de sortie
│   └── samples/          # Exemples
├── tests/                # Tests unitaires
├── logs/                 # Fichiers de log
├── requirements.txt      # Dépendances Python
├── run.py               # Script de lancement
├── simple_app.py        # Version simplifiée
└── README.md            # Documentation
```

## 🚀 Installation et utilisation

### Installation

```bash
# Activer l'environnement virtuel
source .venv/bin/activate

# Installer les dépendances
pip install -r requirements.txt
```

### Lancement

```bash
# Lancement principal
python run.py

# Version simplifiée (en cas de problème)
python simple_app.py
```

## 🎯 Scalabilité et maintenabilité

### Architecture modulaire

- **Séparation des couches** : UI, Services, Modèles
- **Injection de dépendances** : Services découplés
- **Configuration externalisée** : Paramètres modifiables
- **Logging centralisé** : Debugging et monitoring

### Extensibilité

- **Nouveaux formats** : Ajout facile de nouveaux types de fichiers
- **Nouvelles validations** : Extension du système de validation
- **Nouveaux exports** : Ajout de formats d'export
- **Nouvelles analyses** : Extension des statistiques

### Tests et qualité

- **Tests unitaires** : Couverture des composants critiques
- **Gestion d'erreurs** : Récupération gracieuse
- **Documentation** : Code documenté et guides utilisateur

## 📋 Livrables

1. **Application complète** : Code source avec architecture professionnelle
2. **Version simplifiée** : Interface de test et validation
3. **Fichier d'exemple** : CSV conforme à vos spécifications
4. **Documentation** : Guides d'utilisation et technique
5. **Tests** : Framework de tests unitaires
6. **Configuration** : Paramètres adaptés à vos besoins

## 🔄 Prochaines étapes possibles

- **Graphiques avancés** : Visualisations avec matplotlib/seaborn
- **Base de données** : Stockage persistant des données
- **API REST** : Interface web pour usage distant
- **Planification** : Traitement automatisé de fichiers
- **Notifications** : Alertes par email ou autres canaux

---

**L'application est prête à l'emploi et répond à toutes vos contraintes spécifiées !** 🎉
