"""
Module de calcul des statistiques supplémentaires PMT.
Calcule les heures supplémentaires et les statistiques d'arrêts maladie.
Ajoute ces statistiques comme colonnes aux DataFrames existants.

author : CAPELLE Gabin
"""

import pandas as pd
from config import JOURS_WEEKEND, HORAIRE_DEBUT_REFERENCE, HORAIRE_FIN_REFERENCE
from config import CODES_EQUIPES_ASTREINTE, CODES_EQUIPES_HORS_ASTREINTE
from .data_loader import preparer_donnees_3x8


def enrichir_stats_astreinte_avec_heures_supp(stats_astreinte, df_astreinte_original):
    """
    Enrichit les statistiques d'astreinte avec les heures supplémentaires hors cycle d'astreinte.

    Args:
        stats_astreinte: DataFrame des statistiques d'astreinte existantes
        df_astreinte_original: DataFrame original des données d'astreinte

    Returns:
        pd.DataFrame: DataFrame enrichi avec les colonnes d'heures supplémentaires
    """
    if stats_astreinte.empty or df_astreinte_original.empty:
        # Ajouter des colonnes vides si pas de données
        stats_astreinte['Total_Heures_Supp_Hors_Astreinte'] = 0.0
        stats_astreinte['Nb_Jours_Heures_Supp_Hors_Astreinte'] = 0
        stats_astreinte['Moy_Heures_Supp_Par_Jour_Hors_Astreinte'] = 0.0
        return stats_astreinte

    # Calculer les heures supplémentaires hors astreinte
    stats_hs = calculer_heures_supplementaires_hors_astreinte(df_astreinte_original)

    if stats_hs.empty:
        # Ajouter des colonnes vides si pas de données
        stats_astreinte['Total_Heures_Supp_Hors_Astreinte'] = 0.0
        stats_astreinte['Nb_Jours_Heures_Supp_Hors_Astreinte'] = 0
        stats_astreinte['Moy_Heures_Supp_Par_Jour_Hors_Astreinte'] = 0.0
        return stats_astreinte

    # Fusionner avec les statistiques existantes en utilisant Gentile
    stats_enrichi = pd.merge(
        stats_astreinte,
        stats_hs[['Gentile', 'Total_Heures_Supplementaires', 'Nb_Jours_Heures_Supplementaires', 'Moyenne_Heures_Supp_Par_Jour']],
        on='Gentile',
        how='left'
    )

    # Renommer les colonnes pour éviter la confusion
    stats_enrichi = stats_enrichi.rename(columns={
        'Total_Heures_Supplementaires': 'Total_Heures_Supp_Hors_Astreinte',
        'Nb_Jours_Heures_Supplementaires': 'Nb_Jours_Heures_Supp_Hors_Astreinte',
        'Moyenne_Heures_Supp_Par_Jour': 'Moy_Heures_Supp_Par_Jour_Hors_Astreinte'
    })

    # Remplir les valeurs manquantes avec 0
    stats_enrichi['Total_Heures_Supp_Hors_Astreinte'] = stats_enrichi['Total_Heures_Supp_Hors_Astreinte'].fillna(0.0)
    stats_enrichi['Nb_Jours_Heures_Supp_Hors_Astreinte'] = stats_enrichi['Nb_Jours_Heures_Supp_Hors_Astreinte'].fillna(0)
    stats_enrichi['Moy_Heures_Supp_Par_Jour_Hors_Astreinte'] = stats_enrichi['Moy_Heures_Supp_Par_Jour_Hors_Astreinte'].fillna(0.0)

    return stats_enrichi


