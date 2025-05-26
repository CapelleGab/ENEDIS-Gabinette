"""
Interface graphique tkinter pour PMT Analytics.
Affiche les résultats directement dans l'interface.

author : CAPELLE Gabin
"""

import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, ttk
import threading
import os
import traceback
from pathlib import Path
import pandas as pd

# Import des fonctions du script principal
# Gestion spéciale pour les exécutables PyInstaller
try:
    from utils import (
        charger_donnees_csv,
        preparer_donnees,
        supprimer_doublons,
        appliquer_filtres_base,
        calculer_statistiques_employes,
        calculer_moyennes_equipe,
        formater_donnees_finales,
        analyser_codes_presence,
        sauvegarder_excel,
        afficher_resume_final
    )
    import config
except ImportError as e:
    # Si l'import échoue, essayer les imports directs (pour PyInstaller)
    print(f"Import utils échoué, tentative d'imports directs: {e}")
    try:
        from utils.data_loader import charger_donnees_csv, preparer_donnees, supprimer_doublons
        from utils.filtres import appliquer_filtres_base
        from utils.calculateurs import calculer_statistiques_employes, calculer_moyennes_equipe
        from utils.formatters import formater_donnees_finales, analyser_codes_presence
        from utils.excel_writer import sauvegarder_excel
        from utils.reporter import afficher_resume_final
        import config
        print("✅ Imports directs réussis")
    except ImportError as e2:
        print(f"❌ Tous les imports ont échoué: {e2}")
        # Dernière tentative avec sys.path
        import sys
        import os
        if hasattr(sys, '_MEIPASS'):
            # Nous sommes dans un exécutable PyInstaller
            sys.path.insert(0, os.path.join(sys._MEIPASS, 'utils'))
            sys.path.insert(0, sys._MEIPASS)
        try:
            from utils.data_loader import charger_donnees_csv, preparer_donnees, supprimer_doublons
            from utils.filtres import appliquer_filtres_base
            from utils.calculateurs import calculer_statistiques_employes, calculer_moyennes_equipe
            from utils.formatters import formater_donnees_finales, analyser_codes_presence
            from utils.excel_writer import sauvegarder_excel
            from utils.reporter import afficher_resume_final
            import config
            print("✅ Imports PyInstaller réussis")
        except ImportError as e3:
            print(f"❌ Import final échoué: {e3}")
            raise


