import psycopg2

            # -- DROP TABLE IF EXISTS spaces;
            # -- DROP TABLE IF EXISTS items;
            # -- DROP TABLE IF EXISTS space_items;

def create_tables():
    commands = (
        """
        CREATE TABLE spaces (
            id SERIAL PRIMARY KEY,
            spacename TEXT NOT NULL UNIQUE,
            created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
        """,
        """
        CREATE TABLE items (
            id SERIAL PRIMARY KEY,
            item TEXT NOT NULL,
            created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
        """,
        """
        CREATE TABLE space_items (
            space_id INTEGER NOT NULL, 
            item_id INTEGER NOT NULL, 
            info TEXT,
            quantity INTEGER DEFAULT 1 NOT NULL,
            created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (space_id, item_id)
        )
        """)


    conn = None
    

    conn = psycopg2.connect(
            host="ep-hidden-poetry-04269976.eu-central-1.aws.neon.tech",
            database="zeddl",
            user="koyeb-adm",
            password="bKFvslL19MrQ")
    cur = conn.cursor()
    for command in commands:
        cur.execute(command)
        print(command)
    cur.close()
    conn.commit()

create_tables()