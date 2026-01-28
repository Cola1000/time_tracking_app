// Local storage management for custom projects and categories

export function getCustomProjects() {
  if (typeof window === 'undefined') return [];
  const stored = localStorage.getItem('customProjects');
  return stored ? JSON.parse(stored) : [];
}

export function addCustomProject(project) {
  const projects = getCustomProjects();
  if (!projects.includes(project) && project.trim()) {
    projects.push(project);
    localStorage.setItem('customProjects', JSON.stringify(projects));
  }
}

export function getCustomCategories() {
  if (typeof window === 'undefined') return [];
  const stored = localStorage.getItem('customCategories');
  return stored ? JSON.parse(stored) : [];
}

export function addCustomCategory(category) {
  const categories = getCustomCategories();
  if (!categories.includes(category) && category.trim()) {
    categories.push(category);
    localStorage.setItem('customCategories', JSON.stringify(categories));
  }
}
