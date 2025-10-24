"""
Supabase configuration and client setup
"""

import os
from supabase import create_client, Client

# Supabase configuration
SUPABASE_URL = "https://zaqonwxzoafewoloexsk.supabase.co"
SUPABASE_ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InphcW9ud3h6b2FmZXdvbG9leHNrIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjEzMDExODUsImV4cCI6MjA3Njg3NzE4NX0.fKR28ijcpk0XfD1hbEdv9rqPmrnmrIf6S8t0JuuZoeA"
SUPABASE_SERVICE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InphcW9ud3h6b2FmZXdvbG9leHNrIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2MTMwMTE4NSwiZXhwIjoyMDc2ODc3MTg1fQ.hGygXYHIqt8ipZR2Kytzj-xGxGHhBuN2fZp86ytaVgk"

def get_supabase_client() -> Client:
    """Get Supabase client"""
    return create_client(SUPABASE_URL, SUPABASE_ANON_KEY)

def get_supabase_service_client() -> Client:
    """Get Supabase service client with elevated permissions"""
    return create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)
