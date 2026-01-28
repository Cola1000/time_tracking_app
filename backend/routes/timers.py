from fastapi import APIRouter, HTTPException
from models.timer import TimerEntry, TimerCreate, DayActivitySummary
from datetime import datetime, timedelta
import json
import os
import uuid

router = APIRouter()

DATA_DIR = "data"

def get_data_file(date: str) -> str:
    """Get the path to the data file for a given date (YYYY-MM-DD)"""
    return os.path.join(DATA_DIR, f"{date}.json")

def load_day_data(date: str) -> dict:
    """Load all entries for a specific day"""
    file_path = get_data_file(date)
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            return json.load(f)
    return {"date": date, "entries": [], "total_duration": 0}

def save_day_data(date: str, data: dict) -> None:
    """Save entries for a specific day"""
    file_path = get_data_file(date)
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=2)

def calculate_total_duration(entries: list) -> int:
    """Calculate total duration from entries in seconds"""
    return sum(entry.get("duration", 0) for entry in entries)

def ensure_total_duration(date: str, day_data: dict) -> dict:
    """Ensure total_duration matches actual sum of entries"""
    entries = day_data.get("entries", [])
    day_data["total_duration"] = calculate_total_duration(entries)
    return day_data

@router.post("/timers", response_model=TimerEntry)
def create_timer(timer: TimerCreate):
    """Create a new timer entry"""
    entry_id = str(uuid.uuid4())
    date = timer.start_time.strftime("%Y-%m-%d")
    
    entry_dict = {
        "id": entry_id,
        "project": timer.project,
        "category": timer.category,
        "description": timer.description,
        "start_time": timer.start_time.isoformat(),
        "end_time": timer.end_time.isoformat() if timer.end_time else None,
        "duration": timer.duration,
        "date": date
    }
    
    day_data = load_day_data(date)
    day_data["entries"].append(entry_dict)
    day_data["total_duration"] = calculate_total_duration(day_data["entries"])
    save_day_data(date, day_data)
    
    return TimerEntry(**entry_dict)

@router.get("/timers/{date}", response_model=DayActivitySummary)
def get_day_timers(date: str):
    """Get all timer entries for a specific day (format: YYYY-MM-DD)"""
    try:
        datetime.strptime(date, "%Y-%m-%d")
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
    
    day_data = load_day_data(date)
    # Ensure total_duration is correct even if entries were manually deleted
    day_data = ensure_total_duration(date, day_data)
    save_day_data(date, day_data)  # Save corrected data
    return DayActivitySummary(
        date=date,
        total_duration=day_data.get("total_duration", 0),
        entries=[TimerEntry(**entry) for entry in day_data.get("entries", [])]
    )

@router.get("/timers/week/{start_date}", response_model=dict)
def get_week_timers(start_date: str):
    """Get all timer entries for a week (7 days starting from start_date)"""
    try:
        start = datetime.strptime(start_date, "%Y-%m-%d")
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
    
    week_data = {}
    for i in range(7):
        date = (start + timedelta(days=i)).strftime("%Y-%m-%d")
        day_data = load_day_data(date)
        # Ensure total_duration is correct even if entries were manually deleted
        day_data = ensure_total_duration(date, day_data)
        save_day_data(date, day_data)  # Save corrected data
        week_data[date] = {
            "total_duration": day_data.get("total_duration", 0),
            "entries": day_data.get("entries", [])
        }
    
    return week_data

@router.put("/timers/{entry_id}", response_model=TimerEntry)
def update_timer(entry_id: str, timer: TimerCreate):
    """Update an existing timer entry"""
    new_date = timer.start_time.strftime("%Y-%m-%d")
    
    # First, find and delete the old entry from any date (past or future)
    today = datetime.now()
    old_date = None
    # Search 30 days in the past and 30 days in the future
    for i in range(-30, 31):
        date = (today + timedelta(days=i)).strftime("%Y-%m-%d")
        day_data = load_day_data(date)
        
        for idx, entry in enumerate(day_data["entries"]):
            if entry["id"] == entry_id:
                old_date = date
                day_data["entries"].pop(idx)
                day_data["total_duration"] = calculate_total_duration(day_data["entries"])
                save_day_data(date, day_data)
                break
        
        if old_date:
            break
    
    if not old_date:
        raise HTTPException(status_code=404, detail="Timer entry not found")
    
    # Create updated entry on new date
    updated_entry = {
        "id": entry_id,
        "project": timer.project,
        "category": timer.category,
        "description": timer.description,
        "start_time": timer.start_time.isoformat(),
        "end_time": timer.end_time.isoformat() if timer.end_time else None,
        "duration": timer.duration,
        "date": new_date
    }
    
    new_day_data = load_day_data(new_date)
    new_day_data["entries"].append(updated_entry)
    new_day_data["total_duration"] = calculate_total_duration(new_day_data["entries"])
    save_day_data(new_date, new_day_data)
    
    return TimerEntry(**updated_entry)

@router.delete("/timers/{entry_id}")
def delete_timer(entry_id: str):
    """Delete a timer entry"""
    # Search through all recent and future dates to find and delete the entry
    today = datetime.now()
    # Search 30 days in the past and 30 days in the future
    for i in range(-30, 31):
        date = (today + timedelta(days=i)).strftime("%Y-%m-%d")
        day_data = load_day_data(date)
        
        for idx, entry in enumerate(day_data["entries"]):
            if entry["id"] == entry_id:
                day_data["entries"].pop(idx)
                day_data["total_duration"] = calculate_total_duration(day_data["entries"])
                save_day_data(date, day_data)
                return {"message": "Timer entry deleted"}
    
    raise HTTPException(status_code=404, detail="Timer entry not found")

@router.get("/stats/week/{start_date}", response_model=dict)
def get_week_stats(start_date: str):
    """Get weekly statistics with breakdown by project and category"""
    try:
        start = datetime.strptime(start_date, "%Y-%m-%d")
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
    
    week_data = {}
    projects = {}
    categories = {}
    total_seconds = 0
    
    for i in range(7):
        date = (start + timedelta(days=i)).strftime("%Y-%m-%d")
        day_data = load_day_data(date)
        
        week_data[date] = day_data.get("total_duration", 0)
        total_seconds += day_data.get("total_duration", 0)
        
        for entry in day_data.get("entries", []):
            project = entry.get("project", "Uncategorized")
            category = entry.get("category", "Uncategorized")
            duration = entry.get("duration", 0)
            
            projects[project] = projects.get(project, 0) + duration
            categories[category] = categories.get(category, 0) + duration
    
    return {
        "total_seconds": total_seconds,
        "daily_breakdown": week_data,
        "project_breakdown": projects,
        "category_breakdown": categories
    }
