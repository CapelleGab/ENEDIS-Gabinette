"""
Module de gestion de l'export Excel pour PMT Analytics.

author : CAPELLE Gabin
"""

import os
import datetime
from tkinter import filedialog, messagebox
from src.utils.excel_writer import sauvegarder_excel
import pandas as pd


class ExportManager:
    """Gestionnaire de l'export Excel."""
    
    def __init__(self, log_manager):
        self.log_manager = log_manager
    
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
                content_msg += f"\n🏥 Arrêts maladie : {len(arrets_maladie_tous)} employés (tous services)"
            
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

    def export_summary(self, summary_content):
        """Exporte le résumé vers un fichier texte."""
        if not summary_content:
            messagebox.showerror("Erreur", "Aucun résumé à exporter. Veuillez d'abord lancer une analyse.")
            return False
        
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
                f"✅ Résumé exporté avec succès !\n\n"
                f"📁 Emplacement : {file_path}"
            )
            
            # Log dans l'interface
            self.log_manager.log_message(f"📄 Export résumé réussi : {file_path}")
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