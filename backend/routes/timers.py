from fastapi import APIRouter, HTTPException
from models.timer import TimerEntry, TimerCreate, DayActivitySummary, ProjectListSync, CategoryListSync, SettingName, ColorUpdate
from datetime import datetime, timedelta
import json
import os
import uuid

router = APIRouter()

DATA_DIR = "data"
SETTINGS_FILE = os.path.join(DATA_DIR, "settings.json")

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
    date = timer.date  # Use the date provided by client to avoid timezone issues
    
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

def load_settings() -> dict:
    """Load settings from file"""
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, 'r', encoding='utf-8-sig') as f:
            return json.load(f)
    return {"projects": [], "categories": [], "project_colors": {}, "category_colors": {}}

def save_settings(settings: dict) -> None:
    """Save settings to file"""
    with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
        json.dump(settings, f, indent=2)

# Enhanced color palette - vibrant, distinct colors that work well in gradients
# Red/Pink hues
COLOR_PALETTE = [
    "#FF4757",  # Vibrant Red
    "#FF6348",  # Tomato
    "#FF5252",  # Deep Red
    "#FF1744",  # Deep Pink
    "#E91E63",  # Pink
    "#C2185B",  # Darker Pink
    # Orange hues
    "#FF9800",  # Orange
    "#FF8A50",  # Deep Orange
    "#FF6E40",  # Deep Orange 2
    "#FF5722",  # Deep Orange 3
    "#FFA726",  # Orange Accent
    # Yellow hues
    "#FBC02D",  # Amber
    "#FFD54F",  # Amber Light
    "#FDD835",  # Yellow
    "#FFEE58",  # Yellow Light
    # Green hues
    "#4CAF50",  # Green
    "#45B7D1",  # Teal (fresh)
    "#26A69A",  # Teal
    "#009688",  # Teal Dark
    "#00897B",  # Teal Darker
    "#66BB6A",  # Green Light
    # Cyan/Blue hues
    "#00BCD4",  # Cyan
    "#0097A7",  # Cyan Dark
    "#00ACC1",  # Cyan Accent
    "#006064",  # Cyan Very Dark
    "#2196F3",  # Blue
    "#1976D2",  # Blue Dark
    "#1565C0",  # Blue Darker
    "#0D47A1",  # Blue Very Dark
    # Purple/Indigo hues
    "#9C27B0",  # Purple
    "#7B1FA2",  # Purple Dark
    "#512DA8",  # Deep Purple
    "#3F51B5",  # Indigo
    "#303F9F",  # Indigo Dark
    # Pink/Magenta hues
    "#E91E63",  # Pink
    "#F06292",  # Pink Light
    "#F48FB1",  # Pink Lighter
]

def hex_to_rgb(hex_color: str) -> tuple:
    """Convert hex color to RGB tuple"""
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def color_distance(color1: str, color2: str) -> float:
    """Calculate perceived distance between two colors using Euclidean distance in RGB space"""
    if not color1 or not color2:
        return float('inf')
    
    try:
        r1, g1, b1 = hex_to_rgb(color1)
        r2, g2, b2 = hex_to_rgb(color2)
        
        # Weighted distance to account for human perception
        # Green is perceived as brighter than red and blue
        return ((r2 - r1) ** 2 * 0.299 + (g2 - g1) ** 2 * 0.587 + (b2 - b1) ** 2 * 0.114) ** 0.5
    except:
        return float('inf')

def get_color_for_project(project_name: str, project_colors: dict, category_colors: dict = None) -> str:
    """Get or assign a color for a project, ensuring it's distinct from category colors"""
    if project_name in project_colors:
        return project_colors[project_name]
    
    if category_colors is None:
        category_colors = {}
    
    # Find the color that's most different from all category colors
    best_color = None
    best_distance = -1
    
    for color in COLOR_PALETTE:
        if color in project_colors.values():
            continue  # Skip colors already used
        
        # Calculate minimum distance to any category color
        min_distance = min([color_distance(color, cat_color) for cat_color in category_colors.values()], default=float('inf'))
        
        # We want a color that's far from all category colors
        if min_distance > best_distance:
            best_distance = min_distance
            best_color = color
    
    # If all colors are taken or similar, just use sequential
    if best_color is None:
        color_index = len(project_colors) % len(COLOR_PALETTE)
        best_color = COLOR_PALETTE[color_index]
    
    project_colors[project_name] = best_color
    return best_color

def get_color_for_category(category_name: str, category_colors: dict, project_colors: dict = None) -> str:
    """Get or assign a color for a category, ensuring it's distinct from project colors"""
    if category_name in category_colors:
        return category_colors[category_name]
    
    if project_colors is None:
        project_colors = {}
    
    # Find the color that's most different from all project colors
    best_color = None
    best_distance = -1
    
    for color in COLOR_PALETTE:
        if color in category_colors.values():
            continue  # Skip colors already used
        
        # Calculate minimum distance to any project color
        min_distance = min([color_distance(color, proj_color) for proj_color in project_colors.values()], default=float('inf'))
        
        # We want a color that's far from all project colors
        if min_distance > best_distance:
            best_distance = min_distance
            best_color = color
    
    # If all colors are taken or similar, just use sequential
    if best_color is None:
        color_index = len(category_colors) % len(COLOR_PALETTE)
        best_color = COLOR_PALETTE[color_index]
    
    category_colors[category_name] = best_color
    return best_color