class PMTAnalyticsInterface:
    """Interface graphique complète pour PMT Analytics."""
    
    def __init__(self, root):
        self.root = root
        self.csv_file_path = None
        self.stats_final = None
        self.moyennes_equipe = None
        self.setup_ui()
    
    def setup_ui(self):
        """Configure l'interface utilisateur."""
        # Configuration de la fenêtre principale
        self.root.title("📊 PMT Analytics - Analyse des Plannings")
        self.root.geometry("900x700")
        self.root.resizable(True, True)
        
        # Style
        style = ttk.Style()
        style.theme_use('clam')
        
        # Frame principal avec padding
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Configuration du redimensionnement
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(3, weight=1)
        
        # Titre
        title_label = ttk.Label(
            main_frame, 
            text="📊 PMT Analytics",
            font=('Arial', 16, 'bold')
        )
        title_label.grid(row=0, column=0, pady=(0, 10), sticky=tk.W+tk.E)
        
        # Description
        desc_label = ttk.Label(
            main_frame,
            text="Sélectionnez un fichier CSV de planning journalier pour analyser les statistiques.",
            justify=tk.CENTER
        )
        desc_label.grid(row=1, column=0, pady=(0, 20), sticky=tk.W+tk.E)
        
        # Section sélection de fichier
        file_frame = ttk.LabelFrame(main_frame, text="📁 Sélection du fichier", padding="15")
        file_frame.grid(row=2, column=0, sticky=tk.W+tk.E, pady=(0, 15))
        file_frame.columnconfigure(1, weight=1)
        
        # Bouton sélection
        self.select_button = ttk.Button(
            file_frame,
            text="🔍 Sélectionner le fichier CSV",
            command=self.select_csv_file
        )
        self.select_button.grid(row=0, column=0, padx=(0, 10))
        
        # Label fichier sélectionné
        self.file_label = ttk.Label(file_frame, text="Aucun fichier sélectionné")
        self.file_label.grid(row=0, column=1, sticky=tk.W+tk.E)
        
        # Bouton traitement
        self.process_button = ttk.Button(
            file_frame,
            text="🚀 Lancer l'analyse",
            command=self.start_processing,
            state='disabled'
        )
        self.process_button.grid(row=1, column=0, columnspan=2, pady=(15, 0), sticky=tk.W+tk.E)
        
        # Barre de progression
        self.progress = ttk.Progressbar(file_frame, mode='indeterminate')
        self.progress.grid(row=2, column=0, columnspan=2, pady=(10, 0), sticky=tk.W+tk.E)
        
        # Zone de logs/résultats
        log_frame = ttk.LabelFrame(main_frame, text="📋 Journal d'exécution et Résultats", padding="10")
        log_frame.grid(row=3, column=0, sticky=tk.W+tk.E+tk.N+tk.S, pady=(15, 0))
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        
        # Zone de texte avec scrollbar
        self.log_text = scrolledtext.ScrolledText(
            log_frame,
            height=20,
            wrap=tk.WORD,
            font=('Courier', 12)
        )
        self.log_text.grid(row=0, column=0, sticky=tk.W+tk.E+tk.N+tk.S)
        
        # Boutons en bas
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=4, column=0, pady=(15, 0), sticky=tk.W+tk.E)
        
        # Bouton exporter Excel
        self.export_button = ttk.Button(
            button_frame, 
            text="💾 Exporter vers Excel", 
            command=self.export_to_excel,
            state='disabled'
        )
        self.export_button.pack(side=tk.LEFT)
        
        # Bouton aide
        help_button = ttk.Button(button_frame, text="❓ Aide", command=self.show_help)
        help_button.pack(side=tk.RIGHT, padx=(10, 0))
        
        # Message de bienvenue
        self.log_message("🎉 Application prête ! Sélectionnez un fichier CSV pour commencer.")
    

    
    def select_csv_file(self):
        """Ouvre une boîte de dialogue pour sélectionner le fichier CSV."""
        file_path = filedialog.askopenfilename(
            title="Sélectionner le fichier CSV de planning",
            filetypes=[("Fichiers CSV", "*.csv"), ("Tous les fichiers", "*.*")]
        )
        
        if file_path:
            self.csv_file_path = file_path
            file_name = os.path.basename(file_path)
            self.file_label.config(text=f"📄 Fichier : {file_name}")
            self.process_button.config(state='normal')
            self.log_message(f"✅ Fichier sélectionné : {file_path}")
    
    def start_processing(self):
        """Lance le traitement des données en arrière-plan."""
        if not self.csv_file_path:
            messagebox.showerror("Erreur", "Veuillez d'abord sélectionner un fichier CSV.")
            return
        
        # Désactiver les boutons pendant le traitement
        self.select_button.config(state='disabled')
        self.process_button.config(state='disabled')
        self.progress.start(10)
        
        # Vider les logs précédents
        self.log_text.delete(1.0, tk.END)
        self.log_message("🚀 Démarrage du traitement...")
        
        # Lancer le traitement dans un thread séparé
        thread = threading.Thread(target=self.process_data)
        thread.daemon = True
        thread.start()
    
    def process_data(self):
        """Traite les données PMT (exécuté dans un thread séparé)."""
        try:
            # Mise à jour du chemin du fichier CSV dans la config
            import os
            absolute_path = os.path.abspath(self.csv_file_path)
            config.FICHIER_CSV = absolute_path
            
            self.log_message("🔄 Chargement des données CSV...")
            df_originel = charger_donnees_csv(config.FICHIER_CSV)
            self.log_message(f"✅ {len(df_originel)} lignes chargées")
            
            self.log_message("🔄 Préparation des données...")
            df_equipe = preparer_donnees(df_originel)
            
            self.log_message("🔄 Suppression des doublons...")
            df_unique = supprimer_doublons(df_equipe)
            
            self.log_message("🔄 Application des filtres...")
            df_filtre = appliquer_filtres_base(df_unique)
            self.log_message(f"✅ {len(df_filtre)} lignes après filtrage")
            
            self.log_message("🔄 Analyse des codes de présence...")
            codes_uniques = analyser_codes_presence(df_filtre)
            
            self.log_message("🔄 Calcul des statistiques par employé...")
            stats_employes = calculer_statistiques_employes(df_filtre)
            
            self.log_message("🔄 Formatage des données finales...")
            stats_final = formater_donnees_finales(stats_employes)
            
            self.log_message("🔄 Calcul des moyennes par équipe...")
            moyennes_equipe = calculer_moyennes_equipe(stats_final)
            
            # Stocker les résultats
            self.stats_final = stats_final
            self.moyennes_equipe = moyennes_equipe
            
            self.log_message("✅ Traitement terminé avec succès !")
            self.on_success()
            
        except Exception as e:
            error_msg = f"❌ Erreur lors du traitement :\n{str(e)}"
            self.on_error(error_msg)
    
    def on_success(self):
        """Appelé quand le traitement se termine avec succès."""
        self.root.after(0, self._on_success_ui)
    
    def _on_success_ui(self):
        """Met à jour l'UI après un traitement réussi."""
        # Réactiver les boutons
        self.select_button.config(state='normal')
        self.process_button.config(state='normal')
        self.export_button.config(state='normal')
        self.progress.stop()
        
        # Afficher le résumé dans le journal
        self.display_summary_in_log()
        
        # Message de succès
        messagebox.showinfo(
            "Traitement terminé",
            f"✅ Analyse terminée avec succès !\n\n"
            f"• {len(self.stats_final)} employés analysés\n"
            f"• {len(self.moyennes_equipe)} équipes traitées\n\n"
            f"💾 Utilisez 'Exporter vers Excel' pour sauvegarder les résultats"
        )
    
    def display_summary_in_log(self):
        """Affiche le résumé de l'analyse dans le journal d'exécution."""
        if self.stats_final is None or self.moyennes_equipe is None:
            return
        
        # Calculer les statistiques globales
        nb_employes = len(self.stats_final)
        nb_equipes = len(self.moyennes_equipe)
        
        # Statistiques générales
        moy_heures = self.stats_final['Total_Heures_Travaillées'].mean()
        moy_jours = self.stats_final['Total_Jours_Travaillés'].mean()
        moy_presence = self.stats_final['Présence_%_365j'].mean()
        
        # Top 5 employés par heures travaillées
        top_employes = self.stats_final.nlargest(5, 'Total_Heures_Travaillées')
        
        # Trouver la meilleure équipe (vérifier les colonnes disponibles)
        if not self.moyennes_equipe.empty:
            # Chercher la colonne des heures travaillées dans moyennes_equipe
            heures_col = None
            for col in self.moyennes_equipe.columns:
                if 'Heures_Travaillées' in col or 'heures' in col.lower():
                    heures_col = col
                    break
            
            if heures_col:
                best_team = self.moyennes_equipe.loc[self.moyennes_equipe[heures_col].idxmax()]
            else:
                best_team = self.moyennes_equipe.iloc[0]  # Première équipe par défaut
        
        # Ajouter le résumé au journal
        self.log_message("\n" + "="*60)
        self.log_message("📊 RÉSUMÉ DE L'ANALYSE DES STATISTIQUES PMT")
        self.log_message("="*60)
        self.log_message("")
        self.log_message("📈 STATISTIQUES GÉNÉRALES")
        self.log_message(f"• Nombre d'employés analysés : {nb_employes}")
        self.log_message(f"• Nombre d'équipes : {nb_equipes}")
        self.log_message(f"• Moyenne d'heures travaillées par employé : {moy_heures:.1f}h")
        self.log_message(f"• Moyenne de jours travaillés par employé : {moy_jours:.1f} jours")
        self.log_message(f"• Taux de présence moyen : {moy_presence:.1f}%")
        self.log_message("")
        
        self.log_message("🏆 TOP 5 EMPLOYÉS (par heures travaillées)")
        for i, (_, emp) in enumerate(top_employes.iterrows(), 1):
            self.log_message(f"{i}. {emp['Prénom']} {emp['Nom']} ({emp['Équipe']}) : {emp['Total_Heures_Travaillées']:.1f}h")
        self.log_message("")
        
        if heures_col and not self.moyennes_equipe.empty:
            self.log_message("🏢 MEILLEURE ÉQUIPE (par moyenne d'heures)")
            self.log_message(f"• {best_team['Équipe']} : {best_team[heures_col]:.1f}h en moyenne")
            if 'Nb_Employés' in best_team:
                self.log_message(f"• {best_team['Nb_Employés']:.0f} employés")
            self.log_message("")
        
        self.log_message("📋 RÉPARTITION PAR ÉQUIPE")
        for _, team in self.moyennes_equipe.iterrows():
            nb_emp = team.get('Nb_Employés', 'N/A')
            if heures_col:
                heures_moy = team[heures_col]
                self.log_message(f"• {team['Équipe']} : {nb_emp} employés, {heures_moy:.1f}h moy.")
            else:
                self.log_message(f"• {team['Équipe']} : {nb_emp} employés")
        self.log_message("")
        
        self.log_message("📁 FICHIER SOURCE")
        self.log_message(f"• {os.path.basename(self.csv_file_path)}")
        self.log_message(f"• Traité le {pd.Timestamp.now().strftime('%d/%m/%Y à %H:%M')}")
        self.log_message("")
        
        self.log_message("💾 EXPORT")
        self.log_message("• Utilisez le bouton 'Exporter vers Excel' pour sauvegarder les résultats")
        self.log_message("• Le fichier Excel contiendra tous les détails par employé et par équipe")
        self.log_message("")
        self.log_message("="*60)
    
    def export_to_excel(self):
        """Exporte les résultats vers Excel avec choix du dossier de destination."""
        if self.stats_final is None or self.moyennes_equipe is None:
            messagebox.showerror("Erreur", "Aucune donnée à exporter.")
            return
        
        try:
            # Proposer un nom de fichier par défaut basé sur la date
            import datetime
            date_str = datetime.datetime.now().strftime("%Y%m%d_%H%M")
            default_filename = f"Statistiques_PMT_{date_str}.xlsx"
            
            # Proposer le dossier Documents par défaut (plus sûr sur macOS)
            import os
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
                return
            
            # Vérifier les permissions d'écriture avant de tenter l'export
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
                return
            
            # Si le fichier existe déjà, vérifier qu'il n'est pas ouvert
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
                    return
            
            # Exporter vers le fichier choisi (passer directement le chemin)
            sauvegarder_excel(self.stats_final, self.moyennes_equipe, file_path)
            
            # Message de succès avec le chemin complet
            messagebox.showinfo(
                "Export réussi",
                f"✅ Fichier Excel exporté avec succès !\n\n"
                f"📁 Emplacement : {file_path}\n"
                f"📊 Contenu : {len(self.stats_final)} employés, {len(self.moyennes_equipe)} équipes"
            )
            
            # Log dans l'interface
            self.log_message(f"💾 Export Excel réussi : {file_path}")
            
        except PermissionError as e:
            self.log_message(f"❌ Erreur de permissions : {str(e)}")
            messagebox.showerror(
                "Erreur de permissions", 
                f"❌ Erreur de permissions lors de l'export :\n{str(e)}\n\n"
                "💡 Essayez de sauvegarder dans :\n"
                "• Votre dossier Documents\n"
                "• Votre Bureau\n"
                "• Un dossier où vous avez les droits d'écriture"
            )
            
        except OSError as e:
            self.log_message(f"❌ Erreur système : {str(e)}")
            if e.errno == 30:  # Read-only file system
                messagebox.showerror(
                    "Système de fichiers en lecture seule",
                    f"❌ Système de fichiers en lecture seule :\n{str(e)}\n\n"
                    "💡 Essayez de sauvegarder dans un autre emplacement."
                )
            else:
                messagebox.showerror("Erreur système", f"❌ Erreur système lors de l'export :\n{str(e)}")
            
        except Exception as e:
            self.log_message(f"❌ Erreur d'export : {str(e)}")
            messagebox.showerror("Erreur d'export", f"❌ Erreur lors de l'export :\n{str(e)}")
    
    def on_error(self, error_message):
        """Appelé quand une erreur survient pendant le traitement."""
        self.root.after(0, self._on_error_ui, error_message)
    
    def _on_error_ui(self, error_message):
        """Met à jour l'UI après une erreur."""
        self.log_message(error_message)
        
        # Réactiver les boutons
        self.select_button.config(state='normal')
        self.process_button.config(state='normal')
        self.progress.stop()
        
        # Afficher une boîte de dialogue d'erreur
        messagebox.showerror(
            "Erreur de traitement",
            "❌ Une erreur s'est produite pendant le traitement.\n\n"
            "Consultez le journal d'exécution pour plus de détails."
        )
    
    def log_message(self, message):
        """Ajoute un message au journal d'exécution."""
        if threading.current_thread() != threading.main_thread():
            self.root.after(0, self._log_message_ui, message)
        else:
            self._log_message_ui(message)
    
    def _log_message_ui(self, message):
        """Met à jour le journal d'exécution dans l'UI."""
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.root.update_idletasks()
    
    def show_help(self):
        """Affiche l'aide de l'application."""
        help_text = """📊 Aide - PMT Analytics

🎯 OBJECTIF :
Cette application analyse les fichiers CSV de planning journalier Enedis 
et affiche un résumé détaillé des statistiques.

📋 UTILISATION :
1. Cliquez sur "🔍 Sélectionner le fichier CSV"
2. Choisissez votre fichier de planning journalier (.csv)
3. Cliquez sur "🚀 Lancer l'analyse"
4. Consultez le résumé affiché dans le journal d'exécution

💾 EXPORT :
• "💾 Exporter vers Excel" : Choisissez l'emplacement et le nom du fichier
• "⚡ Export rapide" : Export automatique vers un emplacement sûr (Documents)
• Le fichier Excel contiendra tous les détails par employé et par équipe
• En cas d'erreur de permissions, l'export de secours sera proposé automatiquement

📊 RÉSUMÉ AFFICHÉ :
• Statistiques générales (nombre d'employés, moyennes, etc.)
• Top 5 des employés par heures travaillées
• Meilleure équipe par performance
• Répartition détaillée par équipe

⚙️ CONFIGURATION :
Les paramètres (horaires, équipes, etc.) sont configurables dans le fichier config.py

Version : 2.0 (Interface simplifiée)
Auteur : CAPELLE Gabin"""
        
        messagebox.showinfo("Aide", help_text)


def main():
    """Point d'entrée principal de l'application."""
    root = tk.Tk()
    app = PMTAnalyticsInterface(root)
    
    # Centrer la fenêtre
    root.update_idletasks()
    width = root.winfo_width()
    height = root.winfo_height()
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry(f"{width}x{height}+{x}+{y}")
    
    # Lancer l'application
    root.mainloop()


if __name__ == "__main__":
    main() 