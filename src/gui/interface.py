"""
Interface graphique principale pour PMT Analytics.

author : CAPELLE Gabin
"""

import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, ttk
import threading
import os

from .helpers import LogManager, show_help, show_success_message, show_error_message
from .processing import DataProcessor, SummaryDisplayer
from .export import ExportManager


class PMTAnalyticsInterface:
    """Interface graphique complète pour PMT Analytics."""
    
    def __init__(self, root):
        self.root = root
        self.csv_file_path = None
        self.stats_final = None
        self.moyennes_equipe = None
        self.stats_tip = None
        self.moyennes_tip = None
        self.stats_3x8 = None
        self.moyennes_3x8 = None
        self.summary_content = None  # Pour stocker le contenu du résumé
        
        # Initialiser les gestionnaires
        self.log_manager = None
        self.data_processor = None
        self.summary_displayer = None
        self.export_manager = None
        
        self.setup_ui()
        self._init_managers()
    
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
        
        self._create_header(main_frame)
        self._create_file_selection(main_frame)
        self._create_log_area(main_frame)
        self._create_buttons(main_frame)
    
    def _create_header(self, parent):
        """Crée l'en-tête de l'application."""
        # Titre
        title_label = ttk.Label(
            parent, 
            text="📊 PMT Analytics",
            font=('Arial', 16, 'bold')
        )
        title_label.grid(row=0, column=0, pady=(0, 10), sticky=tk.W+tk.E)
        
        # Description
        desc_label = ttk.Label(
            parent,
            text="Sélectionnez un fichier CSV de planning journalier pour analyser les statistiques.",
            justify=tk.CENTER
        )
        desc_label.grid(row=1, column=0, pady=(0, 20), sticky=tk.W+tk.E)
    
    def _create_file_selection(self, parent):
        """Crée la section de sélection de fichier."""
        file_frame = ttk.LabelFrame(parent, text="📁 Sélection du fichier", padding="15")
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
    
    def _create_log_area(self, parent):
        """Crée la zone de logs/résultats."""
        log_frame = ttk.LabelFrame(parent, text="📋 Journal d'exécution et Résultats", padding="10")
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
    
    def _create_buttons(self, parent):
        """Crée les boutons en bas de l'interface."""
        button_frame = ttk.Frame(parent)
        button_frame.grid(row=4, column=0, pady=(15, 0), sticky=tk.W+tk.E)
        
        # Bouton exporter Excel
        self.export_button = ttk.Button(
            button_frame, 
            text="💾 Exporter vers Excel", 
            command=self.export_to_excel,
            state='disabled'
        )
        self.export_button.pack(side=tk.LEFT)
        
        # Bouton exporter résumé
        self.export_summary_button = ttk.Button(
            button_frame, 
            text="📄 Exporter le résumé", 
            command=self.export_summary,
            state='disabled'
        )
        self.export_summary_button.pack(side=tk.LEFT, padx=(10, 0))
        
        # Bouton aide
        help_button = ttk.Button(button_frame, text="❓ Aide", command=show_help)
        help_button.pack(side=tk.RIGHT, padx=(10, 0))
    
    def _init_managers(self):
        """Initialise les gestionnaires après création de l'UI."""
        self.log_manager = LogManager(self.log_text, self.root)
        self.data_processor = DataProcessor(
            self.log_manager, 
            self.on_success, 
            self.on_error
        )
        self.summary_displayer = SummaryDisplayer(self.log_manager)
        self.export_manager = ExportManager(self.log_manager)
        
        # Message de bienvenue
        self.log_manager.log_message("🎉 Application prête ! Sélectionnez un fichier CSV pour commencer.")
    
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
            self.log_manager.log_message(f"✅ Fichier sélectionné : {file_path}")
    
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
        self.log_manager.clear_logs()
        self.log_manager.log_message("🚀 Démarrage du traitement...")
        
        # Lancer le traitement dans un thread séparé
        thread = threading.Thread(target=self.data_processor.process_data, args=(self.csv_file_path,))
        thread.daemon = True
        thread.start()
    
    def on_success(self, stats_final, moyennes_equipe, stats_tip=None, moyennes_tip=None, stats_3x8=None, moyennes_3x8=None):
        """Appelé quand le traitement se termine avec succès."""
        self.stats_final = stats_final
        self.moyennes_equipe = moyennes_equipe
        self.stats_tip = stats_tip
        self.moyennes_tip = moyennes_tip
        self.stats_3x8 = stats_3x8
        self.moyennes_3x8 = moyennes_3x8
        self.root.after(0, self._on_success_ui)
    
    def _on_success_ui(self):
        """Met à jour l'UI après un traitement réussi."""
        # Réactiver les boutons
        self.select_button.config(state='normal')
        self.process_button.config(state='normal')
        self.export_button.config(state='normal')
        self.export_summary_button.config(state='normal')
        self.progress.stop()
        
        # Afficher le résumé dans le journal
        self.summary_content = self.summary_displayer.display_summary(
            self.stats_final, 
            self.moyennes_equipe, 
            self.csv_file_path,
            self.stats_tip,
            self.moyennes_tip,
            self.stats_3x8,
            self.moyennes_3x8
        )
        
        # Message de succès
        show_success_message(self.stats_final, self.moyennes_equipe, self.stats_tip, self.moyennes_tip, self.stats_3x8, self.moyennes_3x8)
    
    def on_error(self, error_message):
        """Appelé quand une erreur survient pendant le traitement."""
        self.root.after(0, self._on_error_ui, error_message)
    
    def _on_error_ui(self, error_message):
        """Met à jour l'UI après une erreur."""
        self.log_manager.log_message(error_message)
        
        # Réactiver les boutons
        self.select_button.config(state='normal')
        self.process_button.config(state='normal')
        self.progress.stop()
        
        # Afficher une boîte de dialogue d'erreur
        show_error_message()
    
    def export_to_excel(self):
        """Exporte les résultats vers Excel."""
        self.export_manager.export_to_excel(
            self.stats_final, 
            self.moyennes_equipe, 
            self.csv_file_path,
            self.stats_tip,
            self.moyennes_tip,
            self.stats_3x8,
            self.moyennes_3x8
        )

    def export_summary(self):
        """Exporte le résumé vers un fichier."""
        self.export_manager.export_summary(self.summary_content) 