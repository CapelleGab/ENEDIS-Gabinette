"""
Module de suppression des enregistrements selon des critères spécifiques.
Permet de nettoyer les données pour éviter les biais statistiques causés par
des employés arrivés en fin d'année ou qui ne sont plus présents.

author : CAPELLE Gabin
"""

import pandas as pd


def supprimer_astreinte_insuffisants(stats_astreinte):
    """
    Supprime les employés d'astreinte qui ont moins de 50 jours présents complets.
    
    Args:
        stats_astreinte (pd.DataFrame): DataFrame avec les statistiques d'astreinte
        
    Returns:
        pd.DataFrame: DataFrame filtré sans les employés ayant moins de 50 jours présents complets
    """
    if stats_astreinte.empty:
        return stats_astreinte
    
    # Vérifier que la colonne existe
    if 'Jours_Présents_Complets' not in stats_astreinte.columns:
        print("Attention: La colonne 'Jours_Présents_Complets' n'existe pas dans les données d'astreinte")
        return stats_astreinte
    
    # Compter le nombre d'employés avant filtrage
    nb_avant = len(stats_astreinte)
    
    # Filtrer les employés avec au moins 50 jours présents complets
    stats_filtre = stats_astreinte[stats_astreinte['Jours_Présents_Complets'] >= 50].copy()
    
    # Compter le nombre d'employés après filtrage
    nb_apres = len(stats_filtre)
    nb_supprimes = nb_avant - nb_apres
    
    if nb_supprimes > 0:
        print(f"ASTREINTE: {nb_supprimes} employé(s) supprimé(s) (moins de 50 jours présents complets)")
        print(f"ASTREINTE: {nb_apres} employé(s) conservé(s) sur {nb_avant}")
    
    return stats_filtre


def supprimer_pit_insuffisants(stats_pit):
    """
    Supprime les employés PIT qui ont moins de 55 jours présents complets.
    
    Args:
        stats_pit (pd.DataFrame): DataFrame avec les statistiques PIT
        
    Returns:
        pd.DataFrame: DataFrame filtré sans les employés ayant moins de 55 jours présents complets
    """
    if stats_pit.empty:
        return stats_pit
    
    # Vérifier que la colonne existe
    if 'Jours_Présents_Complets' not in stats_pit.columns:
        print("Attention: La colonne 'Jours_Présents_Complets' n'existe pas dans les données PIT")
        return stats_pit
    
    # Compter le nombre d'employés avant filtrage
    nb_avant = len(stats_pit)
    
    # Filtrer les employés avec au moins 55 jours présents complets
    stats_filtre = stats_pit[stats_pit['Jours_Présents_Complets'] >= 55].copy()
    
    # Compter le nombre d'employés après filtrage
    nb_apres = len(stats_filtre)
    nb_supprimes = nb_avant - nb_apres
    
    if nb_supprimes > 0:
        print(f"PIT: {nb_supprimes} employé(s) supprimé(s) (moins de 55 jours présents complets)")
        print(f"PIT: {nb_apres} employé(s) conservé(s) sur {nb_avant}")
    
    return stats_filtre


def supprimer_3x8_insuffisants(stats_3x8):
    """
    Supprime les employés 3x8 selon des critères spécifiques.
    Pour l'instant, aucun critère n'est appliqué.
    
    Args:
        stats_3x8 (pd.DataFrame): DataFrame avec les statistiques 3x8
        
    Returns:
        pd.DataFrame: DataFrame non modifié (pour l'instant)
    """
    if stats_3x8.empty:
        return stats_3x8
    
    # Pour l'instant, aucun filtrage n'est appliqué aux employés 3x8
    print(f"3x8: Aucun filtrage appliqué - {len(stats_3x8)} employé(s) conservé(s)")
    
    return stats_3x8.copy() 