def enrichir_stats_3x8_avec_heures_supp_service_continu(stats_3x8, df_3x8_original):
    """
    Enrichit les statistiques 3x8 avec les heures supplémentaires pendant le service continu.

    Args:
        stats_3x8: DataFrame des statistiques 3x8 existantes
        df_3x8_original: DataFrame original des données 3x8

    Returns:
        pd.DataFrame: DataFrame enrichi avec les colonnes d'heures supplémentaires service continu
    """
    if stats_3x8.empty or df_3x8_original.empty:
        # Ajouter des colonnes vides si pas de données
        stats_3x8['Total_Heures_Supp_Service_Continu'] = 0.0
        stats_3x8['Nb_Jours_Service_Continu_Heures_Supp'] = 0
        stats_3x8['Total_Jours_Service_Continu'] = 0
        stats_3x8['Moy_Heures_Supp_Service_Continu'] = 0.0
        return stats_3x8

    # Calculer les heures supplémentaires en service continu
    stats_hs_3x8 = calculer_heures_supplementaires_3x8_service_continu(df_3x8_original)

    if stats_hs_3x8.empty:
        # Ajouter des colonnes vides si pas de données
        stats_3x8['Total_Heures_Supp_Service_Continu'] = 0.0
        stats_3x8['Nb_Jours_Service_Continu_Heures_Supp'] = 0
        stats_3x8['Total_Jours_Service_Continu'] = 0
        stats_3x8['Moy_Heures_Supp_Service_Continu'] = 0.0
        return stats_3x8

    # Fusionner avec les statistiques existantes
    stats_enrichi = pd.merge(
        stats_3x8,
        stats_hs_3x8[['Gentile', 'Total_Heures_Supp_Service_Continu', 'Nb_Jours_Service_Continu_Heures_Supp',
                      'Total_Jours_Service_Continu', 'Moyenne_Heures_Supp_Service_Continu']],
        on='Gentile',
        how='left'
    )

    # Renommer la colonne moyenne pour cohérence
    stats_enrichi = stats_enrichi.rename(columns={
        'Moyenne_Heures_Supp_Service_Continu': 'Moy_Heures_Supp_Service_Continu'
    })

    # Remplir les valeurs manquantes avec 0
    stats_enrichi['Total_Heures_Supp_Service_Continu'] = stats_enrichi['Total_Heures_Supp_Service_Continu'].fillna(0.0)
    stats_enrichi['Nb_Jours_Service_Continu_Heures_Supp'] = stats_enrichi['Nb_Jours_Service_Continu_Heures_Supp'].fillna(0)
    stats_enrichi['Total_Jours_Service_Continu'] = stats_enrichi['Total_Jours_Service_Continu'].fillna(0)
    stats_enrichi['Moy_Heures_Supp_Service_Continu'] = stats_enrichi['Moy_Heures_Supp_Service_Continu'].fillna(0.0)

    return stats_enrichi


def enrichir_stats_avec_arrets_maladie(stats_df, df_original, gentile_col='Gentile'):
    """
    Enrichit un DataFrame de statistiques avec les données d'arrêts maladie simplifiées.
    Ajoute 4 colonnes :
    - Nombre de périodes d'arrêts (tous codes confondus)
    - Nombre de jours d'arrêts code 41
    - Nombre de jours d'arrêts code 5H
    - Moyenne d'heures par jour d'arrêt

    Args:
        stats_df: DataFrame des statistiques existantes
        df_original: DataFrame original contenant les données
        gentile_col: Nom de la colonne d'identifiant unique

    Returns:
        pd.DataFrame: DataFrame enrichi avec les colonnes d'arrêts maladie
    """
    if stats_df.empty or df_original.empty:
        # Ajouter les colonnes vides si pas de données
        stats_df['Nb_Périodes_Arrêts'] = 0
        stats_df['Nb_Jours_Arrêts_41'] = 0
        stats_df['Nb_Jours_Arrêts_5H'] = 0
        stats_df['Moy_Heures_Par_Arrêt_Maladie'] = 0.0
        return stats_df

    # Calculer les statistiques d'arrêts maladie simplifiées
    stats_maladie = calculer_statistiques_arrets_maladie_simplifiees(df_original)

    if stats_maladie.empty:
        # Ajouter les colonnes vides si pas de données
        stats_df['Nb_Périodes_Arrêts'] = 0
        stats_df['Nb_Jours_Arrêts_41'] = 0
        stats_df['Nb_Jours_Arrêts_5H'] = 0
        stats_df['Moy_Heures_Par_Arrêt_Maladie'] = 0.0
        return stats_df

    # Fusionner avec les statistiques existantes
    stats_enrichi = pd.merge(
        stats_df,
        stats_maladie[['Gentile', 'Nb_Périodes_Arrêts', 'Nb_Jours_Arrêts_41', 'Nb_Jours_Arrêts_5H', 'Moy_Heures_Par_Arrêt_Maladie']],
        on=gentile_col,
        how='left'
    )

    # Remplir les valeurs manquantes avec 0
    stats_enrichi['Nb_Périodes_Arrêts'] = stats_enrichi['Nb_Périodes_Arrêts'].fillna(0).astype(int)
    stats_enrichi['Nb_Jours_Arrêts_41'] = stats_enrichi['Nb_Jours_Arrêts_41'].fillna(0).astype(int)
    stats_enrichi['Nb_Jours_Arrêts_5H'] = stats_enrichi['Nb_Jours_Arrêts_5H'].fillna(0).astype(int)
    stats_enrichi['Moy_Heures_Par_Arrêt_Maladie'] = stats_enrichi['Moy_Heures_Par_Arrêt_Maladie'].fillna(0.0)

    return stats_enrichi


