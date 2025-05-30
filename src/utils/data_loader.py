"""
Module de chargement et préparation des données PMT.

author : CAPELLE Gabin
"""

import pandas as pd
from config import *


def charger_donnees_csv(fichier_csv=None):
    """
    Charge les données depuis le fichier CSV.
    
    Args:
        fichier_csv (str, optional): Chemin vers le fichier CSV. Si None, utilise FICHIER_CSV de config.
    
    Returns:
        pd.DataFrame: DataFrame avec les données chargées ou None en cas d'erreur
    """
    import os
    
    # Utiliser le paramètre ou la variable de config
    csv_path = fichier_csv if fichier_csv is not None else FICHIER_CSV
    
    # Vérifications préliminaires
    if not csv_path:
        raise ValueError("Aucun fichier CSV spécifié")
    
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"Le fichier CSV n'existe pas : {csv_path}")
    
    if not os.path.isfile(csv_path):
        raise ValueError(f"Le chemin spécifié n'est pas un fichier : {csv_path}")
    
    # Vérifier la taille du fichier
    file_size = os.path.getsize(csv_path)
    if file_size == 0:
        raise ValueError(f"Le fichier CSV est vide : {csv_path}")
    
    try:
        # Tentative de lecture avec les paramètres par défaut
        df = pd.read_csv(csv_path, encoding=CSV_ENCODING, sep=CSV_SEPARATOR, low_memory=False)
        
        if df.empty:
            raise ValueError("Le DataFrame chargé est vide")
        
        if len(df.columns) == 0:
            raise ValueError("Le DataFrame n'a aucune colonne")
        
        # Vérifier les colonnes essentielles
        required_columns = ['Nom', 'Prénom', 'Equipe (Lib.)', 'Jour', 'Valeur']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            available_columns = list(df.columns)[:10]  # Premières 10 colonnes
            raise ValueError(f"Colonnes manquantes: {missing_columns}. Colonnes disponibles: {available_columns}")
        
        print(f"✅ Données chargées : {len(df)} lignes, {len(df.columns)} colonnes")
        return df
        
    except UnicodeDecodeError as e:
        raise ValueError(f"Erreur d'encodage du fichier CSV. Essayez un autre encodage. Erreur: {e}")
    except pd.errors.EmptyDataError:
        raise ValueError("Le fichier CSV ne contient aucune donnée")
    except pd.errors.ParserError as e:
        raise ValueError(f"Erreur de parsing du CSV. Vérifiez le séparateur et le format. Erreur: {e}")
    except Exception as e:
        raise RuntimeError(f"Erreur inattendue lors du chargement du CSV: {type(e).__name__}: {e}")


def preparer_donnees(df):
    """
    Prépare les données pour l'analyse.
    
    Args:
        df (pd.DataFrame): DataFrame source
        
    Returns:
        pd.DataFrame: DataFrame préparé
    """
    # Créer l'identifiant unique employé
    df['Gentile'] = (df['Nom'] + ' ' + 
                     df['Prénom'] + ' ' + 
                     df['Equipe (Lib.)'])
    
    # Filtrage par équipe
    df_equipe = df[df['Equipe (Lib.)'].isin(CODES_EQUIPES_ASTREINTE)].copy()
    
    # Corriger le format français (virgule) vers format anglais (point) pour les décimales
    df_equipe['Valeur'] = df_equipe['Valeur'].astype(str).str.replace(',', '.', regex=False)
    
    # Conversion numérique des valeurs
    df_equipe['Valeur'] = pd.to_numeric(df_equipe['Valeur'], errors='coerce')
    
    return df_equipe


def preparer_donnees_pit(df):
    """
    Prépare les données pour l'analyse des équipes PIT (hors astreinte).
    
    Args:
        df (pd.DataFrame): DataFrame source
        
    Returns:
        pd.DataFrame: DataFrame préparé pour les équipes PIT
    """
    # Créer l'identifiant unique employé
    df['Gentile'] = (df['Nom'] + ' ' + 
                     df['Prénom'] + ' ' + 
                     df['Equipe (Lib.)'])
    
    # Filtrage par équipe PIT (hors astreinte)
    df_equipe_pit = df[df['Equipe (Lib.)'].isin(CODES_EQUIPES_HORS_ASTREINTE)].copy()
    
    # Corriger le format français (virgule) vers format anglais (point) pour les décimales
    df_equipe_pit['Valeur'] = df_equipe_pit['Valeur'].astype(str).str.replace(',', '.', regex=False)
    
    # Conversion numérique des valeurs
    df_equipe_pit['Valeur'] = pd.to_numeric(df_equipe_pit['Valeur'], errors='coerce')
    
    return df_equipe_pit


def supprimer_doublons(df):
    """
    Supprime les doublons par employé et jour.
    
    Args:
        df (pd.DataFrame): DataFrame source
        
    Returns:
        pd.DataFrame: DataFrame sans doublons
    """
    return df.drop_duplicates(subset=['Gentile', 'Jour'], keep='first').copy() 


def preparer_donnees_3x8(df, df_equipe_pit=None):
    """
    Prépare les données pour l'analyse des équipes en 3x8.
    
    Cette fonction identifie les employés travaillant en 3x8 parmi les équipes PIT
    et les sépare complètement du reste des employés PIT. Cela permet:
    1. D'analyser spécifiquement les employés en 3x8 avec leurs propres statistiques
    2. D'exclure complètement les employés 3x8 des statistiques PIT
    
    Args:
        df (pd.DataFrame): DataFrame source complet
        df_equipe_pit (pd.DataFrame, optional): DataFrame des équipes PIT déjà préparé
        
    Returns:
        pd.DataFrame: DataFrame des employés travaillant en 3x8 (toutes leurs données)
        pd.DataFrame: DataFrame des employés PIT standard (sans les employés 3x8)
    """
    from .calculateurs_3x8 import est_horaire_3x8
    import pandas as pd
    
    # Si df_equipe_pit n'est pas fourni, on le prépare
    if df_equipe_pit is None:
        df_equipe_pit = preparer_donnees_pit(df)
    
    if df_equipe_pit.empty:
        return pd.DataFrame(), df_equipe_pit
    
    # Créer une copie pour éviter de modifier l'original
    df_pit_copy = df_equipe_pit.copy()
    
    # Identifier les lignes qui correspondent à des horaires 3x8
    df_pit_copy['Est_3x8'] = df_pit_copy.apply(est_horaire_3x8, axis=1)
    
    # Identifier les employés qui ont au moins un jour en 3x8
    employes_3x8 = df_pit_copy[df_pit_copy['Est_3x8'] == True]['Gentile'].unique()
    
    # Extraire TOUTES les données des employés qui font du 3x8 (pas seulement les jours 3x8)
    df_employes_3x8 = df_pit_copy[df_pit_copy['Gentile'].isin(employes_3x8)].copy()
    
    # Garder uniquement les employés qui ne font jamais de 3x8
    df_employes_pit_standard = df_pit_copy[~df_pit_copy['Gentile'].isin(employes_3x8)].copy()
    
    # Nettoyer les DataFrames en supprimant la colonne temporaire
    if 'Est_3x8' in df_employes_3x8.columns:
        df_employes_3x8 = df_employes_3x8.drop(columns=['Est_3x8'])
    
    if 'Est_3x8' in df_employes_pit_standard.columns:
        df_employes_pit_standard = df_employes_pit_standard.drop(columns=['Est_3x8'])
    
    return df_employes_3x8, df_employes_pit_standard 