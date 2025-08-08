import typer
from typing import List, Optional
from db import get_connection
from datetime import datetime

app = typer.Typer(help="Personal Database CLI - Manage your notes, ideas, and research")


@app.command()
def list_entries(
    tag: Optional[str] = typer.Option(None, "--tag", "-t", help="Filter by tag"),
    entry_type: Optional[str] = typer.Option(
        None, "--type", help="Filter by type (note, idea, research, etc.)"
    ),
    limit: int = typer.Option(20, "--limit", "-l", help="Number of entries to show"),
):
    """List entries with optional filtering."""
    try:
        conn = get_connection()
        cur = conn.cursor()

        # Build query based on filters
        base_query = """
        SELECT DISTINCT e.title, e.content, e.type, e.created_at, e.updated_at
        FROM entries e
        """

        conditions = []
        params = []

        if tag:
            base_query += """
            LEFT JOIN entry_tags et ON e.id = et.entry_id
            LEFT JOIN tags t ON et.tag_id = t.id
            """
            conditions.append("t.name = %s")
            params.append(tag)

        if entry_type:
            conditions.append("e.type = %s")
            params.append(entry_type)

        if conditions:
            base_query += " WHERE " + " AND ".join(conditions)

        base_query += " ORDER BY e.created_at DESC LIMIT %s"
        params.append(limit)

        cur.execute(base_query, params)
        rows = cur.fetchall()

        if not rows:
            typer.echo("No entries found.")
        else:
            typer.echo(f"\nFound {len(rows)} entries:\n")
            for row in rows:
                title, content, etype, created, updated = row
                preview = content[:100] + "..." if len(content) > 100 else content
                typer.echo(f"📝 {title}")
                typer.echo(
                    f"   Type: {etype} | Created: {created.strftime('%Y-%m-%d %H:%M')}"
                )
                typer.echo(f"   Preview: {preview}")
                typer.echo("-" * 60)

        cur.close()
        conn.close()
    except Exception as e:
        typer.echo(f"Error: {e}")


@app.command()
def add_entry(
    title: str = typer.Argument(..., help="Title of the entry"),
    content: str = typer.Argument(..., help="Content of the entry"),
    entry_type: str = typer.Option(
        "note", "--type", "-t", help="Type of entry (note, idea, research, etc.)"
    ),
    tags: Optional[str] = typer.Option(None, "--tags", help="Comma-separated tags"),
    created_by: str = typer.Option(
        "user", "--author", "-a", help="Author of the entry"
    ),
):
    """Add a new entry to the database."""
    try:
        conn = get_connection()
        cur = conn.cursor()

        # Insert the entry
        cur.execute(
            """
        INSERT INTO entries (title, content, type, created_by)
        VALUES (%s, %s, %s, %s)
        RETURNING id
        """,
            (title, content, entry_type, created_by),
        )

        entry_id = cur.fetchone()[0]

        # Handle tags if provided
        if tags:
            tag_list = [tag.strip() for tag in tags.split(",")]
            for tag_name in tag_list:
                # Insert or get tag
                cur.execute(
                    """
                INSERT INTO tags (name) VALUES (%s)
                ON CONFLICT (name) DO NOTHING
                RETURNING id
                """,
                    (tag_name,),
                )

                result = cur.fetchone()
                if result:
                    tag_id = result[0]
                else:
                    # Tag already exists, get its ID
                    cur.execute("SELECT id FROM tags WHERE name = %s", (tag_name,))
                    tag_id = cur.fetchone()[0]

                # Link entry to tag
                cur.execute(
                    """
                INSERT INTO entry_tags (entry_id, tag_id) VALUES (%s, %s)
                ON CONFLICT DO NOTHING
                """,
                    (entry_id, tag_id),
                )

        conn.commit()
        cur.close()
        conn.close()

        typer.echo(f"✅ Entry '{title}' added successfully!")
        if tags:
            typer.echo(f"   Tags: {tags}")

    except Exception as e:
        typer.echo(f"Error adding entry: {e}")


