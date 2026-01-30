<script>
  import { createEventDispatcher, onMount } from 'svelte';
  import axios from 'axios';
  import { timerStore } from '../stores/timer';
  import { getCustomProjects, getCustomCategories, addCustomProject, addCustomCategory } from '../utils/storage';
  import '../styles/timer.css';

  export let activeDay;

  const dispatch = createEventDispatcher();
  const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

  let intervalId = null;
  let projects = [];
  let categories = [];
  let syncing = true;

  $: ({ isRunning, startTime, elapsedSeconds, stoppedTime, project, category, description, synced } = $timerStore);

  onMount(async () => {
    projects = getCustomProjects();
    categories = getCustomCategories();

    // Try to sync with backend timer first
    const hasBackendTimer = await timerStore.syncWithBackend();
    syncing = false;
    
    // Start the elapsed time updater if timer is running
    if ($timerStore.isRunning && $timerStore.startTime) {
      startElapsedUpdater();
    }

    return () => {
      if (intervalId) clearInterval(intervalId);
    };
  });

  function startElapsedUpdater() {
    if (intervalId) clearInterval(intervalId);
    intervalId = setInterval(() => {
      if ($timerStore.startTime) {
        timerStore.setElapsed(Math.floor((Date.now() - $timerStore.startTime) / 1000));
      }
    }, 100);
  }

  async function startTimer() {
    await timerStore.startTimer();
    startElapsedUpdater();
  }

  function stopTimer() {
    if (intervalId) clearInterval(intervalId);
    timerStore.stopTimer();
  }

  async function resetTimer() {
    if (intervalId) clearInterval(intervalId);
    await timerStore.resetTimer();
  }

  function formatTime(seconds) {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = seconds % 60;
    
    if (hours > 0) { // show hours only if greater than 0
      return `${hours}:${String(minutes).padStart(2, '0')}:${String(secs).padStart(2, '0')}`;
    }
    return `${String(minutes).padStart(2, '0')}:${String(secs).padStart(2, '0')}`;
  }

  function formatLocalTime(date) {
    return date.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', second: '2-digit' });
  }

  async function submitEntry() {
    if (!project || !category) {
      alert('Please select a project and category');
      return;
    }

    if (elapsedSeconds <= 0) {
      alert('Timer must be greater than 0');
      return;
    }

    try {
      // If we have a synced backend timer, use the backend stop endpoint
      if ($timerStore.synced && $timerStore.backendId) {
        // First update project/category if needed
        await axios.put(`${API_URL}/timer/update`, null, {
          params: { project, category, description }
        });
        await timerStore.submitToBackend();
        dispatch('timerAdded');
        return;
      }

      // Fallback to direct submission
      const endDate = new Date();
      const startDate = new Date(Date.now() - elapsedSeconds * 1000);
      
      // Use local date format (YYYY-MM-DD) based on when the timer ENDED
      const year = endDate.getFullYear();
      const month = String(endDate.getMonth() + 1).padStart(2, '0');
      const day = String(endDate.getDate()).padStart(2, '0');
      const dateKey = `${year}-${month}-${day}`;

      const payload = {
        project,
        category,
        description,
        start_time: startDate.toISOString(),
        end_time: endDate.toISOString(),
        duration: elapsedSeconds,
        date: dateKey,
      };
      
      console.log('Submitting timer entry:', payload);
      await axios.post(`${API_URL}/timers`, payload);

      dispatch('timerAdded');
      await resetTimer();
    } catch (error) {
      console.error('Error saving timer:', error);
      if (error.response?.data) {
        console.error('Validation errors:', error.response.data);
      }
      alert('Error saving timer entry');
    }
  }

  async function handleProjectChange(e) {
    if (e.target.value === '__ADD_NEW__') {
      const newProject = prompt('Enter new project name:');
      if (newProject && newProject.trim()) {
        await addCustomProject(newProject.trim());
        await timerStore.setProject(newProject.trim());
        projects = getCustomProjects();
      } else {
        await timerStore.setProject('');
      }
    } else {
      await timerStore.setProject(e.target.value);
    }
  }

  async function handleCategoryChange(e) {
    if (e.target.value === '__ADD_NEW__') {
      const newCategory = prompt('Enter new category name:');
      if (newCategory && newCategory.trim()) {
        await addCustomCategory(newCategory.trim());
        await timerStore.setCategory(newCategory.trim());
        categories = getCustomCategories();
      } else {
        await timerStore.setCategory('');
      }
    } else {
      await timerStore.setCategory(e.target.value);
    }
  }
</script>

<div class="timer-container">
  {#if syncing}
    <div class="timer-display syncing">Syncing...</div>
  {:else}
    <div class="timer-display">
      {formatTime(elapsedSeconds)}
      {#if isRunning && synced}
        <span class="sync-indicator" title="Timer synced with server">⚡</span>
      {/if}
    </div>
  {/if}
  
  {#if stoppedTime && !isRunning}
    <div class="stopped-time">
      Stopped at {formatLocalTime(stoppedTime)}
    </div>
  {/if}
  
  <div class="timer-controls">
    <button 
      class="timer-btn start"
      class:running={isRunning}
      on:click={isRunning ? stopTimer : startTimer}
    >
      {#if isRunning}
        <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <rect width="18" height="18" x="3" y="3" rx="2"/>
        </svg>
        <span>Stop</span>
      {:else}
        <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M5 5a2 2 0 0 1 3.008-1.728l11.997 6.998a2 2 0 0 1 .003 3.458l-12 7A2 2 0 0 1 5 19z"/>
        </svg>
        <span>Start</span>
      {/if}
    </button>
    <button class="timer-btn reset" on:click={resetTimer}>
      <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <path d="M3 12a9 9 0 1 0 9-9 9.75 9.75 0 0 0-6.74 2.74L3 8"/>
        <path d="M3 3v5h5"/>
      </svg>
      <span>Reset</span>
    </button>
  </div>

  <div class="form-section">
    <div class="form-group">
      <label class="form-label">Project</label>
      <select class="form-select" value={project} on:change={handleProjectChange}>
        <option value="">Select a project...</option>
        {#each projects as proj}
          <option value={proj}>{proj}</option>
        {/each}
        <option value="__ADD_NEW__">+ Add New Project</option>
      </select>
    </div>

    <div class="form-group">
      <label class="form-label">Category</label>
      <select class="form-select" value={category} on:change={handleCategoryChange}>
        <option value="">Select a category...</option>
        {#each categories as cat}
          <option value={cat}>{cat}</option>
        {/each}
        <option value="__ADD_NEW__">+ Add New Category</option>
      </select>
    </div>

    <div class="form-group">
      <label class="form-label">Description (optional)</label>
      <textarea
        class="form-textarea"
        value={description}
        on:change={(e) => timerStore.setDescription(e.target.value)}
        placeholder="What are you working on?"
        rows="3"
      ></textarea>
    </div>

    <button class="save-btn" on:click={submitEntry}>
        <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-save-icon lucide-save"><path d="M15.2 3a2 2 0 0 1 1.4.6l3.8 3.8a2 2 0 0 1 .6 1.4V19a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2z"/><path d="M17 21v-7a1 1 0 0 0-1-1H8a1 1 0 0 0-1 1v7"/><path d="M7 3v4a1 1 0 0 0 1 1h7"/></svg>
        <span>Save Entry</span>
    </button>
  </div>
</div>

