#!/usr/bin/env python3
"""
database.py - Database Connection Helper

Handles all interactions with the PostgreSQL database.
Falls back to stub data when PostgreSQL is not available.
"""

try:
    import psycopg2
    HAS_PSYCOPG2 = True
except ImportError:
    HAS_PSYCOPG2 = False

connection_parameters = {
    "dbname": "photon",
    "user": "student",
    "password": "student",
    "host": "localhost",
    "port": "5432",
}

_STUB_PLAYERS = {1: "Opus"}
_DB_AVAILABLE_CACHE = None


def add_player(player_id, name):
    with psycopg2.connect(**connection_parameters) as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                "INSERT INTO players (id, codename) VALUES (%s, %s);",
                (player_id, name),
            )


def get_player_by_id(player_id):
    with psycopg2.connect(**connection_parameters) as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM players WHERE id = %s;", (player_id,)
            )
            return cursor.fetchone()


def delete_player(player_id):
    with psycopg2.connect(**connection_parameters) as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                "DELETE FROM players WHERE id = %s;", (player_id,)
            )


def delete_all_players():
    with psycopg2.connect(**connection_parameters) as conn:
        with conn.cursor() as cursor:
            cursor.execute("DELETE FROM players;")


def show_all_players():
    with psycopg2.connect(**connection_parameters) as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM players;")
            rows = cursor.fetchall()
            for row in rows:
                print(row)
            return rows


def _db_available():
    """Check if the database is reachable. Cached after first call."""
    global _DB_AVAILABLE_CACHE
    if _DB_AVAILABLE_CACHE is not None:
        return _DB_AVAILABLE_CACHE

    if not HAS_PSYCOPG2:
        _DB_AVAILABLE_CACHE = False
        return False

    try:
        conn = psycopg2.connect(**connection_parameters)
        conn.close()
        _DB_AVAILABLE_CACHE = True
    except psycopg2.Error:
        _DB_AVAILABLE_CACHE = False

    return _DB_AVAILABLE_CACHE


def lookup_player_codename(player_id):
    """Look up a player's codename. Returns str or None."""
    if not _db_available():
        return _STUB_PLAYERS.get(player_id)

    try:
        result = get_player_by_id(player_id)
        return result[1] if result else None
    except psycopg2.Error:
        return None


def add_new_player(player_id, codename):
    """Add a new player. Returns True on success, False on failure."""
    if not _db_available():
        _STUB_PLAYERS[player_id] = codename
        return True

    try:
        add_player(player_id, codename)
        return True
    except psycopg2.Error:
        return False


if __name__ == "__main__":
    print("=== Database Connection Test ===\n")

    print("1. lookup_player_codename(1):")
    print(f"   {lookup_player_codename(1)}\n")

    print("2. lookup_player_codename(999):")
    print(f"   {lookup_player_codename(999)}\n")

    print("3. add_new_player(99, 'TestPlayer'):")
    print(f"   {add_new_player(99, 'TestPlayer')}\n")

    print("4. lookup_player_codename(99) after add:")
    print(f"   {lookup_player_codename(99)}\n")

    print("=== Done ===")
