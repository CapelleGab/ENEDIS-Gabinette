"""
Module de gestion des logs structurés pour PMT Analytics.
Permet d'organiser les logs par catégorie d'employés et par agence.

author : CAPELLE Gabin
"""

import pandas as pd


class StructuredLogger:
    """
    Gestionnaire de logs structurés qui organise les données par:
    - Type d'employé (ASTREINTE, TIP, 3x8, Autres)
    - Agence (Batignole, Grenelle, Italy, Paris Est)
    - Global (Toutes agences confondues)
    """
    
    def __init__(self, log_manager=None):
        """
        Initialise le logger structuré.
        
        Args:
            log_manager: LogManager existant pour afficher les logs dans l'UI (facultatif)
        """
        self.log_manager = log_manager
        self.logs = {
            "Employés": {
                "ASTREINTE": [],
                "TIP": [],
                "3x8": [],
                "Autres": []
            },
            "Agences": {
                "Batignole": [],
                "Grenelle": [],
                "Italy": [],
                "Paris Est": []
            },
            "Global": []
        }
    
    def log(self, message, category="Global", subcategory=None):
        """
        Ajoute un message de log dans la catégorie spécifiée.
        
        Args:
            message (str): Message à logger
            category (str): Catégorie principale ("Employés", "Agences", "Global")
            subcategory (str, optional): Sous-catégorie (ex: "ASTREINTE", "Batignole")
        """
        if category == "Global":
            self.logs["Global"].append(message)
        elif category in self.logs and subcategory in self.logs[category]:
            self.logs[category][subcategory].append(message)
        
        # Afficher également dans le log_manager si disponible
        if self.log_manager:
            self.log_manager.log_message(message)
    
    def log_employee_stats(self, stats_df, category, df_type="stats"):
        """
        Ajoute des statistiques d'employés dans la catégorie appropriée.
        
        Args:
            stats_df (pd.DataFrame): DataFrame de statistiques
            category (str): Catégorie d'employés ("ASTREINTE", "TIP", "3x8", "Autres")
            df_type (str): Type de données ("stats" ou "moyennes")
        """
        if stats_df is None or stats_df.empty:
            self.log(f"Aucune donnée disponible pour {category}", "Employés", category)
            return
        
        # Nombre d'employés
        nb_employes = len(stats_df)
        self.log(f"Nombre d'employés {category}: {nb_employes}", "Employés", category)
        
        # Statistiques générales selon le type de données
        if df_type == "stats":
            if 'Total_Heures_Travaillées' in stats_df.columns:
                moy_heures = stats_df['Total_Heures_Travaillées'].mean()
                self.log(f"Moyenne d'heures travaillées {category}: {moy_heures:.1f}h", "Employés", category)
            
            if 'Présence_%_365j' in stats_df.columns:
                moy_presence = stats_df['Présence_%_365j'].mean()
                self.log(f"Taux de présence moyen {category}: {moy_presence:.1f}%", "Employés", category)
            
            if 'Heures_Supp' in stats_df.columns:
                total_hs = stats_df['Heures_Supp'].sum()
                moy_hs = stats_df['Heures_Supp'].mean() if nb_employes > 0 else 0
                self.log(f"Total heures supplémentaires {category}: {total_hs:.1f}h (moy: {moy_hs:.1f}h)", "Employés", category)
            
            if 'Nb_Périodes_Arrêts' in stats_df.columns:
                total_periodes = stats_df['Nb_Périodes_Arrêts'].sum()
                self.log(f"Total périodes d'arrêts maladie {category}: {total_periodes}", "Employés", category)
            
            if 'Nb_Jours_Arrêts_41' in stats_df.columns and 'Nb_Jours_Arrêts_5H' in stats_df.columns:
                total_jours_41 = stats_df['Nb_Jours_Arrêts_41'].sum()
                total_jours_5h = stats_df['Nb_Jours_Arrêts_5H'].sum()
                self.log(f"Total jours arrêts maladie {category}: 41={total_jours_41}, 5H={total_jours_5h}", "Employés", category)
            
            # Statistiques spécifiques 3x8
            if category == "3x8":
                if 'Postes_Matin' in stats_df.columns:
                    total_matin = stats_df['Postes_Matin'].sum()
                    self.log(f"Total postes matin {category}: {total_matin}", "Employés", category)
                
                if 'Postes_Apres_Midi' in stats_df.columns:
                    total_apres_midi = stats_df['Postes_Apres_Midi'].sum()
                    self.log(f"Total postes après-midi {category}: {total_apres_midi}", "Employés", category)
                
                if 'Postes_Nuit' in stats_df.columns:
                    total_nuit = stats_df['Postes_Nuit'].sum()
                    self.log(f"Total postes nuit {category}: {total_nuit}", "Employés", category)
    
    def log_agency_stats(self, stats_df, agency_column="FSDUM (Lib)"):
        """
        Ajoute des statistiques par agence en filtrant par la colonne d'agence.
        
        Args:
            stats_df (pd.DataFrame): DataFrame de statistiques
            agency_column (str): Nom de la colonne contenant l'agence
        """
        if stats_df is None or stats_df.empty or agency_column not in stats_df.columns:
            self.log(f"Aucune donnée d'agence disponible", "Global")
            return
        
        # Pour chaque agence connue
        for agency in ["Batignole", "Grenelle", "Italy", "Paris Est"]:
            # Filtrer les données pour cette agence
            agency_df = stats_df[stats_df[agency_column] == agency]
            
            if agency_df.empty:
                self.log(f"Aucune donnée pour l'agence {agency}", "Agences", agency)
                continue
            
            # Nombre d'employés
            nb_employes = len(agency_df)
            self.log(f"Nombre d'employés: {nb_employes}", "Agences", agency)
            
            # Statistiques générales
            if 'Total_Heures_Travaillées' in agency_df.columns:
                moy_heures = agency_df['Total_Heures_Travaillées'].mean()
                self.log(f"Moyenne d'heures travaillées: {moy_heures:.1f}h", "Agences", agency)
            
            if 'Présence_%_365j' in agency_df.columns:
                moy_presence = agency_df['Présence_%_365j'].mean()
                self.log(f"Taux de présence moyen: {moy_presence:.1f}%", "Agences", agency)
            
            if 'Heures_Supp' in agency_df.columns:
                total_hs = agency_df['Heures_Supp'].sum()
                moy_hs = agency_df['Heures_Supp'].mean() if nb_employes > 0 else 0
                self.log(f"Total heures supplémentaires: {total_hs:.1f}h (moy: {moy_hs:.1f}h)", "Agences", agency)
            
            if 'Nb_Périodes_Arrêts' in agency_df.columns:
                total_periodes = agency_df['Nb_Périodes_Arrêts'].sum()
                self.log(f"Total périodes d'arrêts maladie: {total_periodes}", "Agences", agency)
    
    def format_summary(self):
        """
        Formate tous les logs en un résumé structuré.
        
        Returns:
            str: Résumé formaté
        """
        summary = []
        
        # En-tête
        summary.extend([
            "="*80,
            "                 RÉSUMÉ DES STATISTIQUES PMT ANALYTICS",
            "="*80,
            ""
        ])
        
        # Section Employés
        summary.extend([
            "-"*80,
            "EMPLOYÉS",
            "-"*80,
            ""
        ])
        
        for employee_type, logs in self.logs["Employés"].items():
            if logs:
                summary.append(f"• {employee_type}")
                for log in logs:
                    summary.append(f"  - {log}")
                summary.append("")
        
        # Section Agences
        summary.extend([
            "-"*80,
            "AGENCES",
            "-"*80,
            ""
        ])
        
        for agency, logs in self.logs["Agences"].items():
            if logs:
                summary.append(f"• {agency}")
                for log in logs:
                    summary.append(f"  - {log}")
                summary.append("")
        
        # Section Global
        summary.extend([
            "-"*80,
            "GLOBAL",
            "-"*80,
            ""
        ])
        
        # Ajouter les logs globaux existants
        for log in self.logs["Global"]:
            summary.append(f"• {log}")
        
        # Calculer et ajouter les totaux globaux
        total_employes = 0
        total_heures_supp = 0
        total_periodes_arrets = 0
        total_jours_41 = 0
        total_jours_5h = 0
        
        # Parcourir les logs de chaque catégorie d'employés pour extraire les valeurs
        for employee_type, logs in self.logs["Employés"].items():
            for log in logs:
                # Extraire le nombre d'employés
                if "Nombre d'employés" in log:
                    try:
                        nb_employes = int(log.split(": ")[1])
                        total_employes += nb_employes
                    except (ValueError, IndexError):
                        pass
                
                # Extraire les heures supplémentaires
                if "Total heures supplémentaires" in log:
                    try:
                        hs_value = log.split(": ")[1].split("h")[0]
                        total_heures_supp += float(hs_value)
                    except (ValueError, IndexError):
                        pass
                
                # Extraire les périodes d'arrêts
                if "Total périodes d'arrêts maladie" in log:
                    try:
                        periodes = int(log.split(": ")[1])
                        total_periodes_arrets += periodes
                    except (ValueError, IndexError):
                        pass
                
                # Extraire les jours d'arrêts maladie
                if "Total jours arrêts maladie" in log and "41=" in log and "5H=" in log:
                    try:
                        jours_parts = log.split(": ")[1]
                        jours_41 = int(jours_parts.split("41=")[1].split(",")[0])
                        jours_5h = int(jours_parts.split("5H=")[1])
                        total_jours_41 += jours_41
                        total_jours_5h += jours_5h
                    except (ValueError, IndexError):
                        pass
        
        # Ajouter les totaux globaux au résumé
        if total_employes > 0:
            summary.append(f"• Total employés toutes catégories: {total_employes}")
        
        if total_heures_supp > 0:
            moy_heures_supp = total_heures_supp / total_employes if total_employes > 0 else 0
            summary.append(f"• Total heures supplémentaires: {total_heures_supp:.1f}h (moy: {moy_heures_supp:.1f}h)")
        
        if total_periodes_arrets > 0:
            summary.append(f"• Total périodes d'arrêts maladie: {total_periodes_arrets}")
        
        if total_jours_41 > 0 or total_jours_5h > 0:
            summary.append(f"• Total jours arrêts maladie: 41={total_jours_41}, 5H={total_jours_5h}")
        
        summary.append("")
        summary.append("="*80)
        
        return "\n".join(summary)
    
    def clear(self):
        """Efface tous les logs."""
        for category in self.logs:
            if isinstance(self.logs[category], list):
                self.logs[category] = []
            else:
                for subcategory in self.logs[category]:
                    self.logs[category][subcategory] = [] 