# 🎉 PMT Analytics v1.2.0

**Application d'analyse des plannings PMT d'Enedis** - Interface graphique moderne pour traiter automatiquement les fichiers CSV de planning journalier avec support des équipes d'astreinte, PIT et 3x8.

## 📦 Téléchargements

- **🍎 macOS** : `PMTAnalytics_v1.0.0_macOS.zip` (~30 MB)
- **🪟 Windows** : `PMTAnalytics_v1.0.0_Windows.zip` (~37 MB)

## ✨ Fonctionnalités

- 📊 **Analyse automatique** des fichiers CSV de planning journalier
- 📈 **Statistiques détaillées** par employé et équipe (astreinte + PIT + 3x8)
- 💾 **Export Excel** formaté avec 6 feuilles (astreinte + PIT + 3x8)
- 🖥️ **Interface graphique** moderne et intuitive
- 🔧 **Support équipes PIT** (hors astreinte) en parallèle
- 🔄 **Support équipes 3x8** avec détection automatique des horaires
- ⏰ **Gestion absences partielles** basée sur la colonne Valeur
- 🚀 **Build automatisé** via GitHub Actions

## 🚀 Utilisation rapide

1. **Téléchargez** l'application pour votre OS
2. **Lancez** l'exécutable
3. **Sélectionnez** votre fichier CSV de planning
   - Format attendu : `Planning_journalier_YYYY.csv`
   - Encodage : Latin1 (ISO-8859-1)
   - Séparateur : Point-virgule (;)
4. **Analysez** et exportez vers Excel

## 🛠️ Développement

```bash
# Installation
git clone https://github.com/CapelleGab/ENEDIS-charge-pmt.git
cd StatistiquePMT
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# Lancement
python main.py

# Build local
python src/scripts/build_ci.py
```

## 📋 Structure

```
StatistiquePMT/
├── main.py             # Point d'entrée principal
├── src/                # Code source
│   ├── gui/            # Interface graphique modulaire
│   ├── utils/          # Modules métier
│   └── scripts/        # Build automatisé
├── assets/             # Ressources (icônes)
└── config.py          # Configuration globale
```

## 🔧 Configuration

**Équipes d'astreinte (4) :**

- PV IT ASTREINTE, PV B ASTREINTE, PV G ASTREINTE, PV PE ASTREINTE

**Équipes PIT - Hors astreinte (6) :**

- PV B SANS ASTREINTE, PV B TERRAIN, PV IT SANS ASTREINTE
- PF IT TERRAIN, PV G SANS ASTREINTE, PV PE SANS ASTREINTE

**Horaires 3x8 détectés automatiquement :**

- 🌅 **Matin** : 07:30-15:30
- 🌆 **Après-midi** : 15:30-23:30
- 🌙 **Nuit** : 23:30-07:30

> **Note** : Les employés travaillant en 3x8 sont automatiquement exclus des statistiques PIT pour éviter les doublons.

Modifiez `config.py` pour personnaliser les équipes analysées.

## 📊 Export Excel

Génère automatiquement **6 feuilles** :

**Équipes d'astreinte :**

- **ASTREINTE_STATS** : Statistiques par employé (astreinte)
- **ASTREINTE_EQUIPE_MOYENNES** : Moyennes par équipe (astreinte)

**Équipes PIT (sans employés 3x8) :**

- **PIT_STATS** : Statistiques par employé (hors astreinte)
- **PIT_EQUIPE_MOYENNES** : Moyennes par équipe (hors astreinte)

**Équipes 3x8 :**

- **3x8_STATS** : Statistiques par employé (3x8)
- **3x8_EQUIPE_MOYENNES** : Moyennes par équipe (3x8)

### 🔄 Spécificités 3x8

- **Répartition des postes** : Comptage par créneaux (matin/après-midi/nuit)
- **Absences détaillées** : Distinction entre absences complètes et partielles
- **Calcul précis** : Si Valeur < 8, fraction travaillée = (8-Valeur)/8

## 🤝 Contribution

1. Fork le projet
2. Créez votre branche (`git checkout -b feature/nouvelle-fonctionnalite`)
3. Committez (`git commit -m 'Ajout nouvelle fonctionnalité'`)
4. Push (`git push origin feature/nouvelle-fonctionnalite`)
5. Ouvrez une Pull Request

## 📚 Documentation

- 👥 **[Guide Utilisateur](UTILISATION.md)** - Installation et utilisation de l'application
- 🛠️ **[Guide Développeur](DEVELOPPEUR.md)** - Setup développement et contribution

## 📞 Support

- 🐛 **Issues** : [GitHub Issues](https://github.com/CapelleGab/ENEDIS-charge-pmt/issues)
- 📧 **Contact** : CAPELLE Gabin - Enedis

---

**Développé par** : CAPELLE Gabin - Enedis  
**Version** : v1.2.0  
**Dernière mise à jour** : Mai 2025  
**Usage** : Interne Enedis uniquement  
**Repository** : https://github.com/CapelleGab/ENEDIS-charge-pmt.git
