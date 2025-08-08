import typer
from typing import Optional
from models import Entry, EntryRepository
from db import get_connection
import sys

# Initialize the CLI app
app = typer.Typer(
    help="Personal Database CLI - Manage your notes, ideas, and research",
    add_completion=False
)

# Initialize repository
entry_repo = EntryRepository(get_connection)


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
        entries = entry_repo.get_entries(tag=tag, entry_type=entry_type, limit=limit)
        
        if not entries:
            typer.echo("No entries found.")
            return
        
        typer.echo(f"\nFound {len(entries)} entries:\n")
        for entry in entries:
            preview = _create_preview(entry.content, 100)
            typer.echo(f"📝 {entry.title}")
            typer.echo(f"   Type: {entry.entry_type} | Created: {entry.created_at.strftime('%Y-%m-%d %H:%M')}")
            if entry.tags:
                typer.echo(f"   Tags: {', '.join(entry.tags)}")
            typer.echo(f"   Preview: {preview}")
            typer.echo("-" * 60)
            
    except Exception as e:
        typer.echo(f"Error: {e}", err=True)
        sys.exit(1)


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
        # Parse tags
        tag_list = []
        if tags:
            tag_list = [tag.strip() for tag in tags.split(",") if tag.strip()]
        
        # Create entry object
        entry = Entry(
            title=title,
            content=content,
            entry_type=entry_type,
            created_by=created_by,
            tags=tag_list
        )
        
        # Save to database
        entry_id = entry_repo.create_entry(entry)
        
        typer.echo(f"✅ Entry '{title}' added successfully!")
        typer.echo(f"   ID: {entry_id}")
        typer.echo(f"   Type: {entry_type}")
        if tag_list:
            typer.echo(f"   Tags: {', '.join(tag_list)}")
            
    except Exception as e:
        typer.echo(f"Error adding entry: {e}", err=True)
        sys.exit(1)


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
        if not in_content and not in_title:
            typer.echo("Must search in either title or content!")
            sys.exit(1)
        
        entries = entry_repo.search_entries(query, in_title, in_content)
        
        if not entries:
            typer.echo(f"No entries found matching '{query}'")
            return
        
        typer.echo(f"\nFound {len(entries)} entries matching '{query}':\n")
        for entry in entries:
            preview = _create_preview(entry.content, 150)
            typer.echo(f"🔍 {entry.title}")
            typer.echo(f"   Type: {entry.entry_type} | Created: {entry.created_at.strftime('%Y-%m-%d %H:%M')}")
            if entry.tags:
                typer.echo(f"   Tags: {', '.join(entry.tags)}")
            typer.echo(f"   Preview: {preview}")
            typer.echo("-" * 60)
            
    except Exception as e:
        typer.echo(f"Error searching: {e}", err=True)
        sys.exit(1)


@app.command()
def list_tags():
    """List all available tags and their usage count."""
    try:
        tags = entry_repo.get_all_tags()
        
        if not tags:
            typer.echo("No tags found.")
            return
        
        typer.echo(f"\nAvailable tags ({len(tags)} total):\n")
        for tag in tags:
            typer.echo(f"🏷️  {tag.name} ({tag.usage_count} entries)")
            
    except Exception as e:
        typer.echo(f"Error listing tags: {e}", err=True)
        sys.exit(1)


@app.command()
def show(title: str = typer.Argument(..., help="Title of the entry to show")):
    """Show full content of a specific entry."""
    try:
        entry = entry_repo.get_entry_by_title(title)
        
        if not entry:
            typer.echo(f"No entry found matching '{title}'")
            sys.exit(1)
        
        # Display entry
        typer.echo(f"\n📄 {entry.title}")
        typer.echo("=" * (len(entry.title) + 4))
        typer.echo(f"Type: {entry.entry_type}")
        typer.echo(f"Author: {entry.created_by}")
        typer.echo(f"Created: {entry.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
        typer.echo(f"Updated: {entry.updated_at.strftime('%Y-%m-%d %H:%M:%S')}")
        if entry.tags:
            typer.echo(f"Tags: {', '.join(entry.tags)}")
        typer.echo("\nContent:")
        typer.echo("-" * 40)
        typer.echo(entry.content)
        typer.echo("-" * 40)
        
    except Exception as e:
        typer.echo(f"Error showing entry: {e}", err=True)
        sys.exit(1)


@app.command()
def init_db():
    """Initialize the database with required tables."""
    try:
        from db import initialize_database, test_connection
        
        typer.echo("Testing database connection...")
        if not test_connection():
            typer.echo("❌ Database connection failed. Check your .env file.", err=True)
            sys.exit(1)
        
        typer.echo("✅ Database connection successful!")
        typer.echo("Initializing database tables...")
        
        if initialize_database():
            typer.echo("✅ Database initialized successfully!")
        else:
            typer.echo("❌ Database initialization failed.", err=True)
            sys.exit(1)
            
    except Exception as e:
        typer.echo(f"Error initializing database: {e}", err=True)
        sys.exit(1)


def _create_preview(content: str, max_length: int = 100) -> str:
    """Create a preview of content with ellipsis if too long."""
    if len(content) <= max_length:
        return content
    return content[:max_length].rsplit(' ', 1)[0] + "..."


if __name__ == "__main__":
    app()