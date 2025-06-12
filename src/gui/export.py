"""
Module de gestion de l'export Excel pour PMT Analytics.

author : CAPELLE Gabin
"""

import os
import datetime
from tkinter import filedialog, messagebox
from src.utils.excel_writer import sauvegarder_excel
import pandas as pd
from src.utils.structured_logger import StructuredLogger


class ExportManager:
    """Gestionnaire de l'export Excel."""

    def __init__(self, log_manager):
        self.log_manager = log_manager
        self.structured_logger = StructuredLogger(log_manager)

    def export_to_excel(self, stats_final, moyennes_equipe, csv_file_path, stats_tip=None, moyennes_tip=None, stats_3x8=None, moyennes_3x8=None, arrets_maladie_tous=None):
        """Exporte les données vers Excel."""
        if stats_final is None or moyennes_equipe is None:
            messagebox.showerror("Erreur", "Aucune donnée à exporter.")
            return False

        try:
            # Demander à l'utilisateur où sauvegarder
            file_path = filedialog.asksaveasfilename(
                title="Sauvegarder le fichier Excel",
                defaultextension=".xlsx",
                filetypes=[("Fichiers Excel", "*.xlsx"), ("Tous les fichiers", "*.*")],
                initialfile=f"Statistiques_PMT_{pd.Timestamp.now().strftime('%Y%m%d_%H%M')}.xlsx"
            )

            if not file_path:
                return False

            # Sauvegarder les données
            sauvegarder_excel(stats_final, moyennes_equipe, file_path, stats_tip, moyennes_tip, stats_3x8, moyennes_3x8, arrets_maladie_tous)

            # Message de confirmation
            content_msg = f"📊 Astreinte : {len(stats_final)} employés, {len(moyennes_equipe)} équipes"
            if stats_tip is not None and moyennes_tip is not None:
                content_msg += f"\n📊 TIP : {len(stats_tip)} employés, {len(moyennes_tip)} équipes"
            if stats_3x8 is not None and moyennes_3x8 is not None:
                content_msg += f"\n🔄 3x8 : {len(stats_3x8)} employés, {len(moyennes_3x8)} équipes"
            if arrets_maladie_tous is not None:
                content_msg += f"\n📊 TOUS : {len(arrets_maladie_tous)} employés (arrêts maladie et heures supplémentaires)"

            messagebox.showinfo(
                "Export réussi",
                f"✅ Fichier Excel exporté avec succès !\n\n"
                f"📁 Emplacement : {file_path}\n"
                f"{content_msg}"
            )

            # Log dans l'interface
            self.log_manager.log_message(f"💾 Export Excel réussi : {file_path}")
            return True

        except PermissionError as e:
            self._handle_permission_error(e)
            return False

        except OSError as e:
            self._handle_os_error(e)
            return False

        except Exception as e:
            self._handle_general_error(e)
            return False

    def _check_write_permissions(self, file_path):
        """Vérifie les permissions d'écriture."""
        directory = os.path.dirname(file_path)
        if not os.access(directory, os.W_OK):
            messagebox.showerror(
                "Erreur de permissions",
                f"❌ Impossible d'écrire dans le répertoire :\n{directory}\n\n"
                "💡 Essayez de sauvegarder dans :\n"
                "• Votre dossier Documents\n"
                "• Votre Bureau\n"
                "• Un dossier où vous avez les droits d'écriture"
            )
            return False
        return True

    def _check_file_not_locked(self, file_path):
        """Vérifie que le fichier n'est pas verrouillé."""
        if os.path.exists(file_path):
            try:
                # Tenter d'ouvrir le fichier en mode écriture pour vérifier qu'il n'est pas verrouillé
                with open(file_path, 'a'):
                    pass
            except PermissionError:
                messagebox.showerror(
                    "Fichier verrouillé",
                    f"❌ Le fichier est ouvert dans une autre application :\n{file_path}\n\n"
                    "💡 Fermez le fichier Excel et réessayez, ou choisissez un autre nom."
                )
                return False
        return True

    def _handle_permission_error(self, e):
        """Gère les erreurs de permissions."""
        self.log_manager.log_message(f"❌ Erreur de permissions : {str(e)}")
        messagebox.showerror(
            "Erreur de permissions",
            f"❌ Erreur de permissions lors de l'export :\n{str(e)}\n\n"
            "💡 Essayez de sauvegarder dans :\n"
            "• Votre dossier Documents\n"
            "• Votre Bureau\n"
            "• Un dossier où vous avez les droits d'écriture"
        )

    def _handle_os_error(self, e):
        """Gère les erreurs système."""
        self.log_manager.log_message(f"❌ Erreur système : {str(e)}")
        if e.errno == 30:  # Read-only file system
            messagebox.showerror(
                "Système de fichiers en lecture seule",
                f"❌ Système de fichiers en lecture seule :\n{str(e)}\n\n"
                "💡 Essayez de sauvegarder dans un autre emplacement."
            )
        else:
            messagebox.showerror("Erreur système", f"❌ Erreur système lors de l'export :\n{str(e)}")

    def _handle_general_error(self, e):
        """Gère les erreurs générales."""
        self.log_manager.log_message(f"❌ Erreur d'export : {str(e)}")
        messagebox.showerror("Erreur d'export", f"❌ Erreur lors de l'export :\n{str(e)}")

    def export_summary(self, stats_final, moyennes_equipe, stats_tip=None, moyennes_tip=None, stats_3x8=None, moyennes_3x8=None, arrets_maladie_tous=None):
        """
        Génère et exporte un résumé structuré des statistiques.

        Args:
            stats_final: Statistiques des employés en astreinte
            moyennes_equipe: Moyennes par équipe d'astreinte
            stats_tip: Statistiques des employés TIP
            moyennes_tip: Moyennes par équipe TIP
            stats_3x8: Statistiques des employés 3x8
            moyennes_3x8: Moyennes par équipe 3x8
            arrets_maladie_tous: Statistiques d'arrêts maladie pour tous les employés
        """
        # Réinitialiser le logger structuré
        self.structured_logger.clear()

        # Générer les statistiques pour chaque catégorie
        if stats_final is not None:
            self.structured_logger.log_employee_stats(stats_final, "ASTREINTE")

            # Générer les statistiques par DR pour ASTREINTE
            if "UM (Lib)" in stats_final.columns:
                self.log_manager.log_message(f"✅ Colonne 'UM (Lib)' trouvée dans les données ASTREINTE")
                self.structured_logger.log_dr_stats(stats_final, "ASTREINTE")
            else:
                self.log_manager.log_message(f"⚠️ Colonne 'UM (Lib)' non trouvée dans les données ASTREINTE")
                # Afficher les colonnes disponibles pour diagnostic
                self.log_manager.log_message(f"📊 Colonnes disponibles: {', '.join(stats_final.columns)}")

        if stats_tip is not None:
            self.structured_logger.log_employee_stats(stats_tip, "TIP")

            # Générer les statistiques par DR pour TIP
            if "UM (Lib)" in stats_tip.columns:
                self.log_manager.log_message(f"✅ Colonne 'UM (Lib)' trouvée dans les données TIP")
                self.structured_logger.log_dr_stats(stats_tip, "TIP")
            else:
                self.log_manager.log_message(f"⚠️ Colonne 'UM (Lib)' non trouvée dans les données TIP")

        if stats_3x8 is not None:
            self.structured_logger.log_employee_stats(stats_3x8, "3x8")

            # Générer les statistiques par DR pour 3x8
            if "UM (Lib)" in stats_3x8.columns:
                self.log_manager.log_message(f"✅ Colonne 'UM (Lib)' trouvée dans les données 3x8")
                self.structured_logger.log_dr_stats(stats_3x8, "3x8")
            else:
                self.log_manager.log_message(f"⚠️ Colonne 'UM (Lib)' non trouvée dans les données 3x8")

        if arrets_maladie_tous is not None:
            self.structured_logger.log_employee_stats(arrets_maladie_tous, "Autres")

            # Générer les statistiques par DR pour Autres
            if "UM (Lib)" in arrets_maladie_tous.columns:
                self.log_manager.log_message(f"✅ Colonne 'UM (Lib)' trouvée dans les données Autres")
                # Identifier spécifiquement la DR PARIS et mettre en évidence ses statistiques
                dr_paris = arrets_maladie_tous[arrets_maladie_tous["UM (Lib)"] == "DR PARIS"]
                if not dr_paris.empty:
                    nb_employes_paris = len(dr_paris)
                    self.log_manager.log_message(f"✅ DR PARIS: {nb_employes_paris} employés avec des arrêts maladie")

                self.structured_logger.log_dr_stats(arrets_maladie_tous, "Autres")
            else:
                self.log_manager.log_message(f"⚠️ Colonne 'UM (Lib)' non trouvée dans les données Autres")

        # Générer les statistiques par agence si la colonne FSDUM est disponible
        # Note: on vérifie les 4 DataFrames car chacun pourrait contenir la colonne FSDUM
        dfs_to_check = [df for df in [stats_final, stats_tip, stats_3x8, arrets_maladie_tous]
                         if df is not None and not df.empty]

        for df in dfs_to_check:
            if "FSDUM (Lib)" in df.columns:
                pass  # La méthode log_agency_stats a été supprimée

        # Générer les statistiques globales
        if stats_final is not None:
            total_employes = len(stats_final)
            self.structured_logger.log(f"Total employés astreinte: {total_employes}", "Global")

        if stats_tip is not None:
            total_employes_tip = len(stats_tip)
            self.structured_logger.log(f"Total employés TIP: {total_employes_tip}", "Global")

        if stats_3x8 is not None:
            total_employes_3x8 = len(stats_3x8)
            self.structured_logger.log(f"Total employés 3x8: {total_employes_3x8}", "Global")

        if arrets_maladie_tous is not None:
            total_employes_autres = len(arrets_maladie_tous)
            self.structured_logger.log(f"Total employés autres: {total_employes_autres}", "Global")

        # Formater le résumé
        summary_content = self.structured_logger.format_summary()

        try:
            # Demander à l'utilisateur où sauvegarder
            file_path = filedialog.asksaveasfilename(
                title="Sauvegarder le résumé",
                defaultextension=".txt",
                filetypes=[("Fichiers texte", "*.txt"), ("Tous les fichiers", "*.*")],
                initialfile=f"Resume_PMT_{pd.Timestamp.now().strftime('%Y%m%d_%H%M')}.txt"
            )

            if not file_path:
                return False

            # Sauvegarder le résumé
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(summary_content)

            # Message de confirmation
            messagebox.showinfo(
                "Export réussi",
                f"✅ Résumé structuré exporté avec succès !\n\n"
                f"📁 Emplacement : {file_path}"
            )

            # Log dans l'interface
            self.log_manager.log_message(f"📄 Export résumé structuré réussi : {file_path}")
            return True

        except PermissionError as e:
            self._handle_permission_error(e)
            return False

        except OSError as e:
            self._handle_os_error(e)
            return False

        except Exception as e:
            self._handle_general_error(e)
            return False