def enrichir_moyennes_avec_nouvelles_stats(moyennes_df, stats_enrichi_df):
    """
    Enrichit les moyennes par équipe avec les nouvelles statistiques.

    Args:
        moyennes_df: DataFrame des moyennes par équipe existantes
        stats_enrichi_df: DataFrame des statistiques enrichies par employé

    Returns:
        pd.DataFrame: DataFrame des moyennes enrichi
    """
    if moyennes_df.empty or stats_enrichi_df.empty:
        return moyennes_df

    # Identifier les nouvelles colonnes numériques à moyenner
    nouvelles_colonnes = []
    colonnes_possibles = [
        'Heures_Supp',
        'Nb_Périodes_Arrêts', 'Nb_Jours_Arrêts_41', 'Nb_Jours_Arrêts_5H',
        'Moy_Heures_Par_Arrêt_Maladie'
    ]

    for col in colonnes_possibles:
        if col in stats_enrichi_df.columns:
            nouvelles_colonnes.append(col)

    if not nouvelles_colonnes:
        return moyennes_df

    # Calculer les nouvelles moyennes par équipe
    nouvelles_moyennes = stats_enrichi_df.groupby('Équipe')[nouvelles_colonnes].mean().reset_index()

    # Renommer les colonnes avec le préfixe Moy_ (sauf celles qui l'ont déjà)
    colonnes_rename = {}
    for col in nouvelles_colonnes:
        if not col.startswith('Moy_') and not col.startswith('Moyenne_'):
            colonnes_rename[col] = f'Moy_{col}'

    if colonnes_rename:
        nouvelles_moyennes = nouvelles_moyennes.rename(columns=colonnes_rename)

    # Fusionner avec les moyennes existantes
    moyennes_enrichi = pd.merge(moyennes_df, nouvelles_moyennes, on='Équipe', how='left')

    # Arrondir les nouvelles colonnes
    for col in nouvelles_moyennes.columns:
        if col != 'Équipe' and col in moyennes_enrichi.columns:
            if 'Nb_' in col:
                moyennes_enrichi[col] = moyennes_enrichi[col].fillna(0).round(1)
            else:
                moyennes_enrichi[col] = moyennes_enrichi[col].fillna(0.0).round(2)

    return moyennes_enrichi


def enrichir_stats_avec_heures_supplementaires_hors_astreinte(stats_df, df_original, gentile_col='Gentile'):
    """
    Enrichit un DataFrame de statistiques avec les heures supplémentaires hors astreinte.
    Calcule les heures supplémentaires en excluant les jours marqués "I" dans la colonne Astreinte.

    Args:
        stats_df: DataFrame des statistiques existantes
        df_original: DataFrame original contenant les données
        gentile_col: Nom de la colonne d'identifiant unique

    Returns:
        pd.DataFrame: DataFrame enrichi avec la colonne d'heures supplémentaires
    """
    if stats_df.empty or df_original.empty:
        # Ajouter la colonne vide si pas de données
        stats_df['Heures_Supp'] = 0.0
        return stats_df

    # Calculer les heures supplémentaires hors astreinte
    stats_hs = calculer_heures_supplementaires_hors_astreinte_tous_employes(df_original)

    if stats_hs.empty:
        # Ajouter la colonne vide si pas de données
        stats_df['Heures_Supp'] = 0.0
        return stats_df

    # Fusionner avec les statistiques existantes
    stats_enrichi = pd.merge(
        stats_df,
        stats_hs[['Gentile', 'Heures_Supp']],
        on=gentile_col,
        how='left'
    )

    # Remplir les valeurs manquantes avec 0
    stats_enrichi['Heures_Supp'] = stats_enrichi['Heures_Supp'].fillna(0.0)

    return stats_enrichi


