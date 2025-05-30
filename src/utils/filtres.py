"""
Module de filtrage des données PMT.

author : CAPELLE Gabin
"""

from config import JOURS_WEEKEND, HORAIRE_DEBUT_REFERENCE, HORAIRE_FIN_REFERENCE
from .horaires import get_horaire_final, verifier_horaire_reference


def appliquer_filtres_astreinte(df):
    """
    Applique les filtres spécifiques aux équipes d'astreinte :
    1. Supprime les week-ends
    2. Supprime les jours fériés
    3. GARDE les jours d'astreinte (avec "I")
    4. Garde les horaires 'J' ET tous les codes horaires quand Astreinte='I' (K, H, R, etc.)
    5. Ne garde que les horaires 07:30:00 à 16:15:00 (sauf pour les jours d'astreinte)
    
    Args:
        df (pd.DataFrame): DataFrame source
        
    Returns:
        pd.DataFrame: DataFrame filtré pour les équipes d'astreinte
    """
    # print("Application des filtres pour équipes d'astreinte...")
    
    # Détermination de l'horaire final
    df['Horaire_Final'] = df.apply(get_horaire_final, axis=1)
    
    # 1. Supprimer les week-ends
    df = df[~df['Désignation jour'].isin(JOURS_WEEKEND)].copy()
    # print(f"Après suppression week-ends: {len(df)} lignes")
    
    # 2. Supprimer les jours fériés
    df = df[df['Jour férié'] != 'X'].copy()
    # print(f"Après suppression jours fériés: {len(df)} lignes")
    
    # 3. GARDER les jours d'astreinte (ne pas supprimer les "I")
    # Cette ligne est commentée pour les équipes d'astreinte
    # df = df[df['Astreinte'] != 'I'].copy()
    # print(f"Jours d'astreinte conservés pour équipes d'astreinte")
    
    # 4. Filtrage des horaires : 'J' OU n'importe quel code si Astreinte='I'
    # Garder les lignes où :
    # - Horaire_Final == 'J' (jours normaux)
    # - OU Astreinte == 'I' (jours d'astreinte avec n'importe quel code horaire)
    df = df[(df['Horaire_Final'] == 'J') | (df['Astreinte'] == 'I')].copy()
    # print(f"Après filtrage horaires 'J' + codes astreinte: {len(df)} lignes")
    
    # 5. Filtrage des horaires de référence : seulement pour les jours non-astreinte
    # Pour les jours d'astreinte (I), on ne filtre pas sur les horaires
    df['Horaire_Reference'] = df.apply(verifier_horaire_reference, axis=1)
    df = df[(df['Horaire_Reference'] == True) | (df['Astreinte'] == 'I')].copy()
    # print(f"Après filtrage horaires {HORAIRE_DEBUT_REFERENCE}-{HORAIRE_FIN_REFERENCE} (sauf astreinte): {len(df)} lignes")
    
    return df


def appliquer_filtres_base(df):
    """
    Applique les filtres de base :
    1. Supprime les week-ends
    2. Supprime les jours fériés
    3. Supprime les jours d'astreinte
    4. Ne garde que les horaires 'J'
    5. Ne garde que les horaires 07:30:00 à 16:15:00
    
    Args:
        df (pd.DataFrame): DataFrame source
        
    Returns:
        pd.DataFrame: DataFrame filtré
    """
    # print("Application des filtres de base...")
    
    # Détermination de l'horaire final
    df['Horaire_Final'] = df.apply(get_horaire_final, axis=1)
    
    # 1. Supprimer les week-ends
    df = df[~df['Désignation jour'].isin(JOURS_WEEKEND)].copy()
    # print(f"Après suppression week-ends: {len(df)} lignes")
    
    # 2. Supprimer les jours fériés
    df = df[df['Jour férié'] != 'X'].copy()
    # print(f"Après suppression jours fériés: {len(df)} lignes")
    
    # 3. Supprimer les jours d'astreinte
    df = df[df['Astreinte'] != 'I'].copy()
    # print(f"Après suppression astreintes: {len(df)} lignes")
    
    # 4. Ne garder que les horaires 'J'
    df = df[df['Horaire_Final'] == 'J'].copy()
    # print(f"Après filtrage horaires 'J': {len(df)} lignes")
    
    # 5. Ne garder que les horaires 07:30:00 à 16:15:00
    df['Horaire_Reference'] = df.apply(verifier_horaire_reference, axis=1)
    df = df[df['Horaire_Reference'] == True].copy()
    # print(f"Après filtrage horaires {HORAIRE_DEBUT_REFERENCE}-{HORAIRE_FIN_REFERENCE}: {len(df)} lignes")
    
    return df 