import logging
import os
from datetime import datetime
from pathlib import Path

def setup_logger(name: str = "solana_rfp", level: str = "INFO") -> logging.Logger:
    """Setup comprehensive logging for the application"""
    
    # Create logs directory if it doesn't exist
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper()))
    
    # Clear existing handlers
    logger.handlers.clear()
    
    # Create formatters
    detailed_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(funcName)s - %(message)s'
    )
    
    simple_formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s'
    )
    
    # File handler for all logs
    all_logs_file = log_dir / "all.log"
    file_handler = logging.FileHandler(all_logs_file)
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(detailed_formatter)
    logger.addHandler(file_handler)
    
    # File handler for errors only
    error_logs_file = log_dir / "errors.log"
    error_handler = logging.FileHandler(error_logs_file)
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(detailed_formatter)
    logger.addHandler(error_handler)
    
    # File handler for database operations
    db_logs_file = log_dir / "database.log"
    db_handler = logging.FileHandler(db_logs_file)
    db_handler.setLevel(logging.INFO)
    db_handler.setFormatter(detailed_formatter)
    
    # Create database logger
    db_logger = logging.getLogger(f"{name}.database")
    db_logger.addHandler(db_handler)
    db_logger.setLevel(logging.INFO)
    
    # Console handler for development
    if os.getenv("ENVIRONMENT") != "production":
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(simple_formatter)
        logger.addHandler(console_handler)
    
    return logger

def get_db_logger() -> logging.Logger:
    """Get database-specific logger"""
    return logging.getLogger("solana_rfp.database")

def log_error(logger: logging.Logger, error: Exception, context: str = "", extra_data: dict = None):
    """Log error with context and extra data"""
    error_data = {
        "error_type": type(error).__name__,
        "error_message": str(error),
        "context": context,
        "timestamp": datetime.now().isoformat(),
        "extra_data": extra_data or {}
    }
    
    logger.error(f"Error in {context}: {error}", exc_info=True, extra=error_data)

def log_database_operation(operation: str, table: str, details: str = "", success: bool = True):
    """Log database operations"""
    db_logger = get_db_logger()
    status = "SUCCESS" if success else "FAILED"
    db_logger.info(f"DB {operation} on {table} - {status} - {details}")

# Initialize main logger
main_logger = setup_logger()

