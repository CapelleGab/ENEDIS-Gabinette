"""
Script principal d'analyse des statistiques PMT (Planning de Maintenance Technique).
Architecture modulaire pour une meilleure maintenabilité.

author : CAPELLE Gabin
"""

from utils import (
    charger_donnees_csv,
    preparer_donnees,
    supprimer_doublons,
    appliquer_filtres_base,
    calculer_statistiques_employes,
    calculer_moyennes_equipe,
    formater_donnees_finales,
    analyser_codes_presence,
    sauvegarder_excel,
    afficher_resume_final
)


def main():
    """
    Fonction principale du traitement des données PMT.
    Orchestration de toutes les étapes d'analyse.
    """
    # print(f"Traitement des statistiques PMT pour l'année {ANNEE}")
    
    # ÉTAPE 1 : Chargement des données
    df_originel = charger_donnees_csv()
    if df_originel is None:
        return
    
    # ÉTAPE 2 : Préparation des données
    df_equipe = preparer_donnees(df_originel)
    
    # Analyse des horaires disponibles (pour diagnostic)
    # analyser_horaires_disponibles(df_equipe)
    
    # ÉTAPE 3 : Suppression des doublons
    df_unique = supprimer_doublons(df_equipe)
    
    # ÉTAPE 4 : Application des filtres
    df_filtre = appliquer_filtres_base(df_unique)
    
    # print(f"\nDonnées après filtrage : {len(df_filtre)} lignes")
    
    # ÉTAPE 5 : Analyse des codes présents
    codes_uniques = analyser_codes_presence(df_filtre)
    
    # ÉTAPE 6 : Calcul des statistiques
    stats_employes = calculer_statistiques_employes(df_filtre)
    
    # ÉTAPE 7 : Formatage des données finales
    stats_final = formater_donnees_finales(stats_employes)
    
    # ÉTAPE 8 : Calcul des moyennes par équipe
    moyennes_equipe = calculer_moyennes_equipe(stats_final)
    
    # ÉTAPE 9 : Sauvegarde
    sauvegarder_excel(stats_final, moyennes_equipe)
    
    # ÉTAPE 10 : Affichage du résumé
    afficher_resume_final(stats_final)


if __name__ == "__main__":
    main() 