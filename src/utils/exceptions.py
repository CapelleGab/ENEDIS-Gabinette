"""
Exceptions personnalisées pour PMT Analytics.

Author: CAPELLE Gabin
Version: 2.0.0
"""


class PMTAnalyticsError(Exception):
    """Exception de base pour PMT Analytics."""
    pass


class DataValidationError(PMTAnalyticsError):
    """Exception levée lors d'erreurs de validation des données."""
    pass


class DataProcessingError(PMTAnalyticsError):
    """Exception levée lors d'erreurs de traitement des données."""
    pass


class ConfigurationError(PMTAnalyticsError):
    """Exception levée lors d'erreurs de configuration."""
    pass


class FileOperationError(PMTAnalyticsError):
    """Exception levée lors d'erreurs d'opérations sur les fichiers."""
    pass


class CalculationError(PMTAnalyticsError):
    """Exception levée lors d'erreurs de calcul."""
    pass


class ExportError(PMTAnalyticsError):
    """Exception levée lors d'erreurs d'export."""
    pass
