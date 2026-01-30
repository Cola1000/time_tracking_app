<script>
  import { createEventDispatcher, onMount } from 'svelte';
  import axios from 'axios';
  import { getCustomProjects, getCustomCategories, addCustomProject, addCustomCategory } from '../utils/storage';

  export let isOpen = false;
  export let entry = null; // null for new entry, or entry object for edit mode
  export let selectedDate = null; // date for new entry
  export let selectedTime = null; // time clicked on timeline

  const dispatch = createEventDispatcher();
  const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

  let projects = [];
  let categories = [];
  let isSubmitting = false;

  let project = '';
  let category = '';
  let description = '';
  let startTime = '';
  let endTime = '';

  onMount(() => {
    projects = getCustomProjects();
    categories = getCustomCategories();
  });

  function dateToLocalDatetimeString(date) {
    // Convert Date to local datetime-local format (YYYY-MM-DDTHH:mm)
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    const hours = String(date.getHours()).padStart(2, '0');
    const minutes = String(date.getMinutes()).padStart(2, '0');
    return `${year}-${month}-${day}T${hours}:${minutes}`;
  }

  function localDatetimeStringToDate(dateTimeString) {
    // Convert datetime-local string (YYYY-MM-DDTHH:mm) to Date object in local timezone
    // This properly interprets the string as local time, not UTC
    const [datePart, timePart] = dateTimeString.split('T');
    const [year, month, day] = datePart.split('-').map(Number);
    const [hours, minutes] = timePart.split(':').map(Number);
    return new Date(year, month - 1, day, hours, minutes, 0, 0);
  }

  function initializeForm() {
    if (entry) {
      // Edit mode
      project = entry.project || '';
      category = entry.category || '';
      description = entry.description || '';
      startTime = dateToLocalDatetimeString(new Date(entry.start_time));
      endTime = entry.end_time ? dateToLocalDatetimeString(new Date(entry.end_time)) : '';
    } else if (selectedDate) {
      // New entry mode - use selectedTime if provided, otherwise use selectedDate
      const startDate = selectedTime || new Date(selectedDate);
      const endDate = new Date(startDate.getTime() + 3600000); // Add 1 hour
      project = '';
      category = '';
      description = '';
      startTime = dateToLocalDatetimeString(startDate);
      endTime = dateToLocalDatetimeString(endDate);
    }
  }

  // Initialize form when modal opens
  $: if (isOpen) {
    initializeForm();
  }

  function closeModal() {
    isOpen = false;
    dispatch('close');
  }

  async function addProjectHandler() {
    const newProject = prompt('Enter new project name:');
    if (newProject && newProject.trim()) {
      await addCustomProject(newProject.trim());
      project = newProject.trim();
      projects = getCustomProjects();
    }
  }

  async function addCategoryHandler() {
    const newCategory = prompt('Enter new category name:');
    if (newCategory && newCategory.trim()) {
      await addCustomCategory(newCategory.trim());
      category = newCategory.trim();
      categories = getCustomCategories();
    }
  }

  async function submitForm() {
    if (!project || !category) {
      alert('Please select a project and category');
      return;
    }

    if (!startTime || !endTime) {
      alert('Please set both start and end times');
      return;
    }

    isSubmitting = true;
    try {
      const startDate = localDatetimeStringToDate(startTime);
      const endDate = localDatetimeStringToDate(endTime);
      const duration = Math.floor((endDate - startDate) / 1000);

      if (duration <= 0) {
        alert('End time must be after start time');
        isSubmitting = false;
        return;
      }

      // Get the local date for API call (use local date, not UTC)
      const localDateString = dateToLocalDatetimeString(startDate).split('T')[0];
      const overlaps = await checkOverlaps(startDate, endDate, localDateString);
      
      if (overlaps.length > 0) {
        const overlapDetails = overlaps.map(e => 
          `${new Date(e.start_time).toLocaleTimeString()} - ${new Date(e.end_time).toLocaleTimeString()}`
        ).join(', ');
        
        const confirmed = confirm(
          `This entry overlaps with existing entries (${overlapDetails}).\n\n` +
          `Do you want to continue? Overlapping portions of existing entries will be adjusted.`
        );
        
        if (!confirmed) {
          isSubmitting = false;
          return;
        }
        
        // Remove overlapping portions of existing entries
        await resolveOverlaps(overlaps, startDate, endDate);
      }

      const data = {
        project,
        category,
        description,
        start_time: startDate.toISOString(),
        end_time: endDate.toISOString(),
        duration: duration,
        date: localDateString,  // Send the intended date explicitly
      };

      if (entry && entry.id) {
        // Update existing entry
        await axios.put(`${API_URL}/timers/${entry.id}`, data);
        dispatch('entryUpdated', { id: entry.id });
      } else {
        // Create new entry
        await axios.post(`${API_URL}/timers`, data);
        dispatch('entryCreated');
      }

      closeModal();
    } catch (error) {
      console.error('Error saving entry:', error);
      alert('Error saving entry');
    } finally {
      isSubmitting = false;
    }
  }

  async function checkOverlaps(newStart, newEnd, dateKey) {
    try {
      const response = await axios.get(`${API_URL}/timers/${dateKey}`);
      const entries = response.data.entries || [];
      
      return entries.filter(e => {
        // Skip if checking against itself when editing
        if (entry && e.id === entry.id) return false;
        
        const eStart = new Date(e.start_time);
        const eEnd = new Date(e.end_time);
        
        // Check if there's any overlap
        return (newStart < eEnd && newEnd > eStart);
      });
    } catch (error) {
      console.error('Error checking overlaps:', error);
      return [];
    }
  }

  async function resolveOverlaps(overlaps, newStart, newEnd) {
    for (const overlap of overlaps) {
      const eStart = new Date(overlap.start_time);
      const eEnd = new Date(overlap.end_time);
      
      // Case 1: New entry completely covers existing entry - delete it
      if (newStart <= eStart && newEnd >= eEnd) {
        await axios.delete(`${API_URL}/timers/${overlap.id}`);
      }
      // Case 2: New entry starts in middle - trim existing entry end
      else if (newStart > eStart && newStart < eEnd && newEnd >= eEnd) {
        const newDuration = Math.floor((newStart - eStart) / 1000);
        await axios.put(`${API_URL}/timers/${overlap.id}`, {
          ...overlap,
          end_time: newStart.toISOString(),
          duration: newDuration,
        });
      }
      // Case 3: New entry ends in middle - trim existing entry start
      else if (newEnd > eStart && newEnd < eEnd && newStart <= eStart) {
        const newDuration = Math.floor((eEnd - newEnd) / 1000);
        await axios.put(`${API_URL}/timers/${overlap.id}`, {
          ...overlap,
          start_time: newEnd.toISOString(),
          duration: newDuration,
        });
      }
      // Case 4: New entry is in the middle - split existing entry (keep first part)
      else if (newStart > eStart && newEnd < eEnd) {
        const newDuration = Math.floor((newStart - eStart) / 1000);
        await axios.put(`${API_URL}/timers/${overlap.id}`, {
          ...overlap,
          end_time: newStart.toISOString(),
          duration: newDuration,
        });
      }
    }
  }

  async function deleteEntry() {
    if (!entry || !entry.id) return;

    if (!confirm('Are you sure you want to delete this entry?')) {
      return;
    }

    isSubmitting = true;
    try {
      await axios.delete(`${API_URL}/timers/${entry.id}`);
      dispatch('entryDeleted', { id: entry.id });
      closeModal();
    } catch (error) {
      console.error('Error deleting entry:', error);
      alert('Error deleting entry');
    } finally {
      isSubmitting = false;
    }
  }

  function handleKeydown(e) {
    if (e.key === 'Escape') {
      closeModal();
    }
  }
