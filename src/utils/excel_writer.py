"""
Module de sauvegarde et formatage Excel PMT.

author : CAPELLE Gabin
"""

import pandas as pd
from config import FICHIER_EXCEL, NOMS_FEUILLES


def sauvegarder_excel(stats_final, moyennes_equipe, fichier_path=None, stats_pit=None, moyennes_pit=None, stats_3x8=None, moyennes_3x8=None):
    """
    Sauvegarde les données dans un fichier Excel.
    
    Args:
        stats_final (pd.DataFrame): Statistiques par employé (astreinte)
        moyennes_equipe (pd.DataFrame): Moyennes par équipe (astreinte)
        fichier_path (str, optional): Chemin du fichier Excel. Si None, utilise FICHIER_EXCEL de config.
        stats_pit (pd.DataFrame, optional): Statistiques par employé PIT (hors astreinte)
        moyennes_pit (pd.DataFrame, optional): Moyennes par équipe PIT (hors astreinte)
        stats_3x8 (pd.DataFrame, optional): Statistiques par employé 3x8
        moyennes_3x8 (pd.DataFrame, optional): Moyennes par équipe 3x8
    """
    # Utiliser le chemin fourni ou celui de la config par défaut
    excel_path = fichier_path if fichier_path is not None else FICHIER_EXCEL
    
    # print(f"\nSauvegarde dans {excel_path}...")
    with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
        # Feuilles pour les équipes d'astreinte
        stats_final.to_excel(writer, sheet_name=NOMS_FEUILLES['statistiques'], index=False)
        moyennes_equipe.to_excel(writer, sheet_name=NOMS_FEUILLES['moyennes'], index=False)
        
        # Feuilles pour les équipes PIT (hors astreinte) si les données sont fournies
        if stats_pit is not None and moyennes_pit is not None:
            stats_pit.to_excel(writer, sheet_name=NOMS_FEUILLES['pit_statistiques'], index=False)
            moyennes_pit.to_excel(writer, sheet_name=NOMS_FEUILLES['pit_moyennes'], index=False) 
        
        # Feuilles pour les équipes 3x8 si les données sont fournies
        if stats_3x8 is not None and moyennes_3x8 is not None:
            stats_3x8.to_excel(writer, sheet_name=NOMS_FEUILLES['3x8_statistiques'], index=False)
            moyennes_3x8.to_excel(writer, sheet_name=NOMS_FEUILLES['3x8_moyennes'], index=False) 