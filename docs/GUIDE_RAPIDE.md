# PMT Analytics - Guide d'utilisation rapide

## 🚀 Lancement de l'application

```bash
# Activer l'environnement virtuel
source .venv/bin/activate

# Lancer l'application
python run.py
```

## 📋 Configuration CSV supportée

- **Séparateur** : Point-virgule (`;`)
- **Encodage** : Latin1 (ISO-8859-1)
- **Format** : 42 colonnes exactes dans l'ordre spécifié

### Colonnes attendues :

```
UM;UM (Lib);DUM;DUM (Lib);SDUM;FSDUM;Dom.;Dom.(Lib);SDOM;SDOM.(Lib);
Equipe;Equipe (Lib.);NNI;Nom;Prénom;Jour;Désignation jour;Jour férié;
Fin cycle;Astreinte;Astr. Occas.;HT;De;à;De;à;HTM;De;à;De;à;
HE;De;à;De;à;Code;Désignation code;Valeur;Dés. Unité;Heure début;Heure fin
```

## 🔧 Utilisation de l'application

### 1. Charger un fichier CSV

- Cliquez sur "📁 Ouvrir un fichier CSV"
- Sélectionnez votre fichier PMT
- L'application vérifie automatiquement la structure

### 2. Analyser les données

- Cliquez sur "📊 Analyser" pour voir les statistiques
- Vérifiez la conformité de la structure
- Consultez les informations sur les employés et équipes

### 3. Exporter les résultats

- Cliquez sur "💾 Exporter"
- Choisissez le format (Excel ou CSV)
- Sélectionnez l'emplacement de sauvegarde

## 📁 Fichiers d'exemple

Un fichier d'exemple est disponible dans :

```
data/samples/exemple_pmt.csv
```

## ⚠️ Valeurs attendues

### Champs importants :

- **UM (Lib)** : "DR PARIS"
- **Equipe (Lib.)** : "PV IT ASTREINTE"
- **Jour** : Format "JJ/MM/AAAA" (ex: 01/01/2024)
- **Désignation jour** : Lundi, Mardi, Mercredi, etc.
- **Jour férié** : "X" ou vide
- **Astreinte** : "I" ou vide
- **HT** : "J" ou vide
- **Code** : "D"
- **Dés. Unité** : "Heure(s)" ou "Jour(s)"

## 🛠️ Dépannage

### L'application ne se lance pas

```bash
# Vérifier l'environnement virtuel
source .venv/bin/activate

# Réinstaller les dépendances
pip install -r requirements.txt

# Lancer la version simplifiée
python simple_app.py
```

### Erreur de lecture CSV

- Vérifiez l'encodage (doit être Latin1)
- Vérifiez le séparateur (doit être `;`)
- Vérifiez que toutes les colonnes sont présentes

### Problèmes d'export

- Vérifiez les permissions d'écriture
- Assurez-vous que le fichier de destination n'est pas ouvert
- Essayez un autre format (Excel vs CSV)

## 📞 Support

En cas de problème :

1. Vérifiez les logs dans le répertoire `logs/`
2. Consultez les messages d'erreur dans l'application
3. Utilisez la version simplifiée (`simple_app.py`) pour les tests de base
