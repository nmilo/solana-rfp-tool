"""
Database persistence utilities to prevent data loss
"""
import json
import os
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from app.models.database import KnowledgeBase
from app.core.logger import main_logger, log_error

class DatabasePersistence:
    def __init__(self, db: Session):
        self.db = db
        self.backup_dir = Path("database_backups")
        self.backup_dir.mkdir(exist_ok=True)
    
    def backup_knowledge_base(self) -> str:
        """Create a backup of all knowledge base entries"""
        try:
            main_logger.info("Creating knowledge base backup")
            
            # Get all entries
            entries = self.db.query(KnowledgeBase).all()
            
            # Convert to serializable format
            backup_data = {
                "timestamp": datetime.now().isoformat(),
                "total_entries": len(entries),
                "entries": []
            }
            
            for entry in entries:
                entry_data = {
                    "id": str(entry.id),
                    "question": entry.question,
                    "answer": entry.answer,
                    "category": entry.category,
                    "tags": entry.get_tags(),
                    "confidence_threshold": entry.confidence_threshold,
                    "is_active": entry.is_active,
                    "created_by": entry.created_by,
                    "last_modified_by": entry.last_modified_by,
                    "created_at": entry.created_at.isoformat(),
                    "updated_at": entry.updated_at.isoformat()
                }
                backup_data["entries"].append(entry_data)
            
            # Save backup file
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = self.backup_dir / f"knowledge_base_backup_{timestamp}.json"
            
            with open(backup_file, 'w', encoding='utf-8') as f:
                json.dump(backup_data, f, indent=2, ensure_ascii=False)
            
            main_logger.info(f"Backup created: {backup_file} with {len(entries)} entries")
            return str(backup_file)
            
        except Exception as e:
            log_error(main_logger, e, "backup_knowledge_base")
            raise
    
    def restore_knowledge_base(self, backup_file: str) -> int:
        """Restore knowledge base from backup file"""
        try:
            main_logger.info(f"Restoring knowledge base from {backup_file}")
            
            # Read backup file
            with open(backup_file, 'r', encoding='utf-8') as f:
                backup_data = json.load(f)
            
            # Clear existing entries
            self.db.query(KnowledgeBase).delete()
            self.db.commit()
            
            # Restore entries
            restored_count = 0
            for entry_data in backup_data["entries"]:
                try:
                    # Create new entry
                    kb_entry = KnowledgeBase(
                        question=entry_data["question"],
                        answer=entry_data["answer"],
                        category=entry_data["category"],
                        confidence_threshold=entry_data["confidence_threshold"],
                        is_active=entry_data["is_active"],
                        created_by=entry_data["created_by"],
                        last_modified_by=entry_data["last_modified_by"]
                    )
                    kb_entry.set_tags(entry_data["tags"])
                    
                    self.db.add(kb_entry)
                    restored_count += 1
                    
                except Exception as e:
                    main_logger.error(f"Failed to restore entry: {entry_data.get('question', 'Unknown')[:50]}... - {str(e)}")
                    continue
            
            self.db.commit()
            main_logger.info(f"Restored {restored_count} entries from backup")
            return restored_count
            
        except Exception as e:
            log_error(main_logger, e, "restore_knowledge_base", {"backup_file": backup_file})
            self.db.rollback()
            raise
    
    def get_latest_backup(self) -> str:
        """Get the most recent backup file"""
        backup_files = list(self.backup_dir.glob("knowledge_base_backup_*.json"))
        if not backup_files:
            return None
        
        # Sort by modification time, newest first
        latest_backup = max(backup_files, key=lambda f: f.stat().st_mtime)
        return str(latest_backup)
    
    def auto_backup(self) -> str:
        """Create automatic backup if entries exist"""
        try:
            # Check if we have entries
            entry_count = self.db.query(KnowledgeBase).count()
            
            if entry_count > 0:
                # Check if we need a backup (no recent backup or significant changes)
                latest_backup = self.get_latest_backup()
                
                if not latest_backup:
                    # No backup exists, create one
                    return self.backup_knowledge_base()
                else:
                    # Check if backup is recent (within last hour)
                    backup_time = datetime.fromtimestamp(Path(latest_backup).stat().st_mtime)
                    if (datetime.now() - backup_time).total_seconds() > 3600:  # 1 hour
                        return self.backup_knowledge_base()
            
            return None
            
        except Exception as e:
            log_error(main_logger, e, "auto_backup")
            return None
    
    def check_and_restore(self) -> bool:
        """Check if database is empty and restore from backup if needed"""
        try:
            entry_count = self.db.query(KnowledgeBase).count()
            
            if entry_count == 0:
                main_logger.warning("Knowledge base is empty, checking for backup to restore")
                
                latest_backup = self.get_latest_backup()
                if latest_backup:
                    main_logger.info(f"Restoring from backup: {latest_backup}")
                    restored_count = self.restore_knowledge_base(latest_backup)
                    main_logger.info(f"Restored {restored_count} entries from backup")
                    return True
                else:
                    main_logger.warning("No backup found to restore from")
                    return False
            
            return True
            
        except Exception as e:
            log_error(main_logger, e, "check_and_restore")
            return False
