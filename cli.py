import typer
from db import get_connection

app = typer.Typer()


@app.command()
def list_entries():
    """List all entries in the database."""
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT title, created_at FROM entries ORDER BY created_at DESC")
        rows = cur.fetchall()

        if not rows:
            typer.echo("No entries found.")
        else:
            for row in rows:
                typer.echo(f"{row[0]} | {row[1]}")

        cur.close()
        conn.close()
    except Exception as e:
        typer.echo(f"Error: {e}")


if __name__ == "__main__":
    app()
