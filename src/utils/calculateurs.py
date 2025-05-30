"""
Module de calcul des statistiques PMT.

author : CAPELLE Gabin
"""

import pandas as pd


def calculer_heures_travaillees(row):
    """
    Calcule les heures travaillées selon la logique corrigée :
    - Si code "80TH" : 8 heures travaillées (journée complète)
    - Si la valeur existe et est numérique : 
      * Si unité = "Heure(s)" : valeur = heures travaillées (ex: 6 heures travaillées)
      * Si unité = "Jour(s)" : valeur * 8 = heures travaillées (ex: 1 jour = 8h travaillées)
      * Si pas d'unité : 8 - valeur (comportement par défaut pour les absences)
    - Si code d'absence sans valeur : 0 heures travaillées (8h d'absence)
    - Si pas de code ou valeur invalide : 8 heures travaillées (journée complète)
    
    Args:
        row: Ligne du DataFrame
        
    Returns:
        float: Nombre d'heures travaillées
    """
    try:
        # Si on a un code (absence ou autre)
        if pd.notna(row['Code']) and row['Code'] not in ['', ' ']:
            # Cas spécial : code "80TH" = 8 heures travaillées
            if str(row['Code']).strip().upper() == '80TH':
                return 8.0
            
            # Si on a une valeur numérique avec le code
            if pd.notna(row['Valeur']) and row['Valeur'] != '':
                valeur = float(row['Valeur'])
                if valeur >= 0:
                    # Vérifier l'unité dans la colonne "Dés. unité"
                    unite = str(row.get('Dés. unité', '')).strip().lower() if pd.notna(row.get('Dés. unité', '')) else ''
                    
                    if 'jour' in unite:
                        # Si l'unité est en jours : valeur = nombre de jours travaillés
                        # Exemple: 1 jour travaillé = 8h travaillées
                        heures_travaillees = valeur * 8.0
                        return min(8.0, heures_travaillees)  # Maximum 8 heures par jour
                    elif 'heure' in unite:
                        # Si l'unité est en heures : valeur = nombre d'heures travaillées
                        # Exemple: 6 heures travaillées
                        return min(8.0, valeur)  # Maximum 8 heures par jour
                    else:
                        # Si pas d'unité : valeur = nombre d'heures d'absence (ancien comportement)
                        # Exemple: 2 heures d'absence = 8-2 = 6h travaillées
                    heures_travaillees = 8.0 - valeur
                    return max(0, heures_travaillees)  # Minimum 0 heures
                else:
                    return 8.0  # Valeur négative = journée complète
            else:
                # Code d'absence sans valeur = 8h d'absence = 0h travaillées
                return 0.0
        else:
            # Pas de code = journée complète travaillée
            return 8.0
    except (ValueError, TypeError):
        # Si conversion impossible, considérer comme journée complète
        return 8.0


def calculer_jours_travailles(heures):
    """
    Convertit les heures travaillées en fraction de jour.
    Exemple : 6h = 6/8 = 0.75 jour
    
    Args:
        heures (float): Nombre d'heures travaillées
        
    Returns:
        float: Fraction de jour travaillé
    """
    return heures / 8.0


