"""
Application startup utilities
"""
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.database_persistence import DatabasePersistence
from app.core.logger import main_logger

def initialize_application():
    """Initialize application on startup"""
    try:
        main_logger.info("Initializing application...")
        
        # Get database session
        db = next(get_db())
        
        # Initialize database persistence
        persistence = DatabasePersistence(db)
        
        # Check and restore database if needed
        if not persistence.check_and_restore():
            main_logger.warning("Database is empty and no backup available")
        
        # Create automatic backup
        backup_file = persistence.auto_backup()
        if backup_file:
            main_logger.info(f"Auto-backup created: {backup_file}")
        
        main_logger.info("Application initialization complete")
        
    except Exception as e:
        main_logger.error(f"Failed to initialize application: {str(e)}")
        raise

def create_initial_backup():
    """Create initial backup of knowledge base"""
    try:
        main_logger.info("Creating initial backup...")
        
        db = next(get_db())
        persistence = DatabasePersistence(db)
        
        backup_file = persistence.backup_knowledge_base()
        main_logger.info(f"Initial backup created: {backup_file}")
        
        return backup_file
        
    except Exception as e:
        main_logger.error(f"Failed to create initial backup: {str(e)}")
        raise

