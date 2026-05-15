from database import supabase


def login_player(name: str, password: str):
    response = (
        supabase.table("players")
        .select("*")
        .eq("name", name)
        .eq("password", password)
        .execute()
    )

    if response.data:
        return response.data[0]

    return None


def create_player(name: str, password: str, is_admin: bool = False):
    response = (
        supabase.table("players")
        .insert({
            "name": name,
            "password": password,
            "is_admin": is_admin
        })
        .execute()
    )

    return response.data


def list_players():
    response = (
        supabase.table("players")
        .select("id, name, is_admin, created_at")
        .order("created_at", desc=True)
        .execute()
    )

    return response.data