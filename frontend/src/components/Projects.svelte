<script>
  import { onMount } from 'svelte';
  import axios from 'axios';
  import '../styles/projects.css';

  const API_URL = 'http://localhost:8000/api';

  let allProjects = {};
  let selectedProject = null;
  let loading = false;
  let currentDate = new Date();

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

  onMount(() => {
    loadAllProjects();
  });
</script>

<div class="projects-container">
  <div class="projects-header">
    <h2>Projects</h2>
    <p class="subtitle">View all your projects and their entries</p>
  </div>

  {#if loading}
    <p class="loading">Loading projects...</p>
  {:else if Object.keys(allProjects).length === 0}
    <div class="empty-state">
      <p>No projects found. Start tracking time to create projects!</p>
    </div>
  {:else}
    <div class="projects-list">
      {#each Object.keys(allProjects).sort() as project (project)}
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
              {#each allProjects[project] as entry (entry.id)}
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
                </div>
              {/each}
            </div>
          {/if}
        </div>
      {/each}
    </div>
  {/if}
</div>

