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
        return stats_astreinte
    
    # Filtrer les employés avec au moins 50 jours présents complets
    stats_filtre = stats_astreinte[stats_astreinte['Jours_Présents_Complets'] >= 50].copy()
    
    return stats_filtre


def supprimer_tip_insuffisants(stats_tip):
    """
    Supprime les employés TIP qui ont moins de 55 jours présents complets.
    
    Args:
        stats_tip (pd.DataFrame): DataFrame avec les statistiques TIP
        
    Returns:
        pd.DataFrame: DataFrame filtré sans les employés ayant moins de 55 jours présents complets
    """
    if stats_tip.empty:
        return stats_tip
    
    # Vérifier que la colonne existe
    if 'Jours_Présents_Complets' not in stats_tip.columns:
        return stats_tip
    
    # Filtrer les employés avec au moins 55 jours présents complets
    stats_filtre = stats_tip[stats_tip['Jours_Présents_Complets'] >= 55].copy()
    
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
    return stats_3x8.copy() 