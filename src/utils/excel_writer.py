"""
Module de sauvegarde et formatage Excel PMT.

author : CAPELLE Gabin
"""

import pandas as pd
from config import FICHIER_EXCEL, NOMS_FEUILLES


def sauvegarder_excel(stats_final, moyennes_equipe, fichier_path=None, stats_tip=None, moyennes_tip=None, stats_3x8=None, moyennes_3x8=None, arrets_maladie_tous=None):
    """
    Sauvegarde les données dans un fichier Excel.
    
    Args:
        stats_final (pd.DataFrame): Statistiques par employé (astreinte)
        moyennes_equipe (pd.DataFrame): Moyennes par équipe (astreinte)
        fichier_path (str, optional): Chemin du fichier Excel. Si None, utilise FICHIER_EXCEL de config.
        stats_tip (pd.DataFrame, optional): Statistiques par employé TIP (hors astreinte)
        moyennes_tip (pd.DataFrame, optional): Moyennes par équipe TIP (hors astreinte)
        stats_3x8 (pd.DataFrame, optional): Statistiques par employé 3x8
        moyennes_3x8 (pd.DataFrame, optional): Moyennes par équipe 3x8
        arrets_maladie_tous (pd.DataFrame, optional): Statistiques d'arrêts maladie et heures supplémentaires pour tous les employés
    """
    # Utiliser le chemin fourni ou celui de la config par défaut
    excel_path = fichier_path if fichier_path is not None else FICHIER_EXCEL
    
    # print(f"\nSauvegarde dans {excel_path}...")
    with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
        # Feuilles pour les équipes d'astreinte
        stats_final.to_excel(writer, sheet_name=NOMS_FEUILLES['statistiques'], index=False)
        moyennes_equipe.to_excel(writer, sheet_name=NOMS_FEUILLES['moyennes'], index=False)
        
        # Feuilles pour les équipes TIP (hors astreinte) si les données sont fournies
        if stats_tip is not None and moyennes_tip is not None:
            stats_tip.to_excel(writer, sheet_name=NOMS_FEUILLES['tip_statistiques'], index=False)
            moyennes_tip.to_excel(writer, sheet_name=NOMS_FEUILLES['tip_moyennes'], index=False) 
        
        # Feuilles pour les équipes 3x8 si les données sont fournies
        if stats_3x8 is not None and moyennes_3x8 is not None:
            stats_3x8.to_excel(writer, sheet_name=NOMS_FEUILLES['3x8_statistiques'], index=False)
            moyennes_3x8.to_excel(writer, sheet_name=NOMS_FEUILLES['3x8_moyennes'], index=False)
            
        # Feuille pour les arrêts maladie de tous les employés si les données sont fournies
        if arrets_maladie_tous is not None:
            arrets_maladie_tous.to_excel(writer, sheet_name=NOMS_FEUILLES['arrets_maladie'], index=False) 