</script>

{#if isOpen}
  <div class="modal-overlay" on:click={closeModal} on:keydown={handleKeydown} role="dialog">
    <div class="modal-content" on:click|stopPropagation>
      <div class="modal-header">
        <h2>{entry ? 'Edit Entry' : 'New Entry'}</h2>
        <button class="close-btn" on:click={closeModal}>&times;</button>
      </div>

      <div class="modal-body">
        <div class="form-group">
          <label class="form-label">Project</label>
          <div class="select-wrapper">
            <select 
              class="form-select" 
              bind:value={project}
              on:change={(e) => { project = e.target.value; }}
            >
              <option value="">Select a project...</option>
              {#each projects as proj}
                <option value={proj}>{proj}</option>
              {/each}
            </select>
            <button class="add-btn" on:click={addProjectHandler} title="Add new project">+</button>
          </div>
        </div>

        <div class="form-group">
          <label class="form-label">Category</label>
          <div class="select-wrapper">
            <select 
              class="form-select" 
              bind:value={category}
              on:change={(e) => { category = e.target.value; }}
            >
              <option value="">Select a category...</option>
              {#each categories as cat}
                <option value={cat}>{cat}</option>
              {/each}
            </select>
            <button class="add-btn" on:click={addCategoryHandler} title="Add new category">+</button>
          </div>
        </div>

        <div class="form-group">
          <label class="form-label">Description (optional)</label>
          <textarea
            class="form-textarea"
            bind:value={description}
            placeholder="What are you working on?"
            rows="3"
          ></textarea>
        </div>

        <div class="form-group">
          <label class="form-label">Start Time</label>
          <input class="form-input" type="datetime-local" bind:value={startTime} />
        </div>

        <div class="form-group">
          <label class="form-label">End Time</label>
          <input class="form-input" type="datetime-local" bind:value={endTime} />
        </div>
      </div>

      <div class="modal-footer">
        <button class="btn-cancel" on:click={closeModal} disabled={isSubmitting}>Cancel</button>
        {#if entry && entry.id}
          <button class="btn-delete" on:click={deleteEntry} disabled={isSubmitting}>Delete</button>
        {/if}
        <button class="btn-save" on:click={submitForm} disabled={isSubmitting}>
          {isSubmitting ? 'Saving...' : 'Save Entry'}
        </button>
      </div>
    </div>
  </div>
{/if}

<style>
  .modal-overlay {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0, 0, 0, 0.5);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 1000;
  }

  .modal-content {
    background: var(--bg-secondary, #ffffff);
    border-radius: 8px;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
    max-width: 500px;
    width: 90%;
    max-height: 90vh;
    overflow-y: auto;
    z-index: 1001;
  }

  .modal-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 20px;
    border-bottom: 1px solid var(--border-color, #e0e0e0);
  }

  .modal-header h2 {
    margin: 0;
    font-size: 20px;
    color: var(--text-primary, #000);
  }

  .close-btn {
    background: none;
    border: none;
    font-size: 24px;
    cursor: pointer;
    color: var(--text-primary, #000);
    padding: 0;
    width: 30px;
    height: 30px;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 4px;
    transition: background-color 0.2s;
  }

  .close-btn:hover {
    background-color: var(--bg-tertiary, #f0f0f0);
  }

  .modal-body {
    padding: 20px;
  }

  .form-group {
    margin-bottom: 16px;
  }

  .form-label {
    display: block;
    margin-bottom: 6px;
    font-weight: 500;
    color: var(--text-primary, #000);
    font-size: 14px;
  }

  .select-wrapper {
    display: flex;
    gap: 8px;
  }

  .form-select {
    flex: 1;
    padding: 8px 12px;
    border: 1px solid var(--border-color, #ddd);
    border-radius: 4px;
    background: var(--bg-primary, #fff);
    color: var(--text-primary, #000);
    font-size: 14px;
  }

  .form-select:focus {
    outline: none;
    border-color: var(--accent-primary, #4CAF50);
    box-shadow: 0 0 0 2px rgba(76, 175, 80, 0.1);
  }

  .add-btn {
    padding: 8px 12px;
    background: var(--accent-primary, #4CAF50);
    color: white;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    font-size: 14px;
    font-weight: 600;
    transition: background-color 0.2s;
  }

  .add-btn:hover {
    background: var(--accent-dark, #45a049);
  }

  .form-input {
    width: 100%;
    padding: 8px 12px;
    border: 1px solid var(--border-color, #ddd);
    border-radius: 4px;
    background: var(--bg-primary, #fff);
    color: var(--text-primary, #000);
    font-size: 14px;
    box-sizing: border-box;
  }

  .form-input:focus {
    outline: none;
    border-color: var(--accent-primary, #4CAF50);
    box-shadow: 0 0 0 2px rgba(76, 175, 80, 0.1);
  }

  .form-textarea {
    width: 100%;
    padding: 8px 12px;
    border: 1px solid var(--border-color, #ddd);
    border-radius: 4px;
    background: var(--bg-primary, #fff);
    color: var(--text-primary, #000);
    font-size: 14px;
    font-family: inherit;
    resize: vertical;
    box-sizing: border-box;
  }

  .form-textarea:focus {
    outline: none;
    border-color: var(--accent-primary, #4CAF50);
    box-shadow: 0 0 0 2px rgba(76, 175, 80, 0.1);
  }

  .modal-footer {
    display: flex;
    gap: 12px;
    padding: 20px;
    border-top: 1px solid var(--border-color, #e0e0e0);
    justify-content: flex-end;
  }

  button {
    padding: 10px 20px;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    font-size: 14px;
    font-weight: 600;
    transition: all 0.2s;
  }

  .btn-cancel {
    background: var(--bg-tertiary, #f0f0f0);
    color: var(--text-primary, #000);
  }

  .btn-cancel:hover:not(:disabled) {
    background: var(--bg-tertiary, #e0e0e0);
  }

  .btn-save {
    background: #3b82f6;
    color: white;
  }

  .btn-save:hover:not(:disabled) {
    background: #2563eb;
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(59, 130, 246, 0.4);
  }

  .btn-delete {
    background: #ef4444;
    color: white;
  }

  .btn-delete:hover:not(:disabled) {
    background: #dc2626;
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(239, 68, 68, 0.4);
  }

  button:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }
</style>
