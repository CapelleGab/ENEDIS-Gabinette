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
    - DR (Direction Régionale: DR PARIS, DIR NATIONALE, etc.)
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
            "DR": {},
            "Global": []
        }
    
    def log(self, message, category="Global", subcategory=None):
        """
        Ajoute un message de log dans la catégorie spécifiée.
        
        Args:
            message (str): Message à logger
            category (str): Catégorie principale ("Employés", "DR", "Global")
            subcategory (str, optional): Sous-catégorie (ex: "ASTREINTE", "DR PARIS")
        """
        if category == "Global":
            self.logs["Global"].append(message)
        elif category in self.logs:
            if category == "DR":
                # Pour les DR, créer la sous-catégorie si elle n'existe pas
                if subcategory not in self.logs[category]:
                    self.logs[category][subcategory] = []
                self.logs[category][subcategory].append(message)
            elif subcategory in self.logs[category]:
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
    
    def log_dr_stats(self, stats_df, employee_type, dr_column="UM (Lib)"):
        """
        Ajoute des statistiques par Direction Régionale (DR) en filtrant par la colonne UM.
        
        Args:
            stats_df (pd.DataFrame): DataFrame de statistiques
            employee_type (str): Type d'employés ("ASTREINTE", "TIP", "3x8", "Autres")
            dr_column (str): Nom de la colonne contenant la Direction Régionale
        """
        if stats_df is None or stats_df.empty:
            self.log(f"Aucune donnée pour {employee_type}", "Global")
            return
            
        if dr_column not in stats_df.columns:
            self.log(f"Colonne '{dr_column}' non trouvée pour {employee_type}. Colonnes disponibles: {', '.join(stats_df.columns)}", "Global")
            return
        
        # Identifier toutes les DR présentes dans le DataFrame
        drs = stats_df[dr_column].dropna().unique()
        
        if len(drs) == 0:
            self.log(f"Aucune Direction Régionale trouvée pour {employee_type}", "Global")
            return
            
        # Message de débogage
        self.log(f"Directions Régionales trouvées pour {employee_type}: {len(drs)}", "Global")
        
        for dr in drs:
            if pd.isna(dr) or dr == "":
                continue
                
            # Filtrer les données pour cette DR
            dr_df = stats_df[stats_df[dr_column] == dr]
            
            if dr_df.empty:
                continue
            
            # Nombre d'employés
            nb_employes = len(dr_df)
            self.log(f"Nombre d'employés {employee_type}: {nb_employes}", "DR", dr)
            
            # Statistiques générales
            if 'Total_Heures_Travaillées' in dr_df.columns:
                moy_heures = dr_df['Total_Heures_Travaillées'].mean()
                self.log(f"Moyenne d'heures travaillées {employee_type}: {moy_heures:.1f}h", "DR", dr)
            
            if 'Présence_%_365j' in dr_df.columns:
                moy_presence = dr_df['Présence_%_365j'].mean()
                self.log(f"Taux de présence moyen {employee_type}: {moy_presence:.1f}%", "DR", dr)
            
            if 'Heures_Supp' in dr_df.columns:
                total_hs = dr_df['Heures_Supp'].sum()
                moy_hs = dr_df['Heures_Supp'].mean() if nb_employes > 0 else 0
                self.log(f"Total heures supplémentaires {employee_type}: {total_hs:.1f}h (moy: {moy_hs:.1f}h)", "DR", dr)
            
            if 'Nb_Périodes_Arrêts' in dr_df.columns:
                total_periodes = dr_df['Nb_Périodes_Arrêts'].sum()
                self.log(f"Total périodes d'arrêts maladie {employee_type}: {total_periodes}", "DR", dr)
                
            if 'Nb_Jours_Arrêts_41' in dr_df.columns and 'Nb_Jours_Arrêts_5H' in dr_df.columns:
                total_jours_41 = dr_df['Nb_Jours_Arrêts_41'].sum()
                total_jours_5h = dr_df['Nb_Jours_Arrêts_5H'].sum()
                self.log(f"Total jours arrêts maladie {employee_type}: 41={total_jours_41}, 5H={total_jours_5h}", "DR", dr)
    
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
        
        # Section DR (Directions Régionales) complète
        summary.extend([
            "-"*80,
            "DIRECTIONS RÉGIONALES - DÉTAILS",
            "-"*80,
            ""
        ])
        
        # Vérifier si nous avons des données pour les DR
        if not self.logs["DR"]:
            self.log("Aucune donnée par Direction Régionale disponible", "Global")
            summary.append("• Aucune donnée par Direction Régionale disponible")
            summary.append("")
        else:
            # Parcourir les DR par ordre alphabétique
            for dr in sorted(self.logs["DR"].keys()):
                logs = self.logs["DR"].get(dr, [])
                if logs:
                    summary.append(f"• {dr}")
                    
                    # Filtrer pour afficher d'abord les statistiques ASTREINTE puis les autres
                    astreinte_logs = []
                    other_logs = []
                    
                    for log in logs:
                        if "ASTREINTE" in log:
                            astreinte_logs.append(log)
                        else:
                            other_logs.append(log)
                    
                    # Afficher d'abord les statistiques ASTREINTE
                    for log in astreinte_logs:
                        summary.append(f"  - {log}")
                    
                    # Puis les autres statistiques
                    for log in other_logs:
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
                    
        # Réinitialiser le dictionnaire DR qui peut contenir des clés dynamiques
        self.logs["DR"] = {} 