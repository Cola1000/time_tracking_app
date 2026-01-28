import { writable } from 'svelte/store';

// Get initial theme from environment variable or localStorage
const getInitialTheme = () => {
  // Check if theme is set via environment variable (from start script)
  const envTheme = import.meta.env.VITE_THEME;
  if (envTheme === 'light' || envTheme === 'dark') {
    return envTheme;
  }
  
  // Otherwise check localStorage
  const stored = localStorage.getItem('theme');
  if (stored === 'light' || stored === 'dark') {
    return stored;
  }
  
  // Default to dark
  return 'dark';
};

export const theme = writable(getInitialTheme());

// Apply theme to document
export function applyTheme(themeName) {
  if (themeName === 'dark') {
    document.documentElement.setAttribute('data-theme', 'dark');
  } else {
    document.documentElement.removeAttribute('data-theme');
  }
  localStorage.setItem('theme', themeName);
}

// Toggle theme
export function toggleTheme() {
  theme.update(current => {
    const newTheme = current === 'dark' ? 'light' : 'dark';
    applyTheme(newTheme);
    return newTheme;
  });
}

// Initialize theme on app load
applyTheme(getInitialTheme());
