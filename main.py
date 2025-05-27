"""
Point d'entrée principal de PMT Analytics.
Interface graphique tkinter pour l'analyse des plannings PMT d'Enedis.

author : CAPELLE Gabin
"""

import tkinter as tk
import sys
import os

# Gestion spéciale pour les exécutables PyInstaller
try:
    from src.gui import PMTAnalyticsInterface
    import config
except ImportError as e:
    # Si l'import échoue, essayer les imports directs (pour PyInstaller)
    print(f"Import src.gui échoué, tentative d'imports directs: {e}")
    try:
        from src.gui.interface import PMTAnalyticsInterface
        import config
        print("✅ Imports directs réussis")
    except ImportError as e2:
        print(f"❌ Tous les imports ont échoué: {e2}")
        # Dernière tentative avec sys.path
        if hasattr(sys, '_MEIPASS'):
            # Nous sommes dans un exécutable PyInstaller
            sys.path.insert(0, os.path.join(sys._MEIPASS, 'src', 'gui'))
            sys.path.insert(0, os.path.join(sys._MEIPASS, 'src'))
            sys.path.insert(0, sys._MEIPASS)
        try:
            from src.gui.interface import PMTAnalyticsInterface
            import config
            print("✅ Imports PyInstaller réussis")
        except ImportError as e3:
            print(f"❌ Import final échoué: {e3}")
            raise


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