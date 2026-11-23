from getpass import getpass

import psycopg2
import requests
from psycopg2.extras import Json


def main():
    conn = psycopg2.connect(
        host="pg.pg4e.com",
        port=5432,
        user="pg4e_da795b0640",
        dbname="pg4e_da795b0640",
        password=getpass("Personal PostgreSQL password: "),
        connect_timeout=5,
    )

    try:
        with conn.cursor() as cur, requests.Session() as session:
            # Find the Pokémon IDs already saved in the JSON.
            cur.execute("SELECT (body->>'id')::integer FROM public.pokeapi")
            existing_ids = {row[0] for row in cur.fetchall()}
            missing_ids = sorted(set(range(1, 808)) - existing_ids)

            # Check whether the table requires us to supply its id.
            cur.execute("""
                SELECT 1
                FROM information_schema.columns
                WHERE table_schema = 'public'
                  AND table_name = 'pokeapi'
                  AND column_name = 'id'
                  AND is_nullable = 'NO'
                  AND column_default IS NULL
                  AND is_identity = 'NO'
                  AND is_generated = 'NEVER'
            """)
            needs_id = cur.fetchone() is not None
            conn.commit()

            print(f"Found {len(missing_ids)} Pokémon to add.", flush=True)

            for pokemon_id in missing_ids:
                url = f"https://pokeapi.co/api/v2/pokemon/{pokemon_id}/"
                response = session.get(url, timeout=30)
                response.raise_for_status()
                body = Json(response.json())

                if needs_id:
                    cur.execute(
                        "INSERT INTO public.pokeapi (id, body) VALUES (%s, %s)",
                        (pokemon_id, body),
                    )
                else:
                    cur.execute(
                        "INSERT INTO public.pokeapi (body) VALUES (%s)",
                        (body,),
                    )

                conn.commit()
                print(f"Saved Pokémon {pokemon_id}", flush=True)

            cur.execute("SELECT COUNT(*) FROM public.pokeapi")
            print(f"Final row count: {cur.fetchone()[0]}")
    finally:
        conn.close()


if __name__ == "__main__":
    main()