"""
Module de sauvegarde et formatage Excel PMT.

author : CAPELLE Gabin
"""

import pandas as pd
from config import FICHIER_EXCEL, NOMS_FEUILLES


def sauvegarder_excel(stats_final, moyennes_equipe):
    """
    Sauvegarde les données dans un fichier Excel.
    
    Args:
        stats_final (pd.DataFrame): Statistiques par employé
        moyennes_equipe (pd.DataFrame): Moyennes par équipe
    """
    # print(f"\nSauvegarde dans {FICHIER_EXCEL}...")
    with pd.ExcelWriter(FICHIER_EXCEL, engine='openpyxl') as writer:
        stats_final.to_excel(writer, sheet_name=NOMS_FEUILLES['statistiques'], index=False)
        moyennes_equipe.to_excel(writer, sheet_name=NOMS_FEUILLES['moyennes'], index=False) 