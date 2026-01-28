<script>
  import { onMount } from 'svelte';
  import axios from 'axios';
  import { Chart } from 'chart.js/auto';
  import '../styles/reports.css';

  const API_URL = 'http://localhost:8000/api';

  let weekStart = getWeekStart(new Date());
  let selectedDate = new Date().toISOString().split('T')[0];
  let weekData = {};
  let dayEntries = [];
  let loading = false;
  let barChartCanvas;
  let pieChartCanvas;
  let barChartInstance;
  let pieChartInstance;

  function getWeekStart(date) {
    const d = new Date(date);
    const day = d.getDay();
    const diff = d.getDate() - day + (day === 0 ? -6 : 1);
    return new Date(d.setDate(diff));
  }

  function formatDate(date) {
    return date.toISOString().split('T')[0];
  }

  function getDayName(date) {
    return date.toLocaleDateString('en-US', { weekday: 'short' });
  }

  function getFormattedDate(date) {
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
  }

  function secondsToHours(seconds) {
    return (seconds / 3600).toFixed(2);
  }

  function formatDuration(seconds) {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    if (hours > 0) {
      return `${hours}h ${minutes}m`;
    }
    return `${minutes}m`;
  }

  async function loadWeekData() {
    loading = true;
    try {
      const response = await axios.get(`${API_URL}/timers/week/${formatDate(weekStart)}`);
      weekData = response.data;
      selectedDate = formatDate(new Date());
      loadDayEntries();
      drawBarChart();
    } catch (error) {
      console.error('Error loading week data:', error);
    }
    loading = false;
  }

  function loadDayEntries() {
    const entries = weekData[selectedDate]?.entries || [];
    dayEntries = entries;
    drawPieChart();
  }

  function selectDay(date) {
    selectedDate = formatDate(date);
    loadDayEntries();
  }

  function previousWeek() {
    weekStart.setDate(weekStart.getDate() - 7);
    weekStart = weekStart;
    loadWeekData();
  }

  function nextWeek() {
    weekStart.setDate(weekStart.getDate() + 7);
    weekStart = weekStart;
    loadWeekData();
  }

  function getWeekDays() {
    const days = [];
    for (let i = 0; i < 7; i++) {
      const date = new Date(weekStart);
      date.setDate(date.getDate() + i);
      days.push(date);
    }
    return days;
  }

  function drawBarChart() {
    const days = getWeekDays();
    const labels = days.map(d => getDayName(d) + '\n' + getFormattedDate(d));
    const data = days.map(d => {
      const key = formatDate(d);
      return parseFloat(secondsToHours(weekData[key]?.total_duration || 0));
    });

    if (barChartInstance) {
      barChartInstance.destroy();
    }

    const ctx = barChartCanvas.getContext('2d');
    barChartInstance = new Chart(ctx, {
      type: 'bar',
      data: {
        labels: labels,
        datasets: [
          {
            label: 'Hours Tracked',
            data: data,
            backgroundColor: '#4CAF50',
            borderColor: '#45a049',
            borderWidth: 2,
            borderRadius: 4,
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: true,
        plugins: {
          legend: {
            display: false,
          },
        },
        scales: {
          y: {
            beginAtZero: true,
            title: {
              display: true,
              text: 'Hours',
            },
          },
        },
        onClick: (event, elements) => {
          if (elements.length > 0) {
            const index = elements[0].index;
            const date = getWeekDays()[index];
            selectDay(date);
          }
        },
      },
    });
  }

  function drawPieChart() {
    const projectBreakdown = {};

    dayEntries.forEach(entry => {
      const project = entry.project || 'Uncategorized';
      const hours = parseFloat(secondsToHours(entry.duration));
      projectBreakdown[project] = (projectBreakdown[project] || 0) + hours;
    });

    const labels = Object.keys(projectBreakdown);
    const data = Object.values(projectBreakdown);

    const colors = [
      '#FF6384',
      '#36A2EB',
      '#FFCE56',
      '#4BC0C0',
      '#9966FF',
      '#FF9F40',
      '#FF6384',
      '#C9CBCF',
    ];

    if (pieChartInstance) {
      pieChartInstance.destroy();
    }

    if (labels.length === 0) {
      return;
    }

    const ctx = pieChartCanvas.getContext('2d');
    pieChartInstance = new Chart(ctx, {
      type: 'doughnut',
      data: {
        labels: labels,
        datasets: [
          {
            data: data,
            backgroundColor: colors.slice(0, labels.length),
            borderColor: '#fff',
            borderWidth: 2,
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: true,
        plugins: {
          legend: {
            position: 'bottom',
          },
        },
      },
    });
  }

  onMount(() => {
    loadWeekData();
  });
</script>

<div class="reports-container">
  <div class="reports-header">
    <div class="week-selector">
      <button on:click={previousWeek}>‹</button>
      <span>Week of {weekStart.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}</span>
      <button on:click={nextWeek}>›</button>
    </div>
  </div>

  <div class="charts-section">
    <div class="bar-chart-container">
      <h3>Hours per Day</h3>
      <canvas bind:this={barChartCanvas}></canvas>
      <p class="chart-hint">Click on a bar to view details for that day</p>
    </div>

    {#if dayEntries.length > 0}
      <div class="detail-section">
        <div class="entries-breakdown">
          <h3>Daily Entries</h3>
          <div class="entries-list">
            {#each dayEntries as entry (entry.id)}
              <div class="entry-card">
                <div class="entry-header">
                  <span class="project-tag">{entry.project || 'Uncategorized'}</span>
                  <span class="category-tag">{entry.category || 'Uncategorized'}</span>
                </div>
                {#if entry.description}
                  <p class="entry-description">{entry.description}</p>
                {/if}
                <div class="entry-time">
                  <span>{new Date(entry.start_time).toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' })}</span>
                  {#if entry.end_time}
                    <span>→ {new Date(entry.end_time).toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' })}</span>
                  {/if}
                </div>
                <div class="entry-duration">{formatDuration(entry.duration)}</div>
              </div>
            {/each}
          </div>
        </div>

        <div class="pie-chart-container">
          <h3>
            Project Breakdown for {new Date(selectedDate).toLocaleDateString('en-US', { weekday: 'long', month: 'short', day: 'numeric' })}
          </h3>
          <canvas bind:this={pieChartCanvas}></canvas>
        </div>
      </div>
    {:else}
      <div class="empty-state">
        <p>No entries for this day</p>
      </div>
    {/if}
  </div>
</div>

