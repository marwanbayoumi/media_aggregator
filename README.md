# media_aggregator

A personal media aggregator web application for tracking and managing albums and other media you've consumed. Built with Flask, HTMX, Tailwind CSS, and DaisyUI for a modern, interactive user experience.

## Features

- **Album Management**: Add, edit, and delete albums from your collection
- **Rich Metadata**: Track artist name, album title, release year, cover art, and ratings
- **Responsive Design**: Clean, modern UI built with Tailwind CSS and DaisyUI components
- **Interactive UI**: Smooth interactions powered by HTMX for seamless updates without page reloads
- **SQLite Database**: Persistent storage of your media collection
- **Docker Support**: Easy deployment with included Dockerfile

## Tech Stack

- **Backend**: Flask (Python)
- **Frontend**: HTMX, Tailwind CSS, DaisyUI
- **Database**: SQLite
- **Containerization**: Docker

## Installation

### Prerequisites

- Python 3.7+
- Flask and dependencies (see requirements.txt)

### Local Setup

1. Clone the repository:

```bash
git clone <repository-url>
cd media_aggregator
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Initialize the database:

```bash
sqlite3 < schema.sql
```

4. Run the application:

```bash
python app.py
```

The application will start on `http://localhost:5000`

### Docker Setup

Build and run with Docker:

```bash
docker build -t media_aggregator .
docker run -p 5000:5000 media_aggregator
```

## Usage

- **View Albums**: Navigate to the Albums section to see your collection
- **Add Album**: Click the "Add Album" button to create a new album entry
- **Edit Album**: Click on an album card to edit its details
- **Delete Album**: Remove albums from your collection with the delete button
- **Sort & Filter**: Albums are displayed sorted by year

## Project Structure

```
.
├── app.py                  # Flask application and routes
├── schema.sql              # Database schema
├── requirements.txt        # Python dependencies
├── Dockerfile              # Docker configuration
├── albums.csv              # Sample album data
├── static/                 # Static assets (CSS, images, etc.)
└── templates/              # HTML templates
    ├── base.html           # Base template layout
    ├── index.html          # Home page
    ├── _albums.html        # Albums list template
    ├── _album_card.html    # Individual album card
    └── _form.html          # Add/edit form template
```

## API Routes

- `GET /` - Home page
- `GET /albums` - Fetch all albums
- `GET /form` - Display add album form
- `GET /form/<id>` - Display edit form for album
- `POST /create` - Create new album
- `POST /edit/<id>` - Update existing album
- `DELETE /delete/<id>` - Delete album

## Database Schema

Albums table contains:

- `id`: Unique identifier
- `artist`: Artist name
- `title`: Album title
- `year`: Release year
- `cover`: Cover art URL
- `rating`: User rating

## Contributing

Feel free to fork this project and submit pull requests for any improvements.

## License

This project is open source and available under the MIT License.
