<script>
  import { createEventDispatcher } from 'svelte';
  import { theme, toggleTheme } from '../stores/theme';

  const dispatch = createEventDispatcher();
  let currentView = 'calendar';

  const menuItems = [
    { id: 'calendar', label: 'Calendar', icon: '📅' },
    { id: 'reports', label: 'Reports', icon: '📊' },
    { id: 'projects', label: 'Projects', icon: '🏷️' },
  ];

  function handleMenuClick(view) {
    currentView = view;
    dispatch('viewChange', view);
  }

  function handleThemeToggle() {
    toggleTheme();
  }
</script>

<aside class="sidebar">
  <div class="app-title">
    ⏱️ Time Tracker
  </div>

  <nav>
    <ul class="nav-menu">
      {#each menuItems as item (item.id)}
        <li
          class="nav-item"
          class:active={currentView === item.id}
          on:click={() => handleMenuClick(item.id)}
        >
          <span>{item.icon}</span>
          <span>{item.label}</span>
        </li>
      {/each}
    </ul>
  </nav>

  <div class="theme-toggle">
    <button class="theme-toggle-btn" on:click={handleThemeToggle}>
      {#if $theme === 'dark'}
        ☀️ Light Mode
      {:else}
        🌙 Dark Mode
      {/if}
    </button>
  </div>
</aside>
