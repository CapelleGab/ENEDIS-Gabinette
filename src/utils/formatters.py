"""
Module de formatage des données PMT.

author : CAPELLE Gabin
"""

from config import COLONNES_FINALES


def formater_donnees_finales(stats_employes):
    """
    Formate le DataFrame final avec les colonnes demandées et les renomme.
    
    Args:
        stats_employes (pd.DataFrame): Statistiques brutes par employé
        
    Returns:
        pd.DataFrame: DataFrame formaté avec les bonnes colonnes
    """
    # Colonnes de base toujours présentes
    colonnes_base = ['Nom', 'Prénom', 'Equipe (Lib.)', 
                     'Nb_Jours_Presents', 'Nb_Jours_Partiels', 'Total_Jours_Travailles',
                     'Total_Heures_Travaillees', 'Nb_Jours_Complets', 
                     'Nb_Jours_Absents', 'Total_Heures_Absence', 
                     'Presence_Pourcentage_365j']
    
    # Nouvelles colonnes optionnelles (peuvent ne pas être présentes)
    nouvelles_colonnes = [
        'Heures_Supp',
        'Nb_Périodes_Arrêts', 'Nb_Jours_Arrêts_41', 'Nb_Jours_Arrêts_5H',
        'Moy_Heures_Par_Arrêt_Maladie'
    ]
    
    # Sélectionner les colonnes disponibles
    colonnes_a_garder = colonnes_base.copy()
    for col in nouvelles_colonnes:
        if col in stats_employes.columns:
            colonnes_a_garder.append(col)
    
    # Formatage du DataFrame final avec les colonnes disponibles
    stats_final = stats_employes[colonnes_a_garder].copy()
    
    # Créer le mapping de renommage dynamique
    mapping_renommage = {
        'Equipe (Lib.)': 'Équipe',
        'Nb_Jours_Presents': 'Jours_Présents_Complets',
        'Nb_Jours_Partiels': 'Jours_Partiels',
        'Total_Jours_Travailles': 'Total_Jours_Travaillés',
        'Total_Heures_Travaillees': 'Total_Heures_Travaillées',
        'Nb_Jours_Complets': 'Jours_Complets',
        'Nb_Jours_Absents': 'Jours_Absents',
        'Total_Heures_Absence': 'Total_Heures_Absence',
        'Presence_Pourcentage_365j': 'Présence_%_365j'
    }
    
    # Renommer les colonnes
    stats_final = stats_final.rename(columns=mapping_renommage)
    
    return stats_final


def analyser_codes_presence(df_filtre):
    """
    Analyse les codes présents dans les données filtrées.
    
    Args:
        df_filtre (pd.DataFrame): DataFrame filtré
        
    Returns:
        pd.Series: Comptage des codes
    """
    codes_uniques = df_filtre['Code'].value_counts()
    # print(f"\nCodes présents dans les données filtrées :")
    # for code, count in codes_uniques.head(10).items(): 
    #     print(f"  '{code}': {count} occurrences")
    return codes_uniques 