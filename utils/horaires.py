"""
Module de gestion des horaires PMT.

author : CAPELLE Gabin
"""

import pandas as pd
from config import HORAIRE_DEBUT_REFERENCE, HORAIRE_FIN_REFERENCE


def get_horaire_final(row):
    """
    Détermine le code horaire final selon la priorité :
    1. HTM (Horaire Théorique Modifié) si disponible
    2. HT (Horaire Théorique) sinon
    
    Args:
        row: Ligne du DataFrame
        
    Returns:
        str: Code horaire final
    """
    if pd.notna(row['HTM']) and row['HTM'] not in [' ', '']:
        return row['HTM']
    elif pd.notna(row['HT']) and row['HT'] not in [' ', '']:
        return row['HT']
    else:
        return ''


def get_horaires_effectifs(row):
    """
    Récupère les horaires effectifs selon la priorité :
    1. HTM avec ses colonnes De.2, à.2, De.3, à.3
    2. HT avec ses colonnes De, à, De.1, à.1
    
    Args:
        row: Ligne du DataFrame
        
    Returns:
        dict: Dictionnaire avec debut1, fin1, debut2, fin2
    """
    if pd.notna(row['HTM']) and row['HTM'] not in [' ', '']:
        return {
            'debut1': row['De.2'],
            'fin1': row['à.2'], 
            'debut2': row['De.3'],
            'fin2': row['à.3']
        }
    elif pd.notna(row['HT']) and row['HT'] not in [' ', '']:
        return {
            'debut1': row['De'],
            'fin1': row['à'],
            'debut2': row['De.1'], 
            'fin2': row['à.1']
        }
    else:
        return {
            'debut1': None,
            'fin1': None,
            'debut2': None,
            'fin2': None
        }


def verifier_horaire_reference(row):
    """
    Vérifie si l'employé a l'horaire de référence.
    Accepte soit :
    - 07:30:00 à 16:15:00 (horaire continu)
    - 07:30:00 à 12:00:00 + 12:45:00 à 16:15:00 (horaire avec pause)
    
    Args:
        row: Ligne du DataFrame
        
    Returns:
        bool: True si l'horaire correspond à la référence
    """
    horaires = get_horaires_effectifs(row)
    
    # Vérifier l'horaire continu 07:30:00 à 16:15:00
    if (horaires['debut1'] == HORAIRE_DEBUT_REFERENCE and 
        horaires['fin1'] == HORAIRE_FIN_REFERENCE):
        return True
    
    if (horaires['debut2'] == HORAIRE_DEBUT_REFERENCE and 
        horaires['fin2'] == HORAIRE_FIN_REFERENCE):
        return True
    
    # Vérifier l'horaire avec pause : 07:30:00 à 12:00:00 + 12:45:00 à 16:15:00
    if (horaires['debut1'] == '07:30:00' and horaires['fin1'] == '12:00:00' and
        horaires['debut2'] == '12:45:00' and horaires['fin2'] == '16:15:00'):
        return True
    
    # Vérifier l'inverse (au cas où les colonnes seraient inversées)
    if (horaires['debut2'] == '07:30:00' and horaires['fin2'] == '12:00:00' and
        horaires['debut1'] == '12:45:00' and horaires['fin1'] == '16:15:00'):
        return True
    
    return False


def analyser_horaires_disponibles(df):
    """
    Analyse les différents horaires présents dans les données pour diagnostic.
    
    Args:
        df (pd.DataFrame): DataFrame à analyser
    """
    print("\n" + "="*50)
    print("ANALYSE DES HORAIRES DISPONIBLES")
    print("="*50)
    
    # Analyser les horaires HT
    horaires_ht = df[['De', 'à', 'De.1', 'à.1']].drop_duplicates()
    print(f"\nHoraires HT uniques trouvés: {len(horaires_ht)}")
    for _, row in horaires_ht.head(10).iterrows():
        if pd.notna(row['De']) and pd.notna(row['à']):
            print(f"  HT: {row['De']} à {row['à']}", end="")
            if pd.notna(row['De.1']) and pd.notna(row['à.1']):
                print(f" + {row['De.1']} à {row['à.1']}")
            else:
                print()
    
    # Analyser les horaires HTM
    horaires_htm = df[['De.2', 'à.2', 'De.3', 'à.3']].drop_duplicates()
    print(f"\nHoraires HTM uniques trouvés: {len(horaires_htm)}")
    for _, row in horaires_htm.head(10).iterrows():
        if pd.notna(row['De.2']) and pd.notna(row['à.2']):
            print(f"  HTM: {row['De.2']} à {row['à.2']}", end="")
            if pd.notna(row['De.3']) and pd.notna(row['à.3']):
                print(f" + {row['De.3']} à {row['à.3']}")
            else:
                print() 