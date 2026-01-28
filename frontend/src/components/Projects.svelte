<script>
  import { onMount } from 'svelte';
  import axios from 'axios';
  import '../styles/projects.css';

  const API_URL = 'http://localhost:8000/api';

  let allProjects = {};
  let selectedProject = null;
  let loading = false;
  let currentDate = new Date();
  let searchQuery = '';
  let filteredProjects = {};

  function formatDate(date) {
    return date.toISOString().split('T')[0];
  }

  function formatDuration(seconds) {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    if (hours > 0) {
      return `${hours}h ${minutes}m`;
    }
    return `${minutes}m`;
  }

  async function loadAllProjects() {
    loading = true;
    try {
      const allData = allProjects;
      const projects = {};

      // Load data for last 90 days to build project list
      for (let i = 0; i < 90; i++) {
        const date = new Date();
        date.setDate(date.getDate() - i);
        const dateStr = formatDate(date);

        try {
          const response = await axios.get(`${API_URL}/timers/${dateStr}`);
          const entries = response.data.entries || [];

          entries.forEach(entry => {
            const project = entry.project || 'Uncategorized';
            if (!projects[project]) {
              projects[project] = [];
            }
            projects[project].push({
              ...entry,
              date: dateStr,
            });
          });
        } catch (error) {
          // Date might not exist, continue
        }
      }

      // Sort entries by date descending (newest first)
      Object.keys(projects).forEach(project => {
        projects[project].sort((a, b) => new Date(b.date) - new Date(a.date));
      });

      allProjects = projects;
      filteredProjects = projects; // Initialize filtered projects
    } catch (error) {
      console.error('Error loading projects:', error);
    }
    loading = false;
  }

  function selectProject(project) {
    selectedProject = selectedProject === project ? null : project;
  }

  function getTotalHours(entries) {
    const totalSeconds = entries.reduce((sum, entry) => sum + entry.duration, 0);
    return (totalSeconds / 3600).toFixed(2);
  }

  function getProjectStats(project) {
    const entries = allProjects[project] || [];
    const totalSeconds = entries.reduce((sum, entry) => sum + entry.duration, 0);
    const totalHours = (totalSeconds / 3600).toFixed(2);
    const avgDuration = entries.length > 0 ? (totalSeconds / entries.length).toFixed(0) : 0;

    return {
      totalHours,
      totalEntries: entries.length,
      avgDuration: formatDuration(avgDuration),
    };
  }

  async function deleteEntry(entryId, project, date) {
    if (!confirm('Are you sure you want to delete this entry?')) {
      return;
    }

    try {
      await axios.delete(`${API_URL}/timers/${entryId}`);
      
      // Remove entry from local state
      allProjects[project] = allProjects[project].filter(e => e.id !== entryId);
      
      // If project has no more entries, remove it
      if (allProjects[project].length === 0) {
        delete allProjects[project];
        if (selectedProject === project) {
          selectedProject = null;
        }
      }
      
      allProjects = allProjects; // Trigger reactivity
      filterProjects(); // Update filtered view
    } catch (error) {
      console.error('Error deleting entry:', error);
      alert('Failed to delete entry. Please try again.');
    }
  }

  function filterProjects() {
    if (!searchQuery.trim()) {
      filteredProjects = allProjects;
      return;
    }

    const query = searchQuery.toLowerCase();
    const filtered = {};

    Object.keys(allProjects).forEach(project => {
      const matchingEntries = allProjects[project].filter(entry => {
        const projectMatch = (entry.project || '').toLowerCase().includes(query);
        const categoryMatch = (entry.category || '').toLowerCase().includes(query);
        const descriptionMatch = (entry.description || '').toLowerCase().includes(query);
        const dateMatch = entry.date.includes(query);
        const formattedDateMatch = new Date(entry.date).toLocaleDateString('en-US').toLowerCase().includes(query);
        
        return projectMatch || categoryMatch || descriptionMatch || dateMatch || formattedDateMatch;
      });

      if (matchingEntries.length > 0) {
        filtered[project] = matchingEntries;
      }
    });

    filteredProjects = filtered;
  }

  $: {
    searchQuery;
    filterProjects();
  }

  onMount(() => {
    loadAllProjects();
  });
</script>

<div class="projects-container">
  <div class="projects-header">
    <h2>Projects</h2>
    <p class="subtitle">View all your projects and their entries</p>
    
    <div class="search-container">
      <input 
        type="text" 
        placeholder="Search by project, category, description, or date..." 
        bind:value={searchQuery}
        class="search-input"
      />
      {#if searchQuery}
        <button class="clear-search" on:click={() => searchQuery = ''}>✕</button>
      {/if}
    </div>
  </div>

  {#if loading}
    <p class="loading">Loading projects...</p>
  {:else if Object.keys(filteredProjects).length === 0}
    <div class="empty-state">
      {#if searchQuery}
        <p>No entries found matching "{searchQuery}"</p>
      {:else}
        <p>No projects found. Start tracking time to create projects!</p>
      {/if}
    </div>
  {:else}
    <div class="projects-list">
      {#each Object.keys(filteredProjects).sort() as project (project)}
        <div class="project-item">
          <div class="project-header" on:click={() => selectProject(project)}>
            <h3>{project}</h3>
            <div class="project-stats">
              <span class="stat-item">
                <span class="stat-label">Total Hours:</span>
                <span class="stat-value">{getProjectStats(project).totalHours}h</span>
              </span>
              <span class="stat-item">
                <span class="stat-label">Entries:</span>
                <span class="stat-value">{getProjectStats(project).totalEntries}</span>
              </span>
              <span class="stat-item">
                <span class="stat-label">Avg Duration:</span>
                <span class="stat-value">{getProjectStats(project).avgDuration}</span>
              </span>
              <span class="toggle-icon">{selectedProject === project ? '▼' : '▶'}</span>
            </div>
          </div>

          {#if selectedProject === project}
            <div class="project-entries">
              {#each filteredProjects[project] as entry (entry.id)}
                <div class="entry-item">
                  <div class="entry-date-time">
                    <span class="date">{new Date(entry.date).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: '2-digit' })}</span>
                    <span class="time">
                      {new Date(entry.start_time).toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' })}
                      {#if entry.end_time}
                        → {new Date(entry.end_time).toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' })}
                      {/if}
                    </span>
                  </div>
                  <div class="entry-details">
                    <span class="category-tag">{entry.category || 'Uncategorized'}</span>
                    {#if entry.description}
                      <p class="description">{entry.description}</p>
                    {/if}
                  </div>
                  <div class="entry-duration">
                    {formatDuration(entry.duration)}
                  </div>
                  <button 
                    class="delete-btn" 
                    on:click={() => deleteEntry(entry.id, project, entry.date)}
                    title="Delete entry"
                  >
                    🗑️
                  </button>
                </div>
              {/each}
            </div>
          {/if}
        </div>
      {/each}
    </div>
  {/if}
</div>

