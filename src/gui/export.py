"""
Module de gestion de l'export Excel pour PMT Analytics.

author : CAPELLE Gabin
"""

import os
import datetime
from tkinter import filedialog, messagebox
from src.utils.excel_writer import sauvegarder_excel


class ExportManager:
    """Gestionnaire de l'export Excel."""
    
    def __init__(self, log_manager):
        self.log_manager = log_manager
    
    def export_to_excel(self, stats_final, moyennes_equipe, csv_file_path, stats_pit=None, moyennes_pit=None):
        """Exporte les résultats vers Excel avec choix du dossier de destination."""
        if stats_final is None or moyennes_equipe is None:
            messagebox.showerror("Erreur", "Aucune donnée à exporter.")
            return False
        
        try:
            # Proposer un nom de fichier par défaut basé sur la date
            date_str = datetime.datetime.now().strftime("%Y%m%d_%H%M")
            default_filename = f"Statistiques_PMT_{date_str}.xlsx"
            
            # Proposer le dossier Documents par défaut (plus sûr sur macOS)
            home_dir = os.path.expanduser("~")
            documents_dir = os.path.join(home_dir, "Documents")
            if not os.path.exists(documents_dir):
                documents_dir = home_dir  # Fallback vers le dossier utilisateur
            
            # Ouvrir la boîte de dialogue pour choisir l'emplacement et le nom
            file_path = filedialog.asksaveasfilename(
                title="Enregistrer le fichier Excel",
                defaultextension=".xlsx",
                filetypes=[
                    ("Fichiers Excel", "*.xlsx"),
                    ("Tous les fichiers", "*.*")
                ],
                initialfile=default_filename,
                initialdir=documents_dir
            )
            
            if not file_path:
                # L'utilisateur a annulé
                return False
            
            # Vérifier les permissions d'écriture avant de tenter l'export
            if not self._check_write_permissions(file_path):
                return False
            
            # Si le fichier existe déjà, vérifier qu'il n'est pas ouvert
            if not self._check_file_not_locked(file_path):
                return False
            
            # Exporter vers le fichier choisi
            sauvegarder_excel(stats_final, moyennes_equipe, file_path, stats_pit, moyennes_pit)
            
            # Message de succès avec le chemin complet
            content_msg = f"📊 Contenu : {len(stats_final)} employés, {len(moyennes_equipe)} équipes"
            if stats_pit is not None and moyennes_pit is not None:
                content_msg += f"\n📊 PIT : {len(stats_pit)} employés, {len(moyennes_pit)} équipes"
            
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