@router.get("/settings/projects", response_model=list)
def get_projects():
    """Get all custom projects"""
    settings = load_settings()
    return settings.get("projects", [])

@router.post("/settings/projects", response_model=list)
def add_project(project: SettingName):
    """Add a new project"""
    settings = load_settings()
    projects = settings.get("projects", [])
    
    project_name = project.name.strip()
    if project_name and project_name not in projects:
        projects.append(project_name)
        settings["projects"] = projects
        
        # Auto-assign color, considering existing category colors
        project_colors = settings.get("project_colors", {})
        category_colors = settings.get("category_colors", {})
        if project_name not in project_colors:
            project_colors[project_name] = get_color_for_project(project_name, project_colors, category_colors)
            settings["project_colors"] = project_colors
        
        save_settings(settings)
    
    return settings.get("projects", [])

@router.put("/settings/projects", response_model=list)
def sync_projects(projects_data: ProjectListSync):
    """Sync projects list (merge with existing)"""
    settings = load_settings()
    existing_projects = set(settings.get("projects", []))
    new_projects = set(projects_data.projects)
    
    # Merge both lists
    merged = sorted(list(existing_projects.union(new_projects)))
    settings["projects"] = merged
    
    # Assign colors to new projects, considering existing category colors
    project_colors = settings.get("project_colors", {})
    category_colors = settings.get("category_colors", {})
    for proj in merged:
        if proj not in project_colors:
            project_colors[proj] = get_color_for_project(proj, project_colors, category_colors)
    settings["project_colors"] = project_colors
    
    save_settings(settings)
    
    return merged

@router.get("/settings/categories", response_model=list)
def get_categories():
    """Get all custom categories"""
    settings = load_settings()
    return settings.get("categories", [])

@router.post("/settings/categories", response_model=list)
def add_category(category: SettingName):
    """Add a new category"""
    settings = load_settings()
    categories = settings.get("categories", [])
    
    category_name = category.name.strip()
    if category_name and category_name not in categories:
        categories.append(category_name)
        settings["categories"] = categories
        
        # Auto-assign color, considering existing project colors
        category_colors = settings.get("category_colors", {})
        project_colors = settings.get("project_colors", {})
        if category_name not in category_colors:
            category_colors[category_name] = get_color_for_category(category_name, category_colors, project_colors)
            settings["category_colors"] = category_colors
        
        save_settings(settings)
    
    return settings.get("categories", [])

@router.put("/settings/categories", response_model=list)
def sync_categories(categories_data: CategoryListSync):
    """Sync categories list (merge with existing)"""
    settings = load_settings()
    existing_categories = set(settings.get("categories", []))
    new_categories = set(categories_data.categories)
    
    # Merge both lists
    merged = sorted(list(existing_categories.union(new_categories)))
    settings["categories"] = merged
    
    # Assign colors to new categories, considering existing project colors
    category_colors = settings.get("category_colors", {})
    project_colors = settings.get("project_colors", {})
    for cat in merged:
        if cat not in category_colors:
            category_colors[cat] = get_color_for_category(cat, category_colors, project_colors)
    settings["category_colors"] = category_colors
    
    save_settings(settings)
    
    return merged

@router.get("/settings/colors", response_model=dict)
def get_all_colors():
    """Get all project and category colors"""
    settings = load_settings()
    
    # Ensure color dicts exist
    project_colors = settings.get("project_colors", {})
    category_colors = settings.get("category_colors", {})
    
    # Auto-assign colors to any projects/categories without them
    projects = settings.get("projects", [])
    categories = settings.get("categories", [])
    
    colors_updated = False
    for project in projects:
        if project not in project_colors:
            project_colors[project] = get_color_for_project(project, project_colors, category_colors)
            colors_updated = True
    
    for category in categories:
        if category not in category_colors:
            category_colors[category] = get_color_for_category(category, category_colors, project_colors)
            colors_updated = True
    
    if colors_updated:
        settings["project_colors"] = project_colors
        settings["category_colors"] = category_colors
        save_settings(settings)
    
    return {
        "project_colors": project_colors,
        "category_colors": category_colors
    }

@router.put("/settings/project-color/{project_name}", response_model=dict)
def set_project_color(project_name: str, color_data: ColorUpdate):
    """Set a specific color for a project"""
    settings = load_settings()
    project_colors = settings.get("project_colors", {})
    
    if color_data.color:
        project_colors[project_name] = color_data.color
        settings["project_colors"] = project_colors
        save_settings(settings)
    
    return {"project_name": project_name, "color": project_colors.get(project_name)}

@router.put("/settings/category-color/{category_name}", response_model=dict)
def set_category_color(category_name: str, color_data: ColorUpdate):
    """Set a specific color for a category"""
    settings = load_settings()
    category_colors = settings.get("category_colors", {})
    
    if color_data.color:
        category_colors[category_name] = color_data.color
        settings["category_colors"] = category_colors
        save_settings(settings)
    
    return {"category_name": category_name, "color": category_colors.get(category_name)}
