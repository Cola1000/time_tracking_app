// Local storage management for custom projects and categories
import axios from 'axios';

const API_URL = 'http://localhost:8000/api';

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
}
