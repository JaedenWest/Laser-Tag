import psycopg2

#Define connection parameters
connection_parameters = {
    'dbname': 'photon',
    'user': 'student',
    'password': 'student',
    'host': 'localhost',
    'port': '5432'
}

#import database in the main file and call this as "database.add_player(id, "name")"
def add_player(player_id, name):
    with psycopg2.connect(**connection_parameters) as conn:
        with conn.cursor() as cursor:
            cursor.execute("INSERT INTO players (id, codename) VALUES (%s, %s);", (player_id, name))

def get_player_by_id(player_id):
    with psycopg2.connect(**connection_parameters) as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM players WHERE id = %s;", (player_id,))
            player = cursor.fetchone()
            return player

def delete_player(player_id):
    with psycopg2.connect(**connection_parameters) as conn:
        with conn.cursor() as cursor:
            cursor.execute("DELETE FROM players WHERE id = %s;", (player_id,))

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
            return rows #returns a list of tuples [(id1, player1), (id2, player2)]