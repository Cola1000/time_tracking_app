<script>
  import Timer from './Timer.svelte';
  import { onMount } from 'svelte';
  import axios from 'axios';

  let currentDate = new Date();
  let weekStart = getWeekStart(currentDate);
  let weekData = {};
  let loading = false;
  let activeDay = new Date().toISOString().split('T')[0];

  const API_URL = 'http://localhost:8000/api';

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

  function getDayOfWeek(date) {
    const days = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];
    return days[date.getDay()];
  }

  async function loadWeekData() {
    loading = true;
    try {
      const response = await axios.get(`${API_URL}/timers/week/${formatDate(weekStart)}`);
      weekData = response.data;
    } catch (error) {
      console.error('Error loading week data:', error);
    }
    loading = false;
  }

  function previousWeek() {
    weekStart.setDate(weekStart.getDate() - 7);
    weekStart = weekStart;
    activeDay = formatDate(new Date());
    loadWeekData();
  }

  function nextWeek() {
    weekStart.setDate(weekStart.getDate() + 7);
    weekStart = weekStart;
    activeDay = formatDate(new Date());
    loadWeekData();
  }

  function selectDay(date) {
    activeDay = formatDate(date);
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

  function formatDuration(seconds) {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    if (hours > 0) {
      return `${hours}h ${minutes}m`;
    }
    return `${minutes}m`;
  }

  onMount(() => {
    activeDay = formatDate(new Date());
    loadWeekData();
  });
</script>

<div class="calendar-container">
  <div class="calendar-header">
    <h2>Time Tracker</h2>
    <p class="week-range">
      Week of {weekStart.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}
    </p>
  </div>

  <div class="week-navigation">
    <button on:click={previousWeek}>← Previous</button>
    <button on:click={() => {
      weekStart = getWeekStart(new Date());
      activeDay = formatDate(new Date());
      loadWeekData();
    }}>Today</button>
    <button on:click={nextWeek}>Next →</button>
  </div>

  <div class="week-view">
    {#each getWeekDays() as date (formatDate(date))}
      <div
        class="day-card"
        class:active={activeDay === formatDate(date)}
        on:click={() => selectDay(date)}
      >
        <div class="day-header">
          <div class="day-name">{getDayName(date)}</div>
          <div class="day-date">{getFormattedDate(date)}</div>
        </div>
        <div class="day-content">
          <div class="time-display">
            {#if weekData[formatDate(date)]}
              <div class="duration">
                {formatDuration(weekData[formatDate(date)].total_duration || 0)}
              </div>
              <div class="entries-count">
                {weekData[formatDate(date)].entries.length} entries
              </div>
            {:else}
              <div class="duration">0m</div>
              <div class="entries-count">0 entries</div>
            {/if}
          </div>
        </div>
      </div>
    {/each}
  </div>

  <div class="timer-section">
    <Timer {activeDay} on:timerAdded={() => loadWeekData()} />
  </div>

  <div class="day-entries">
    <h3>Entries for {new Date(activeDay).toLocaleDateString('en-US', { weekday: 'long', month: 'long', day: 'numeric' })}</h3>
    {#if weekData[activeDay] && weekData[activeDay].entries.length > 0}
      <div class="entries-list">
        {#each weekData[activeDay].entries as entry (entry.id)}
          <div class="entry-item">
            <div class="entry-header">
              <span class="project-tag">{entry.project}</span>
              <span class="category-tag">{entry.category}</span>
            </div>
            {#if entry.description}
              <p class="entry-description">{entry.description}</p>
            {/if}
            <div class="entry-time">
              <span>{new Date(entry.start_time).toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' })}</span>
              {#if entry.end_time}
                <span>→ {new Date(entry.end_time).toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' })}</span>
              {/if}
              <span class="duration">{formatDuration(entry.duration)}</span>
            </div>
          </div>
        {/each}
      </div>
    {:else}
      <p class="no-entries">No entries for this day</p>
    {/if}
  </div>
</div>

<style>
  .calendar-container {
    padding: 20px;
    max-width: 1200px;
    margin: 0 auto;
  }

  .calendar-header {
    margin-bottom: 20px;
  }

  .calendar-header h2 {
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
    margin-bottom: 20px;
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

  .week-view {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
    gap: 12px;
    margin-bottom: 30px;
  }

  .day-card {
    background-color: #f8f9fa;
    border: 2px solid #ecf0f1;
    border-radius: 8px;
    padding: 16px;
    cursor: pointer;
    transition: all 0.2s ease;
  }

  .day-card:hover {
    border-color: #4CAF50;
    background-color: #f0f8f5;
  }

  .day-card.active {
    border-color: #4CAF50;
    background-color: #e8f5e9;
    box-shadow: 0 2px 8px rgba(76, 175, 80, 0.2);
  }

  .day-header {
    text-align: center;
    margin-bottom: 12px;
  }

  .day-name {
    font-weight: 600;
    color: #2c3e50;
    font-size: 14px;
  }

  .day-date {
    font-size: 12px;
    color: #7f8c8d;
    margin-top: 4px;
  }

  .day-content {
    text-align: center;
  }

  .duration {
    font-size: 20px;
    font-weight: 700;
    color: #4CAF50;
    margin-bottom: 4px;
  }

  .entries-count {
    font-size: 12px;
    color: #7f8c8d;
  }

  .timer-section {
    background-color: #f8f9fa;
    border: 1px solid #ecf0f1;
    border-radius: 8px;
    padding: 20px;
    margin-bottom: 30px;
  }

  .day-entries {
    background-color: #f8f9fa;
    border-radius: 8px;
    padding: 20px;
  }

  .day-entries h3 {
    margin: 0 0 16px 0;
    color: #2c3e50;
  }

  .entries-list {
    display: flex;
    flex-direction: column;
    gap: 12px;
  }

  .entry-item {
    background-color: white;
    border-left: 4px solid #4CAF50;
    padding: 12px;
    border-radius: 4px;
  }

  .entry-header {
    display: flex;
    gap: 8px;
    margin-bottom: 8px;
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
    gap: 12px;
    font-size: 12px;
    color: #7f8c8d;
    flex-wrap: wrap;
  }

  .entry-time .duration {
    margin-left: auto;
    color: #4CAF50;
    font-weight: 600;
  }

  .no-entries {
    text-align: center;
    color: #95a5a6;
    padding: 20px;
  }

  @media (max-width: 768px) {
    .week-view {
      grid-template-columns: repeat(auto-fit, minmax(100px, 1fr));
    }

    .calendar-header h2 {
      font-size: 20px;
    }
  }
</style>
