<script>
  import { onMount } from 'svelte';
  import axios from 'axios';

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

<style>
  .projects-container {
    padding: 20px;
    max-width: 1200px;
    margin: 0 auto;
  }

  .projects-header {
    margin-bottom: 30px;
  }

  .projects-header h2 {
    margin: 0;
    font-size: 28px;
    color: #2c3e50;
  }

  .subtitle {
    margin: 8px 0 0 0;
    color: #7f8c8d;
    font-size: 14px;
  }

  .loading {
    text-align: center;
    color: #7f8c8d;
    padding: 20px;
  }

  .empty-state {
    text-align: center;
    padding: 40px;
    background-color: #f8f9fa;
    border-radius: 8px;
    color: #95a5a6;
  }

  .projects-list {
    display: flex;
    flex-direction: column;
    gap: 12px;
  }

  .project-item {
    background-color: white;
    border: 1px solid #ecf0f1;
    border-radius: 8px;
    overflow: hidden;
  }

  .project-header {
    padding: 20px;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    cursor: pointer;
    display: flex;
    justify-content: space-between;
    align-items: center;
    transition: all 0.2s ease;
  }

  .project-header:hover {
    opacity: 0.9;
  }

  .project-header h3 {
    margin: 0;
    font-size: 20px;
    font-weight: 600;
  }

  .project-stats {
    display: flex;
    gap: 20px;
    align-items: center;
    flex-wrap: wrap;
  }

  .stat-item {
    display: flex;
    flex-direction: column;
    align-items: flex-end;
    font-size: 12px;
  }

  .stat-label {
    opacity: 0.9;
    font-size: 11px;
  }

  .stat-value {
    font-weight: 700;
    font-size: 14px;
  }

  .toggle-icon {
    font-size: 16px;
    transition: transform 0.2s ease;
  }

  .project-entries {
    display: flex;
    flex-direction: column;
    border-top: 1px solid #ecf0f1;
  }

  .entry-item {
    padding: 16px 20px;
    border-bottom: 1px solid #ecf0f1;
    display: grid;
    grid-template-columns: 1fr auto;
    gap: 20px;
    align-items: start;
  }

  .entry-item:last-child {
    border-bottom: none;
  }

  .entry-date-time {
    display: flex;
    flex-direction: column;
    gap: 4px;
  }

  .date {
    font-weight: 600;
    color: #2c3e50;
    font-size: 14px;
  }

  .time {
    color: #7f8c8d;
    font-size: 13px;
  }

  .entry-details {
    flex: 1;
    display: flex;
    flex-direction: column;
    gap: 8px;
  }

  .category-tag {
    display: inline-block;
    background-color: #2196F3;
    color: white;
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 12px;
    font-weight: 500;
    width: fit-content;
  }

  .description {
    margin: 0;
    color: #2c3e50;
    font-size: 14px;
  }

  .entry-duration {
    font-weight: 700;
    color: #4CAF50;
    font-size: 16px;
    text-align: right;
  }

  @media (max-width: 768px) {
    .project-header {
      flex-direction: column;
      align-items: flex-start;
      gap: 12px;
    }

    .project-stats {
      width: 100%;
      justify-content: space-between;
    }

    .entry-item {
      grid-template-columns: 1fr;
      gap: 12px;
    }

    .entry-duration {
      text-align: left;
    }
  }
</style>
