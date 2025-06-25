"""
Service d'export pour La Gabinette
"""

from pathlib import Path
from typing import List, Dict, Any, Optional
import pandas as pd
from datetime import datetime

from src.config.settings import OUTPUT_DIR, EXPORT_CONFIG
from src.models.data_model import PMTRecord, ValidationResult
from src.services.employee_classifier import EmployeeClassifier
from src.services.overtime_calculator import OvertimeCalculator
from src.services.sick_leave_calculator import SickLeaveCalculator
from src.services.work_time_calculator import WorkTimeCalculator
from src.utils.logger import logger
from src.utils.helpers import create_backup_filename


class ExportService:
    """Service d'export des données PMT"""

    def __init__(self):
        self.logger = logger.get_logger("ExportService")
        self.classifier = EmployeeClassifier()
        self.overtime_calculator = OvertimeCalculator()
        self.sick_leave_calculator = SickLeaveCalculator()
        self.work_time_calculator = WorkTimeCalculator()

    def export_to_excel(self, records: List[PMTRecord], output_path: Optional[str] = None,
                       use_file_dialog: bool = False) -> str:
        """
        Exporte les enregistrements vers un fichier Excel avec classification par catégorie d'employés

        Args:
            records: Liste des enregistrements à exporter
            output_path: Chemin de sortie (optionnel)
            use_file_dialog: Si True, ouvre un sélecteur de fichier

        Returns:
            Chemin du fichier créé
        """
        if use_file_dialog:
            # Ouvrir un sélecteur de fichier
            import tkinter as tk
            from tkinter import filedialog

            # Créer une fenêtre temporaire (cachée) pour le dialog
            root = tk.Tk()
            root.withdraw()  # Cacher la fenêtre

            # Générer un nom de fichier par défaut
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            default_filename = f"export_pmt_categories_{timestamp}.xlsx"

            # Utiliser le dossier Documents comme dossier par défaut
            documents_path = Path.home() / "Documents"

            output_path = filedialog.asksaveasfilename(
                title="Sauvegarder l'export Excel",
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
            output_path = OUTPUT_DIR / f"export_pmt_categories_{timestamp}.xlsx"
        else:
            output_path = Path(output_path)

        self.logger.info(f"Export Excel avec classification vers: {output_path}")

        try:
            # Classifier les employés
            classifications = self.classifier.classify_employees(records)

            # Calculer les heures supplémentaires pour tous les employés
            overtime_by_employee = self.overtime_calculator.calculate_all_employees_overtime(records)

            # Calculer les arrêts maladie pour tous les employés
            sick_leave_by_employee = self.sick_leave_calculator.calculate_all_employees_sick_leave(records)
            self.logger.info(f"Statistiques d'arrêt maladie calculées pour {len(sick_leave_by_employee)} employés")

            # Calculer les jours de travail pour tous les employés
            work_days_by_category = self.work_time_calculator.calculate_all_employees_work_days(records, classifications)
            self.logger.info(f"Statistiques de jours de travail calculées pour {len(work_days_by_category)} catégories")

            # Créer le fichier Excel avec les 4 feuilles par catégorie
            with pd.ExcelWriter(output_path, engine='xlsxwriter') as writer:

                # Créer une feuille pour chaque catégorie
                for category in ['ASTREINTES', 'TIPS', '3X8', 'AUTRES']:
                    category_records = classifications.get(category, [])

                    if category_records:
                        # Appliquer les règles métier pour filtrer les enregistrements
                        filtered_records = self.classifier.filter_records_by_business_rules(
                            category_records, category
                        )

                        if filtered_records:
                            # Grouper par employé pour avoir une ligne par employé distinct
                            employees = {}
                            for record in filtered_records:
                                nni = record.nni
                                if nni and nni not in employees:
                                    # Déterminer l'agence à partir de l'équipe
                                    agence = self._get_agence_from_equipe_lib(record.equipe_lib)

                                    # Récupérer les heures supplémentaires pour cet employé
                                    overtime_hours = overtime_by_employee.get(nni, 0.0)

                                    # Récupérer les statistiques d'arrêts maladie pour cet employé
                                    sick_leave_stats = sick_leave_by_employee.get(nni, {})
                                    classic_sick_leaves = sick_leave_stats.get('classic_sick_leaves', 0)
                                    long_sick_leaves = sick_leave_stats.get('long_sick_leaves', 0)
                                    sick_leave_periods = sick_leave_stats.get('sick_leave_periods', 0)
                                    avg_hours_per_sick_leave = sick_leave_stats.get('avg_hours_per_sick_leave', 0.0)

                                    # Récupérer les statistiques de jours de travail pour cet employé
                                    work_days_stats = {}
                                    if category in work_days_by_category:
                                        work_days_stats = work_days_by_category[category].get(nni, {})
                                    full_days = work_days_stats.get('full_days', 0)
                                    partial_days = work_days_stats.get('partial_days', 0)
                                    total_absence_hours = work_days_stats.get('total_absence_hours', 0.0)

                                    employees[nni] = {
                                        'NNI': nni,
                                        'Équipe': record.equipe_lib or '',
                                        'Nom': record.nom or '',
                                        'Prénom': record.prenom or '',
                                        'Agence': agence,
                                        'Heure_Supp': overtime_hours,
                                        'Arret_Maladie_41': classic_sick_leaves,
                                        'Arret_Maladie_5H': long_sick_leaves,
                                        'Periode_Arret_Maladie': sick_leave_periods,
                                        'Moy_Heures_Par_Arret': avg_hours_per_sick_leave,
                                        'Jour_Complet': full_days,
                                        'Jour_Partiel': partial_days,
                                        'Total_Heures_Absence': total_absence_hours
                                    }

                            if employees:
                                # Convertir en DataFrame avec les colonnes spécifiées
                                df = pd.DataFrame(list(employees.values()))

                                # Réorganiser les colonnes dans l'ordre souhaité
                                if category == '3X8':
                                    # Pour la feuille 3X8, on affiche Heure_Supp mais pas Jour_Complet, Jour_Partiel, Total_Heures_Absence
                                    column_order = ['NNI', 'Agence', 'Équipe', 'Nom', 'Prénom', 'Heure_Supp',
                                                   'Arret_Maladie_41', 'Arret_Maladie_5H',
                                                   'Periode_Arret_Maladie', 'Moy_Heures_Par_Arret']
                                    # Supprimer seulement les colonnes de jours de travail
                                    columns_to_remove = ['Jour_Complet', 'Jour_Partiel', 'Total_Heures_Absence']
                                    for col in columns_to_remove:
                                        if col in df.columns:
                                            df = df.drop(columns=[col])
                                elif category == 'AUTRES':
                                    # Pour la feuille AUTRES, on n'affiche pas Heure_Supp, Jour_Complet, Jour_Partiel, Total_Heures_Absence
                                    column_order = ['NNI', 'Agence', 'Équipe', 'Nom', 'Prénom',
                                                   'Arret_Maladie_41', 'Arret_Maladie_5H',
                                                   'Periode_Arret_Maladie', 'Moy_Heures_Par_Arret']
                                    # Supprimer les colonnes non désirées
                                    columns_to_remove = ['Heure_Supp', 'Jour_Complet', 'Jour_Partiel', 'Total_Heures_Absence']
                                    for col in columns_to_remove:
                                        if col in df.columns:
                                            df = df.drop(columns=[col])
                                else:
                                    # Pour ASTREINTES et TIPS, afficher toutes les colonnes avec Jour_Complet, Jour_Partiel, Total_Heures_Absence après Prénom
                                    column_order = ['NNI', 'Agence', 'Équipe', 'Nom', 'Prénom',
                                                   'Jour_Complet', 'Jour_Partiel', 'Total_Heures_Absence',
                                                   'Heure_Supp', 'Arret_Maladie_41', 'Arret_Maladie_5H',
                                                   'Periode_Arret_Maladie', 'Moy_Heures_Par_Arret']

                                df = df[column_order]

                                # Exporter vers la feuille avec nom d'affichage
                                sheet_name = 'HORS ASTREINTE' if category == 'TIPS' else category
                                df.to_excel(writer, sheet_name=sheet_name, index=False)
                                self.logger.info(f"Feuille {category}: {len(employees)} employés uniques")
                            else:
                                # Créer une feuille vide avec un message
                                sheet_name = 'HORS ASTREINTE' if category == 'TIPS' else category
                                empty_df = pd.DataFrame({'Message': ['Aucun employé avec NNI valide pour cette catégorie']})
                                empty_df.to_excel(writer, sheet_name=sheet_name, index=False)
                        else:
                            # Créer une feuille vide avec un message
                            sheet_name = 'HORS ASTREINTE' if category == 'TIPS' else category
                            empty_df = pd.DataFrame({'Message': ['Aucun enregistrement après application des règles métier']})
                            empty_df.to_excel(writer, sheet_name=sheet_name, index=False)
                    else:
                        # Créer une feuille vide
                        sheet_name = 'HORS ASTREINTE' if category == 'TIPS' else category
                        empty_df = pd.DataFrame({'Message': ['Aucun employé dans cette catégorie']})
                        empty_df.to_excel(writer, sheet_name=sheet_name, index=False)

                # Créer une feuille avec des graphiques
                self._create_charts_sheet(writer, classifications, overtime_by_employee, sick_leave_by_employee, work_days_by_category)

                # Formatage des feuilles
                self._format_classification_sheets(writer, classifications)

            self.logger.info(f"Export Excel terminé: 4 catégories d'employés exportées + feuille graphiques")
            return str(output_path)

        except Exception as e:
            error_msg = f"Erreur lors de l'export Excel: {str(e)}"
            self.logger.error(error_msg)
            raise Exception(error_msg)

    def export_summary_to_text(self, records: List[PMTRecord], output_path: Optional[str] = None,
                           use_file_dialog: bool = False) -> str:
        """
        Exporte le résumé des classifications vers un fichier texte avec un format amélioré

        Args:
            records: Liste des enregistrements à exporter
            output_path: Chemin de sortie (optionnel)
            use_file_dialog: Si True, ouvre un sélecteur de fichier

        Returns:
            Chemin du fichier créé
        """
        if use_file_dialog:
            # Ouvrir un sélecteur de fichier
            import tkinter as tk
            from tkinter import filedialog

            # Créer une fenêtre temporaire (cachée) pour le dialog
            root = tk.Tk()
            root.withdraw()  # Cacher la fenêtre

            # Générer un nom de fichier par défaut
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            default_filename = f"resume_classifications_{timestamp}.txt"

            # Utiliser le dossier Documents comme dossier par défaut
            documents_path = Path.home() / "Documents"

            output_path = filedialog.asksaveasfilename(
                title="Sauvegarder le résumé",
                defaultextension=".txt",
                filetypes=[("Fichiers texte", "*.txt"), ("Tous les fichiers", "*.*")],
                initialdir=str(documents_path),
                initialfile=default_filename
            )

            root.destroy()  # Détruire la fenêtre temporaire

            if not output_path:  # L'utilisateur a annulé
                raise Exception("Export annulé par l'utilisateur")

        if not output_path:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = OUTPUT_DIR / f"resume_classifications_{timestamp}.txt"
        else:
            output_path = Path(output_path)

        self.logger.info(f"Export du résumé des classifications vers: {output_path}")

        try:
            # Classifier les employés
            classifications = self.classifier.classify_employees(records)

            # Calculer les heures supplémentaires pour tous les employés
            overtime_by_employee = self.overtime_calculator.calculate_all_employees_overtime(records)

            # Calculer les arrêts maladie pour tous les employés
            sick_leave_by_employee = self.sick_leave_calculator.calculate_all_employees_sick_leave(records)
            self.logger.info(f"Statistiques d'arrêt maladie calculées pour {len(sick_leave_by_employee)} employés")

            # Calculer les jours de travail pour tous les employés
            work_days_by_category = self.work_time_calculator.calculate_all_employees_work_days(records, classifications)
            self.logger.info(f"Statistiques de jours de travail calculées pour {len(work_days_by_category)} catégories")

            # Créer le contenu du résumé avec le nouveau format
            summary_text = self._create_formatted_summary_text(classifications, overtime_by_employee, sick_leave_by_employee, work_days_by_category)

            # Écrire dans le fichier texte
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(summary_text)

            self.logger.info(f"Export du résumé terminé: {output_path}")
            return str(output_path)

        except Exception as e:
            error_msg = f"Erreur lors de l'export du résumé: {str(e)}"
            self.logger.error(error_msg)
            raise Exception(error_msg)

    def _create_formatted_summary_text(self, classifications: Dict[str, List[PMTRecord]],
                                       overtime_by_employee: Dict[str, float],
                                       sick_leave_by_employee: Dict[str, Dict[str, Any]],
                                       work_days_by_category: Dict[str, Dict[str, Dict[str, Any]]]) -> str:
        """
        Crée un texte de résumé formaté selon les spécifications

        Args:
            classifications: Classifications des employés
            overtime_by_employee: Heures supplémentaires par employé
            sick_leave_by_employee: Arrêts maladie par employé
            work_days_by_category: Jours de travail par catégorie puis par employé

        Returns:
            Texte formaté du résumé
        """
        # Constantes pour le formatage
        LINE_WIDTH = 80
        SEPARATOR = "=" * LINE_WIDTH

        # Initialiser le texte du résumé
        summary = []
        summary.append(SEPARATOR)
        summary.append("RÉSUMÉ DES STATISTIQUES PAR CATÉGORIE".center(LINE_WIDTH))
        summary.append(SEPARATOR)
        summary.append("")

        # --- SECTION EMPLOYÉS ---
        summary.append(SEPARATOR)
        summary.append("EMPLOYÉS".center(LINE_WIDTH))
        summary.append(SEPARATOR)
        summary.append("")

        # Statistiques par catégorie d'employés
        categories = {
            'ASTREINTES': 'Astreinte',
            'TIPS': 'HORS ASTREINTE',
            '3X8': '3x8',
            'AUTRES': 'Autres'
        }

        # Nombre total d'employés uniques
        all_employees = set()
        for records in classifications.values():
            for record in records:
                if record.nni:
                    all_employees.add(record.nni)

        total_employees = len(all_employees)

        # Statistiques pour chaque catégorie
        for category_key, category_name in categories.items():
            category_records = classifications.get(category_key, [])

            # Filtrer les enregistrements selon les règles métier
            filtered_records = self.classifier.filter_records_by_business_rules(
                category_records, category_key
            )

            # Employés uniques dans cette catégorie
            unique_employees = set()
            for record in filtered_records:
                if record.nni:
                    unique_employees.add(record.nni)

            employee_count = len(unique_employees)
            percentage = (employee_count / total_employees * 100) if total_employees > 0 else 0

            # Calculer les statistiques des heures supplémentaires pour cette catégorie
            category_overtime = [overtime_by_employee.get(nni, 0.0) for nni in unique_employees]
            employees_with_overtime = [h for h in category_overtime if h > 0]

            # Moyenne incluant tous les employés (avec et sans heures supp)
            avg_overtime_all = sum(category_overtime) / len(category_overtime) if category_overtime else 0

            # Moyenne uniquement parmi ceux qui ont fait des heures supplémentaires
            avg_overtime_with_overtime_only = sum(employees_with_overtime) / len(employees_with_overtime) if employees_with_overtime else 0

            # Pourcentage d'employés ayant fait des heures supplémentaires
            percentage_with_overtime = (len(employees_with_overtime) / len(unique_employees) * 100) if unique_employees else 0

            # Calculer les statistiques d'arrêts maladie pour cette catégorie
            total_classic_sick_leaves = 0
            total_long_sick_leaves = 0
            total_sick_leave_periods = 0
            total_sick_leave_hours = 0

            for nni in unique_employees:
                if nni in sick_leave_by_employee:
                    stats = sick_leave_by_employee[nni]
                    total_classic_sick_leaves += stats.get('classic_sick_leaves', 0)
                    total_long_sick_leaves += stats.get('long_sick_leaves', 0)
                    total_sick_leave_periods += stats.get('sick_leave_periods', 0)

                    # Calculer le total des heures d'arrêt maladie
                    classic_sick_leaves = stats.get('classic_sick_leaves', 0)
                    long_sick_leaves = stats.get('long_sick_leaves', 0)
                    avg_hours = stats.get('avg_hours_per_sick_leave', 0.0)
                    total_sick_leave_hours += (classic_sick_leaves + long_sick_leaves) * avg_hours

            # Calculer les moyennes par employé
            avg_classic_sick_leaves = total_classic_sick_leaves / len(unique_employees) if unique_employees else 0
            avg_long_sick_leaves = total_long_sick_leaves / len(unique_employees) if unique_employees else 0
            avg_sick_leave_periods = total_sick_leave_periods / len(unique_employees) if unique_employees else 0
            avg_sick_leave_hours = total_sick_leave_hours / len(unique_employees) if unique_employees else 0

            # Calculer les statistiques de jours de travail pour cette catégorie
            total_full_days = 0
            total_partial_days = 0

            # Récupérer les données de jours de travail pour cette catégorie
            category_work_days = work_days_by_category.get(category_key, {})

            for nni in unique_employees:
                if nni in category_work_days:
                    stats = category_work_days[nni]
                    total_full_days += stats.get('full_days', 0)
                    total_partial_days += stats.get('partial_days', 0)

            # Calculer les moyennes par employé
            avg_full_days = total_full_days / len(unique_employees) if unique_employees else 0
            avg_partial_days = total_partial_days / len(unique_employees) if unique_employees else 0
            total_work_days = total_full_days + total_partial_days
            percentage_full_days = (total_full_days / total_work_days * 100) if total_work_days > 0 else 0

            # Convertir en jours (en supposant 7 heures par jour)
            avg_overtime_all_days = avg_overtime_all / 7.0
            avg_overtime_with_overtime_only_days = avg_overtime_with_overtime_only / 7.0
            avg_sick_leave_days = avg_sick_leave_hours / 7.0

            summary.append(f"{category_name} :")
            summary.append(f"- Nombre d'employés : {employee_count} ({percentage:.1f}% du total)")
            if category_key != 'AUTRES':  # Ne pas afficher les heures supp pour la catégorie AUTRES
                summary.append(f"- Employés avec heures supplémentaires : {len(employees_with_overtime)} ({percentage_with_overtime:.1f}%)")
                if employees_with_overtime:
                    summary.append(f"- Moyenne heures supplémentaires par employé : {avg_overtime_with_overtime_only:.2f}h ({avg_overtime_with_overtime_only_days:.2f} jours)")
            summary.append(f"- Arrêts maladie classiques (41) : {total_classic_sick_leaves} (moy. {avg_classic_sick_leaves:.2f} par employé)")
            summary.append(f"- Arrêts maladie longs (5H) : {total_long_sick_leaves} (moy. {avg_long_sick_leaves:.2f} par employé)")
            summary.append(f"- Périodes d'arrêt maladie : {total_sick_leave_periods} (moy. {avg_sick_leave_periods:.2f} par employé)")
            summary.append(f"- Moyenne des heures par arrêt maladie : {avg_sick_leave_hours:.2f}h ({avg_sick_leave_days:.2f} jours)")
            # Afficher les jours complets/partiels seulement pour ASTREINTES et TIPS
            if category_key in ['ASTREINTES', 'TIPS']:
                summary.append(f"- Jours complets (8h) : {total_full_days} (moy. {avg_full_days:.2f} par employé)")
                summary.append(f"- Jours partiels (<8h) : {total_partial_days} (moy. {avg_partial_days:.2f} par employé)")
                summary.append(f"- Pourcentage jours complets : {percentage_full_days:.1f}%")
            summary.append("")

        # --- SECTION AGENCES ---
        summary.append(SEPARATOR)
        summary.append("AGENCES".center(LINE_WIDTH))
        summary.append(SEPARATOR)
        summary.append("")

        # Statistiques par agence
        agence_stats = self._get_agence_statistics(classifications)
        agences = {
            'Batignolles': 'Batignolles',
            'Italie': 'Italie',
            'Grenelle': 'Grenelle',
            'Paris Est': 'Paris Est'
        }

        for agence_key, agence_name in agences.items():
            stats = agence_stats.get(agence_key, {'employees': 0, 'records': 0, 'percentage': 0})

            # Calculer la moyenne des heures supplémentaires pour cette agence
            agence_employees = set()
            for category, records in classifications.items():
                for record in records:
                    if record.nni and self._get_agence_from_equipe_lib(record.equipe_lib) == agence_key:
                        agence_employees.add(record.nni)

            # Statistiques des heures supplémentaires
            agence_overtime = [overtime_by_employee.get(nni, 0.0) for nni in agence_employees]
            employees_with_overtime_agence = [h for h in agence_overtime if h > 0]

            # Moyennes pour l'agence
            avg_overtime_all = sum(agence_overtime) / len(agence_overtime) if agence_overtime else 0
            avg_overtime_with_overtime_only = sum(employees_with_overtime_agence) / len(employees_with_overtime_agence) if employees_with_overtime_agence else 0
            percentage_with_overtime_agence = (len(employees_with_overtime_agence) / len(agence_employees) * 100) if agence_employees else 0

            avg_overtime_all_days = avg_overtime_all / 7.0
            avg_overtime_with_overtime_only_days = avg_overtime_with_overtime_only / 7.0

            # Statistiques des arrêts maladie
            total_classic_sick_leaves = 0
            total_long_sick_leaves = 0
            total_sick_leave_periods = 0
            total_sick_leave_hours = 0

            for nni in agence_employees:
                if nni in sick_leave_by_employee:
                    stats = sick_leave_by_employee[nni]
                    total_classic_sick_leaves += stats.get('classic_sick_leaves', 0)
                    total_long_sick_leaves += stats.get('long_sick_leaves', 0)
                    total_sick_leave_periods += stats.get('sick_leave_periods', 0)

                    # Calculer le total des heures d'arrêt maladie
                    classic_sick_leaves = stats.get('classic_sick_leaves', 0)
                    long_sick_leaves = stats.get('long_sick_leaves', 0)
                    avg_hours = stats.get('avg_hours_per_sick_leave', 0.0)
                    total_sick_leave_hours += (classic_sick_leaves + long_sick_leaves) * avg_hours

            # Statistiques des jours de travail
            total_full_days_agence = 0
            total_partial_days_agence = 0

            for nni in agence_employees:
                # Chercher dans toutes les catégories car un employé peut être dans n'importe laquelle
                for category_key in ['ASTREINTES', 'TIPS']:  # Seulement ces 2 catégories ont des données
                    category_work_days = work_days_by_category.get(category_key, {})
                    if nni in category_work_days:
                        stats = category_work_days[nni]
                        total_full_days_agence += stats.get('full_days', 0)
                        total_partial_days_agence += stats.get('partial_days', 0)
                        break  # Trouvé dans une catégorie, pas besoin de chercher dans les autres

            # Moyennes par employé
            employee_count = len(agence_employees)
            avg_classic_sick_leaves = total_classic_sick_leaves / employee_count if employee_count else 0
            avg_long_sick_leaves = total_long_sick_leaves / employee_count if employee_count else 0
            avg_sick_leave_periods = total_sick_leave_periods / employee_count if employee_count else 0
            avg_sick_leave_hours = total_sick_leave_hours / employee_count if employee_count else 0
            avg_sick_leave_days = avg_sick_leave_hours / 7.0

            avg_full_days_agence = total_full_days_agence / employee_count if employee_count else 0
            avg_partial_days_agence = total_partial_days_agence / employee_count if employee_count else 0
            total_work_days_agence = total_full_days_agence + total_partial_days_agence
            percentage_full_days_agence = (total_full_days_agence / total_work_days_agence * 100) if total_work_days_agence > 0 else 0

            summary.append(f"{agence_name} :")
            summary.append(f"- Nombre d'employés : {employee_count}")
            summary.append(f"- Employés avec heures supplémentaires : {len(employees_with_overtime_agence)} ({percentage_with_overtime_agence:.1f}%)")
            if employees_with_overtime_agence:
                summary.append(f"- Moyenne heures supplémentaires par employé : {avg_overtime_with_overtime_only:.2f}h ({avg_overtime_with_overtime_only_days:.2f} jours)")
            summary.append(f"- Arrêts maladie classiques (41) : {total_classic_sick_leaves} (moy. {avg_classic_sick_leaves:.2f} par employé)")
            summary.append(f"- Arrêts maladie longs (5H) : {total_long_sick_leaves} (moy. {avg_long_sick_leaves:.2f} par employé)")
            summary.append(f"- Périodes d'arrêt maladie : {total_sick_leave_periods} (moy. {avg_sick_leave_periods:.2f} par employé)")
            summary.append(f"- Moyenne des heures par arrêt maladie : {avg_sick_leave_hours:.2f}h ({avg_sick_leave_days:.2f} jours)")
            summary.append(f"- Jours complets (8h) : {total_full_days_agence} (moy. {avg_full_days_agence:.2f} par employé)")
            summary.append(f"- Jours partiels (<8h) : {total_partial_days_agence} (moy. {avg_partial_days_agence:.2f} par employé)")
            summary.append(f"- Pourcentage jours complets : {percentage_full_days_agence:.1f}%")
            summary.append("")

        # --- SECTION DIRECTION RÉGIONALE ---
        summary.append(SEPARATOR)
        summary.append("DIRECTION RÉGIONALE".center(LINE_WIDTH))
        summary.append(SEPARATOR)
        summary.append("")

        # Statistiques globales pour la DR Paris
        # Heures supplémentaires
        all_overtime = [overtime_by_employee.get(nni, 0.0) for nni in all_employees]
        employees_with_overtime_dr = [h for h in all_overtime if h > 0]

        avg_overtime_all_dr = sum(all_overtime) / len(all_overtime) if all_overtime else 0
        avg_overtime_with_overtime_only_dr = sum(employees_with_overtime_dr) / len(employees_with_overtime_dr) if employees_with_overtime_dr else 0
        percentage_with_overtime_dr = (len(employees_with_overtime_dr) / len(all_employees) * 100) if all_employees else 0

        avg_overtime_all_days_dr = avg_overtime_all_dr / 7.0
        avg_overtime_with_overtime_only_days_dr = avg_overtime_with_overtime_only_dr / 7.0

        # Arrêts maladie
        total_classic_sick_leaves_dr = 0
        total_long_sick_leaves_dr = 0
        total_sick_leave_periods_dr = 0
        total_sick_leave_hours_dr = 0

        for nni in all_employees:
            if nni in sick_leave_by_employee:
                stats = sick_leave_by_employee[nni]
                total_classic_sick_leaves_dr += stats.get('classic_sick_leaves', 0)
                total_long_sick_leaves_dr += stats.get('long_sick_leaves', 0)
                total_sick_leave_periods_dr += stats.get('sick_leave_periods', 0)

                # Calculer le total des heures d'arrêt maladie
                classic_sick_leaves = stats.get('classic_sick_leaves', 0)
                long_sick_leaves = stats.get('long_sick_leaves', 0)
                avg_hours = stats.get('avg_hours_per_sick_leave', 0.0)
                total_sick_leave_hours_dr += (classic_sick_leaves + long_sick_leaves) * avg_hours

        # Jours de travail
        total_full_days_dr = 0
        total_partial_days_dr = 0

        for nni in all_employees:
            # Chercher dans toutes les catégories car un employé peut être dans n'importe laquelle
            for category_key in ['ASTREINTES', 'TIPS']:  # Seulement ces 2 catégories ont des données
                category_work_days = work_days_by_category.get(category_key, {})
                if nni in category_work_days:
                    stats = category_work_days[nni]
                    total_full_days_dr += stats.get('full_days', 0)
                    total_partial_days_dr += stats.get('partial_days', 0)
                    break  # Trouvé dans une catégorie, pas besoin de chercher dans les autres

        # Moyennes par employé
        total_employees_dr = len(all_employees)
        avg_classic_sick_leaves_dr = total_classic_sick_leaves_dr / total_employees_dr if total_employees_dr else 0
        avg_long_sick_leaves_dr = total_long_sick_leaves_dr / total_employees_dr if total_employees_dr else 0
        avg_sick_leave_periods_dr = total_sick_leave_periods_dr / total_employees_dr if total_employees_dr else 0
        avg_sick_leave_hours_dr = total_sick_leave_hours_dr / total_employees_dr if total_employees_dr else 0
        avg_sick_leave_days_dr = avg_sick_leave_hours_dr / 7.0

        avg_full_days_dr = total_full_days_dr / total_employees_dr if total_employees_dr else 0
        avg_partial_days_dr = total_partial_days_dr / total_employees_dr if total_employees_dr else 0
        total_work_days_dr = total_full_days_dr + total_partial_days_dr
        percentage_full_days_dr = (total_full_days_dr / total_work_days_dr * 100) if total_work_days_dr > 0 else 0

        summary.append("DR PARIS :")
        summary.append(f"- Nombre total d'employés : {total_employees}")
        summary.append(f"- Employés avec heures supplémentaires : {len(employees_with_overtime_dr)} ({percentage_with_overtime_dr:.1f}%)")
        if employees_with_overtime_dr:
            summary.append(f"- Moyenne heures supplémentaires par employé : {avg_overtime_with_overtime_only_dr:.2f}h ({avg_overtime_with_overtime_only_days_dr:.2f} jours)")
        summary.append(f"- Total arrêts maladie classiques (41) : {total_classic_sick_leaves_dr} (moy. {avg_classic_sick_leaves_dr:.2f} par employé)")
        summary.append(f"- Total arrêts maladie longs (5H) : {total_long_sick_leaves_dr} (moy. {avg_long_sick_leaves_dr:.2f} par employé)")
        summary.append(f"- Total périodes d'arrêt maladie : {total_sick_leave_periods_dr} (moy. {avg_sick_leave_periods_dr:.2f} par employé)")
        summary.append(f"- Moyenne des heures par arrêt maladie : {avg_sick_leave_hours_dr:.2f}h ({avg_sick_leave_days_dr:.2f} jours)")
        summary.append(f"- Total jours complets (8h) : {total_full_days_dr} (moy. {avg_full_days_dr:.2f} par employé)")
        summary.append(f"- Total jours partiels (<8h) : {total_partial_days_dr} (moy. {avg_partial_days_dr:.2f} par employé)")
        summary.append(f"- Pourcentage jours complets : {percentage_full_days_dr:.1f}%")

        # Joindre toutes les lignes
        return "\n".join(summary)

    def _format_excel_sheets(self, writer, main_df: pd.DataFrame) -> None:
        """
        Formate les feuilles Excel

        Args:
            writer: Writer Excel
            main_df: DataFrame principal
        """
        try:
            workbook = writer.book

            # Format pour les en-têtes
            header_format = workbook.add_format({
                'bold': True,
                'text_wrap': True,
                'valign': 'top',
                'fg_color': '#D7E4BC',
                'border': 1
            })

            # Format pour les cellules de données
            cell_format = workbook.add_format({
                'text_wrap': True,
                'valign': 'top',
                'border': 1
            })

            # Formater la feuille principale
            worksheet = writer.sheets['Données']

            # Ajuster la largeur des colonnes
            for i, col in enumerate(main_df.columns):
                max_length = max(
                    main_df[col].astype(str).map(len).max(),
                    len(col)
                )
                worksheet.set_column(i, i, min(max_length + 2, 50))

            # Appliquer le format aux en-têtes
            for col_num, value in enumerate(main_df.columns.values):
                worksheet.write(0, col_num, value, header_format)

        except Exception as e:
            self.logger.warning(f"Erreur lors du formatage Excel: {str(e)}")

    def _create_classification_summary(self, classifications: Dict[str, List[PMTRecord]]) -> List[Dict[str, Any]]:
        """
        Crée un résumé des classifications pour l'export

        Args:
            classifications: Résultat de la classification

        Returns:
            Liste des données de résumé
        """
        summary_data = []

        # Résumé général
        total_records = sum(len(records) for records in classifications.values())
        total_employees = len(set(
            record.nni for records in classifications.values()
            for record in records if record.nni
        ))

        summary_data.append({
            'Catégorie': 'TOTAL GÉNÉRAL',
            'Nombre d\'employés': total_employees,
            'Nombre d\'enregistrements': total_records,
            'Pourcentage': '100%'
        })

        # Résumé par catégorie
        for category, records in classifications.items():
            if records:
                # Appliquer les règles métier pour obtenir les vrais chiffres
                filtered_records = self.classifier.filter_records_by_business_rules(records, category)

                # Compter les employés uniques avec NNI valide
                unique_employees = set()
                for record in filtered_records:
                    if record.nni:
                        unique_employees.add(record.nni)

                unique_count = len(unique_employees)
                percentage = (unique_count / total_employees * 100) if total_employees > 0 else 0

                summary_data.append({
                    'Catégorie': category,
                    'Nombre d\'employés': unique_count,
                    'Nombre d\'enregistrements': len(filtered_records),
                    'Pourcentage': f"{percentage:.1f}%"
                })
            else:
                summary_data.append({
                    'Catégorie': category,
                    'Nombre d\'employés': 0,
                    'Nombre d\'enregistrements': 0,
                    'Pourcentage': '0%'
                })

        # Ajouter les détails par agence
        summary_data.append({})  # Ligne vide
        summary_data.append({
            'Catégorie': 'RÉPARTITION PAR AGENCE',
            'Nombre d\'employés': '',
            'Nombre d\'enregistrements': '',
            'Pourcentage': ''
        })

        # Statistiques par agence
        agence_stats = self._get_agence_statistics(classifications)
        for agence, stats in agence_stats.items():
            summary_data.append({
                'Catégorie': f"  {agence}",
                'Nombre d\'employés': stats['employees'],
                'Nombre d\'enregistrements': stats['records'],
                'Pourcentage': f"{stats['percentage']:.1f}%"
            })

        return summary_data

    def _get_agence_statistics(self, classifications: Dict[str, List[PMTRecord]]) -> Dict[str, Dict[str, Any]]:
        """
        Calcule les statistiques par agence

        Args:
            classifications: Classifications des employés

        Returns:
            Statistiques par agence
        """
        agence_stats = {
            'Italie': {'employees': set(), 'records': 0},
            'Grenelle': {'employees': set(), 'records': 0},
            'Batignolles': {'employees': set(), 'records': 0},
            'Paris Est': {'employees': set(), 'records': 0},
            'Autres': {'employees': set(), 'records': 0}
        }

        total_records = 0

        for category, records in classifications.items():
            filtered_records = self.classifier.filter_records_by_business_rules(records, category)
            total_records += len(filtered_records)

            for record in filtered_records:
                equipe_lib = getattr(record, 'equipe_lib', '') or ''
                nni = record.nni

                if 'IT' in equipe_lib:
                    agence_stats['Italie']['employees'].add(nni)
                    agence_stats['Italie']['records'] += 1
                elif 'G' in equipe_lib:
                    agence_stats['Grenelle']['employees'].add(nni)
                    agence_stats['Grenelle']['records'] += 1
                elif 'B' in equipe_lib:
                    agence_stats['Batignolles']['employees'].add(nni)
                    agence_stats['Batignolles']['records'] += 1
                elif 'PE' in equipe_lib:
                    agence_stats['Paris Est']['employees'].add(nni)
                    agence_stats['Paris Est']['records'] += 1
                else:
                    agence_stats['Autres']['employees'].add(nni)
                    agence_stats['Autres']['records'] += 1

        # Convertir les sets en nombres et calculer les pourcentages
        result = {}
        for agence, stats in agence_stats.items():
            percentage = (stats['records'] / total_records * 100) if total_records > 0 else 0
            result[agence] = {
                'employees': len(stats['employees']),
                'records': stats['records'],
                'percentage': percentage
            }

        return result

    def _format_classification_sheets(self, writer, classifications: Dict[str, List[PMTRecord]]) -> None:
        """
        Formate les feuilles de classification

        Args:
            writer: Writer Excel
            classifications: Classifications des employés
        """
        try:
            workbook = writer.book

            # Formats différents pour chaque catégorie
            formats = {
                'ASTREINTES': {
                    'bg_color': '#E74C3C',  # Rouge
                    'font_color': 'white'
                },
                'TIPS': {
                    'bg_color': '#3498DB',  # Bleu
                    'font_color': 'white'
                },
                '3X8': {
                    'bg_color': '#F39C12',  # Orange
                    'font_color': 'white'
                },
                'AUTRES': {
                    'bg_color': '#27AE60',  # Vert
                    'font_color': 'white'
                }
            }

            # Appliquer le formatage à chaque feuille
            for sheet_name in writer.sheets:
                # Mapper le nom de feuille au format approprié
                format_key = 'TIPS' if sheet_name == 'HORS ASTREINTE' else sheet_name
                if format_key in formats:
                    worksheet = writer.sheets[sheet_name]

                    # Format pour les en-têtes
                    header_format = workbook.add_format({
                        'bold': True,
                        'font_color': formats[format_key]['font_color'],
                        'bg_color': formats[format_key]['bg_color'],
                        'border': 1,
                        'align': 'center',
                        'valign': 'vcenter'
                    })

                    # Appliquer le format à la première ligne
                    worksheet.set_row(0, 25, header_format)

                    # Auto-ajuster les colonnes
                    worksheet.autofit()

        except Exception as e:
            self.logger.warning(f"Erreur lors du formatage des feuilles de classification: {str(e)}")

    def _get_agence_from_equipe_lib(self, equipe_lib: str) -> str:
        """
        Détermine l'agence à partir de l'équipe_lib

        Args:
            equipe_lib: Équipe_lib de l'employé

        Returns:
            Nom de l'agence
        """
        if 'IT' in equipe_lib:
            return 'Italie'
        elif 'G' in equipe_lib:
            return 'Grenelle'
        elif 'B' in equipe_lib:
            return 'Batignolles'
        elif 'PE' in equipe_lib:
            return 'Paris Est'
        else:
            return 'Autres'

    def _get_agence_from_sdum_lib(self, sdum_lib: str) -> str:
        """
        Détermine l'agence à partir de la colonne SDUM (Lib)

        Args:
            sdum_lib: SDUM (Lib) de l'employé

        Returns:
            Nom de l'agence
        """
        if sdum_lib == 'INT ITALIE':
            return 'Italie'
        elif sdum_lib == 'INT BATIGNOLLES':
            return 'Batignolles'
        elif sdum_lib == 'INT GRENELLE':
            return 'Grenelle'
        elif sdum_lib == 'INT PARIS EST':
            return 'Paris Est'
        elif sdum_lib == 'AIS':
            return 'AIS'
        elif sdum_lib == 'ASGARD':
            return 'ASGARD'
        elif sdum_lib == 'CELL PILOT ACT':
            return 'CELL PILOT ACT'
        else:
            return 'Autres'

    def _create_charts_sheet(self, writer, classifications: Dict[str, List[PMTRecord]],
                           overtime_by_employee: Dict[str, float],
                           sick_leave_by_employee: Dict[str, Dict[str, Any]],
                           work_days_by_category: Dict[str, Dict[str, Dict[str, Any]]]) -> None:
        """
        Crée une feuille avec des graphiques statistiques

        Args:
            writer: Writer Excel
            classifications: Classifications des employés
            overtime_by_employee: Heures supplémentaires par employé
            sick_leave_by_employee: Arrêts maladie par employé
            work_days_by_category: Jours de travail par catégorie
        """
        try:
            workbook = writer.book

            # Créer une feuille pour les graphiques
            worksheet = workbook.add_worksheet('GRAPHIQUES')

            # Préparer les données pour les graphiques
            chart_data = self._prepare_chart_data(classifications, overtime_by_employee, sick_leave_by_employee, work_days_by_category)

            # 1. Graphique en barres - Heures supplémentaires ASTREINTES par agence (total)
            self._create_bar_chart_astreintes_overtime_by_agency(workbook, worksheet, classifications, overtime_by_employee, 0, 0)

            # 2. Graphique en barres - Moyenne heures supplémentaires ASTREINTES par agence
            self._create_bar_chart_astreintes_avg_overtime_by_agency(workbook, worksheet, classifications, overtime_by_employee, 0, 12)

            # 3. Graphique en barres - Heures supplémentaires 3X8 par agence (total)
            self._create_bar_chart_3x8_overtime_by_agency(workbook, worksheet, classifications, overtime_by_employee, 27, 0)

            # 4. Graphique en barres - Moyenne heures supplémentaires 3X8 par agence
            self._create_bar_chart_3x8_avg_overtime_by_agency(workbook, worksheet, classifications, overtime_by_employee, 27, 12)

            # 5. Graphique en barres - Nombre d'arrêts maladie 41 et 5H par agence
            self._create_bar_chart_sick_leaves_by_agency(workbook, worksheet, classifications, sick_leave_by_employee, 54, 0)

            # 6. Graphique en barres - Moyenne jours d'arrêt maladie par agence
            self._create_bar_chart_avg_sick_leave_days_by_agency(workbook, worksheet, classifications, sick_leave_by_employee, 54, 12)

            # 7. Graphique en barres - Nombre de périodes d'arrêt maladie par agence
            self._create_bar_chart_sick_leave_periods_by_agency(workbook, worksheet, classifications, sick_leave_by_employee, 87, 0)

            # 8. Graphique en barres - Moyenne de jours d'arrêt par période par agence
            self._create_bar_chart_avg_days_per_period_by_agency(workbook, worksheet, classifications, sick_leave_by_employee, 87, 12)

            # 9. Graphique en barres - Nombre de périodes d'arrêt par agent par agence
            self._create_bar_chart_avg_periods_per_agent_by_agency(workbook, worksheet, classifications, sick_leave_by_employee, 120, 0)

            self.logger.info("Feuille graphiques créée avec succès")

        except Exception as e:
            self.logger.error(f"Erreur lors de la création des graphiques: {str(e)}")

    def _prepare_chart_data(self, classifications: Dict[str, List[PMTRecord]],
                          overtime_by_employee: Dict[str, float],
                          sick_leave_by_employee: Dict[str, Dict[str, Any]],
                          work_days_by_category: Dict[str, Dict[str, Dict[str, Any]]]) -> Dict[str, Any]:
        """
        Prépare les données pour les graphiques

        Returns:
            Dictionnaire avec toutes les données nécessaires pour les graphiques
        """
        data = {
            'categories': {},
            'agencies': {},
            'overtime_by_category': {},
            'sick_leave_by_category': {},
            'work_days_by_category': {}
        }

        # Données par catégorie
        for category, records in classifications.items():
            filtered_records = self.classifier.filter_records_by_business_rules(records, category)
            unique_employees = set(record.nni for record in filtered_records if record.nni)

            # Nombre d'employés par catégorie
            data['categories'][category] = len(unique_employees)

            # Heures supplémentaires par catégorie
            total_overtime = sum(overtime_by_employee.get(nni, 0.0) for nni in unique_employees)
            data['overtime_by_category'][category] = total_overtime

            # Arrêts maladie par catégorie
            total_sick_leaves = 0
            for nni in unique_employees:
                if nni in sick_leave_by_employee:
                    stats = sick_leave_by_employee[nni]
                    total_sick_leaves += stats.get('classic_sick_leaves', 0) + stats.get('long_sick_leaves', 0)
            data['sick_leave_by_category'][category] = total_sick_leaves

            # Jours de travail par catégorie (seulement pour ASTREINTES et TIPS)
            if category in ['ASTREINTES', 'TIPS']:
                category_work_days = work_days_by_category.get(category, {})
                total_full_days = sum(stats.get('full_days', 0) for stats in category_work_days.values())
                total_partial_days = sum(stats.get('partial_days', 0) for stats in category_work_days.values())
                data['work_days_by_category'][category] = {
                    'full_days': total_full_days,
                    'partial_days': total_partial_days
                }

        # Données par agence
        agence_stats = self._get_agence_statistics(classifications)
        for agence, stats in agence_stats.items():
            data['agencies'][agence] = stats['employees']

        return data

    def _create_bar_chart_astreintes_overtime_by_agency(self, workbook, worksheet,
                                                      classifications: Dict[str, List[PMTRecord]],
                                                      overtime_by_employee: Dict[str, float],
                                                      row: int, col: int) -> None:
        """Crée un graphique en barres pour les heures supplémentaires des ASTREINTES par agence"""

        # Obtenir les employés ASTREINTES seulement
        astreintes_records = classifications.get('ASTREINTES', [])
        filtered_astreintes = self.classifier.filter_records_by_business_rules(astreintes_records, 'ASTREINTES')

        # Grouper les employés ASTREINTES par agence
        agence_overtime = {
            'Batignolles': 0.0,
            'Grenelle': 0.0,
            'Italie': 0.0,
            'Paris Est': 0.0
        }

        # Calculer les heures supplémentaires par agence pour les ASTREINTES uniquement
        # D'abord, grouper les employés uniques par agence
        employees_by_agency = {
            'Batignolles': set(),
            'Grenelle': set(),
            'Italie': set(),
            'Paris Est': set()
        }

        for record in filtered_astreintes:
            if record.nni:
                agence = self._get_agence_from_equipe_lib(record.equipe_lib or '')
                if agence in employees_by_agency:
                    employees_by_agency[agence].add(record.nni)

        # Ensuite, calculer le total des heures supplémentaires par agence
        for agence, employees in employees_by_agency.items():
            total_overtime = sum(overtime_by_employee.get(nni, 0.0) for nni in employees)
            agence_overtime[agence] = total_overtime

        # Écrire les données dans la feuille
        agencies = ['Batignolles', 'Grenelle', 'Italie', 'Paris Est']

        worksheet.write(row, col, 'Agence')
        worksheet.write(row, col + 1, 'Heures supplémentaires ASTREINTES')

        for i, agency in enumerate(agencies):
            overtime = agence_overtime.get(agency, 0.0)
            worksheet.write(row + 1 + i, col, agency)
            worksheet.write(row + 1 + i, col + 1, overtime if overtime != 0 else "")

        # Créer le graphique
        chart = workbook.add_chart({'type': 'column'})
        chart.add_series({
            'name': 'Heures supplémentaires ASTREINTES',
            'categories': [worksheet.name, row + 1, col, row + len(agencies), col],
            'values': [worksheet.name, row + 1, col + 1, row + len(agencies), col + 1],
            'fill': {'color': '#E74C3C'},  # Rouge pour ASTREINTES
            'data_labels': {'value': True},  # Afficher les valeurs sur les barres
        })

        chart.set_title({'name': 'Total heures supplémentaires des employés ASTREINTES par agence'})
        chart.set_x_axis({'name': 'Agence'})
        chart.set_y_axis({'name': 'Heures supplémentaires (total)'})
        chart.set_size({'width': 600, 'height': 400})  # Un peu plus grand pour la lisibilité
        worksheet.insert_chart(row + len(agencies) + 2, col, chart)

    def _create_bar_chart_astreintes_avg_overtime_by_agency(self, workbook, worksheet,
                                                          classifications: Dict[str, List[PMTRecord]],
                                                          overtime_by_employee: Dict[str, float],
                                                          row: int, col: int) -> None:
        """Crée un graphique en barres pour la moyenne des heures supplémentaires des ASTREINTES par agence"""

        # Obtenir les employés ASTREINTES seulement
        astreintes_records = classifications.get('ASTREINTES', [])
        filtered_astreintes = self.classifier.filter_records_by_business_rules(astreintes_records, 'ASTREINTES')

        # Grouper les employés ASTREINTES par agence
        employees_by_agency = {
            'Batignolles': set(),
            'Grenelle': set(),
            'Italie': set(),
            'Paris Est': set()
        }

        for record in filtered_astreintes:
            if record.nni:
                agence = self._get_agence_from_equipe_lib(record.equipe_lib or '')
                if agence in employees_by_agency:
                    employees_by_agency[agence].add(record.nni)

        # Calculer la moyenne des heures supplémentaires par agence
        agence_avg_overtime = {}
        for agence, employees in employees_by_agency.items():
            if employees:  # Éviter division par zéro
                total_overtime = sum(overtime_by_employee.get(nni, 0.0) for nni in employees)
                avg_overtime = total_overtime / len(employees)
                agence_avg_overtime[agence] = avg_overtime
            else:
                agence_avg_overtime[agence] = 0.0

        # Écrire les données dans la feuille
        agencies = ['Batignolles', 'Grenelle', 'Italie', 'Paris Est']

        worksheet.write(row, col, 'Agence')
        worksheet.write(row, col + 1, 'Moyenne heures supp ASTREINTES')

        for i, agency in enumerate(agencies):
            avg_overtime = agence_avg_overtime.get(agency, 0.0)
            worksheet.write(row + 1 + i, col, agency)
            worksheet.write(row + 1 + i, col + 1, round(avg_overtime, 2) if avg_overtime != 0 else "")  # Arrondir à 2 décimales

        # Créer le graphique
        chart = workbook.add_chart({'type': 'column'})
        chart.add_series({
            'name': 'Moyenne heures supplémentaires ASTREINTES',
            'categories': [worksheet.name, row + 1, col, row + len(agencies), col],
            'values': [worksheet.name, row + 1, col + 1, row + len(agencies), col + 1],
            'fill': {'color': '#8E44AD'},  # Violet pour différencier de la couleur rouge du total
            'data_labels': {'value': True},  # Afficher les valeurs sur les barres
        })

        chart.set_title({'name': 'Moyenne heures supplémentaires par employé ASTREINTES par agence'})
        chart.set_x_axis({'name': 'Agence'})
        chart.set_y_axis({'name': 'Heures supplémentaires (moyenne par employé)'})
        chart.set_size({'width': 600, 'height': 400})
        worksheet.insert_chart(row + len(agencies) + 2, col, chart)

    def _create_bar_chart_3x8_overtime_by_agency(self, workbook, worksheet,
                                                classifications: Dict[str, List[PMTRecord]],
                                                overtime_by_employee: Dict[str, float],
                                                row: int, col: int) -> None:
        """Crée un graphique en barres pour les heures supplémentaires des 3X8 par agence"""

        # Obtenir les employés 3X8 seulement
        three_x8_records = classifications.get('3X8', [])
        filtered_3x8 = self.classifier.filter_records_by_business_rules(three_x8_records, '3X8')

        # Grouper les employés 3X8 par agence
        employees_by_agency = {
            'Batignolles': set(),
            'Grenelle': set(),
            'Italie': set(),
            'Paris Est': set()
        }

        for record in filtered_3x8:
            if record.nni:
                agence = self._get_agence_from_equipe_lib(record.equipe_lib or '')
                if agence in employees_by_agency:
                    employees_by_agency[agence].add(record.nni)

        # Calculer le total des heures supplémentaires par agence
        agence_overtime = {}
        for agence, employees in employees_by_agency.items():
            total_overtime = sum(overtime_by_employee.get(nni, 0.0) for nni in employees)
            agence_overtime[agence] = total_overtime

        # Écrire les données dans la feuille
        agencies = ['Batignolles', 'Grenelle', 'Italie', 'Paris Est']

        worksheet.write(row, col, 'Agence')
        worksheet.write(row, col + 1, 'Heures supplémentaires 3X8')

        for i, agency in enumerate(agencies):
            overtime = agence_overtime.get(agency, 0.0)
            worksheet.write(row + 1 + i, col, agency)
            worksheet.write(row + 1 + i, col + 1, overtime if overtime != 0 else "")

        # Créer le graphique
        chart = workbook.add_chart({'type': 'column'})
        chart.add_series({
            'name': 'Heures supplémentaires 3X8',
            'categories': [worksheet.name, row + 1, col, row + len(agencies), col],
            'values': [worksheet.name, row + 1, col + 1, row + len(agencies), col + 1],
            'fill': {'color': '#F39C12'},  # Orange pour 3X8
            'data_labels': {'value': True},  # Afficher les valeurs sur les barres
        })

        chart.set_title({'name': 'Total heures supplémentaires des employés 3X8 par agence'})
        chart.set_x_axis({'name': 'Agence'})
        chart.set_y_axis({'name': 'Heures supplémentaires (total)'})
        chart.set_size({'width': 600, 'height': 400})
        worksheet.insert_chart(row + len(agencies) + 2, col, chart)

    def _create_bar_chart_3x8_avg_overtime_by_agency(self, workbook, worksheet,
                                                   classifications: Dict[str, List[PMTRecord]],
                                                   overtime_by_employee: Dict[str, float],
                                                   row: int, col: int) -> None:
        """Crée un graphique en barres pour la moyenne des heures supplémentaires des 3X8 par agence"""

        # Obtenir les employés 3X8 seulement
        three_x8_records = classifications.get('3X8', [])
        filtered_3x8 = self.classifier.filter_records_by_business_rules(three_x8_records, '3X8')

        # Grouper les employés 3X8 par agence
        employees_by_agency = {
            'Batignolles': set(),
            'Grenelle': set(),
            'Italie': set(),
            'Paris Est': set()
        }

        for record in filtered_3x8:
            if record.nni:
                agence = self._get_agence_from_equipe_lib(record.equipe_lib or '')
                if agence in employees_by_agency:
                    employees_by_agency[agence].add(record.nni)

        # Calculer la moyenne des heures supplémentaires par agence
        agence_avg_overtime = {}
        for agence, employees in employees_by_agency.items():
            if employees:  # Éviter division par zéro
                total_overtime = sum(overtime_by_employee.get(nni, 0.0) for nni in employees)
                avg_overtime = total_overtime / len(employees)
                agence_avg_overtime[agence] = avg_overtime
            else:
                agence_avg_overtime[agence] = 0.0

        # Écrire les données dans la feuille
        agencies = ['Batignolles', 'Grenelle', 'Italie', 'Paris Est']

        worksheet.write(row, col, 'Agence')
        worksheet.write(row, col + 1, 'Moyenne heures supp 3X8')

        for i, agency in enumerate(agencies):
            avg_overtime = agence_avg_overtime.get(agency, 0.0)
            worksheet.write(row + 1 + i, col, agency)
            worksheet.write(row + 1 + i, col + 1, round(avg_overtime, 2) if avg_overtime != 0 else "")  # Arrondir à 2 décimales

        # Créer le graphique
        chart = workbook.add_chart({'type': 'column'})
        chart.add_series({
            'name': 'Moyenne heures supplémentaires 3X8',
            'categories': [worksheet.name, row + 1, col, row + len(agencies), col],
            'values': [worksheet.name, row + 1, col + 1, row + len(agencies), col + 1],
            'fill': {'color': '#27AE60'},  # Vert pour différencier de l'orange du total
            'data_labels': {'value': True},  # Afficher les valeurs sur les barres
        })

        chart.set_title({'name': 'Moyenne heures supplémentaires par employé 3X8 par agence'})
        chart.set_x_axis({'name': 'Agence'})
        chart.set_y_axis({'name': 'Heures supplémentaires (moyenne par employé)'})
        chart.set_size({'width': 600, 'height': 400})
        worksheet.insert_chart(row + len(agencies) + 2, col, chart)

    def _create_bar_chart_sick_leaves_by_agency(self, workbook, worksheet,
                                              classifications: Dict[str, List[PMTRecord]],
                                              sick_leave_by_employee: Dict[str, Dict[str, Any]],
                                              row: int, col: int) -> None:
        """Crée un graphique en barres pour les arrêts maladie 41 et 5H par agence (uniquement pour les 4 agences spécifiées)"""

        # Agences spécifiques pour ce graphique
        target_agencies = ['Batignolles', 'Grenelle', 'Paris Est', 'Italie', 'AIS', 'ASGARD', 'CELL PILOT ACT']

        # Initialiser les compteurs pour chaque agence
        sick_leave_data = {}
        for agency in target_agencies:
            sick_leave_data[agency] = {
                'code_41': 0,  # Arrêts maladie classiques
                'code_5H': 0   # Arrêts maladie longs
            }

        # Regrouper tous les employés par agence (toutes catégories confondues)
        employees_by_agency = {agency: set() for agency in target_agencies}

        for category, records in classifications.items():
            filtered_records = self.classifier.filter_records_by_business_rules(records, category)

            for record in filtered_records:
                if record.nni:
                    agence = self._get_agence_from_sdum_lib(record.sdum_lib or '')
                    if agence in employees_by_agency:
                        employees_by_agency[agence].add(record.nni)

        # Calculer le nombre d'arrêts 41 et 5H par agence
        for agency, employees in employees_by_agency.items():
            for nni in employees:
                if nni in sick_leave_by_employee:
                    stats = sick_leave_by_employee[nni]
                    sick_leave_data[agency]['code_41'] += stats.get('classic_sick_leaves', 0)
                    sick_leave_data[agency]['code_5H'] += stats.get('long_sick_leaves', 0)

        # Écrire les données dans la feuille
        worksheet.write(row, col, 'Agence')
        worksheet.write(row, col + 1, 'Arrêts 41')
        worksheet.write(row, col + 2, 'Arrêts 5H')

        for i, agency in enumerate(target_agencies):
            worksheet.write(row + 1 + i, col, agency)
            worksheet.write(row + 1 + i, col + 1, sick_leave_data[agency]['code_41'] if sick_leave_data[agency]['code_41'] != 0 else "")
            worksheet.write(row + 1 + i, col + 2, sick_leave_data[agency]['code_5H'] if sick_leave_data[agency]['code_5H'] != 0 else "")

        # Créer le graphique avec deux séries de données
        chart = workbook.add_chart({'type': 'column'})

        # Série pour les arrêts 41
        chart.add_series({
            'name': 'Arrêts maladie 41',
            'categories': [worksheet.name, row + 1, col, row + len(target_agencies), col],
            'values': [worksheet.name, row + 1, col + 1, row + len(target_agencies), col + 1],
            'fill': {'color': '#E74C3C'},  # Rouge pour les arrêts 41
            'data_labels': {'value': True},
        })

        # Série pour les arrêts 5H
        chart.add_series({
            'name': 'Arrêts maladie 5H',
            'categories': [worksheet.name, row + 1, col, row + len(target_agencies), col],
            'values': [worksheet.name, row + 1, col + 2, row + len(target_agencies), col + 2],
            'fill': {'color': '#F39C12'},  # Orange pour les arrêts 5H
            'data_labels': {'value': True},
        })

        chart.set_title({'name': 'Nombre d\'arrêts maladie par agence (41 et 5H)'})
        chart.set_x_axis({'name': 'Agence'})
        chart.set_y_axis({'name': 'Nombre d\'arrêts'})
        chart.set_size({'width': 700, 'height': 450})  # Un peu plus grand pour accommoder les deux séries
        worksheet.insert_chart(row + len(target_agencies) + 2, col, chart)

    def _create_bar_chart_avg_sick_leave_days_by_agency(self, workbook, worksheet,
                                              classifications: Dict[str, List[PMTRecord]],
                                              sick_leave_by_employee: Dict[str, Dict[str, Any]],
                                              row: int, col: int) -> None:
        """Crée un graphique en barres pour la moyenne de jours d'arrêt maladie (41+5H) par employé et par agence (7 agences)"""

        target_agencies = ['Batignolles', 'Grenelle', 'Paris Est', 'Italie', 'AIS', 'ASGARD', 'CELL PILOT ACT']
        avg_sick_leave = {}
        employees_by_agency = {agency: set() for agency in target_agencies}

        # Regrouper les employés par agence
        for category, records in classifications.items():
            filtered_records = self.classifier.filter_records_by_business_rules(records, category)
            for record in filtered_records:
                if record.nni:
                    agence = self._get_agence_from_sdum_lib(record.sdum_lib or '')
                    if agence in employees_by_agency:
                        employees_by_agency[agence].add(record.nni)

        # Calculer la moyenne de jours d'arrêt par agence
        for agency, employees in employees_by_agency.items():
            total_sick_leaves = 0
            for nni in employees:
                if nni in sick_leave_by_employee:
                    stats = sick_leave_by_employee[nni]
                    total_sick_leaves += stats.get('classic_sick_leaves', 0) + stats.get('long_sick_leaves', 0)
            nb_employes = len(employees)
            avg = total_sick_leaves / nb_employes if nb_employes > 0 else 0
            avg_sick_leave[agency] = avg

        # Écrire les données dans la feuille
        worksheet.write(row, col, 'Agence')
        worksheet.write(row, col + 1, 'Moyenne jours d\'arrêt maladie par employé')
        for i, agency in enumerate(target_agencies):
            worksheet.write(row + 1 + i, col, agency)
            worksheet.write(row + 1 + i, col + 1, round(avg_sick_leave[agency], 2) if avg_sick_leave[agency] != 0 else "")

        # Créer le graphique
        chart = workbook.add_chart({'type': 'column'})
        chart.add_series({
            'name': 'Moyenne jours d\'arrêt maladie',
            'categories': [worksheet.name, row + 1, col, row + len(target_agencies), col],
            'values': [worksheet.name, row + 1, col + 1, row + len(target_agencies), col + 1],
            'fill': {'color': '#3498DB'},  # Bleu
            'data_labels': {'value': True},
        })
        chart.set_title({'name': 'Moyenne de jours d\'arrêt maladie par employé et par agence'})
        chart.set_x_axis({'name': 'Agence'})
        chart.set_y_axis({'name': 'Moyenne de jours d\'arrêt'})
        chart.set_size({'width': 700, 'height': 450})
        worksheet.insert_chart(row + len(target_agencies) + 2, col, chart)

    def _create_bar_chart_sick_leave_periods_by_agency(self, workbook, worksheet,
                                              classifications: Dict[str, List[PMTRecord]],
                                              sick_leave_by_employee: Dict[str, Dict[str, Any]],
                                              row: int, col: int) -> None:
        """Crée un graphique en barres pour le nombre total de périodes d'arrêt maladie par agence (7 agences)"""
        target_agencies = ['Batignolles', 'Grenelle', 'Paris Est', 'Italie', 'AIS', 'ASGARD', 'CELL PILOT ACT']
        periods_by_agency = {agency: 0 for agency in target_agencies}
        employees_by_agency = {agency: set() for agency in target_agencies}

        # Regrouper les employés par agence
        for category, records in classifications.items():
            filtered_records = self.classifier.filter_records_by_business_rules(records, category)
            for record in filtered_records:
                if record.nni:
                    agence = self._get_agence_from_sdum_lib(record.sdum_lib or '')
                    if agence in employees_by_agency:
                        employees_by_agency[agence].add(record.nni)

        # Additionner les périodes d'arrêt par agence
        for agency, employees in employees_by_agency.items():
            for nni in employees:
                if nni in sick_leave_by_employee:
                    stats = sick_leave_by_employee[nni]
                    periods_by_agency[agency] += stats.get('sick_leave_periods', 0)

        # Écrire les données dans la feuille
        worksheet.write(row, col, 'Agence')
        worksheet.write(row, col + 1, 'Nombre de périodes d\'arrêt maladie')
        for i, agency in enumerate(target_agencies):
            worksheet.write(row + 1 + i, col, agency)
            worksheet.write(row + 1 + i, col + 1, periods_by_agency[agency] if periods_by_agency[agency] != 0 else "")

        # Créer le graphique
        chart = workbook.add_chart({'type': 'column'})
        chart.add_series({
            'name': 'Nombre de périodes d\'arrêt maladie',
            'categories': [worksheet.name, row + 1, col, row + len(target_agencies), col],
            'values': [worksheet.name, row + 1, col + 1, row + len(target_agencies), col + 1],
            'fill': {'color': '#8E44AD'},  # Violet
            'data_labels': {'value': True},
        })
        chart.set_title({'name': 'Nombre de périodes d\'arrêt maladie par agence'})
        chart.set_x_axis({'name': 'Agence'})
        chart.set_y_axis({'name': 'Nombre de périodes'})
        chart.set_size({'width': 700, 'height': 450})
        worksheet.insert_chart(row + len(target_agencies) + 2, col, chart)

    def _create_bar_chart_avg_days_per_period_by_agency(self, workbook, worksheet,
                                              classifications: Dict[str, List[PMTRecord]],
                                              sick_leave_by_employee: Dict[str, Dict[str, Any]],
                                              row: int, col: int) -> None:
        """Crée un graphique en barres pour la moyenne de jours d'arrêt par période par agence (7 agences)"""
        target_agencies = ['Batignolles', 'Grenelle', 'Paris Est', 'Italie', 'AIS', 'ASGARD', 'CELL PILOT ACT']
        avg_days_per_period = {}
        employees_by_agency = {agency: set() for agency in target_agencies}

        # Regrouper les employés par agence
        for category, records in classifications.items():
            filtered_records = self.classifier.filter_records_by_business_rules(records, category)
            for record in filtered_records:
                if record.nni:
                    agence = self._get_agence_from_sdum_lib(record.sdum_lib or '')
                    if agence in employees_by_agency:
                        employees_by_agency[agence].add(record.nni)

        # Calculer la moyenne de jours par période par agence
        for agency, employees in employees_by_agency.items():
            total_days = 0
            total_periods = 0
            for nni in employees:
                if nni in sick_leave_by_employee:
                    stats = sick_leave_by_employee[nni]
                    total_days += stats.get('classic_sick_leaves', 0) + stats.get('long_sick_leaves', 0)
                    total_periods += stats.get('sick_leave_periods', 0)
            avg = total_days / total_periods if total_periods > 0 else 0
            avg_days_per_period[agency] = avg

        # Écrire les données dans la feuille
        worksheet.write(row, col, 'Agence')
        worksheet.write(row, col + 1, 'Moyenne jours par période')
        for i, agency in enumerate(target_agencies):
            worksheet.write(row + 1 + i, col, agency)
            worksheet.write(row + 1 + i, col + 1, round(avg_days_per_period[agency], 2) if avg_days_per_period[agency] != 0 else "")

        # Créer le graphique
        chart = workbook.add_chart({'type': 'column'})
        chart.add_series({
            'name': 'Moyenne jours par période',
            'categories': [worksheet.name, row + 1, col, row + len(target_agencies), col],
            'values': [worksheet.name, row + 1, col + 1, row + len(target_agencies), col + 1],
            'fill': {'color': '#2ECC71'},  # Vert
            'data_labels': {'value': True},
        })
        chart.set_title({'name': 'Moyenne de jours d\'arrêt par période par agence'})
        chart.set_x_axis({'name': 'Agence'})
        chart.set_y_axis({'name': 'Moyenne jours/période'})
        chart.set_size({'width': 700, 'height': 450})
        worksheet.insert_chart(row + len(target_agencies) + 2, col, chart)

    def _create_bar_chart_avg_periods_per_agent_by_agency(self, workbook, worksheet,
                                              classifications: Dict[str, List[PMTRecord]],
                                              sick_leave_by_employee: Dict[str, Dict[str, Any]],
                                              row: int, col: int) -> None:
        """Crée un graphique en barres pour la moyenne du nombre de périodes d'arrêt par agent par agence (7 agences)"""
        target_agencies = ['Batignolles', 'Grenelle', 'Paris Est', 'Italie', 'AIS', 'ASGARD', 'CELL PILOT ACT']
        avg_periods_per_agent = {}
        employees_by_agency = {agency: set() for agency in target_agencies}

        # Regrouper les employés par agence
        for category, records in classifications.items():
            filtered_records = self.classifier.filter_records_by_business_rules(records, category)
            for record in filtered_records:
                if record.nni:
                    agence = self._get_agence_from_sdum_lib(record.sdum_lib or '')
                    if agence in employees_by_agency:
                        employees_by_agency[agence].add(record.nni)

        # Calculer la moyenne de périodes par agent par agence
        for agency, employees in employees_by_agency.items():
            total_periods = 0
            nb_agents = len(employees)
            for nni in employees:
                if nni in sick_leave_by_employee:
                    stats = sick_leave_by_employee[nni]
                    total_periods += stats.get('sick_leave_periods', 0)
            avg = total_periods / nb_agents if nb_agents > 0 else None
            avg_periods_per_agent[agency] = avg

        # Écrire les données dans la feuille
        worksheet.write(row, col, 'Agence')
        worksheet.write(row, col + 1, 'Moyenne périodes d\'arrêt par agent')
        for i, agency in enumerate(target_agencies):
            value = round(avg_periods_per_agent[agency], 2) if avg_periods_per_agent[agency] not in (None, 0) else ""
            worksheet.write(row + 1 + i, col, agency)
            worksheet.write(row + 1 + i, col + 1, value)

        # Créer le graphique
        chart = workbook.add_chart({'type': 'column'})
        chart.add_series({
            'name': 'Moyenne périodes d\'arrêt par agent',
            'categories': [worksheet.name, row + 1, col, row + len(target_agencies), col],
            'values': [worksheet.name, row + 1, col + 1, row + len(target_agencies), col + 1],
            'fill': {'color': '#E67E22'},  # Orange foncé
            'data_labels': {'value': True},
        })
        chart.set_title({'name': 'Moyenne de périodes d\'arrêt par agent par agence'})
        chart.set_x_axis({'name': 'Agence'})
        chart.set_y_axis({'name': 'Moyenne périodes/agent'})
        chart.set_size({'width': 700, 'height': 450})
        worksheet.insert_chart(row + len(target_agencies) + 2, col, chart)
