<script>
  import { onMount } from 'svelte';
  import axios from 'axios';
  import { Chart } from 'chart.js/auto';

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
    <h2>Reports</h2>
    <p class="week-range">
      Week of {weekStart.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}
    </p>
  </div>

  <div class="week-navigation">
    <button on:click={previousWeek}>← Previous</button>
    <button on:click={() => {
      weekStart = getWeekStart(new Date());
      selectedDate = formatDate(new Date());
      loadWeekData();
    }}>Today</button>
    <button on:click={nextWeek}>Next →</button>
  </div>

  <div class="charts-section">
    <div class="bar-chart-container">
      <h3>Hours per Day</h3>
      <canvas bind:this={barChartCanvas}></canvas>
      <p class="chart-hint">Click on a bar to view details for that day</p>
    </div>

    {#if dayEntries.length > 0}
      <div class="pie-chart-container">
        <h3>
          Project Breakdown for {new Date(selectedDate).toLocaleDateString('en-US', { weekday: 'long', month: 'short', day: 'numeric' })}
        </h3>
        <canvas bind:this={pieChartCanvas}></canvas>
      </div>

      <div class="entries-breakdown">
        <h3>Daily Entries</h3>
        <div class="entries-grid">
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
    {:else}
      <div class="empty-state">
        <p>No entries for this day</p>
      </div>
    {/if}
  </div>
</div>

<style>
  .reports-container {
    padding: 20px;
    max-width: 1400px;
    margin: 0 auto;
  }

  .reports-header {
    margin-bottom: 20px;
  }

  .reports-header h2 {
    margin: 0;
    font-size: 28px;
    color: #2c3e50;
  }

  .week-range {
    margin: 8px 0 0 0;
    color: #7f8c8d;
    font-size: 14px;
  }

  .week-navigation {
    display: flex;
    gap: 10px;
    margin-bottom: 30px;
  }

  .week-navigation button {
    padding: 10px 16px;
    background-color: #ecf0f1;
    color: #2c3e50;
    border-radius: 6px;
    font-weight: 500;
    transition: background-color 0.2s ease;
  }

  .week-navigation button:hover {
    background-color: #bdc3c7;
  }

  .charts-section {
    display: flex;
    flex-direction: column;
    gap: 30px;
  }

  .bar-chart-container {
    background-color: #f8f9fa;
    border-radius: 8px;
    padding: 20px;
    border: 1px solid #ecf0f1;
  }

  .bar-chart-container h3 {
    margin: 0 0 20px 0;
    color: #2c3e50;
  }

  .bar-chart-container canvas {
    max-height: 400px;
  }

  .chart-hint {
    margin-top: 12px;
    color: #7f8c8d;
    font-size: 12px;
    text-align: center;
  }

  .pie-chart-container {
    background-color: #f8f9fa;
    border-radius: 8px;
    padding: 20px;
    border: 1px solid #ecf0f1;
  }

  .pie-chart-container h3 {
    margin: 0 0 20px 0;
    color: #2c3e50;
  }

  .pie-chart-container canvas {
    max-width: 100%;
  }

  .entries-breakdown {
    background-color: #f8f9fa;
    border-radius: 8px;
    padding: 20px;
    border: 1px solid #ecf0f1;
  }

  .entries-breakdown h3 {
    margin: 0 0 20px 0;
    color: #2c3e50;
  }

  .entries-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
    gap: 16px;
  }

  .entry-card {
    background-color: white;
    border: 1px solid #ecf0f1;
    border-radius: 8px;
    padding: 16px;
    border-left: 4px solid #4CAF50;
  }

  .entry-header {
    display: flex;
    gap: 8px;
    margin-bottom: 12px;
    flex-wrap: wrap;
  }

  .project-tag {
    display: inline-block;
    background-color: #4CAF50;
    color: white;
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 12px;
    font-weight: 500;
  }

  .category-tag {
    display: inline-block;
    background-color: #2196F3;
    color: white;
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 12px;
    font-weight: 500;
  }

  .entry-description {
    margin: 8px 0;
    color: #2c3e50;
    font-size: 14px;
  }

  .entry-time {
    display: flex;
    gap: 8px;
    font-size: 12px;
    color: #7f8c8d;
    margin-bottom: 8px;
    flex-wrap: wrap;
  }

  .entry-duration {
    font-weight: 600;
    color: #4CAF50;
    font-size: 16px;
  }

  .empty-state {
    text-align: center;
    padding: 40px;
    color: #95a5a6;
  }

  @media (max-width: 768px) {
    .entries-grid {
      grid-template-columns: 1fr;
    }
  }
</style>
