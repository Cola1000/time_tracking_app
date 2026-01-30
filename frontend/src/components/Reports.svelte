<script>
  import { onMount } from 'svelte';
  import axios from 'axios';
  import { Chart } from 'chart.js/auto';
  import { getColors } from '../utils/storage';
  import '../styles/reports.css';

  const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

  let weekStart = getWeekStart(new Date());
  let selectedDate = new Date().toISOString().split('T')[0];
  let weekData = {};
  let dayEntries = [];
  let loading = false;
  let barChartCanvas;
  let pieChartCanvas;
  let barChartInstance;
  let pieChartInstance;
  let colors = { project_colors: {}, category_colors: {} };

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
    const newDate = new Date(weekStart);
    newDate.setDate(newDate.getDate() - 7);
    weekStart = newDate;
    loadWeekData();
  }

  function nextWeek() {
    const newDate = new Date(weekStart);
    newDate.setDate(newDate.getDate() + 7);
    weekStart = newDate;
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
    if (!barChartCanvas) return;

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
    if (!ctx) return;

    // Enable better rendering quality
    const gradient = ctx.createLinearGradient(0, 0, 0, 400);
    gradient.addColorStop(0, '#4CAF50');
    gradient.addColorStop(1, '#45a049');

    barChartInstance = new Chart(ctx, {
      type: 'bar',
      data: {
        labels: labels,
        datasets: [
          {
            label: 'Hours Tracked',
            data: data,
            backgroundColor: gradient,
            borderColor: '#2E7D32',
            borderWidth: 0,
            borderRadius: 8,
            borderSkipped: false,
            barPercentage: 0.7,
            categoryPercentage: 0.8,
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        devicePixelRatio: 2,
        interaction: {
          mode: 'index',
          intersect: false,
        },
        plugins: {
          legend: {
            display: false,
          },
          tooltip: {
            enabled: true,
            backgroundColor: 'rgba(0, 0, 0, 0.8)',
            titleFont: {
              size: 14,
              weight: 'bold',
            },
            bodyFont: {
              size: 13,
            },
            padding: 12,
            cornerRadius: 6,
            displayColors: false,
            callbacks: {
              title: (context) => {
                return context[0].label.replace('\n', ' ');
              },
              label: (context) => {
                const hours = context.parsed.y;
                const wholeHours = Math.floor(hours);
                const minutes = Math.round((hours - wholeHours) * 60);
                return `${wholeHours}h ${minutes}m tracked`;
              },
            },
          },
        },
        scales: {
          y: {
            beginAtZero: true,
            ticks: {
              font: {
                size: 12,
                weight: '500',
              },
              color: '#888',
              padding: 8,
            },
            grid: {
              color: 'rgba(255, 255, 255, 0.05)',
              lineWidth: 1,
            },
            title: {
              display: true,
              text: 'Hours',
              font: {
                size: 14,
                weight: 'bold',
              },
              color: '#aaa',
              padding: 10,
            },
          },
          x: {
            ticks: {
              font: {
                size: 12,
                weight: '500',
              },
              color: '#888',
              padding: 8,
            },
            grid: {
              display: false,
            },
          },
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

  async function loadColors() {
    try {
      colors = await getColors();
    } catch (error) {
      console.error('Error loading colors:', error);
    }
  }

  onMount(() => {
    loadWeekData();
    loadColors();
  });

  // Redraw bar chart when canvas becomes available and we have data
  $: if (barChartCanvas && weekData && Object.keys(weekData).length > 0) {
    drawBarChart();
  }
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
    <div class="chart-and-selector">
      <div class="bar-chart-container">
        <h3>Hours per Day</h3>
        <canvas bind:this={barChartCanvas}></canvas>
      </div>

      <div class="day-selector">
        {#each getWeekDays() as date}
          <button 
            class="day-btn {formatDate(date) === selectedDate ? 'active' : ''}"
            on:click={() => selectDay(date)}
          >
            {getDayName(date)}
          </button>
        {/each}
      </div>
    </div>

    <div class="detail-section">
      {#if dayEntries.length > 0}
        <div class="entries-breakdown">
          <h3>Daily Entries</h3>
          <div class="entries-list">
            {#each dayEntries as entry (entry.id)}
              {@const projectColor = colors.project_colors[entry.project] || '#808080'}
              {@const categoryColor = colors.category_colors[entry.category] || '#808080'}
              <div class="entry-card" style="border-left-color: {projectColor}; background: linear-gradient(90deg, rgba({parseInt(projectColor.slice(1,3),16)},${parseInt(projectColor.slice(3,5),16)},${parseInt(projectColor.slice(5,7),16)},0.1) 0%, rgba(${parseInt(categoryColor.slice(1,3),16)},${parseInt(categoryColor.slice(3,5),16)},${parseInt(categoryColor.slice(5,7),16)},0.1) 100%)">
                <div class="entry-header">
                  <span class="project-tag" style="background-color: {projectColor}; color: #fff;">{entry.project || 'Uncategorized'}</span>
                  <span class="category-tag" style="background-color: {categoryColor}; color: #fff;">{entry.category || 'Uncategorized'}</span>
                </div>
                {#if entry.description}
                  <p class="entry-description">{entry.description}</p>
                {/if}
                <div class="entry-time">
                  <span>{new Date(entry.start_time).toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' })}</span>
                  {#if entry.end_time}
                    <span> 

                      <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-move-right-icon lucide-move-right"><path d="M18 8L22 12L18 16"/><path d="M2 12H22"/></svg>

                       {new Date(entry.end_time).toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' })}
                      </span>
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
          <p>if there's nothing here, press the day again</p>
        </div>
      {:else}
        <div class="empty-section">
          <p>No entries for this day</p>
        </div>
      {/if}
    </div>
  </div>
</div>

