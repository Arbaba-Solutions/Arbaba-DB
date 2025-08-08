# Arbaba-DB

A powerful command-line tool for managing your personal notes, ideas, research, and knowledge with advanced tagging, searching, and filtering capabilities.

## ✨ Features

- **Centralized Storage**: Store all your important information in one organized place
- **Flexible Tagging System**: Add multiple tags per entry for easy organization
- **Advanced Search**: Search through titles and content with powerful filtering
- **Multiple Entry Types**: Organize by type (notes, ideas, research, etc.)
- **Clean CLI Interface**: Simple and intuitive command-line interface
- **Cloud Database**: Uses Supabase for reliable cloud storage
- **Scalable Design**: Built with expansion in mind

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- A Supabase account and project

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/Arbaba-Solutions/Arbaba-DB
   cd Arbaba-DB
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   
   Create a `.env` file in the project root:
   ```bash
   user=postgres.your_project_id
   password=your_database_password
   host=aws-0-region.pooler.supabase.com
   port=6543
   dbname=postgres
   ```

4. **Initialize the database**
   ```bash
   python main.py init-db
   ```

5. **Start using the CLI**
   ```bash
   python main.py --help
   ```

## 📖 Usage

### Basic Commands

#### Add a New Entry
```bash
python main.py add-entry "My First Note" "This is the content of my note"
```

#### Add Entry with Tags and Type
```bash
python main.py add-entry "Python Tips" "Use list comprehensions for cleaner code" --tags "python,programming,tips" --type "learning"
```

#### List All Entries
```bash
python main.py list-entries
```

#### Filter Entries by Tag
```bash
python main.py list-entries --tag python
```

#### Filter by Entry Type
```bash
python main.py list-entries --type research --limit 10
```

#### Search Entries
```bash
# Search in both title and content
python main.py search "python"

# Search only in titles
python main.py search "learning" --no-content

# Search only in content
python main.py search "API" --no-title
```

#### Show Full Entry Content
```bash
python main.py show "Python Tips"
```

#### List All Tags
```bash
python main.py list-tags
```

### Advanced Usage Examples

#### Research Workflow
```bash
# Add research entries
python main.py add-entry "Machine Learning Paper" "Summary of the attention mechanism paper" --type research --tags "ML,papers,attention"

# Find all research entries
python main.py list-entries --type research

# Search within research
python main.py search "attention" --type research
```

#### Idea Management
```bash
# Capture ideas quickly
python main.py add-entry "App Idea" "A todo app with AI suggestions" --type idea --tags "apps,AI,productivity"

# Review all ideas
python main.py list-entries --type idea
```

## 🏗️ Project Structure

```
personal-database-cli/
│
├── main.py           # Application entry point
├── db.py             # Database connection and management
├── models.py         # Data models and repository pattern
├── cli.py            # Command-line interface
├── .env              # Environment variables (create this)
├── requirements.txt  # Project dependencies
└── README.md         # This file
```

### File Descriptions

- **`main.py`**: Entry point with initialization and error handling
- **`db.py`**: Database connection management, configuration validation
- **`models.py`**: Data classes and repository pattern for database operations
- **`cli.py`**: Typer-based CLI with all user commands
- **`.env`**: Database configuration (not tracked in git)

## 🛠️ Configuration

### Database Setup (Supabase)

1. Create a new Supabase project
2. Get your database credentials from Settings > Database
3. Add the credentials to your `.env` file
4. Run the database initialization command

### Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `user` | Database username | `postgres.abcdefghij` |
| `password` | Database password | `your_secure_password` |
| `host` | Database host | `aws-0-eu-central-1.pooler.supabase.com` |
| `port` | Database port | `6543` |
| `dbname` | Database name | `postgres` |

## 🗄️ Database Schema

The application uses three main tables:

### `entries`
- `id` (UUID, Primary Key)
- `title` (Text, Required)
- `content` (Text, Required)
- `type` (Text, Default: 'note')
- `created_at` (Timestamp)
- `updated_at` (Timestamp)
- `created_by` (Text)

### `tags`
- `id` (UUID, Primary Key)
- `name` (Text, Unique)

### `entry_tags` (Junction Table)
- `entry_id` (UUID, Foreign Key)
- `tag_id` (UUID, Foreign Key)

## 🔧 Development

### Setting Up Development Environment

```bash
# Install development dependencies
pip install -r requirements.txt

# Run tests (when available)
pytest

# Code formatting
black .

# Linting
flake8
```

### Adding New Features

The codebase follows these patterns:

1. **Repository Pattern**: Database operations in `models.py`
2. **Separation of Concerns**: CLI logic separate from business logic
3. **Type Hints**: Use type annotations for better code documentation
4. **Error Handling**: Comprehensive error handling with user-friendly messages

## 🚧 Future Roadmap

- [ ] **Edit/Update Entries**: Modify existing entries
- [ ] **Delete Entries**: Remove entries safely
- [ ] **Export Data**: Export to various formats (JSON, CSV, Markdown)
- [ ] **Import Data**: Import from existing note systems
- [ ] **Linking System**: Zettelkasten-style note linking
- [ ] **Full-Text Search**: Advanced search with PostgreSQL's full-text capabilities
- [ ] **Web Interface**: Browser-based GUI
- [ ] **Backup/Sync**: Automated backup and sync features
- [ ] **AI Integration**: AI-powered tagging and content suggestions
- [ ] **Multi-user Support**: Shared databases and collaboration

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Troubleshooting

### Common Issues

#### Database Connection Error
```bash
Error: invalid integer value for connection option "port"
```
**Solution**: Check that your password doesn't contain special characters. If it does, URL-encode them or use individual environment variables.

#### No entries found
**Solution**: Make sure you've initialized the database with `python main.py init-db`

#### Module not found
**Solution**: Ensure you're running commands from the project root directory and have installed all dependencies.

### Getting Help

- Check the command help: `python main.py [command] --help`
- Verify your `.env` file configuration
- Test database connection: `python main.py init-db`

## 🙏 Acknowledgments

- Built with [Typer](https://typer.tiangolo.com/) for the CLI interface
- Uses [Supabase](https://supabase.com/) for cloud database hosting
- Inspired by note-taking systems like Zettelkasten and PKM tools

---

**Happy note-taking! 📝✨**
