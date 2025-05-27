# 🎉 PMT Analytics v1.0.0

**Application d'analyse des plannings PMT d'Enedis** - Interface graphique moderne pour traiter automatiquement les fichiers CSV de planning journalier.

## 📦 Téléchargements

- **🍎 macOS** : `PMTAnalytics_v1.0.0_macOS.zip` (~30 MB)
- **🪟 Windows** : `PMTAnalytics_v1.0.0_Windows.zip` (~37 MB)

## ✨ Fonctionnalités

- 📊 **Analyse automatique** des fichiers CSV de planning journalier
- 📈 **Statistiques détaillées** par employé et équipe
- 💾 **Export Excel** formaté avec graphiques
- 🖥️ **Interface graphique** moderne et intuitive
- 🚀 **Build automatisé** via GitHub Actions

## 🚀 Utilisation rapide

1. **Téléchargez** l'application pour votre OS
2. **Lancez** l'exécutable
3. **Sélectionnez** votre fichier CSV de planning
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

Équipes analysées par défaut :

- PV IT ASTREINTE
- PV B ASTREINTE
- PV G ASTREINTE
- PV PE ASTREINTE

Modifiez `config.py` pour personnaliser.

## 📊 Export Excel

Génère automatiquement :

- **Feuille 1** : Statistiques par employé
- **Feuille 2** : Moyennes par équipe

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
**Version** : v1.0.0  
**Dernière mise à jour** : Mai 2025  
**Usage** : Interne Enedis uniquement  
**Repository** : https://github.com/CapelleGab/ENEDIS-charge-pmt.git
