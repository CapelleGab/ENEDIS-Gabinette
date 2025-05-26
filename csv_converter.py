"""
Convertisseur CSV vers XLSX
Classe utilitaire pour convertir les fichiers CSV en format Excel XLSX
"""

import pandas as pd
import os
from pathlib import Path


class CSVToXLSXConverter:
    """
    Classe pour convertir les fichiers CSV en format XLSX.
    """
    
    def __init__(self, encoding='latin1', separator=';'):
        """
        Initialise le convertisseur avec les paramètres par défaut.
        
        Args:
            encoding (str): Encodage du fichier CSV (défaut: 'latin1')
            separator (str): Séparateur utilisé dans le CSV (défaut: ';')
        """
        self.encoding = encoding
        self.separator = separator
    
    def convert_file(self, csv_path, xlsx_path=None, sheet_name='Données'):
        """
        Convertit un fichier CSV en XLSX.
        
        Args:
            csv_path (str): Chemin vers le fichier CSV source
            xlsx_path (str, optional): Chemin vers le fichier XLSX de destination.
                                     Si None, utilise le même nom avec extension .xlsx
            sheet_name (str): Nom de la feuille Excel (défaut: 'Données')
        
        Returns:
            str: Chemin vers le fichier XLSX créé
        
        Raises:
            FileNotFoundError: Si le fichier CSV n'existe pas
            Exception: En cas d'erreur lors de la conversion
        """
        # Vérifier que le fichier CSV existe
        if not os.path.exists(csv_path):
            raise FileNotFoundError(f"Le fichier CSV '{csv_path}' n'existe pas.")
        
        # Générer le nom du fichier XLSX si non fourni
        if xlsx_path is None:
            csv_file = Path(csv_path)
            xlsx_path = csv_file.with_suffix('.xlsx')
        
        try:
            print(f"Conversion de '{csv_path}' vers '{xlsx_path}'...")
            
            # Lire le fichier CSV
            df = pd.read_csv(csv_path, encoding=self.encoding, sep=self.separator, low_memory=False)
            
            print(f"Fichier CSV lu avec succès : {len(df)} lignes, {len(df.columns)} colonnes")
            
            # Écrire en format XLSX
            with pd.ExcelWriter(xlsx_path, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name=sheet_name, index=False)
            
            print(f"Conversion terminée : '{xlsx_path}' créé avec succès")
            return str(xlsx_path)
            
        except Exception as e:
            raise Exception(f"Erreur lors de la conversion : {str(e)}")
    
    def convert_multiple_files(self, csv_files, output_dir=None):
        """
        Convertit plusieurs fichiers CSV en XLSX.
        
        Args:
            csv_files (list): Liste des chemins vers les fichiers CSV
            output_dir (str, optional): Répertoire de destination pour les fichiers XLSX.
                                       Si None, utilise le même répertoire que les CSV
        
        Returns:
            dict: Dictionnaire {csv_path: xlsx_path} des conversions réussies
        """
        converted_files = {}
        
        for csv_file in csv_files:
            try:
                if output_dir:
                    csv_name = Path(csv_file).stem
                    xlsx_path = Path(output_dir) / f"{csv_name}.xlsx"
                else:
                    xlsx_path = None
                
                result_path = self.convert_file(csv_file, xlsx_path)
                converted_files[csv_file] = result_path
                
            except Exception as e:
                print(f"Erreur lors de la conversion de '{csv_file}': {str(e)}")
        
        return converted_files
    
    def get_csv_info(self, csv_path):
        """
        Obtient des informations sur un fichier CSV sans le convertir.
        
        Args:
            csv_path (str): Chemin vers le fichier CSV
        
        Returns:
            dict: Informations sur le fichier (nombre de lignes, colonnes, etc.)
        """
        try:
            df = pd.read_csv(csv_path, encoding=self.encoding, sep=self.separator, nrows=5)
            
            # Compter le nombre total de lignes
            with open(csv_path, 'r', encoding=self.encoding) as f:
                total_lines = sum(1 for line in f) - 1  # -1 pour l'en-tête
            
            return {
                'total_lines': total_lines,
                'columns_count': len(df.columns),
                'columns_names': list(df.columns),
                'sample_data': df.head().to_dict('records')
            }
            
        except Exception as e:
            return {'error': str(e)}


# Fonction utilitaire pour usage simple
def convert_csv_to_xlsx(csv_path, xlsx_path=None, encoding='latin1', separator=';'):
    """
    Fonction utilitaire pour convertir rapidement un CSV en XLSX.
    
    Args:
        csv_path (str): Chemin vers le fichier CSV
        xlsx_path (str, optional): Chemin vers le fichier XLSX de destination
        encoding (str): Encodage du CSV (défaut: 'latin1')
        separator (str): Séparateur du CSV (défaut: ';')
    
    Returns:
        str: Chemin vers le fichier XLSX créé
    """
    converter = CSVToXLSXConverter(encoding=encoding, separator=separator)
    return converter.convert_file(csv_path, xlsx_path)


if __name__ == "__main__":
    # Exemple d'utilisation
    converter = CSVToXLSXConverter()
    
    # Convertir le fichier de planning
    try:
        result = converter.convert_file('Planning_journalier_2024.csv')
        print(f"Conversion réussie : {result}")
    except Exception as e:
        print(f"Erreur : {e}") 