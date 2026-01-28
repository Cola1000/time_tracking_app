# Time Tracking App 🕐

A local time tracking application built with FastAPI (Python) backend, Svelte frontend, and Docker. No authentication required - designed to run locally on your browser with JSON file storage.

## Features

✅ **Start/Stop Timer** - Real-time timer with pause and reset  
✅ **Manual Entry** - Create time entries manually with custom times  
✅ **Projects & Categories** - Organize time entries by project and category  
✅ **Weekly Calendar View** - Toggl-style calendar divided by week and day  
✅ **Daily Reports** - View total time per day with breakdown by project/category  
✅ **JSON Storage** - All data saved locally as JSON files (no database needed)  
✅ **Responsive Design** - Works on desktop and mobile browsers  

## Tech Stack

- **Backend**: FastAPI (Python)
- **Frontend**: Svelte + Vite
- **Storage**: JSON files (local)
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
│   │   │   └── Timer.svelte
│   │   ├── styles/
│   │   └── main.js
│   ├── package.json
│   ├── vite.config.js
│   └── Dockerfile
└── docker-compose.yml      # Docker orchestration
```

## Quick Start

### Option 1: Using Docker Compose (Recommended)

```bash
# Start both backend and frontend
docker-compose up --build

# App will be available at http://localhost:5173
```

### Option 2: Local Development

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
