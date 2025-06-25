"""
Fenêtre principale de l'application La Gabinette
"""

import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import ttkbootstrap as ttk_bs
from ttkbootstrap.constants import *
from pathlib import Path
from typing import Optional, List, Dict, Any
import threading
from PIL import Image, ImageTk
import io

from src.config.settings import UI_CONFIG, OUTPUT_DIR
from src.services.csv_processor import CSVProcessor
from src.services.export_service import ExportService
from src.models.data_model import PMTRecord, ProcessingResult
from src.utils.logger import logger


class MainWindow:
    """Fenêtre principale de l'application"""

    def __init__(self):
        self.logger = logger.get_logger("MainWindow")

        # Services
        self.csv_processor = CSVProcessor()
        self.export_service = ExportService()

        # État de l'application
        self.current_file_path: Optional[str] = None
        self.current_records: List[PMTRecord] = []
        self.filtered_records: List[PMTRecord] = []

        # Interface
        self.root = ttk_bs.Window(
            title=UI_CONFIG["window_title"],
            themename=UI_CONFIG["theme"],
            size=tuple(map(int, UI_CONFIG["window_size"].split('x')))
        )

        self._setup_ui()
        self._setup_bindings()
        self._center_window()

        self.logger.info("Interface utilisateur initialisée")

    def _setup_ui(self):
        """Configure l'interface utilisateur"""
        # Configuration de la grille principale
        self.root.grid_rowconfigure(1, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        # Barre d'outils
        self._create_toolbar()

        # Zone principale avec onglets
        self._create_main_area()

        # Barre de statut
        self._create_status_bar()

    def _create_toolbar(self):
        """Crée la barre d'outils avec un design moderne"""
        # Frame principal avec fond transparent
        toolbar_frame = ttk_bs.Frame(self.root)
        toolbar_frame.grid(row=0, column=0, sticky="ew", padx=8, pady=8)

        # Ajouter un padding interne
        toolbar_inner = ttk_bs.Frame(toolbar_frame)
        toolbar_inner.pack(fill="both", expand=True, padx=15, pady=10)

        # Frame pour les boutons principaux (à gauche)
        main_buttons_frame = ttk_bs.Frame(toolbar_inner)
        main_buttons_frame.pack(side=LEFT)

        # Bouton Ouvrir - Style principal avec icône moderne
        open_btn = ttk_bs.Button(
            main_buttons_frame,
            text="📂  Ouvrir CSV",
            bootstyle="primary-outline",
            command=self._open_file,
            width=15
        )
        open_btn.pack(side=LEFT, padx=(0, 8))
        self._create_tooltip(open_btn, "Ouvrir un fichier CSV pour l'analyser")

        # Séparateur avec style
        sep1 = ttk_bs.Separator(main_buttons_frame, orient=VERTICAL)
        sep1.pack(side=LEFT, fill=Y, padx=10)

        # Frame pour les boutons d'export
        export_frame = ttk_bs.Frame(main_buttons_frame)
        export_frame.pack(side=LEFT)

        # Stockage des références pour activation/désactivation
        self.toolbar_buttons = {}

        # Bouton Export Excel - Style succès
        self.toolbar_buttons["export_excel"] = ttk_bs.Button(
            export_frame,
            text="📊  Excel",
            bootstyle="success",
            command=self._export_excel,
            state=DISABLED,
            width=12
        )
        self.toolbar_buttons["export_excel"].pack(side=LEFT, padx=(0, 6))
        self._create_tooltip(self.toolbar_buttons["export_excel"], "Exporter les données vers un fichier Excel")

        # Bouton Export Résumé - Style info
        self.toolbar_buttons["export_summary"] = ttk_bs.Button(
            export_frame,
            text="📋  Résumé",
            bootstyle="info",
            command=self._export_summary,
            state=DISABLED,
            width=12
        )
        self.toolbar_buttons["export_summary"].pack(side=LEFT, padx=(0, 8))
        self._create_tooltip(self.toolbar_buttons["export_summary"], "Exporter un résumé détaillé au format texte")

        # Séparateur
        sep2 = ttk_bs.Separator(main_buttons_frame, orient=VERTICAL)
        sep2.pack(side=LEFT, fill=Y, padx=10)

        # Bouton Actualiser - Style moderne
        self.toolbar_buttons["refresh"] = ttk_bs.Button(
            main_buttons_frame,
            text="🔄  Actualiser",
            bootstyle="secondary-outline",
            command=self._refresh_data,
            state=DISABLED,
            width=13
        )
        self.toolbar_buttons["refresh"].pack(side=LEFT, padx=(0, 8))
        self._create_tooltip(self.toolbar_buttons["refresh"], "Actualiser l'affichage des données")

        # Logo Enedis (à droite)
        self._create_logo(toolbar_inner)

    def _create_logo(self, parent_frame):
        """Crée et affiche le logo Enedis"""
        try:
            # Chemin vers le logo SVG
            logo_path = Path(__file__).parent.parent.parent / "assets" / "logo" / "enedis.svg"

            if logo_path.exists():
                # Essayer d'abord avec cairosvg si disponible
                try:
                    import cairosvg
                    # Convertir SVG en PNG en mémoire
                    png_data = cairosvg.svg2png(url=str(logo_path), output_width=160, output_height=80)

                    # Charger l'image avec PIL
                    image = Image.open(io.BytesIO(png_data))
                    photo = ImageTk.PhotoImage(image)

                    # Créer le label avec l'image
                    logo_label = ttk_bs.Label(parent_frame, image=photo)
                    logo_label.image = photo  # Garder une référence
                    logo_label.pack(side=RIGHT, padx=(10, 0))

                    self.logger.info("Logo Enedis chargé avec succès")
                    return

                except ImportError:
                    # cairosvg n'est pas disponible, utiliser une approche alternative
                    self.logger.warning("cairosvg non disponible, affichage du texte à la place")

            # Fallback : afficher le nom Enedis en texte
            logo_label = ttk_bs.Label(
                parent_frame,
                text="ENEDIS",
                font=("Arial", 16, "bold"),
                foreground="#3b5ea6"  # Couleur bleue d'Enedis
            )
            logo_label.pack(side=RIGHT, padx=(10, 0))

        except Exception as e:
            self.logger.error(f"Erreur lors du chargement du logo : {e}")
            # Fallback simple
            logo_label = ttk_bs.Label(parent_frame, text="ENEDIS", font=("Arial", 14, "bold"))
            logo_label.pack(side=RIGHT, padx=(10, 0))

    def _create_tooltip(self, widget, text):
        """Crée une info-bulle pour un widget"""
        def on_enter(event):
            # Créer la tooltip
            tooltip = tk.Toplevel()
            tooltip.wm_overrideredirect(True)
            tooltip.wm_geometry(f"+{event.x_root+10}+{event.y_root+10}")

            label = tk.Label(
                tooltip,
                text=text,
                background="#ffffe0",
                relief="solid",
                borderwidth=1,
                font=("Arial", 9),
                padx=8,
                pady=4
            )
            label.pack()

            widget.tooltip = tooltip

        def on_leave(event):
            if hasattr(widget, 'tooltip'):
                widget.tooltip.destroy()
                delattr(widget, 'tooltip')

        widget.bind("<Enter>", on_enter)
        widget.bind("<Leave>", on_leave)

    def _create_main_area(self):
        """Crée la zone principale avec onglets"""
        # Notebook pour les onglets
        self.notebook = ttk_bs.Notebook(self.root)
        self.notebook.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)

        # Onglet Données
        self._create_data_tab()

        # Onglet Filtres
        self._create_filters_tab()

        # Onglet Classifications
        self._create_classification_tab()

    def _create_data_tab(self):
        """Crée l'onglet des données"""
        data_frame = ttk_bs.Frame(self.notebook)
        self.notebook.add(data_frame, text="📊 Données")

        # Configuration de la grille
        data_frame.grid_rowconfigure(1, weight=1)
        data_frame.grid_columnconfigure(0, weight=1)

        # Zone d'information du fichier
        info_frame = ttk_bs.LabelFrame(data_frame, text="Informations du fichier", padding=10)
        info_frame.grid(row=0, column=0, sticky="ew", padx=5, pady=5)

        self.file_info_text = ttk_bs.Text(info_frame, height=4, state=DISABLED)
        self.file_info_text.pack(fill=BOTH, expand=True)

        # Tableau des données
        table_frame = ttk_bs.LabelFrame(data_frame, text="Données", padding=5)
        table_frame.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)

        # Treeview avec scrollbars
        self.data_tree = ttk_bs.Treeview(table_frame, show="headings")

        # Scrollbars
        v_scrollbar = ttk_bs.Scrollbar(table_frame, orient=VERTICAL, command=self.data_tree.yview)
        h_scrollbar = ttk_bs.Scrollbar(table_frame, orient=HORIZONTAL, command=self.data_tree.xview)

        self.data_tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)

        # Placement
        self.data_tree.grid(row=0, column=0, sticky="nsew")
        v_scrollbar.grid(row=0, column=1, sticky="ns")
        h_scrollbar.grid(row=1, column=0, sticky="ew")

    def _create_filters_tab(self):
        """Crée l'onglet des filtres"""
        filters_frame = ttk_bs.Frame(self.notebook)
        self.notebook.add(filters_frame, text="🔍 Filtres")

        # Configuration de la grille
        filters_frame.grid_rowconfigure(1, weight=1)
        filters_frame.grid_columnconfigure(0, weight=1)

        # Zone des contrôles de filtre
        controls_frame = ttk_bs.LabelFrame(filters_frame, text="Filtres", padding=10)
        controls_frame.grid(row=0, column=0, sticky="ew", padx=5, pady=5)

        # Filtres par équipe
        ttk_bs.Label(controls_frame, text="Équipe:").grid(row=0, column=0, sticky="w", padx=(0, 5))
        self.team_filter = ttk_bs.Combobox(controls_frame, state="readonly")
        self.team_filter.grid(row=0, column=1, sticky="ew", padx=(0, 10))

        # Filtres par nom
        ttk_bs.Label(controls_frame, text="Nom:").grid(row=0, column=2, sticky="w", padx=(0, 5))
        self.name_filter = ttk_bs.Entry(controls_frame)
        self.name_filter.grid(row=0, column=3, sticky="ew", padx=(0, 10))

        # Filtres par date
        ttk_bs.Label(controls_frame, text="Date:").grid(row=1, column=0, sticky="w", padx=(0, 5), pady=(5, 0))
        self.date_filter = ttk_bs.Entry(controls_frame)
        self.date_filter.grid(row=1, column=1, sticky="ew", padx=(0, 10), pady=(5, 0))

        # Ajouter un placeholder manuel
        self.date_filter.insert(0, "JJ/MM/AAAA")
        self.date_filter.bind("<FocusIn>", self._on_date_filter_focus_in)
        self.date_filter.bind("<FocusOut>", self._on_date_filter_focus_out)
        self.date_filter.config(foreground="gray")

        # Boutons de filtre
        button_frame = ttk_bs.Frame(controls_frame)
        button_frame.grid(row=1, column=2, columnspan=2, sticky="e", pady=(5, 0))

        ttk_bs.Button(
            button_frame,
            text="Appliquer",
            bootstyle=PRIMARY,
            command=self._apply_filters
        ).pack(side=RIGHT, padx=(5, 0))

        ttk_bs.Button(
            button_frame,
            text="Réinitialiser",
            bootstyle=SECONDARY,
            command=self._reset_filters
        ).pack(side=RIGHT)

        # Configuration des colonnes
        controls_frame.grid_columnconfigure(1, weight=1)
        controls_frame.grid_columnconfigure(3, weight=1)

        # Zone des résultats filtrés
        results_frame = ttk_bs.LabelFrame(filters_frame, text="Résultats filtrés", padding=5)
        results_frame.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        results_frame.grid_rowconfigure(0, weight=1)
        results_frame.grid_columnconfigure(0, weight=1)

        # Treeview pour les résultats filtrés
        self.filtered_tree = ttk_bs.Treeview(results_frame, show="headings")

        # Scrollbars pour les résultats filtrés
        v_scrollbar_filtered = ttk_bs.Scrollbar(results_frame, orient=VERTICAL, command=self.filtered_tree.yview)
        h_scrollbar_filtered = ttk_bs.Scrollbar(results_frame, orient=HORIZONTAL, command=self.filtered_tree.xview)

        self.filtered_tree.configure(yscrollcommand=v_scrollbar_filtered.set, xscrollcommand=h_scrollbar_filtered.set)

        # Placement
        self.filtered_tree.grid(row=0, column=0, sticky="nsew")
        v_scrollbar_filtered.grid(row=0, column=1, sticky="ns")
        h_scrollbar_filtered.grid(row=1, column=0, sticky="ew")


    def _create_classification_tab(self):
        """Crée l'onglet des classifications d'employés"""
        classification_frame = ttk_bs.Frame(self.notebook)
        self.notebook.add(classification_frame, text="👥 Classifications")

        # Configuration de la grille
        classification_frame.grid_rowconfigure(1, weight=1)
        classification_frame.grid_columnconfigure(0, weight=1)

        # Zone de résumé des classifications
        summary_frame = ttk_bs.LabelFrame(classification_frame, text="Résumé des classifications", padding=10)
        summary_frame.grid(row=0, column=0, sticky="ew", padx=5, pady=5)

        self.classification_summary_text = ttk_bs.Text(summary_frame, height=8, state=DISABLED)
        self.classification_summary_text.pack(fill=BOTH, expand=True)

        # Zone des graphiques
        charts_frame = ttk_bs.LabelFrame(classification_frame, text="Graphiques", padding=10)
        charts_frame.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)

        ttk_bs.Label(
            charts_frame,
            text="📊 Zone réservée aux graphiques de classification\n(Fonctionnalité à développer)",
            font=("Arial", 12),
            foreground="gray"
        ).pack(expand=True)

    def _create_status_bar(self):
        """Crée la barre de statut"""
        status_frame = ttk_bs.Frame(self.root)
        status_frame.grid(row=2, column=0, sticky="ew", padx=5, pady=5)

        self.status_label = ttk_bs.Label(
            status_frame,
            text="Prêt - Aucun fichier chargé",
            relief=SUNKEN,
            anchor=W
        )
        self.status_label.pack(side=LEFT, fill=X, expand=True)

        # Barre de progression
        self.progress_bar = ttk_bs.Progressbar(
            status_frame,
            mode='indeterminate',
            bootstyle=INFO
        )
        self.progress_bar.pack(side=RIGHT, padx=(5, 0))

    def _setup_bindings(self):
        """Configure les liaisons d'événements"""
        # Liaison pour la fermeture de l'application
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)

        # Liaisons pour les filtres
        self.name_filter.bind('<KeyRelease>', self._on_filter_change)
        self.date_filter.bind('<KeyRelease>', self._on_filter_change)
        self.team_filter.bind('<<ComboboxSelected>>', self._on_filter_change)

    def _open_file(self):
        """Ouvre un fichier CSV"""
        file_path = filedialog.askopenfilename(
            title="Sélectionner un fichier CSV",
            filetypes=[("Fichiers CSV", "*.csv"), ("Tous les fichiers", "*.*")],
            initialdir=str(Path.home())
        )

        if file_path:
            self._load_file_async(file_path)

    def _load_file_async(self, file_path: str):
        """Charge un fichier de manière asynchrone"""
        self._set_loading_state(True)
        self.status_label.config(text=f"Chargement de {Path(file_path).name}...")

        def load_worker():
            try:
                result = self.csv_processor.load_file(file_path)
                self.root.after(0, lambda: self._on_file_loaded(result, file_path))
            except Exception as e:
                self.root.after(0, lambda: self._on_file_error(str(e)))

        thread = threading.Thread(target=load_worker, daemon=True)
        thread.start()

    def _on_file_loaded(self, result: ProcessingResult, file_path: str):
        """Callback appelé quand le fichier est chargé"""
        self._set_loading_state(False)

        if result.success:
            self.current_file_path = file_path
            self.current_records = self.csv_processor.get_records()
            self.filtered_records = self.current_records.copy()

            self._update_file_info(result)
            self._update_data_display()
            self._update_filters()
            self._update_classifications()
            self._enable_toolbar_buttons()

            self.status_label.config(
                text=f"Fichier chargé: {result.records_processed} enregistrements"
            )

            self.logger.info(f"Fichier chargé avec succès: {file_path}")
        else:
            messagebox.showerror(
                "Erreur de chargement",
                f"Impossible de charger le fichier:\n{result.error_message}"
            )
            self.status_label.config(text="Erreur de chargement")

    def _on_file_error(self, error_message: str):
        """Callback appelé en cas d'erreur de chargement"""
        self._set_loading_state(False)
        messagebox.showerror("Erreur", f"Erreur lors du chargement:\n{error_message}")
        self.status_label.config(text="Erreur de chargement")

    def _set_loading_state(self, loading: bool):
        """Active/désactive l'état de chargement"""
        if loading:
            self.progress_bar.start()
            self.root.config(cursor="wait")
        else:
            self.progress_bar.stop()
            self.root.config(cursor="")

    def _update_file_info(self, result: ProcessingResult):
        """Met à jour les informations du fichier"""
        info_text = f"""Fichier: {result.file_info.name}
Taille: {result.file_info.size_formatted}
Modifié: {result.file_info.modified.strftime('%d/%m/%Y %H:%M:%S') if result.file_info.modified else 'N/A'}
Enregistrements traités: {result.records_processed}
Enregistrements valides: {result.records_valid}
Avertissements: {result.records_with_warnings}
Erreurs: {result.records_with_errors}
Temps de traitement: {result.processing_time:.2f}s"""

        self.file_info_text.config(state=NORMAL)
        self.file_info_text.delete(1.0, tk.END)
        self.file_info_text.insert(1.0, info_text)
        self.file_info_text.config(state=DISABLED)

    def _update_data_display(self):
        """Met à jour l'affichage des données"""
        # Effacer les données existantes
        for item in self.data_tree.get_children():
            self.data_tree.delete(item)

        if not self.current_records:
            return

        # Configurer les colonnes (afficher seulement les principales)
        main_columns = ["nom", "prenom", "equipe_lib", "jour", "designation_jour", "valeur", "des_unite"]
        column_headers = ["Nom", "Prénom", "Équipe", "Date", "Jour", "Valeur", "Unité"]

        self.data_tree["columns"] = main_columns

        for col, header in zip(main_columns, column_headers):
            self.data_tree.heading(col, text=header)
            self.data_tree.column(col, width=120)

        # Ajouter les données
        for record in self.current_records[:1000]:  # Limiter à 1000 pour les performances
            values = []
            for col in main_columns:
                value = getattr(record, col, None)
                # Gérer les valeurs None et les convertir en chaîne
                if value is None:
                    values.append("")
                else:
                    values.append(str(value))
            self.data_tree.insert("", tk.END, values=values)

    def _update_filters(self):
        """Met à jour les options de filtres"""
        if not self.current_records:
            return

        # Mettre à jour les équipes disponibles
        teams = sorted(set(record.equipe_lib for record in self.current_records if record.equipe_lib))
        self.team_filter["values"] = ["Toutes"] + teams
        self.team_filter.set("Toutes")



    def _update_classifications(self):
        """Met à jour l'affichage des classifications d'employés"""
        if not self.current_records:
            return

        try:
            # Obtenir les classifications
            classifications = self.csv_processor.get_classifications()

            # Mettre à jour le résumé
            self._update_classification_summary(classifications)

        except Exception as e:
            self.logger.error(f"Erreur lors de la mise à jour des classifications: {str(e)}")

    def _update_classification_summary(self, classifications: Dict[str, List[PMTRecord]]):
        """Met à jour le résumé des classifications"""
        try:
            summary = self.csv_processor.get_classification_summary()

            summary_text = "RÉSUMÉ DES CLASSIFICATIONS D'EMPLOYÉS\n"
            summary_text += "=" * 60 + "\n\n"

            # Statistiques générales
            total_employees = sum(data.get('nombre_employes', 0) for data in summary.values())
            total_records = sum(data.get('nombre_enregistrements', 0) for data in summary.values())

            summary_text += f"Total employés classifiés: {total_employees}\n"
            summary_text += f"Total enregistrements: {total_records}\n\n"

            # Détails par catégorie
            for category, data in summary.items():
                summary_text += f"{category}:\n"
                summary_text += f"  • Employés: {data.get('nombre_employes', 0)}\n"
                summary_text += f"  • Enregistrements: {data.get('nombre_enregistrements', 0)}\n"
                summary_text += f"  • Pourcentage: {data.get('nombre_enregistrements', 0) / total_records * 100:.1f}%\n"

                # Répartition par agence
                agences = data.get('repartition_agences', {})
                if agences:
                    summary_text += "  • Répartition par agence:\n"
                    for agence, count in agences.items():
                        if count > 0:
                            summary_text += f"    - {agence}: {count}\n"
                summary_text += "\n"

            # Mettre à jour le widget texte
            self.classification_summary_text.config(state=NORMAL)
            self.classification_summary_text.delete(1.0, tk.END)
            self.classification_summary_text.insert(1.0, summary_text)
            self.classification_summary_text.config(state=DISABLED)

        except Exception as e:
            self.logger.error(f"Erreur lors de la mise à jour du résumé: {str(e)}")



    def _get_agence_from_equipe(self, equipe_lib: str) -> str:
        """Détermine l'agence à partir du libellé d'équipe"""
        if not equipe_lib:
            return "Inconnue"

        equipe_lib = equipe_lib.upper()
        if 'IT' in equipe_lib:
            return "Italie"
        elif 'G' in equipe_lib and 'G' != equipe_lib:  # Éviter les faux positifs
            return "Grenelle"
        elif 'B' in equipe_lib:
            return "Batignolles"
        elif 'PE' in equipe_lib:
            return "Paris Est"
        else:
            return "Autre"

    def _apply_filters(self):
        """Applique les filtres sélectionnés"""
        if not self.current_records:
            return

        filters = {}

        # Filtre par équipe
        team = self.team_filter.get()
        if team and team != "Toutes":
            filters["equipe_lib"] = team

        # Filtre par nom
        name = self.name_filter.get().strip()
        if name:
            # Recherche partielle dans nom ou prénom
            self.filtered_records = [
                record for record in self.current_records
                if name.lower() in record.nom.lower() or name.lower() in record.prenom.lower()
            ]
        else:
            self.filtered_records = self.current_records.copy()

        # Appliquer les autres filtres
        if filters:
            self.filtered_records = self.csv_processor.filter_records(**filters)

        # Filtre par date
        date = self.date_filter.get().strip()
        if date and date != "JJ/MM/AAAA":
            self.filtered_records = [
                record for record in self.filtered_records
                if date in record.jour
            ]

        self._update_filtered_display()
        self.status_label.config(text=f"Filtres appliqués: {len(self.filtered_records)} enregistrements")

    def _reset_filters(self):
        """Réinitialise tous les filtres"""
        self.team_filter.set("Toutes")
        self.name_filter.delete(0, tk.END)
        self.date_filter.delete(0, tk.END)
        self.date_filter.insert(0, "JJ/MM/AAAA")
        self.date_filter.config(foreground="gray")

        self.filtered_records = self.current_records.copy()
        self._update_filtered_display()
        self.status_label.config(text="Filtres réinitialisés")

    def _on_filter_change(self, event=None):
        """Callback appelé quand un filtre change"""
        # Auto-application des filtres après un délai
        self.root.after(500, self._apply_filters)

    def _on_date_filter_focus_in(self, event):
        """Appelé quand le champ date reçoit le focus"""
        if self.date_filter.get() == "JJ/MM/AAAA":
            self.date_filter.delete(0, tk.END)
            self.date_filter.config(foreground="black")

    def _on_date_filter_focus_out(self, event):
        """Appelé quand le champ date perd le focus"""
        if not self.date_filter.get().strip():
            self.date_filter.insert(0, "JJ/MM/AAAA")
            self.date_filter.config(foreground="gray")

    def _update_filtered_display(self):
        """Met à jour l'affichage des données filtrées"""
        # Effacer les données existantes
        for item in self.filtered_tree.get_children():
            self.filtered_tree.delete(item)

        if not self.filtered_records:
            return

        # Configurer les colonnes (mêmes que l'onglet principal)
        main_columns = ["nom", "prenom", "equipe_lib", "jour", "designation_jour", "valeur", "des_unite"]
        column_headers = ["Nom", "Prénom", "Équipe", "Date", "Jour", "Valeur", "Unité"]

        self.filtered_tree["columns"] = main_columns

        for col, header in zip(main_columns, column_headers):
            self.filtered_tree.heading(col, text=header)
            self.filtered_tree.column(col, width=120)

        # Ajouter les données filtrées
        for record in self.filtered_records[:1000]:  # Limiter pour les performances
            values = []
            for col in main_columns:
                value = getattr(record, col, None)
                # Gérer les valeurs None et les convertir en chaîne
                if value is None:
                    values.append("")
                else:
                    values.append(str(value))
            self.filtered_tree.insert("", tk.END, values=values)

    def _enable_toolbar_buttons(self):
        """Active les boutons de la barre d'outils"""
        for button in self.toolbar_buttons.values():
            button.config(state=NORMAL)

    def _export_excel(self):
        """Exporte vers Excel"""
        if not self.current_records:
            return

        try:
            records_to_export = self.filtered_records if self.filtered_records != self.current_records else self.current_records
            export_path = self.export_service.export_to_excel(records_to_export, use_file_dialog=True)
            messagebox.showinfo("Export réussi", f"Fichier exporté vers:\n{export_path}")
            self.logger.info(f"Export Excel réussi: {export_path}")

        except Exception as e:
            if "annulé par l'utilisateur" not in str(e):
                messagebox.showerror("Erreur d'export", f"Erreur lors de l'export Excel:\n{str(e)}")
                self.logger.error(f"Erreur export Excel: {str(e)}")
            # Si l'export est annulé, on ne fait rien (pas d'erreur)

    def _export_summary(self):
        """Exporte le résumé vers un fichier texte"""
        if not self.current_records:
            return

        try:
            records_to_export = self.filtered_records if self.filtered_records != self.current_records else self.current_records
            summary_path = self.export_service.export_summary_to_text(records_to_export, use_file_dialog=True)
            messagebox.showinfo("Export réussi", f"Résumé exporté vers:\n{summary_path}")
            self.logger.info(f"Export résumé réussi: {summary_path}")

        except Exception as e:
            if "annulé par l'utilisateur" not in str(e):
                messagebox.showerror("Erreur d'export", f"Erreur lors de l'export résumé:\n{str(e)}")
                self.logger.error(f"Erreur export résumé: {str(e)}")
            # Si l'export est annulé, on ne fait rien (pas d'erreur)

    def _refresh_data(self):
        """Actualise les données"""
        if self.current_file_path:
            self._load_file_async(self.current_file_path)

    def _on_closing(self):
        """Callback appelé à la fermeture de l'application"""
        self.logger.info("Fermeture de l'application")
        self.root.destroy()

    def _center_window(self):
        """Centre la fenêtre sur l'écran"""
        # Mettre à jour la fenêtre pour obtenir les dimensions correctes
        self.root.update_idletasks()

        # Obtenir les dimensions de la fenêtre
        window_width = self.root.winfo_width()
        window_height = self.root.winfo_height()

        # Obtenir les dimensions de l'écran
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        # Calculer la position pour centrer la fenêtre
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2

        # Positionner la fenêtre
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")

        self.logger.info(f"Fenêtre centrée à la position ({x}, {y})")

    def run(self):
        """Lance l'application"""
        self.logger.info("Démarrage de l'application")
        self.root.mainloop()