def calculer_heures_supplementaires_hors_astreinte_tous_employes(df):
    """
    Calcule les heures supplémentaires hors astreinte pour tous les employés.
    Exclut EXPLICITEMENT les jours où la colonne Astreinte contient "I".
    Les heures supplémentaires sont identifiées par des heures travaillées > 8h par jour
    ou des codes spécifiques d'heures supplémentaires.

    Args:
        df: DataFrame contenant toutes les données

    Returns:
        pd.DataFrame: DataFrame avec les heures supplémentaires par employé
    """
    if df.empty:
        return pd.DataFrame()

    # Copie du DataFrame pour éviter les modifications
    df_hs = df.copy()

    # Exclure les jours d'astreinte (on veut les heures supplémentaires HORS astreinte)
    # IMPORTANT: Cette étape garantit que tous les jours avec "I" dans la colonne Astreinte sont exclus
    if 'Astreinte' in df_hs.columns:
        df_hs = df_hs[df_hs['Astreinte'] != 'I'].copy()

    if df_hs.empty:
        return pd.DataFrame()

    # Exclure les lignes avec des codes spécifiques d'heures supplémentaires
    # On ne veut pas compter ces codes, mais calculer les heures supplémentaires à partir des horaires
    codes_heures_supp = ['HS', 'HSN', 'HSJ', 'HSUP', 'H.SUP']
    if 'Code' in df_hs.columns:
        # Créer un masque pour filtrer les codes d'heures supplémentaires
        mask_code_hs = df_hs['Code'].apply(
            lambda x: not any(code_hs in str(x).strip().upper() for code_hs in codes_heures_supp)
            if pd.notna(x) else True
        )
        df_hs = df_hs[mask_code_hs].copy()

    if df_hs.empty:
        return pd.DataFrame()

    # Calculer les heures supplémentaires par ligne
    df_hs['Heures_Supplementaires'] = df_hs.apply(_calculer_heures_supp_ligne, axis=1)

    # Calculer les statistiques par employé
    stats_hs = df_hs.groupby(['Gentile', 'Equipe (Lib.)', 'Nom', 'Prénom']).agg(
        Heures_Supp=('Heures_Supplementaires', 'sum')
    ).reset_index()

    # Renommer les colonnes
    stats_hs = stats_hs.rename(columns={
        'Equipe (Lib.)': 'Équipe'
    })

    # Arrondir les valeurs
    stats_hs['Heures_Supp'] = stats_hs['Heures_Supp'].round(2)

    return stats_hs


def calculer_heures_supplementaires_hors_astreinte(df_astreinte):
    """
    Calcule les heures supplémentaires hors cycle d'astreinte.
    Les heures supplémentaires sont identifiées par des heures travaillées en dehors de la plage horaire normale.
    Exclut explicitement les jours d'astreinte (marqués "I") et les codes spécifiques d'heures supplémentaires.

    Args:
        df_astreinte: DataFrame contenant les données d'astreinte

    Returns:
        pd.DataFrame: DataFrame avec les statistiques d'heures supplémentaires par employé
    """
    if df_astreinte.empty:
        return pd.DataFrame()

    # Copie du DataFrame pour éviter les modifications
    df_hs = df_astreinte.copy()

    # Filtrer les jours de weekend et jours fériés
    if 'Désignation jour' in df_hs.columns:
        df_hs = df_hs[~df_hs['Désignation jour'].isin(JOURS_WEEKEND)].copy()

    if 'Jour férié' in df_hs.columns:
        df_hs = df_hs[df_hs['Jour férié'] != 'X'].copy()

    # Exclure les jours d'astreinte (on veut les heures supplémentaires HORS astreinte)
    if 'Astreinte' in df_hs.columns:
        df_hs = df_hs[df_hs['Astreinte'] != 'I'].copy()

    if df_hs.empty:
        return pd.DataFrame()

    # Exclure les lignes avec des codes spécifiques d'heures supplémentaires
    # On ne veut pas compter ces codes, mais calculer les heures supplémentaires à partir des horaires
    codes_heures_supp = ['HS', 'HSN', 'HSJ', 'HSUP', 'H.SUP']
    if 'Code' in df_hs.columns:
        # Créer un masque pour filtrer les codes d'heures supplémentaires
        mask_code_hs = df_hs['Code'].apply(
            lambda x: not any(code_hs in str(x).strip().upper() for code_hs in codes_heures_supp)
            if pd.notna(x) else True
        )
        df_hs = df_hs[mask_code_hs].copy()

    if df_hs.empty:
        return pd.DataFrame()

    # Calculer les heures supplémentaires par ligne
    df_hs['Heures_Supplementaires'] = df_hs.apply(_calculer_heures_supp_ligne, axis=1)

    # Calculer les statistiques par employé
    stats_hs = df_hs.groupby(['Gentile', 'Equipe (Lib.)', 'Nom', 'Prénom']).agg(
        Total_Heures_Supplementaires=('Heures_Supplementaires', 'sum'),
        Nb_Jours_Heures_Supplementaires=('Heures_Supplementaires', lambda x: sum(x > 0)),
        Moyenne_Heures_Supp_Par_Jour=('Heures_Supplementaires', lambda x: x[x > 0].mean() if sum(x > 0) > 0 else 0)
    ).reset_index()

    # Renommer les colonnes
    stats_hs = stats_hs.rename(columns={
        'Equipe (Lib.)': 'Équipe'
    })

    # Arrondir les valeurs
    stats_hs['Total_Heures_Supplementaires'] = stats_hs['Total_Heures_Supplementaires'].round(2)
    stats_hs['Moyenne_Heures_Supp_Par_Jour'] = stats_hs['Moyenne_Heures_Supp_Par_Jour'].round(2)

    return stats_hs


