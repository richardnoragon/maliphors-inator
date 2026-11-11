"""maliphors-inator core exports; Qt utilities are optional."""
from app_version import __version__
from maliphors_inator_logic import MalaphorGenerator
from maliphors_inator_ui import MaliphorsInatorApp

__all__ = ['MalaphorGenerator', 'MaliphorsInatorApp', '__version__']
