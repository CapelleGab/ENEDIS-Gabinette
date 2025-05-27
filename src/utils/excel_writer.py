"""
Module de sauvegarde et formatage Excel PMT.

author : CAPELLE Gabin
"""

import pandas as pd
from config import FICHIER_EXCEL, NOMS_FEUILLES


def sauvegarder_excel(stats_final, moyennes_equipe, fichier_path=None):
    """
    Sauvegarde les données dans un fichier Excel.
    
    Args:
        stats_final (pd.DataFrame): Statistiques par employé
        moyennes_equipe (pd.DataFrame): Moyennes par équipe
        fichier_path (str, optional): Chemin du fichier Excel. Si None, utilise FICHIER_EXCEL de config.
    """
    # Utiliser le chemin fourni ou celui de la config par défaut
    excel_path = fichier_path if fichier_path is not None else FICHIER_EXCEL
    
    # print(f"\nSauvegarde dans {excel_path}...")
    with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
        stats_final.to_excel(writer, sheet_name=NOMS_FEUILLES['statistiques'], index=False)
        moyennes_equipe.to_excel(writer, sheet_name=NOMS_FEUILLES['moyennes'], index=False) 