def calculer_heures_supplementaires_3x8_service_continu(df_3x8):
    """
    Calcule les heures supplémentaires des employés 3x8 pendant le service continu.
    Le service continu inclut les weekends et jours fériés.
    Exclut les codes spécifiques d'heures supplémentaires.

    Args:
        df_3x8: DataFrame contenant les données des employés 3x8

    Returns:
        pd.DataFrame: DataFrame avec les statistiques d'heures supplémentaires 3x8
    """
    if df_3x8.empty:
        return pd.DataFrame()

    # Copie du DataFrame
    df_hs_3x8 = df_3x8.copy()

    # Exclure les lignes avec des codes spécifiques d'heures supplémentaires
    # On ne veut pas compter ces codes, mais calculer les heures supplémentaires à partir des horaires
    codes_heures_supp = ['HS', 'HSN', 'HSJ', 'HSUP', 'H.SUP']
    if 'Code' in df_hs_3x8.columns:
        # Créer un masque pour filtrer les codes d'heures supplémentaires
        mask_code_hs = df_hs_3x8['Code'].apply(
            lambda x: not any(code_hs in str(x).strip().upper() for code_hs in codes_heures_supp)
            if pd.notna(x) else True
        )
        df_hs_3x8 = df_hs_3x8[mask_code_hs].copy()

    if df_hs_3x8.empty:
        return pd.DataFrame()

    # Pour le service continu, on garde TOUS les jours (y compris weekends et fériés)
    # mais on se concentre sur les heures supplémentaires

    # Calculer les heures supplémentaires par ligne
    df_hs_3x8['Heures_Supplementaires'] = df_hs_3x8.apply(_calculer_heures_supp_ligne, axis=1)

    # Identifier les jours de service continu (weekends + jours fériés)
    df_hs_3x8['Est_Service_Continu'] = False

    if 'Désignation jour' in df_hs_3x8.columns:
        df_hs_3x8['Est_Service_Continu'] |= df_hs_3x8['Désignation jour'].isin(JOURS_WEEKEND)

    if 'Jour férié' in df_hs_3x8.columns:
        df_hs_3x8['Est_Service_Continu'] |= (df_hs_3x8['Jour férié'] == 'X')

    # Filtrer uniquement les jours de service continu
    df_service_continu = df_hs_3x8[df_hs_3x8['Est_Service_Continu']].copy()

    if df_service_continu.empty:
        return pd.DataFrame()

    # Calculer les statistiques par employé pour le service continu
    stats_hs_3x8 = df_service_continu.groupby(['Gentile', 'Equipe (Lib.)', 'Nom', 'Prénom']).agg(
        Total_Heures_Supp_Service_Continu=('Heures_Supplementaires', 'sum'),
        Nb_Jours_Service_Continu_Heures_Supp=('Heures_Supplementaires', lambda x: sum(x > 0)),
        Total_Jours_Service_Continu=('Est_Service_Continu', 'sum'),
        Moyenne_Heures_Supp_Service_Continu=('Heures_Supplementaires', lambda x: x[x > 0].mean() if sum(x > 0) > 0 else 0)
    ).reset_index()

    # Renommer les colonnes
    stats_hs_3x8 = stats_hs_3x8.rename(columns={
        'Equipe (Lib.)': 'Équipe'
    })

    # Arrondir les valeurs
    stats_hs_3x8['Total_Heures_Supp_Service_Continu'] = stats_hs_3x8['Total_Heures_Supp_Service_Continu'].round(2)
    stats_hs_3x8['Moyenne_Heures_Supp_Service_Continu'] = stats_hs_3x8['Moyenne_Heures_Supp_Service_Continu'].round(2)

    return stats_hs_3x8