def calculer_statistiques_employes(df_filtre):
    """
    Calcule les statistiques pour chaque employé selon la nouvelle logique.
    Sépare les jours complets, partiels et absents.
    
    Args:
        df_filtre (pd.DataFrame): DataFrame filtré
        
    Returns:
        pd.DataFrame: DataFrame avec les statistiques par employé
    """
    # Calculer les heures travaillées pour chaque ligne
    df_filtre['Heures_Travaillees'] = df_filtre.apply(calculer_heures_travaillees, axis=1)
    
    # Calculer les jours travaillés (en fraction)
    df_filtre['Jours_Travailles'] = df_filtre['Heures_Travaillees'].apply(calculer_jours_travailles)
    
    # Identifier les jours partiels : quand il y a un code d'absence avec une valeur
    # Cela signifie que l'employé a travaillé partiellement (8h - valeur)
    df_filtre['Est_Jour_Partiel'] = (
        pd.notna(df_filtre['Code']) & 
        (df_filtre['Code'] != '') & 
        (df_filtre['Code'] != ' ') &
        pd.notna(df_filtre['Valeur']) & 
        (df_filtre['Valeur'] > 0)
    )
    
    # Calculer les statistiques par employé
    stats = df_filtre.groupby(['Gentile', 'Equipe (Lib.)', 'Nom', 'Prénom']).agg(
        # Jours complets (8h exactement)
        Nb_Jours_Complets=('Heures_Travaillees', lambda x: sum(x == 8.0)),
        
        # Jours partiels (heures entre 0 et 8, exclus)
        Nb_Jours_Partiels=('Est_Jour_Partiel', 'sum'),
        
        # Jours absents (0h)
        Nb_Jours_Absents=('Heures_Travaillees', lambda x: sum(x == 0.0)),
        
        # Jours présents = jours complets uniquement (pas les partiels)
        Nb_Jours_Presents=('Heures_Travaillees', lambda x: sum(x == 8.0)),
        
        # Total jours travaillés (en fraction de jours)
        Total_Jours_Travailles=('Jours_Travailles', 'sum'),
        
        # Total heures travaillées
        Total_Heures_Travaillees=('Heures_Travaillees', 'sum'),
        
        # Total heures d'absence
        Total_Heures_Absence=('Heures_Travaillees', lambda x: sum(8.0 - x))
    ).reset_index()
    
    # Calculer le pourcentage de présence sur 365 jours (basé sur les jours complets)
    stats['Presence_Pourcentage_365j'] = (stats['Nb_Jours_Presents'] / 365 * 100).round(2)
    
    # Calculer la moyenne d'heures par jour présent (jours complets + partiels)
    stats['Moyenne_Heures_Par_Jour'] = (
        stats['Total_Heures_Travaillees'] / 
        (stats['Nb_Jours_Presents'] + stats['Nb_Jours_Partiels']).replace(0, 1)
    ).round(2)
    
    # Arrondir Total_Jours_Travailles au centième près (2 décimales)
    stats['Total_Jours_Travailles'] = stats['Total_Jours_Travailles'].round(2)
    
    return stats


def calculer_moyennes_equipe(df_stats):
    """
    Calcule les moyennes par équipe selon la nouvelle structure.
    
    Args:
        df_stats (pd.DataFrame): DataFrame avec les statistiques par employé
        
    Returns:
        pd.DataFrame: DataFrame avec les moyennes par équipe
    """
    moyennes = df_stats.groupby('Équipe').agg(
        Nb_Employés=('Nom', 'count'),
        Moy_Jours_Présents_Complets=('Jours_Présents_Complets', 'mean'),
        Moy_Jours_Partiels=('Jours_Partiels', 'mean'),
        Moy_Total_Jours_Travaillés=('Total_Jours_Travaillés', 'mean'),
        Moy_Total_Heures=('Total_Heures_Travaillées', 'mean'),
        Moy_Jours_Complets=('Jours_Complets', 'mean'),
        Moy_Jours_Absents=('Jours_Absents', 'mean'),
        Moy_Heures_Absence=('Total_Heures_Absence', 'mean'),
        Moy_Présence_365j=('Présence_%_365j', 'mean'),
        Moy_Heures_Par_Jour_Présent=('Moyenne_Heures_Par_Jour_Présent', 'mean')
    ).reset_index()
    
    # Arrondir toutes les colonnes à 2 décimales
    moyennes = moyennes.round(2)
    
    # Arrondir spécifiquement Moy_Jours_Partiels à 1 décimale (dixième près)
    if 'Moy_Jours_Partiels' in moyennes.columns:
        moyennes['Moy_Jours_Partiels'] = moyennes['Moy_Jours_Partiels'].round(1)
    
    return moyennes 