"""
Fonctions utilitaires pour l'interface PMT Analytics.

author : CAPELLE Gabin
"""

import tkinter as tk
from tkinter import messagebox
import threading


class LogManager:
    """Gestionnaire des logs pour l'interface."""
    
    def __init__(self, log_text_widget, root):
        self.log_text = log_text_widget
        self.root = root
    
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
    
    def clear_logs(self):
        """Vide les logs."""
        self.log_text.delete(1.0, tk.END)


def show_help():
    """Affiche l'aide de l'application."""
    help_text = """📊 Aide - PMT Analytics v2.0.0

🎯 OBJECTIF :
Cette application analyse les fichiers CSV de planning journalier Enedis 
et affiche un résumé détaillé des statistiques pour les équipes d'astreinte, 
TIP (hors astreinte) et 3x8.

📋 UTILISATION :
1. Cliquez sur "🔍 Sélectionner le fichier CSV"
2. Choisissez votre fichier de planning journalier (.csv)
3. Cliquez sur "🚀 Lancer l'analyse"
4. Consultez le résumé affiché dans le journal d'exécution

💾 EXPORT :
• "💾 Exporter vers Excel" : Données complètes avec 6 feuilles détaillées
• "📄 Exporter le résumé" : Résumé de l'analyse en fichier texte (NOUVEAU)
• En cas d'erreur de permissions, essayez de sauvegarder dans Documents

📊 RÉSUMÉ AFFICHÉ :
• Statistiques générales (nombre d'employés, moyennes, etc.)
• Top 5 des employés par heures travaillées (Astreinte)
• Top 3 des employés TIP et 3x8
• Meilleure équipe par performance
• Répartition détaillée par équipe
• Statistiques spécifiques 3x8 (postes matin/après-midi/nuit)

🔧 FILTRAGE AUTOMATIQUE :
• Astreinte : Supprime les employés avec < 50 jours présents complets
• TIP : Supprime les employés avec < 55 jours présents complets
• 3x8 : Pas de filtrage appliqué

⚙️ CONFIGURATION :
Les paramètres (horaires, équipes, etc.) sont configurables dans le fichier config.py

Version : v2.0.0
Auteur : CAPELLE Gabin - Enedis"""
    
    messagebox.showinfo("Aide", help_text)


def show_success_message(stats_final, moyennes_equipe, stats_tip=None, moyennes_tip=None, stats_3x8=None, moyennes_3x8=None):
    """Affiche un message de succès avec les statistiques."""
    message = (f"✅ Traitement terminé avec succès !\n\n"
               f"📊 Résultats :\n"
               f"• {len(stats_final)} employés analysés (Astreinte)\n"
               f"• {len(moyennes_equipe)} équipes traitées (Astreinte)")
    
    if stats_tip is not None and moyennes_tip is not None:
        message += (f"\n• {len(stats_tip)} employés analysés (TIP)\n"
                   f"• {len(moyennes_tip)} équipes traitées (TIP)")
    
    if stats_3x8 is not None and moyennes_3x8 is not None:
        message += (f"\n• {len(stats_3x8)} employés analysés (3x8)\n"
                   f"• {len(moyennes_3x8)} équipes traitées (3x8)")
    
    message += ("\n\n💾 OPTIONS D'EXPORT :\n"
               "• 'Exporter vers Excel' : Données complètes et détaillées\n"
               "• 'Exporter le résumé' : Résumé de l'analyse en texte")
    
    messagebox.showinfo("Traitement terminé", message)


def show_error_message():
    """Affiche le message d'erreur."""
    messagebox.showerror(
        "Erreur de traitement",
        "❌ Une erreur s'est produite pendant le traitement.\n\n"
        "Consultez le journal d'exécution pour plus de détails."
     ) 