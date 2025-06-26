"""
Service de comparaison de fichiers Excel pour La Gabinette
"""

import pandas as pd
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import tkinter as tk
from tkinter import filedialog

from src.utils.logger import logger


class ComparisonService:
    """Service de comparaison de fichiers Excel exportés par La Gabinette"""

    def __init__(self):
        self.logger = logger.get_logger("ComparisonService")
        
        # Colonnes attendues dans les fichiers Excel exportés
        self.expected_columns = {
            'ASTREINTES': ['NNI', 'Agence', 'Équipe', 'Nom', 'Prénom', 'Jour_Complet', 'Jour_Partiel', 
                          'Total_Heures_Absence', 'Heure_Supp', 'Arret_Maladie_41', 'Arret_Maladie_5H', 
                          'Periode_Arret_Maladie', 'Moy_Heures_Par_Arret'],
            'HORS ASTREINTE': ['NNI', 'Agence', 'Équipe', 'Nom', 'Prénom', 'Jour_Complet', 'Jour_Partiel', 
                              'Total_Heures_Absence', 'Heure_Supp', 'Arret_Maladie_41', 'Arret_Maladie_5H', 
                              'Periode_Arret_Maladie', 'Moy_Heures_Par_Arret'],
            '3X8': ['NNI', 'Agence', 'Équipe', 'Nom', 'Prénom', 'Heure_Supp', 'Arret_Maladie_41', 
                   'Arret_Maladie_5H', 'Periode_Arret_Maladie', 'Moy_Heures_Par_Arret'],
            'AUTRES': ['NNI', 'Agence', 'Équipe', 'Nom', 'Prénom', 'Arret_Maladie_41', 'Arret_Maladie_5H', 
                      'Periode_Arret_Maladie', 'Moy_Heures_Par_Arret']
        }
        
        # Feuilles attendues dans les fichiers Excel exportés
        self.expected_sheets = ['ASTREINTES', 'HORS ASTREINTE', '3X8', 'AUTRES', 'GRAPHIQUES']

    def validate_excel_file(self, file_path: str) -> Tuple[bool, str, Dict[str, pd.DataFrame]]:
        """
        Valide qu'un fichier Excel correspond au format attendu
        
        Args:
            file_path: Chemin vers le fichier Excel
            
        Returns:
            Tuple (is_valid, error_message, dataframes_dict)
        """
        try:
            # Vérifier que le fichier existe
            if not Path(file_path).exists():
                return False, f"Le fichier {file_path} n'existe pas", {}
            
            # Lire toutes les feuilles du fichier Excel
            try:
                excel_file = pd.ExcelFile(file_path)
                sheet_names = excel_file.sheet_names
            except Exception as e:
                return False, f"Impossible de lire le fichier Excel: {str(e)}", {}
            
            # Vérifier que les feuilles attendues sont présentes (sauf GRAPHIQUES qui est optionnelle)
            required_sheets = ['ASTREINTES', 'HORS ASTREINTE', '3X8', 'AUTRES']
            missing_sheets = [sheet for sheet in required_sheets if sheet not in sheet_names]
            
            if missing_sheets:
                return False, f"Feuilles manquantes dans le fichier: {', '.join(missing_sheets)}", {}
            
            # Lire les données de chaque feuille et valider les colonnes
            dataframes = {}
            for sheet_name in required_sheets:
                try:
                    df = pd.read_excel(file_path, sheet_name=sheet_name)
                    
                    # Vérifier si la feuille contient des données ou juste un message
                    if len(df.columns) == 1 and 'Message' in df.columns:
                        # Feuille vide avec message, on la garde mais vide
                        dataframes[sheet_name] = pd.DataFrame()
                        continue
                    
                    # Vérifier que les colonnes attendues sont présentes
                    expected_cols = self.expected_columns.get(sheet_name, [])
                    missing_cols = [col for col in expected_cols if col not in df.columns]
                    
                    if missing_cols:
                        return False, f"Colonnes manquantes dans la feuille {sheet_name}: {', '.join(missing_cols)}", {}
                    
                    dataframes[sheet_name] = df
                    
                except Exception as e:
                    return False, f"Erreur lors de la lecture de la feuille {sheet_name}: {str(e)}", {}
            
            self.logger.info(f"Fichier {file_path} validé avec succès")
            return True, "", dataframes
            
        except Exception as e:
            return False, f"Erreur lors de la validation: {str(e)}", {}

    def compare_files(self, file1_path: str, file2_path: str) -> Dict[str, Any]:
        """
        Compare deux fichiers Excel et retourne les différences
        
        Args:
            file1_path: Chemin vers le premier fichier
            file2_path: Chemin vers le deuxième fichier
            
        Returns:
            Dictionnaire contenant les résultats de la comparaison
        """
        self.logger.info(f"Début de la comparaison entre {file1_path} et {file2_path}")
        
        # Valider les deux fichiers
        valid1, error1, data1 = self.validate_excel_file(file1_path)
        if not valid1:
            raise ValueError(f"Fichier 1 invalide: {error1}")
        
        valid2, error2, data2 = self.validate_excel_file(file2_path)
        if not valid2:
            raise ValueError(f"Fichier 2 invalide: {error2}")
        
        # Effectuer la comparaison
        comparison_results = {
            'file1_path': file1_path,
            'file2_path': file2_path,
            'file1_name': Path(file1_path).name,
            'file2_name': Path(file2_path).name,
            'comparison_date': datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
            'sheets_comparison': {},
            'summary': ""
        }
        
        # Comparer chaque feuille
        for sheet_name in ['ASTREINTES', 'HORS ASTREINTE', '3X8', 'AUTRES']:
            df1 = data1.get(sheet_name, pd.DataFrame())
            df2 = data2.get(sheet_name, pd.DataFrame())
            
            sheet_comparison = self._compare_sheets(df1, df2, sheet_name)
            comparison_results['sheets_comparison'][sheet_name] = sheet_comparison
        
        # Générer le résumé
        comparison_results['summary'] = self._generate_summary(comparison_results)
        
        self.logger.info("Comparaison terminée avec succès")
        return comparison_results

    def _compare_sheets(self, df1: pd.DataFrame, df2: pd.DataFrame, sheet_name: str) -> Dict[str, Any]:
        """
        Compare deux feuilles Excel
        
        Args:
            df1: DataFrame du premier fichier
            df2: DataFrame du deuxième fichier
            sheet_name: Nom de la feuille
            
        Returns:
            Dictionnaire contenant les résultats de la comparaison de la feuille
        """
        comparison = {
            'sheet_name': sheet_name,
            'file1_rows': len(df1),
            'file2_rows': len(df2),
            'employees_only_in_file1': [],
            'employees_only_in_file2': [],
            'common_employees': [],
            'differences': []
        }
        
        # Si une des feuilles est vide, traitement spécial
        if df1.empty and df2.empty:
            return comparison
        elif df1.empty:
            comparison['employees_only_in_file2'] = df2['NNI'].tolist() if 'NNI' in df2.columns else []
            return comparison
        elif df2.empty:
            comparison['employees_only_in_file1'] = df1['NNI'].tolist() if 'NNI' in df1.columns else []
            return comparison
        
        # Comparer les employés (NNI)
        nni1 = set(df1['NNI'].dropna().astype(str))
        nni2 = set(df2['NNI'].dropna().astype(str))
        
        comparison['employees_only_in_file1'] = list(nni1 - nni2)
        comparison['employees_only_in_file2'] = list(nni2 - nni1)
        comparison['common_employees'] = list(nni1 & nni2)
        
        # Comparer les valeurs pour les employés communs
        for nni in comparison['common_employees']:
            row1 = df1[df1['NNI'].astype(str) == nni].iloc[0]
            row2 = df2[df2['NNI'].astype(str) == nni].iloc[0]
            
            employee_diff = self._compare_employee_data(row1, row2, nni, sheet_name)
            if employee_diff['has_differences']:
                comparison['differences'].append(employee_diff)
        
        return comparison

    def _compare_employee_data(self, row1: pd.Series, row2: pd.Series, nni: str, sheet_name: str) -> Dict[str, Any]:
        """
        Compare les données d'un employé entre deux fichiers
        
        Args:
            row1: Ligne de données du premier fichier
            row2: Ligne de données du deuxième fichier
            nni: NNI de l'employé
            sheet_name: Nom de la feuille
            
        Returns:
            Dictionnaire contenant les différences pour cet employé
        """
        employee_diff = {
            'nni': nni,
            'nom': row1.get('Nom', ''),
            'prenom': row1.get('Prénom', ''),
            'has_differences': False,
            'field_differences': {}
        }
        
        # Colonnes numériques à comparer
        numeric_columns = ['Heure_Supp', 'Arret_Maladie_41', 'Arret_Maladie_5H', 
                          'Periode_Arret_Maladie', 'Moy_Heures_Par_Arret']
        
        # Ajouter les colonnes spécifiques selon la feuille
        if sheet_name in ['ASTREINTES', 'HORS ASTREINTE']:
            numeric_columns.extend(['Jour_Complet', 'Jour_Partiel', 'Total_Heures_Absence'])
        
        for col in numeric_columns:
            if col in row1.index and col in row2.index:
                val1 = pd.to_numeric(row1[col], errors='coerce')
                val2 = pd.to_numeric(row2[col], errors='coerce')
                
                # Traiter les NaN comme 0
                val1 = 0 if pd.isna(val1) else val1
                val2 = 0 if pd.isna(val2) else val2
                
                if abs(val1 - val2) > 0.01:  # Tolérance pour les erreurs d'arrondi
                    employee_diff['has_differences'] = True
                    employee_diff['field_differences'][col] = {
                        'file1_value': val1,
                        'file2_value': val2,
                        'difference': val2 - val1
                    }
        
        return employee_diff

    def _generate_summary(self, comparison_results: Dict[str, Any]) -> str:
        """
        Génère un résumé textuel de la comparaison
        
        Args:
            comparison_results: Résultats de la comparaison
            
        Returns:
            Résumé textuel formaté
        """
        summary_lines = []
        summary_lines.append("RÉSUMÉ DE LA COMPARAISON")
        summary_lines.append("=" * 50)
        summary_lines.append("")
        summary_lines.append(f"Fichier 1: {comparison_results['file1_name']}")
        summary_lines.append(f"Fichier 2: {comparison_results['file2_name']}")
        summary_lines.append(f"Date de comparaison: {comparison_results['comparison_date']}")
        summary_lines.append("")
        
        # Résumé par feuille
        for sheet_name, sheet_comp in comparison_results['sheets_comparison'].items():
            summary_lines.append(f"FEUILLE: {sheet_name}")
            summary_lines.append("-" * 30)
            summary_lines.append(f"Employés dans fichier 1: {sheet_comp['file1_rows']}")
            summary_lines.append(f"Employés dans fichier 2: {sheet_comp['file2_rows']}")
            summary_lines.append(f"Employés communs: {len(sheet_comp['common_employees'])}")
            summary_lines.append(f"Uniquement dans fichier 1: {len(sheet_comp['employees_only_in_file1'])}")
            summary_lines.append(f"Uniquement dans fichier 2: {len(sheet_comp['employees_only_in_file2'])}")
            summary_lines.append(f"Employés avec différences: {len(sheet_comp['differences'])}")
            
            # Détails des employés uniques
            if sheet_comp['employees_only_in_file1']:
                summary_lines.append(f"  NNI uniquement dans fichier 1: {', '.join(sheet_comp['employees_only_in_file1'][:10])}")
                if len(sheet_comp['employees_only_in_file1']) > 10:
                    summary_lines.append(f"    ... et {len(sheet_comp['employees_only_in_file1']) - 10} autres")
            
            if sheet_comp['employees_only_in_file2']:
                summary_lines.append(f"  NNI uniquement dans fichier 2: {', '.join(sheet_comp['employees_only_in_file2'][:10])}")
                if len(sheet_comp['employees_only_in_file2']) > 10:
                    summary_lines.append(f"    ... et {len(sheet_comp['employees_only_in_file2']) - 10} autres")
            
            # Détails des différences
            if sheet_comp['differences']:
                summary_lines.append("  Principales différences:")
                for diff in sheet_comp['differences'][:5]:  # Limiter à 5 exemples
                    summary_lines.append(f"    {diff['nni']} ({diff['nom']} {diff['prenom']}):")
                    for field, field_diff in diff['field_differences'].items():
                        summary_lines.append(f"      {field}: {field_diff['file1_value']} → {field_diff['file2_value']} (Δ{field_diff['difference']:+.2f})")
                
                if len(sheet_comp['differences']) > 5:
                    summary_lines.append(f"    ... et {len(sheet_comp['differences']) - 5} autres employés avec différences")
            
            summary_lines.append("")
        
        return "\n".join(summary_lines)

    def export_comparison_results(self, results: Dict[str, Any], output_path: Optional[str] = None,
                                 use_file_dialog: bool = False) -> str:
        """
        Exporte les résultats de comparaison vers un fichier Excel
        
        Args:
            results: Résultats de la comparaison
            output_path: Chemin de sortie (optionnel)
            use_file_dialog: Si True, ouvre un sélecteur de fichier
            
        Returns:
            Chemin du fichier créé
        """
        if use_file_dialog:
            # Ouvrir un sélecteur de fichier
            root = tk.Tk()
            root.withdraw()  # Cacher la fenêtre

            # Générer un nom de fichier par défaut
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            default_filename = f"comparaison_{timestamp}.xlsx"

            # Utiliser le dossier Documents comme dossier par défaut
            documents_path = Path.home() / "Documents"

            output_path = filedialog.asksaveasfilename(
                title="Sauvegarder la comparaison",
                defaultextension=".xlsx",
                filetypes=[("Fichiers Excel", "*.xlsx"), ("Tous les fichiers", "*.*")],
                initialdir=str(documents_path),
                initialfile=default_filename
            )

            root.destroy()  # Détruire la fenêtre temporaire

            if not output_path:  # L'utilisateur a annulé
                raise Exception("Export annulé par l'utilisateur")

        if not output_path:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = Path.home() / "Documents" / f"comparaison_{timestamp}.xlsx"
        else:
            output_path = Path(output_path)

        self.logger.info(f"Export de la comparaison vers: {output_path}")

        try:
            with pd.ExcelWriter(output_path, engine='xlsxwriter') as writer:
                # Feuille de résumé
                summary_df = pd.DataFrame({'Résumé': [results['summary']]})
                summary_df.to_excel(writer, sheet_name='RÉSUMÉ', index=False)

                # Feuille pour chaque catégorie avec les détails
                for sheet_name, sheet_comp in results['sheets_comparison'].items():
                    # Créer un DataFrame avec les différences détaillées
                    if sheet_comp['differences']:
                        diff_data = []
                        for diff in sheet_comp['differences']:
                            base_row = {
                                'NNI': diff['nni'],
                                'Nom': diff['nom'],
                                'Prénom': diff['prenom']
                            }
                            
                            for field, field_diff in diff['field_differences'].items():
                                row = base_row.copy()
                                row.update({
                                    'Champ': field,
                                    'Valeur_Fichier1': field_diff['file1_value'],
                                    'Valeur_Fichier2': field_diff['file2_value'],
                                    'Différence': field_diff['difference']
                                })
                                diff_data.append(row)
                        
                        diff_df = pd.DataFrame(diff_data)
                        diff_df.to_excel(writer, sheet_name=f'DIFF_{sheet_name}', index=False)
                    
                    # Feuille avec les employés uniques
                    unique_data = []
                    for nni in sheet_comp['employees_only_in_file1']:
                        unique_data.append({'NNI': nni, 'Présent_dans': 'Fichier 1 uniquement'})
                    for nni in sheet_comp['employees_only_in_file2']:
                        unique_data.append({'NNI': nni, 'Présent_dans': 'Fichier 2 uniquement'})
                    
                    if unique_data:
                        unique_df = pd.DataFrame(unique_data)
                        unique_df.to_excel(writer, sheet_name=f'UNIQUE_{sheet_name}', index=False)

            self.logger.info(f"Export de comparaison terminé: {output_path}")
            return str(output_path)

        except Exception as e:
            error_msg = f"Erreur lors de l'export de la comparaison: {str(e)}"
            self.logger.error(error_msg)
            raise Exception(error_msg) 