def calculer_statistiques_arrets_maladie_simplifiees(df):
    """
    Calcule les statistiques d'arrêts maladie simplifiées :
    - Nombre de périodes d'arrêts (tous codes confondus)
    - Nombre de jours d'arrêts code 41
    - Nombre de jours d'arrêts code 5H
    - Moyenne d'heures par jour d'arrêt (tous codes confondus)

    Une période d'arrêt est une séquence continue de jours d'arrêt, peu importe le code.

    Args:
        df: DataFrame contenant toutes les données

    Returns:
        pd.DataFrame: Statistiques par employé avec 4 colonnes
    """
    if df.empty:
        return pd.DataFrame()

    # Filtrer les lignes avec les codes de maladie
    df_maladie = df[df['Code'].isin(['41', '5H'])].copy()

    if df_maladie.empty:
        return pd.DataFrame()

    # Calculer les heures d'absence par ligne
    df_maladie['Heures_Absence'] = df_maladie.apply(_calculer_heures_absence_ligne, axis=1)

    # Trier par employé et date
    df_maladie = df_maladie.sort_values(['Gentile', 'Jour'])

    # Calculer les statistiques par employé
    stats_par_employe = []

    for gentile in df_maladie['Gentile'].unique():
        df_employe = df_maladie[df_maladie['Gentile'] == gentile].copy()

        # Compter les jours d'arrêts par code
        nb_jours_41 = len(df_employe[df_employe['Code'] == '41'])
        nb_jours_5h = len(df_employe[df_employe['Code'] == '5H'])

        # Calculer le nombre de périodes d'arrêts (séquences continues)
        df_employe['Jour_Date'] = pd.to_datetime(df_employe['Jour'], format='%d/%m/%Y', errors='coerce')
        df_employe = df_employe.sort_values('Jour_Date')

        # Créer un groupe pour chaque période continue
        df_employe['diff_jours'] = df_employe['Jour_Date'].diff().dt.days
        # Une nouvelle période commence quand la différence de jours est > 1 (plus d'un jour d'écart)
        df_employe['nouvelle_periode'] = (df_employe['diff_jours'] > 1) | pd.isna(df_employe['diff_jours'])
        df_employe['id_periode'] = df_employe['nouvelle_periode'].cumsum()

        # Compter le nombre de périodes uniques
        nb_periodes = df_employe['id_periode'].nunique()

        # Calculer la moyenne d'heures par jour d'arrêt (tous codes confondus)
        total_heures = df_employe['Heures_Absence'].sum()
        total_jours = len(df_employe)
        moy_heures_par_arret = total_heures / total_jours if total_jours > 0 else 0.0

        # Récupérer les infos de l'employé
        info_employe = df_employe.iloc[0]

        stats_par_employe.append({
            'Gentile': gentile,
            'Équipe': info_employe['Equipe (Lib.)'],
            'Nom': info_employe['Nom'],
            'Prénom': info_employe['Prénom'],
            'Nb_Périodes_Arrêts': nb_periodes,
            'Nb_Jours_Arrêts_41': nb_jours_41,
            'Nb_Jours_Arrêts_5H': nb_jours_5h,
            'Moy_Heures_Par_Arrêt_Maladie': round(moy_heures_par_arret, 2)
        })

    return pd.DataFrame(stats_par_employe)


def _calculer_heures_supp_ligne(row):
    """
    Calcule les heures supplémentaires pour une ligne donnée.

    NOUVEAU: Les heures supplémentaires sont identifiées par le code 'D' dans la colonne 'Code'.
    La valeur est récupérée dans la colonne 'Valeur' et l'unité dans 'Dés. unité'.

    Args:
        row: Ligne du DataFrame

    Returns:
        float: Nombre d'heures supplémentaires
    """
    try:
        # IMPORTANT: Ne pas compter les heures supplémentaires pour les jours d'astreinte
        if 'Astreinte' in row and pd.notna(row['Astreinte']) and row['Astreinte'] == 'I':
            return 0.0

        # Vérifier s'il y a un code spécifique d'heures supplémentaires
        code = str(row.get('Code', '')).strip().upper() if pd.notna(row.get('Code', '')) else ''

        # NOUVEAU: Si le code est 'D', on a des heures supplémentaires
        if code == 'D':
            # Récupérer la valeur dans la colonne 'Valeur'
            if pd.notna(row.get('Valeur', '')) and row.get('Valeur', '') != '':
                valeur = float(row.get('Valeur', 0))

                # Vérifier l'unité dans la colonne "Dés. unité"
                unite = str(row.get('Dés. unité', '')).strip().lower() if pd.notna(row.get('Dés. unité', '')) else ''

                if 'jour' in unite:
                    # Si l'unité est en jours, convertir en heures (1 jour = 8 heures)
                    return valeur * 8.0
                elif 'heure' in unite:
                    # Si l'unité est en heures, utiliser directement la valeur
                    return valeur
                else:
                    # Si pas d'unité spécifiée, considérer comme des heures
                    return valeur

            return 0.0  # Pas de valeur, donc pas d'heures supplémentaires

        # Si ce n'est pas un code 'D', renvoyer 0 heures supplémentaires
        return 0.0

    except (ValueError, TypeError, AttributeError, KeyError):
        # En cas d'erreur, retourner 0
        return 0.0


