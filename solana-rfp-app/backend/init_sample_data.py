#!/usr/bin/env python3
"""
Initialize the database with sample RFP knowledge base data
"""
import os
import sys
from sqlalchemy.orm import Session
from app.core.database import SessionLocal, engine, Base
from app.models.database import KnowledgeBase

def init_sample_data():
    """Initialize database with sample RFP data"""
    
    # Create tables
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        # Check if data already exists
        existing_count = db.query(KnowledgeBase).count()
        if existing_count > 0:
            print(f"Database already has {existing_count} entries. Skipping initialization.")
            return
        
        # Sample RFP knowledge base data
        sample_data = [
            {
                "question": "Are there support and training programs for developers?",
                "answer": "Yes, Solana provides comprehensive support and training programs for developers including documentation, tutorials, workshops, and community support through Discord and forums.",
                "category": "Support",
                "tags": ["support", "training", "developers", "documentation"]
            },
            {
                "question": "Do you have testnets? Do you provide faucets for them?",
                "answer": "Yes, Solana operates multiple testnets including devnet and testnet. We provide faucets for both testnets to help developers get test tokens for development and testing purposes.",
                "category": "Technical",
                "tags": ["testnet", "faucet", "development", "testing"]
            },
            {
                "question": "Do you provide faucets or institutional access to tokens for testnets?",
                "answer": "Yes, we provide both public faucets for individual developers and institutional access to larger amounts of test tokens for organizations and enterprises.",
                "category": "Technical",
                "tags": ["faucet", "institutional", "testnet", "tokens"]
            },
            {
                "question": "Do you organize hackathons or events for developers?",
                "answer": "Yes, Solana regularly organizes hackathons and developer events worldwide. We host events in major cities and also support community-organized events. Previous events have had thousands of participants and significant prize pools.",
                "category": "Events",
                "tags": ["hackathon", "events", "developers", "community"]
            },
            {
                "question": "What are the technical requirements for integration?",
                "answer": "Technical requirements include Rust or JavaScript/TypeScript development, understanding of Solana's architecture, and access to our development tools and SDKs. We provide comprehensive documentation and examples.",
                "category": "Technical",
                "tags": ["requirements", "integration", "rust", "javascript", "sdk"]
            },
            {
                "question": "What is the expected timeline for project completion?",
                "answer": "Project timelines vary based on scope and complexity. Typical RFP projects range from 3-12 months. We work with teams to establish realistic milestones and provide ongoing support throughout the development process.",
                "category": "Project Management",
                "tags": ["timeline", "milestones", "project", "completion"]
            }
        ]
        
        # Import sample data
        imported_count = 0
        for item in sample_data:
            kb_entry = KnowledgeBase(
                question=item["question"],
                answer=item["answer"],
                category=item["category"],
                created_by="system_init",
                last_modified_by="system_init"
            )
            kb_entry.set_tags(item["tags"])
            db.add(kb_entry)
            imported_count += 1
        
        db.commit()
        print(f"Successfully initialized database with {imported_count} sample knowledge base entries")
        
    except Exception as e:
        print(f"Error initializing sample data: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    init_sample_data()