@app.command()
def search(
    query: str = typer.Argument(..., help="Search term"),
    in_content: bool = typer.Option(
        True, "--content/--no-content", help="Search in content"
    ),
    in_title: bool = typer.Option(True, "--title/--no-title", help="Search in title"),
):
    """Search entries by title or content."""
    try:
        conn = get_connection()
        cur = conn.cursor()

        conditions = []
        search_term = f"%{query}%"

        if in_title:
            conditions.append("title ILIKE %s")
        if in_content:
            conditions.append("content ILIKE %s")

        if not conditions:
            typer.echo("Must search in either title or content!")
            return

        where_clause = " OR ".join(conditions)
        params = [search_term] * len(conditions)

        cur.execute(
            f"""
        SELECT title, content, type, created_at 
        FROM entries 
        WHERE {where_clause}
        ORDER BY created_at DESC
        """,
            params,
        )

        rows = cur.fetchall()

        if not rows:
            typer.echo(f"No entries found matching '{query}'")
        else:
            typer.echo(f"\nFound {len(rows)} entries matching '{query}':\n")
            for row in rows:
                title, content, etype, created = row
                preview = content[:150] + "..." if len(content) > 150 else content
                typer.echo(f"🔍 {title}")
                typer.echo(
                    f"   Type: {etype} | Created: {created.strftime('%Y-%m-%d %H:%M')}"
                )
                typer.echo(f"   Preview: {preview}")
                typer.echo("-" * 60)

        cur.close()
        conn.close()
    except Exception as e:
        typer.echo(f"Error searching: {e}")


@app.command()
def list_tags():
    """List all available tags and their usage count."""
    try:
        conn = get_connection()
        cur = conn.cursor()

        cur.execute(
            """
        SELECT t.name, COUNT(et.entry_id) as usage_count
        FROM tags t
        LEFT JOIN entry_tags et ON t.id = et.tag_id
        GROUP BY t.id, t.name
        ORDER BY usage_count DESC, t.name
        """
        )

        rows = cur.fetchall()

        if not rows:
            typer.echo("No tags found.")
        else:
            typer.echo(f"\nAvailable tags ({len(rows)} total):\n")
            for tag_name, count in rows:
                typer.echo(f"🏷️  {tag_name} ({count} entries)")

        cur.close()
        conn.close()
    except Exception as e:
        typer.echo(f"Error listing tags: {e}")


@app.command()
def show(title: str = typer.Argument(..., help="Title of the entry to show")):
    """Show full content of a specific entry."""
    try:
        conn = get_connection()
        cur = conn.cursor()

        # Get entry details
        cur.execute(
            """
        SELECT title, content, type, created_at, updated_at, created_by
        FROM entries 
        WHERE title ILIKE %s
        """,
            (f"%{title}%",),
        )

        entry = cur.fetchone()

        if not entry:
            typer.echo(f"No entry found matching '{title}'")
            return

        title, content, etype, created, updated, author = entry

        # Get tags for this entry
        cur.execute(
            """
        SELECT t.name
        FROM tags t
        JOIN entry_tags et ON t.id = et.tag_id
        JOIN entries e ON et.entry_id = e.id
        WHERE e.title = %s
        """,
            (title,),
        )

        tags = [row[0] for row in cur.fetchall()]

        # Display entry
        typer.echo(f"\n📄 {title}")
        typer.echo("=" * (len(title) + 4))
        typer.echo(f"Type: {etype}")
        typer.echo(f"Author: {author}")
        typer.echo(f"Created: {created.strftime('%Y-%m-%d %H:%M:%S')}")
        typer.echo(f"Updated: {updated.strftime('%Y-%m-%d %H:%M:%S')}")
        if tags:
            typer.echo(f"Tags: {', '.join(tags)}")
        typer.echo("\nContent:")
        typer.echo("-" * 40)
        typer.echo(content)
        typer.echo("-" * 40)

        cur.close()
        conn.close()
    except Exception as e:
        typer.echo(f"Error showing entry: {e}")


if __name__ == "__main__":
    app()
