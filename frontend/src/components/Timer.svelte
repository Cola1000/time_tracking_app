<script>
  import { createEventDispatcher, onMount } from 'svelte';
  import axios from 'axios';
  import { getCustomProjects, getCustomCategories, addCustomProject, addCustomCategory } from '../utils/storage';

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
  <div class="timer-display">
    <div class="timer-time">{formatTime(elapsedSeconds)}</div>
    <div class="timer-controls">
      <button 
        class="btn-primary"
        on:click={isRunning ? stopTimer : startTimer}
      >
        {isRunning ? '⏸ Stop' : '▶ Start'}
      </button>
      <button class="btn-secondary" on:click={resetTimer}>⟲ Reset</button>
    </div>
  </div>

  <div class="form-section">
    <div class="form-group">
      <label>Project</label>
      <div class="input-group">
        <select bind:value={formData.project}>
          <option value="">Select a project...</option>
          {#each projects as project}
            <option value={project}>{project}</option>
          {/each}
        </select>
        <input 
          type="text" 
          placeholder="New project name"
          bind:value={customProjectInput}
        />
        <button 
          class="btn-add"
          on:click={() => {
            if (customProjectInput.trim()) {
              addCustomProject(customProjectInput);
              formData.project = customProjectInput;
              projects = getCustomProjects();
              customProjectInput = '';
            }
          }}
        >
          Add
        </button>
      </div>
    </div>

    <div class="form-group">
      <label>Category</label>
      <div class="input-group">
        <select bind:value={formData.category}>
          <option value="">Select a category...</option>
          {#each categories as category}
            <option value={category}>{category}</option>
          {/each}
        </select>
        <input 
          type="text" 
          placeholder="New category name"
          bind:value={customCategoryInput}
        />
        <button 
          class="btn-add"
          on:click={() => {
            if (customCategoryInput.trim()) {
              addCustomCategory(customCategoryInput);
              formData.category = customCategoryInput;
              categories = getCustomCategories();
              customCategoryInput = '';
            }
          }}
        >
          Add
        </button>
      </div>
    </div>

    <div class="form-group">
      <label>Description (optional)</label>
      <textarea
        bind:value={formData.description}
        placeholder="What are you working on?"
        rows="3"
      ></textarea>
    </div>

    <div class="form-row">
      <div class="form-group">
        <label>Start Time</label>
        <input type="datetime-local" bind:value={formData.startTime} />
      </div>
      <div class="form-group">
        <label>End Time</label>
        <input type="datetime-local" bind:value={formData.endTime} />
      </div>
    </div>

    <button class="btn-save" on:click={submitEntry}>💾 Save Entry</button>
  </div>
</div>

<style>
  .timer-container {
    display: flex;
    flex-direction: column;
    gap: 20px;
  }

  .timer-display {
    text-align: center;
  }

  .timer-time {
    font-size: 48px;
    font-weight: 700;
    color: #4CAF50;
    font-family: 'Monaco', 'Courier New', monospace;
    margin-bottom: 16px;
    letter-spacing: 4px;
  }

  .timer-controls {
    display: flex;
    gap: 12px;
    justify-content: center;
    flex-wrap: wrap;
  }

  .btn-primary {
    background-color: #4CAF50;
    color: white;
    padding: 12px 24px;
    font-size: 16px;
    font-weight: 600;
    min-width: 120px;
  }

  .btn-primary:hover {
    background-color: #45a049;
  }

  .btn-secondary {
    background-color: #ff9800;
    color: white;
    padding: 12px 24px;
    font-size: 16px;
    font-weight: 600;
    min-width: 120px;
  }

  .btn-secondary:hover {
    background-color: #e68900;
  }

  .form-section {
    display: flex;
    flex-direction: column;
    gap: 16px;
  }

  .form-group {
    display: flex;
    flex-direction: column;
    gap: 8px;
  }

  .form-group label {
    font-weight: 600;
    color: #2c3e50;
    font-size: 14px;
  }

  .input-group {
    display: flex;
    gap: 8px;
    align-items: center;
  }

  .input-group select {
    flex: 1;
  }

  .input-group input {
    flex: 1;
  }

  .btn-add {
    background-color: #4CAF50;
    color: white;
    padding: 8px 16px;
    font-size: 14px;
    font-weight: 600;
    white-space: nowrap;
  }

  .btn-add:hover {
    background-color: #45a049;
  }

  .form-group select,
  .form-group input,
  .form-group textarea {
    width: 100%;
  }

  .form-row {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 16px;
  }

  .btn-save {
    background-color: #2196F3;
    color: white;
    padding: 14px;
    font-size: 16px;
    font-weight: 600;
    margin-top: 8px;
  }

  .btn-save:hover {
    background-color: #1976D2;
  }

  @media (max-width: 768px) {
    .form-row {
      grid-template-columns: 1fr;
    }

    .timer-time {
      font-size: 36px;
    }
  }
</style>
