import json
import getpass
import urllib.request

import psycopg2

# Enter the password from your assignment page.
password = getpass.getpass("Database password: ")

# Connect to your assigned PostgreSQL database.
conn = psycopg2.connect(
    host="pg.pg4e.com",
    port=5432,
    database="pg4e_da795b0640",
    user="pg4e_da795b0640",
    password=password,
)

try:
    with conn.cursor() as cur:
        # Create the table required by the assignment.
        cur.execute("""
            CREATE TABLE IF NOT EXISTS pokeapi (
                id INTEGER,
                body JSONB
            );
        """)

        # Prevent duplicate records when rerunning this script.
        cur.execute("DELETE FROM pokeapi WHERE id BETWEEN 1 AND 100;")

        # Retrieve Pokémon numbered 1 through 100.
        for pokemon_id in range(1, 101):
            url = f"https://pokeapi.co/api/v2/pokemon/{pokemon_id}/"

            # Add a browser-style header to the download request.
            request = urllib.request.Request(
                url,
                headers={
                    "User-Agent": "Mozilla/5.0",
                    "Accept": "application/json",
                },
            )

            # Download the complete Pokémon JSON document.
            with urllib.request.urlopen(request, timeout=60) as response:
                pokemon = json.load(response)

            # Store the Pokémon ID and JSON document.
            cur.execute(
                "INSERT INTO pokeapi (id, body) VALUES (%s, %s::jsonb);",
                (pokemon_id, json.dumps(pokemon)),
            )

            print(f"Loaded {pokemon_id}: {pokemon['name']}")

    # Save all records so the autograder can access them.
    conn.commit()
    print("Successfully saved all 100 Pokémon!")

except Exception:
    # Undo changes from this run if something fails.
    conn.rollback()
    print("The script failed. Changes from this run were not saved.")
    raise

finally:
    conn.close()