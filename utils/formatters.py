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
    # Formatage du DataFrame final avec UNIQUEMENT les colonnes demandées
    stats_final = stats_employes[['Nom', 'Prénom', 'Equipe (Lib.)', 
                                 'Nb_Jours_Presents', 'Nb_Jours_Partiels', 'Total_Jours_Travailles',
                                 'Total_Heures_Travaillees', 'Nb_Jours_Complets', 
                                 'Nb_Jours_Absents', 'Total_Heures_Absence', 
                                 'Presence_Pourcentage_365j']].copy()
    
    # Calculer la moyenne d'heures de présence par jour OÙ L'EMPLOYÉ ÉTAIT PRÉSENT
    # (Total heures travaillées / (Jours présents + Jours partiels))
    stats_final['Moyenne_Heures_Par_Jour_Present'] = (
        stats_final['Total_Heures_Travaillees'] / 
        (stats_final['Nb_Jours_Presents'] + stats_final['Nb_Jours_Partiels']).replace(0, 1)
    ).round(2)
    
    # Renommage des colonnes selon les spécifications
    stats_final.columns = COLONNES_FINALES
    
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