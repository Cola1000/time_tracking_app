# Time Tracking App

A local time tracking application built with FastAPI (Python) backend, Svelte frontend, and Docker. No authentication required - designed to run locally on your browser with JSON file storage.

## Features

✅ **Start/Stop Timer** - Real-time timer with pause and reset  
✅ **Manual Entry** - Create time entries manually with custom times  
✅ **Projects & Categories** - Organize time entries by project and category  
✅ **Weekly Calendar View** - Toggl-style calendar divided by week and day  
✅ **Daily Reports** - Bar and pie charts showing time breakdown  
✅ **Project Overview** - View all projects with expandable entry history  
✅ **Light/Dark Mode** - Toggle between themes via UI or startup flag  
✅ **Custom Projects** - Add and persist custom projects using localStorage  
✅ **JSON Storage** - All data saved locally as JSON files (no database needed)  
✅ **Responsive Design** - Works on desktop and mobile browsers  
✅ **Auto Browser Launch** - Automatically opens browser on startup  

## Tech Stack

- **Backend**: FastAPI (Python 3.11)
- **Frontend**: Svelte 4 + Vite 5
- **Charts**: Chart.js
- **Storage**: JSON files (local) + localStorage
- **Containerization**: Docker & Docker Compose

## Project Structure

```
time_tracking_app/
├── backend/                 # FastAPI application
│   ├── main.py             # Main app entry point
│   ├── routes/
│   │   └── timers.py       # Timer endpoints
│   ├── models/
│   │   └── timer.py        # Data models
│   ├── data/               # JSON storage directory
│   ├── requirements.txt    # Python dependencies
│   └── Dockerfile
├── frontend/               # Svelte application
│   ├── src/
│   │   ├── App.svelte
│   │   ├── components/
│   │   │   ├── Sidebar.svelte
│   │   │   ├── Calendar.svelte
│   │   │   ├── Timer.svelte
│   │   │   ├── Reports.svelte
│   │   │   └── Projects.svelte
│   │   ├── styles/         # CSS modules
│   │   │   ├── theme.css   # Theme variables
│   │   │   ├── calendar.css
│   │   │   ├── sidebar.css
│   │   │   ├── timer.css
│   │   │   ├── reports.css
│   │   │   └── projects.css
│   │   ├── stores/
│   │   │   └── theme.js    # Theme state management
│   │   ├── utils/
│   │   │   └── storage.js  # localStorage utilities
│   │   └── main.js
│   ├── package.json
│   ├── vite.config.js
│   └── Dockerfile
├── docker-compose.yml      # Docker orchestration
├── start.bat              # Windows startup script
└── start.sh               # Linux/Mac startup script
```

## Quick Start

### Option 1: Using Startup Scripts (Recommended)

**Windows:**
```bash
# Start with dark theme (default)
.\start.bat

# Start with light theme
.\start.bat light

# Start with dark theme (explicit)
.\start.bat dark
```

**Linux/Mac:**
```bash
# Make script executable (first time only)
chmod +x start.sh

# Start with dark theme (default)
./start.sh

# Start with light theme
./start.sh light

# Start with dark theme (explicit)
./start.sh dark
```

The script will:
- Check if Docker is running
- Build and start both containers
- Automatically open your browser to http://localhost:5173
- Display the app in your chosen theme

### Option 2: Using Docker Compose Manually

```bash
# Start both backend and frontend with dark theme (default)
docker-compose up --build

# Start with light theme
VITE_THEME=light docker-compose up --build

# App will be available at http://localhost:5173
```

### Option 3: Local Development

#### Backend
```bash
cd backend
pip install -r requirements.txt
python main.py
# Backend runs on http://localhost:8000
```

#### Frontend
```bash
cd frontend
npm install
npm run dev
# Frontend runs on http://localhost:5173
```

## Theme System

The app supports both light and dark modes:

### Switching Themes

1. **Via Startup Script**: Pass `light` or `dark` as an argument (see Quick Start)
2. **Via UI**: Click the theme toggle button at the bottom of the sidebar
3. **Via Environment Variable**: Set `VITE_THEME=light` or `VITE_THEME=dark`

Themes are managed through:
- CSS custom properties in `frontend/src/styles/theme.css`
- Svelte store in `frontend/src/stores/theme.js`
- localStorage for persistence across sessions

## API Endpoints

### Timer Management
- `POST /api/timers` - Create new timer entry
- `GET /api/timers/{date}` - Get entries for a specific day (YYYY-MM-DD)
- `GET /api/timers/week/{start_date}` - Get entries for a week
- `PUT /api/timers/{entry_id}` - Update timer entry
- `DELETE /api/timers/{entry_id}` - Delete timer entry

### Statistics
- `GET /api/stats/week/{start_date}` - Get weekly statistics with project/category breakdown

## Data Storage

All data is stored as JSON files in the `backend/data/` directory:
- Files are named by date: `YYYY-MM-DD.json`
- Each file contains entries for that day with timestamps and durations
- Data persists between sessions

Example JSON structure:
```json
{
  "date": "2026-01-28",
  "total_duration": 3600,
  "entries": [
    {
      "id": "uuid-string",
      "project": "Development",
      "category": "Work",
      "description": "Building features",
      "start_time": "2026-01-28T09:00:00",
      "end_time": "2026-01-28T10:00:00",
      "duration": 3600
    }
  ]
}
```

## Usage

1. **Start Timer**: Click the ▶ Start button to begin tracking time
2. **Stop/Pause**: Click ⏸ Stop to pause the timer
3. **Select Project & Category**: Choose from predefined options or add custom ones
4. **Add Description**: Optionally add notes about what you're working on
5. **Save Entry**: Click 💾 Save Entry to log the time
6. **View Calendar**: See weekly breakdown of your time tracking
7. **Navigate Weeks**: Use Previous/Next buttons to view past or future weeks

## Development

### Add New Features

**Add a new timer endpoint:**
- Edit `backend/routes/timers.py`
- Update `backend/models/timer.py` if needed

**Add a new Svelte component:**
- Create new file in `frontend/src/components/`
- Import and use in `App.svelte`

### Rebuild Docker Image
```bash
docker-compose build --no-cache
```

## Troubleshooting

**Port conflicts:**
- Backend: Change port 8000 in `docker-compose.yml`
- Frontend: Change port 5173 in `docker-compose.yml`

**CORS errors:**
- Ensure backend is running on http://localhost:8000
- Check `API_URL` in frontend environment variables

**Data not persisting:**
- Ensure `backend/data/` directory is created
- Check file permissions in the data directory

## Future Enhancements

- [ ] Reporting/analytics dashboard
- [ ] Export data to CSV
- [ ] Recurring tasks
- [ ] Time blocking/planning
- [ ] Search functionality
- [ ] Settings and preferences

## License

MIT