def _calculer_heures_travaillees_ligne(row):
    """
    Calcule les heures travaillées pour une ligne (similaire au module calculateurs.py).

    Args:
        row: Ligne du DataFrame

    Returns:
        float: Nombre d'heures travaillées
    """
    try:
        # Si on a un code (absence ou autre)
        if pd.notna(row.get('Code', '')) and row.get('Code', '') not in ['', ' ']:
            # Cas spécial : code "80TH" = 8 heures travaillées
            if str(row.get('Code', '')).strip().upper() == '80TH':
                return 8.0

            # Si on a une valeur numérique avec le code
            if pd.notna(row.get('Valeur', '')) and row.get('Valeur', '') != '':
                valeur = float(row.get('Valeur', 0))
                if valeur >= 0:
                    # Vérifier l'unité dans la colonne "Dés. unité"
                    unite = str(row.get('Dés. unité', '')).strip().lower() if pd.notna(row.get('Dés. unité', '')) else ''

                    if 'jour' in unite:
                        # Si l'unité est en jours : valeur = nombre de jours travaillés
                        heures_travaillees = valeur * 8.0
                        return min(8.0, heures_travaillees)  # Maximum 8 heures par jour
                    elif 'heure' in unite:
                        # Si l'unité est en heures : valeur = nombre d'heures travaillées
                        return min(8.0, valeur)  # Maximum 8 heures par jour
                    else:
                        # Si pas d'unité : valeur = nombre d'heures d'absence (ancien comportement)
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


def _calculer_heures_absence_ligne(row):
    """
    Calcule les heures d'absence pour une ligne donnée.

    Args:
        row: Ligne du DataFrame

    Returns:
        float: Nombre d'heures d'absence
    """
    try:
        # Si on a une valeur numérique
        if pd.notna(row.get('Valeur', '')) and row.get('Valeur', '') != '':
            valeur = float(row.get('Valeur', 0))
            if valeur >= 0:
                # Vérifier l'unité dans la colonne "Dés. unité"
                unite = str(row.get('Dés. unité', '')).strip().lower() if pd.notna(row.get('Dés. unité', '')) else ''

                if 'jour' in unite:
                    # Si l'unité est en jours : valeur = nombre de jours d'absence
                    return valeur * 8.0  # Conversion en heures
                elif 'heure' in unite:
                    # Si l'unité est en heures : valeur = nombre d'heures d'absence
                    return valeur
                else:
                    # Si pas d'unité : considérer comme des heures d'absence
                    return valeur
            else:
                return 8.0  # Valeur négative = journée complète d'absence
        else:
            # Code d'absence sans valeur = 8h d'absence
            return 8.0
    except (ValueError, TypeError):
        # Si conversion impossible, considérer comme journée complète d'absence
        return 8.0


def calculer_statistiques_arrets_maladie_tous_employes(df):
    """
    Calcule les statistiques d'arrêts maladie pour AUTRES (employés n'étant ni ASTREINTE, ni TIP, ni 3x8).
    Inclut également les heures supplémentaires pour ces employés.
    """
    try:
        if df.empty:
            return pd.DataFrame()

        # Exclure les équipes ASTREINTE et TIP
        df_autres = df[
            (~df['Equipe (Lib.)'].isin(CODES_EQUIPES_ASTREINTE)) &
            (~df['Equipe (Lib.)'].isin(CODES_EQUIPES_HORS_ASTREINTE))
        ].copy()

        # Exclure les employés 3x8 (tous leurs jours)
        # On identifie les Gentile des 3x8 à partir de preparer_donnees_3x8
        _, df_3x8 = preparer_donnees_3x8(df)
        gentiles_3x8 = df_3x8['Gentile'].unique() if not df_3x8.empty else []
        df_autres = df_autres[~df_autres['Gentile'].isin(gentiles_3x8)].copy()

        # On continue le calcul sur df_autres
        if df_autres.empty:
            return pd.DataFrame()
        return _calculer_statistiques_arrets_maladie_tous_employes_core(df_autres)
    except Exception as e:
        print(f"Erreur lors du calcul des arrêts maladie AUTRES: {str(e)}")
        if df is not None:
            print(f"Colonnes disponibles: {df.columns.tolist()}")
        return pd.DataFrame()


