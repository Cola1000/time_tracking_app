<script>
  import { onMount } from 'svelte';
  import Sidebar from './components/Sidebar.svelte';
  import Calendar from './components/Calendar.svelte';
  import Reports from './components/Reports.svelte';
  import Projects from './components/Projects.svelte';
  import { syncAll } from './utils/storage';
  import './styles/theme.css';
  import './styles/sidebar.css';
  
  let currentView = 'calendar';
  let selectedDate = new Date();

  function handleViewChange(event) {
    currentView = event.detail;
  }

  function handleDateChange(date) {
    selectedDate = date;
  }

  onMount(async () => {
    // Sync projects and categories on app load
    await syncAll();
  });
</script>

<div class="app-container">
  <Sidebar on:viewChange={handleViewChange} />
  <main class="main-content">
    {#if currentView === 'calendar'}
      <Calendar {selectedDate} on:dateChange={(e) => handleDateChange(e.detail)} />
    {:else if currentView === 'reports'}
      <Reports />
    {:else if currentView === 'projects'}
      <Projects />
    {/if}
  </main>
</div>

<style>
  .app-container {
    display: flex;
    height: 100vh;
    width: 100%;
  }

  .main-content {
    flex: 1;
    overflow-y: auto;
    background-color: var(--bg-primary);
  }
</style>
