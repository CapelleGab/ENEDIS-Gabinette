"""
Point d'entrée principal de PMT Analytics.
Interface graphique tkinter pour l'analyse des plannings PMT d'Enedis.

Author: CAPELLE Gabin
Version: 2.0.0
"""

import sys
import logging
from pathlib import Path

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def setup_paths():
    """Configure les chemins d'importation pour l'application."""
    # Ajouter le répertoire racine au path
    root_dir = Path(__file__).parent
    if str(root_dir) not in sys.path:
        sys.path.insert(0, str(root_dir))

    # Gestion spéciale pour PyInstaller
    if hasattr(sys, '_MEIPASS'):
        bundle_dir = Path(sys._MEIPASS)
        sys.path.insert(0, str(bundle_dir))
        sys.path.insert(0, str(bundle_dir / 'src'))


def import_dependencies():
    """Importe les dépendances nécessaires avec gestion d'erreurs."""
    try:
        import tkinter as tk
        from src.gui.interface import PMTAnalyticsInterface
        return tk, PMTAnalyticsInterface
    except ImportError as e:
        logger.error(f"Erreur d'importation: {e}")
        logger.error("Vérifiez que tous les modules sont installés correctement")
        raise


def center_window(root):
    """Centre la fenêtre sur l'écran."""
    root.update_idletasks()
    width = root.winfo_width()
    height = root.winfo_height()
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry(f"{width}x{height}+{x}+{y}")


def main():
    """Point d'entrée principal de l'application."""
    try:
        logger.info("Démarrage de PMT Analytics")

        # Configuration des chemins
        setup_paths()

        # Import des dépendances
        tk, PMTAnalyticsInterface = import_dependencies()

        # Création de l'interface
        root = tk.Tk()
        app = PMTAnalyticsInterface(root)

        # Configuration de la fenêtre
        center_window(root)

        # Gestion de la fermeture propre
        def on_closing():
            logger.info("Fermeture de l'application")
            root.destroy()

        root.protocol("WM_DELETE_WINDOW", on_closing)

        # Lancement de l'application
        logger.info("Interface graphique initialisée")
        root.mainloop()

    except Exception as e:
        logger.error(f"Erreur fatale: {e}")
        # Affichage d'un message d'erreur simple si tkinter n'est pas disponible
        try:
            import tkinter.messagebox as messagebox
            messagebox.showerror(
                "Erreur fatale",
                f"Impossible de démarrer l'application:\n{e}"
            )
        except ImportError:
            print(f"Erreur fatale: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
