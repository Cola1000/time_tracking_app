<script>
  import Sidebar from './components/Sidebar.svelte';
  import Calendar from './components/Calendar.svelte';
  import Reports from './components/Reports.svelte';
  import Projects from './components/Projects.svelte';
  
  let currentView = 'calendar';
  let selectedDate = new Date();

  function handleViewChange(view) {
    currentView = view;
  }

  function handleDateChange(date) {
    selectedDate = date;
  }
</script>

<div class="app-container">
  <Sidebar on:viewChange={(e) => handleViewChange(e.detail)} />
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
    background-color: #fff;
  }
</style>