def _calculer_statistiques_arrets_maladie_tous_employes_core(df):
    try:
        # Vérifier les colonnes nécessaires
        for colonne in ['Code', 'Jour']:
            if colonne not in df.columns:
                print(f"Colonne manquante pour le calcul des arrêts maladie: '{colonne}'")
                return pd.DataFrame()

        # Vérifier si la colonne Gentile existe, sinon utiliser un identifiant alternatif
        id_col = 'Gentile'
        if id_col not in df.columns:
            # Essayer d'utiliser une combinaison Nom+Prénom comme identifiant unique
            if 'Nom' in df.columns and 'Prénom' in df.columns:
                print("Création d'un identifiant unique à partir de Nom et Prénom")
                df['Gentile'] = df['Nom'] + '_' + df['Prénom']
                id_col = 'Gentile'
            else:
                print("Colonnes Nom et/ou Prénom manquantes")
                return pd.DataFrame()

        # Filtrer les lignes avec les codes de maladie
        df_maladie = df[df['Code'].isin(['41', '5H'])].copy()

        # Calculer les heures supplémentaires pour tous les employés
        stats_hs = calculer_heures_supplementaires_hors_astreinte_tous_employes(df)

        # Initialiser le DataFrame final
        stats_par_employe = []

        # Calculer les heures d'absence pour les lignes de maladie
        if not df_maladie.empty:
            df_maladie['Heures_Absence'] = df_maladie.apply(_calculer_heures_absence_ligne, axis=1)

        # Calculer les statistiques par employé pour les arrêts maladie
        for gentile in df_maladie[id_col].unique():
            df_employe = df_maladie[df_maladie[id_col] == gentile].copy()

            # Compter les jours d'arrêts par code
            nb_jours_41 = len(df_employe[df_employe['Code'] == '41'])
            nb_jours_5h = len(df_employe[df_employe['Code'] == '5H'])

            # Calculer le nombre de périodes d'arrêts (séquences continues)
            df_employe['Jour_Date'] = pd.to_datetime(df_employe['Jour'], format='%d/%m/%Y', errors='coerce')
            df_employe = df_employe.sort_values('Jour_Date')

            # Créer un groupe pour chaque période continue
            df_employe['diff_jours'] = df_employe['Jour_Date'].diff().dt.days
            # Une nouvelle période commence quand la différence de jours est > 1 (plus d'un jour d'écart)
            df_employe['nouvelle_periode'] = (df_employe['diff_jours'] > 1) | pd.isna(df_employe['diff_jours'])
            df_employe['id_periode'] = df_employe['nouvelle_periode'].cumsum()

            # Compter le nombre de périodes uniques
            nb_periodes = df_employe['id_periode'].nunique()

            # Calculer la moyenne d'heures par jour d'arrêt (tous codes confondus)
            total_heures = df_employe['Heures_Absence'].sum()
            total_jours = len(df_employe)
            moy_heures_par_arret = total_heures / total_jours if total_jours > 0 else 0.0

            # Récupérer les infos de l'employé
            info_employe = df_employe.iloc[0]

            # Récupérer les heures supplémentaires si disponibles
            heures_supp = 0.0
            if not stats_hs.empty:
                # Trouver la ligne correspondant à cet employé dans stats_hs
                employe_hs = stats_hs[stats_hs[id_col] == gentile]
                if not employe_hs.empty:
                    heures_supp = employe_hs.iloc[0]['Heures_Supp']

            # NOUVEAU: Récupérer la Direction Régionale (UM (Lib))
            dr = info_employe.get('UM (Lib)', '') if 'UM (Lib)' in info_employe else ''

            stats_par_employe.append({
                'Nom': info_employe.get('Nom', 'Inconnu'),
                'Prénom': info_employe.get('Prénom', 'Inconnu'),
                'Équipe': info_employe.get('Equipe (Lib.)', 'Non spécifiée'),
                'UM (Lib)': dr,  # NOUVEAU: Ajout de la colonne Direction Régionale
                'Nb_Périodes_Arrêts': nb_periodes,
                'Nb_Jours_Arrêts_41': nb_jours_41,
                'Nb_Jours_Arrêts_5H': nb_jours_5h,
                'Moy_Heures_Par_Arrêt_Maladie': round(moy_heures_par_arret, 2),
                'Heures_Supp': heures_supp
            })

        # Ajouter les employés qui ont des heures supplémentaires mais pas d'arrêts maladie
        if not stats_hs.empty:
            for index, row in stats_hs.iterrows():
                gentile = row[id_col]
                # Vérifier si cet employé n'est pas déjà dans le DataFrame final
                if not any(emp.get(id_col) == gentile for emp in stats_par_employe if id_col in emp):
                    # NOUVEAU: Récupérer la Direction Régionale (UM (Lib)) pour les employés sans arrêts maladie
                    dr = ''
                    employe_rows = df[df[id_col] == gentile]
                    if not employe_rows.empty and 'UM (Lib)' in employe_rows.columns:
                        dr_values = employe_rows['UM (Lib)'].dropna().unique()
                        if len(dr_values) > 0:
                            dr = dr_values[0]

                    stats_par_employe.append({
                        'Nom': row['Nom'],
                        'Prénom': row['Prénom'],
                        'Équipe': row['Équipe'],
                        'UM (Lib)': dr,  # NOUVEAU: Ajout de la colonne Direction Régionale
                        'Nb_Périodes_Arrêts': 0,
                        'Nb_Jours_Arrêts_41': 0,
                        'Nb_Jours_Arrêts_5H': 0,
                        'Moy_Heures_Par_Arrêt_Maladie': 0.0,
                        'Heures_Supp': row['Heures_Supp']
                    })

        return pd.DataFrame(stats_par_employe)
    except Exception as e:
        print(f"Erreur lors du calcul des arrêts maladie et heures supplémentaires: {str(e)}")
        if df is not None:
            print(f"Colonnes disponibles: {df.columns.tolist()}")
        return pd.DataFrame()
