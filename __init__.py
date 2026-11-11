"""maliphors-inator package."""

try:
    if __package__:
        from .maliphors_inator_logic import MalaphorGenerator
        from .maliphors_inator_ui import MaliphorsInatorApp
        from .log_manager import LogManager, log_message
    else:
        from maliphors_inator_logic import MalaphorGenerator
        from maliphors_inator_ui import MaliphorsInatorApp
        from log_manager import LogManager, log_message
except Exception:
    # Importing this package during pytest collection can happen without an active package context.
    MalaphorGenerator = None
    MaliphorsInatorApp = None
    LogManager = None
    log_message = None

__version__ = '1.0.0'
__all__ = ['MalaphorGenerator', 'MaliphorsInatorApp', 'LogManager', 'log_message']