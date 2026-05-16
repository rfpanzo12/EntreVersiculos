from database import supabase

response = supabase.table("players").select("*").execute()

print(response.data)