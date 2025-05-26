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
    df_equipe = df[df['Equipe (Lib.)'].isin(CODES_EQUIPES)].copy()
    
    # Corriger le format français (virgule) vers format anglais (point) pour les décimales
    df_equipe['Valeur'] = df_equipe['Valeur'].astype(str).str.replace(',', '.', regex=False)
    
    # Conversion numérique des valeurs
    df_equipe['Valeur'] = pd.to_numeric(df_equipe['Valeur'], errors='coerce')
    
    return df_equipe


def supprimer_doublons(df):
    """
    Supprime les doublons par employé et jour.
    
    Args:
        df (pd.DataFrame): DataFrame source
        
    Returns:
        pd.DataFrame: DataFrame sans doublons
    """
    return df.drop_duplicates(subset=['Gentile', 'Jour'], keep='first').copy() 