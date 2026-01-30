// Local storage management for custom projects and categories
import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

// Color palette - same as backend, vibrant and distinct
const COLOR_PALETTE = [
  "#FF4757",  // Vibrant Red
  "#FF6348",  // Tomato
  "#FF5252",  // Deep Red
  "#FF1744",  // Deep Pink
  "#E91E63",  // Pink
  "#C2185B",  // Darker Pink
  // Orange hues
  "#FF9800",  // Orange
  "#FF8A50",  // Deep Orange
  "#FF6E40",  // Deep Orange 2
  "#FF5722",  // Deep Orange 3
  "#FFA726",  // Orange Accent
  // Yellow hues
  "#FBC02D",  // Amber
  "#FFD54F",  // Amber Light
  "#FDD835",  // Yellow
  "#FFEE58",  // Yellow Light
  // Green hues
  "#4CAF50",  // Green
  "#45B7D1",  // Teal (fresh)
  "#26A69A",  // Teal
  "#009688",  // Teal Dark
  "#00897B",  // Teal Darker
  "#66BB6A",  // Green Light
  // Cyan/Blue hues
  "#00BCD4",  // Cyan
  "#0097A7",  // Cyan Dark
  "#00ACC1",  // Cyan Accent
  "#006064",  // Cyan Very Dark
  "#2196F3",  // Blue
  "#1976D2",  // Blue Dark
  "#1565C0",  // Blue Darker
  "#0D47A1",  // Blue Very Dark
  // Purple/Indigo hues
  "#9C27B0",  // Purple
  "#7B1FA2",  // Purple Dark
  "#512DA8",  // Deep Purple
  "#3F51B5",  // Indigo
  "#303F9F",  // Indigo Dark
  // Pink/Magenta hues
  "#E91E63",  // Pink
  "#F06292",  // Pink Light
  "#F48FB1",  // Pink Lighter
];

export function getCustomProjects() {
  if (typeof window === 'undefined') return [];
  const stored = localStorage.getItem('customProjects');
  return stored ? JSON.parse(stored) : [];
}

export async function addCustomProject(project) {
  const projects = getCustomProjects();
  if (!projects.includes(project) && project.trim()) {
    projects.push(project);
    localStorage.setItem('customProjects', JSON.stringify(projects));
    
    // Also save to backend
    try {
      await axios.post(`${API_URL}/settings/projects`, { name: project });
    } catch (error) {
      console.error('Error saving project to backend:', error);
    }
  }
}

export function getCustomCategories() {
  if (typeof window === 'undefined') return [];
  const stored = localStorage.getItem('customCategories');
  return stored ? JSON.parse(stored) : [];
}

export async function addCustomCategory(category) {
  const categories = getCustomCategories();
  if (!categories.includes(category) && category.trim()) {
    categories.push(category);
    localStorage.setItem('customCategories', JSON.stringify(categories));
    
    // Also save to backend
    try {
      await axios.post(`${API_URL}/settings/categories`, { name: category });
    } catch (error) {
      console.error('Error saving category to backend:', error);
    }
  }
}

// Color management
let colorCache = null;

export async function getColors() {
  try {
    if (!colorCache) {
      const response = await axios.get(`${API_URL}/settings/colors`);
      colorCache = response.data;
      // Store in localStorage for quick access
      localStorage.setItem('colorCache', JSON.stringify(colorCache));
    }
    return colorCache;
  } catch (error) {
    console.error('Error fetching colors:', error);
    // Fall back to localStorage cache if available
    const cached = localStorage.getItem('colorCache');
    return cached ? JSON.parse(cached) : { project_colors: {}, category_colors: {} };
  }
}

export function getCachedColors() {
  if (colorCache) {
    return colorCache;
  }
  
  const cached = localStorage.getItem('colorCache');
  if (cached) {
    colorCache = JSON.parse(cached);
    return colorCache;
  }
  
  return { project_colors: {}, category_colors: {} };
}

export function getProjectColor(projectName) {
  const colors = getCachedColors();
  return colors.project_colors[projectName] || "#808080";
}

export function getCategoryColor(categoryName) {
  const colors = getCachedColors();
  return colors.category_colors[categoryName] || "#808080";
}

export function getGradientStyle(projectName, categoryName) {
  const projectColor = getProjectColor(projectName);
  const categoryColor = getCategoryColor(categoryName);
  return `linear-gradient(135deg, ${projectColor} 0%, ${categoryColor} 100%)`;
}

// Sync functions to merge localStorage with backend
export async function syncProjects() {
  try {
    const localProjects = getCustomProjects();
    
    // Send local projects to backend and get merged list
    const response = await axios.put(`${API_URL}/settings/projects`, { 
      projects: localProjects 
    });
    
    const mergedProjects = response.data;
    
    // Update localStorage with merged list
    localStorage.setItem('customProjects', JSON.stringify(mergedProjects));
    
    return mergedProjects;
  } catch (error) {
    console.error('Error syncing projects:', error);
    return getCustomProjects();
  }
}

export async function syncCategories() {
  try {
    const localCategories = getCustomCategories();
    
    // Send local categories to backend and get merged list
    const response = await axios.put(`${API_URL}/settings/categories`, { 
      categories: localCategories 
    });
    
    const mergedCategories = response.data;
    
    // Update localStorage with merged list
    localStorage.setItem('customCategories', JSON.stringify(mergedCategories));
    
    return mergedCategories;
  } catch (error) {
    console.error('Error syncing categories:', error);
    return getCustomCategories();
  }
}

// Sync both projects and categories
export async function syncAll() {
  await Promise.all([
    syncProjects(),
    syncCategories()
  ]);
  
  // Also refresh colors
  colorCache = null;
  await getColors();
}
