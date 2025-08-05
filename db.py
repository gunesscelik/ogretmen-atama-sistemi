# db.py
from supabase import create_client

SUPABASE_URL = "https://fcbodvbschphjkgyeiqb.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImZjYm9kdmJzY2hwaGprZ3llaXFiIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTI5NzM4NzcsImV4cCI6MjA2ODU0OTg3N30.aXPNvYXLLAtifZvdwyirE-I5hCMbUTfg6sXP84Ex7C4"

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)


