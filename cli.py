import typer
from db import get_connection

app = typer.Typer()


@app.command()
def list_entries():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT title, created_at FROM entries ORDER BY created_at DESC")
    rows = cur.fetchall()
    for row in rows:
        typer.echo(f"{row[0]} | {row[1]}")
    conn.close()


if __name__ == "__main__":
    app()
