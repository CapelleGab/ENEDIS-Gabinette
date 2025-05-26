"""
Module de chargement et préparation des données PMT.

author : CAPELLE Gabin
"""

import pandas as pd
from config import *


def charger_donnees_csv():
    """
    Charge les données depuis le fichier CSV.
    
    Returns:
        pd.DataFrame: DataFrame avec les données chargées ou None en cas d'erreur
    """
    try:
        df = pd.read_csv(FICHIER_CSV, encoding=CSV_ENCODING, sep=CSV_SEPARATOR, low_memory=False)
        # print(f"Données chargées : {len(df)} lignes, {len(df.columns)} colonnes")
        return df
    except Exception as e:
        print(f"ERREUR lors du chargement du fichier CSV : {e}")
        return None


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