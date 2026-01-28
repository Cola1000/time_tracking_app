<script>
  import { createEventDispatcher } from 'svelte';

  const dispatch = createEventDispatcher();

  let menuOpen = false;

  const menuItems = [
    { id: 'calendar', label: '📅 Calendar', icon: '📅' },
    { id: 'reports', label: '📊 Reports', icon: '📊' },
    { id: 'projects', label: '🏷️ Projects', icon: '🏷️' },
  ];

  function handleMenuClick(view) {
    dispatch('viewChange', view);
    menuOpen = false;
  }

  function toggleMenu() {
    menuOpen = !menuOpen;
  }
</script>

<aside class="sidebar" class:open={menuOpen}>
  <div class="sidebar-header">
    <h1>⏱️ Time Tracker</h1>
    <button class="menu-toggle" on:click={toggleMenu}>
      {menuOpen ? '✕' : '☰'}
    </button>
  </div>

  <nav class="sidebar-nav">
    {#each menuItems as item (item.id)}
      <button
        class="nav-item"
        on:click={() => handleMenuClick(item.id)}
      >
        <span class="icon">{item.icon}</span>
        <span class="label">{item.label}</span>
      </button>
    {/each}
  </nav>

  <div class="sidebar-footer">
    <p>v0.0.1</p>
  </div>
</aside>

<style>
  .sidebar {
    width: 250px;
    background-color: #2c3e50;
    color: white;
    padding: 20px;
    display: flex;
    flex-direction: column;
    border-right: 1px solid #1a252f;
    transition: transform 0.3s ease;
  }

  .sidebar-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 30px;
  }

  .sidebar-header h1 {
    margin: 0;
    font-size: 24px;
    font-weight: 600;
  }

  .menu-toggle {
    display: none;
    background: none;
    color: white;
    font-size: 24px;
    padding: 0;
  }

  .sidebar-nav {
    flex: 1;
    display: flex;
    flex-direction: column;
    gap: 10px;
  }

  .nav-item {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 12px 16px;
    background-color: transparent;
    color: white;
    border-radius: 8px;
    text-align: left;
    font-size: 14px;
    font-weight: 500;
    transition: background-color 0.2s ease;
  }

  .nav-item:hover {
    background-color: #34495e;
  }

  .icon {
    font-size: 20px;
  }

  .label {
    flex: 1;
  }

  .sidebar-footer {
    padding-top: 20px;
    border-top: 1px solid #34495e;
    text-align: center;
    font-size: 12px;
    color: #95a5a6;
  }

  @media (max-width: 768px) {
    .sidebar {
      position: fixed;
      left: 0;
      top: 0;
      height: 100vh;
      z-index: 1000;
      transform: translateX(-100%);
    }

    .sidebar.open {
      transform: translateX(0);
    }

    .menu-toggle {
      display: block;
    }

    .label {
      display: none;
    }

    .sidebar {
      width: 80px;
    }

    .sidebar.open {
      width: 250px;
    }

    .sidebar.open .label {
      display: block;
    }

    .sidebar-header h1 {
      display: none;
    }

    .sidebar.open .sidebar-header h1 {
      display: block;
    }
  }
</style>
