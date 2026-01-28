<script>
  import Timer from './Timer.svelte';
  import { onMount } from 'svelte';
  import axios from 'axios';
  import '../styles/calendar.css';
  import '../styles/timer.css';

  let weekStart = getWeekStart(new Date());
  let weekData = {};
  let loading = false;
  let currentTime = new Date();
  let timelineHours = Array.from({ length: 24 }, (_, i) => i);

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
    return date.toLocaleDateString('en-US', { weekday: 'short' }).toUpperCase();
  }

  function getFormattedDate(date) {
    return date.getDate();
  }

  function formatDuration(seconds) {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    if (hours > 0) {
      return `${hours}h ${String(minutes).padStart(2, '0')}m`;
    }
    return `${String(minutes).padStart(2, '0')}m`;
  }

  function getWeekTotalSeconds() {
    let total = 0;
    Object.keys(weekData).forEach(key => {
      total += weekData[key]?.total_duration || 0;
    });
    return total;
  }

  function getTimePosition(timeStr) {
    const time = new Date(timeStr);
    const hours = time.getHours();
    const minutes = time.getMinutes();
    return (hours * 60 + minutes);
  }

  function getDurationMinutes(seconds) {
    return Math.round(seconds / 60);
  }

  function updateCurrentTime() {
    currentTime = new Date();
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

  function getWeekNumber(date) {
    const d = new Date(date);
    d.setHours(0, 0, 0, 0);
    d.setDate(d.getDate() + 4 - (d.getDay() || 7));
    const yearStart = new Date(d.getFullYear(), 0, 1);
    const weekNum = Math.ceil((((d - yearStart) / 86400000) + 1) / 7);
    return weekNum;
  }

  onMount(() => {
    loadWeekData();
    setInterval(updateCurrentTime, 60000);
  });
</script>

<div class="calendar-container">
  <div class="top-bar">
    <div class="week-selector">
      <button on:click={previousWeek}>‹</button>
      <span>This week - W{getWeekNumber(weekStart)}</span>
      <button on:click={nextWeek}>›</button>
    </div>

    <div class="week-total">
      WEEK TOTAL: {formatDuration(getWeekTotalSeconds())}
    </div>

    <div class="view-selector">
      <select>
        <option>Week view</option>
      </select>
      <button class="calendar-btn">Calendar</button>
    </div>
  </div>

  <div class="input-section">INPUT</div>

  <div class="timeline-container">
    <div class="timer-section-inline">
      <Timer activeDay={formatDate(new Date())} on:timerAdded={() => loadWeekData()} />
    </div>

    <div class="timeline-wrapper">
      <div class="time-labels">
        {#each timelineHours as hour}
          <div class="time-label">
            {String(hour).padStart(2, '0')}:00
          </div>
        {/each}
      </div>

      <div class="days-grid">
        {#each getWeekDays() as date (formatDate(date))}
          <div class="day-column">
            <div class="day-header">
              <div class="day-name">{getDayName(date)}</div>
              <div class="day-number">{getFormattedDate(date)}</div>
              <div class="day-time">
                {weekData[formatDate(date)]?.total_duration
                  ? formatDuration(weekData[formatDate(date)].total_duration)
                  : '0:00:00'}
              </div>
            </div>

            <div class="day-timeline">
              {#each timelineHours as hour}
                <div class="hour-row"></div>
              {/each}

              {#if weekData[formatDate(date)]?.entries}
                {#each weekData[formatDate(date)].entries as entry (entry.id)}
                  <div
                    class="time-entry"
                    style="
                      top: {getTimePosition(entry.start_time)}px;
                      height: {getDurationMinutes(entry.duration)}px;
                    "
                    title="{entry.project} - {entry.category} ({formatDuration(entry.duration)})"
                  >
                    <div class="entry-content">
                      <div class="entry-project">{entry.project}</div>
                      <div class="entry-category">{entry.category}</div>
                      <div class="entry-duration">{formatDuration(entry.duration)}</div>
                    </div>
                  </div>
                {/each}
              {/if}

              {#if formatDate(date) === formatDate(currentTime)}
                <div
                  class="current-time-line"
                  style="top: {getTimePosition(currentTime.toISOString())}px;"
                ></div>
              {/if}
            </div>
          </div>
        {/each}
      </div>
    </div>
  </div>
</div>

