<script>
  import { createEventDispatcher, onMount } from 'svelte';
  import axios from 'axios';
  import { getCustomProjects, getCustomCategories, addCustomProject, addCustomCategory } from '../utils/storage';
  import '../styles/timer.css';

  export let activeDay;

  const dispatch = createEventDispatcher();
  const API_URL = 'http://localhost:8000/api';

  let isRunning = false;
  let startTime = null;
  let elapsedSeconds = 0;
  let intervalId = null;

  let formData = {
    project: '',
    category: '',
    description: '',
    startTime: new Date().toISOString().slice(0, 16),
    endTime: null,
  };

  let projects = [];
  let categories = [];
  let customProjectInput = '';
  let customCategoryInput = '';

  onMount(() => {
    projects = getCustomProjects();
    categories = getCustomCategories();
  });

  function startTimer() {
    isRunning = true;
    startTime = Date.now();
    
    intervalId = setInterval(() => {
      elapsedSeconds = Math.floor((Date.now() - startTime) / 1000);
    }, 100);
  }

  function stopTimer() {
    isRunning = false;
    if (intervalId) {
      clearInterval(intervalId);
    }
    formData.endTime = new Date().toISOString().slice(0, 16);
  }

  function resetTimer() {
    isRunning = false;
    if (intervalId) {
      clearInterval(intervalId);
    }
    elapsedSeconds = 0;
    startTime = null;
    formData.endTime = null;
    formData.startTime = new Date().toISOString().slice(0, 16);
  }

  function formatTime(seconds) {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = seconds % 60;
    
    if (hours > 0) {
      return `${hours}:${String(minutes).padStart(2, '0')}:${String(secs).padStart(2, '0')}`;
    }
    return `${String(minutes).padStart(2, '0')}:${String(secs).padStart(2, '0')}`;
  }

  async function submitEntry() {
    if (!formData.project || !formData.category) {
      alert('Please select a project and category');
      return;
    }

    const duration = formData.endTime 
      ? Math.floor((new Date(formData.endTime) - new Date(formData.startTime)) / 1000)
      : elapsedSeconds;

    const endTime = formData.endTime || new Date().toISOString();

    try {
      await axios.post(`${API_URL}/timers`, {
        project: formData.project,
        category: formData.category,
        description: formData.description,
        start_time: new Date(formData.startTime).toISOString(),
        end_time: new Date(endTime).toISOString(),
        duration: duration,
      });

      dispatch('timerAdded');
      resetTimer();
      formData.project = '';
      formData.category = '';
      formData.description = '';
    } catch (error) {
      console.error('Error saving timer:', error);
      alert('Error saving timer entry');
    }
  }
</script>

<div class="timer-container">
  <div class="timer-display">{formatTime(elapsedSeconds)}</div>
  
  <div class="timer-controls">
    <button 
      class="timer-btn start"
      on:click={isRunning ? stopTimer : startTimer}
    >
      {isRunning ? 'Stop' : 'Start'}
    </button>
    <button class="timer-btn reset" on:click={resetTimer}>Reset</button>
  </div>

  <div class="form-section">
    <div class="form-group">
      <label class="form-label">Project</label>
      <select class="form-select" bind:value={formData.project} on:change={(e) => {
        if (e.target.value === '__ADD_NEW__') {
          const newProject = prompt('Enter new project name:');
          if (newProject && newProject.trim()) {
            addCustomProject(newProject.trim());
            formData.project = newProject.trim();
            projects = getCustomProjects();
          } else {
            formData.project = '';
          }
        }
      }}>
        <option value="">Select a project...</option>
        {#each projects as project}
          <option value={project}>{project}</option>
        {/each}
        <option value="__ADD_NEW__">+ Add New Project</option>
      </select>
    </div>

    <div class="form-group">
      <label class="form-label">Category</label>
      <select class="form-select" bind:value={formData.category} on:change={(e) => {
        if (e.target.value === '__ADD_NEW__') {
          const newCategory = prompt('Enter new category name:');
          if (newCategory && newCategory.trim()) {
            addCustomCategory(newCategory.trim());
            formData.category = newCategory.trim();
            categories = getCustomCategories();
          } else {
            formData.category = '';
          }
        }
      }}>
        <option value="">Select a category...</option>
        {#each categories as category}
          <option value={category}>{category}</option>
        {/each}
        <option value="__ADD_NEW__">+ Add New Category</option>
      </select>
  </div>

    <div class="form-group">
      <label class="form-label">Description (optional)</label>
      <textarea
        class="form-textarea"
        bind:value={formData.description}
        placeholder="What are you working on?"
        rows="3"
      ></textarea>
    </div>

    <div class="form-row">
      <div class="form-group">
        <label class="form-label">Start Time</label>
        <input class="form-input" type="datetime-local" bind:value={formData.startTime} />
      </div>
      <div class="form-group">
        <label class="form-label">End Time</label>
        <input class="form-input" type="datetime-local" bind:value={formData.endTime} />
      </div>
    </div>

    <button class="save-btn" on:click={submitEntry}>Save Entry</button>
  </div>
</div>

