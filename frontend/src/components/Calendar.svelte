<script>
  import Timer from './Timer.svelte';
  import Modal from './Modal.svelte';
  import { onMount } from 'svelte';
  import axios from 'axios';
  import { getColors } from '../utils/storage';
  import '../styles/calendar.css';
  import '../styles/timer.css';

  let weekStart = getWeekStart(new Date());
  let weekData = {};
  let weekTotal = 0;
  let loading = false;
  let currentTime = new Date();
  let timelineHours = Array.from({ length: 24 }, (_, i) => i);
  let modalOpen = false;
  let selectedDate = null;
  let selectedEntry = null;
  let selectedTime = null; // Time when clicking on timeline
  let colors = { project_colors: {}, category_colors: {} };

  const API_URL = 'http://localhost:8000/api';
  const MIN_ENTRY_DURATION = 900; // 15 minutes in seconds - entries shorter than this won't display on calendar

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
    if (!weekData || Object.keys(weekData).length === 0) {
      return 0;
    }
    Object.keys(weekData).forEach(key => {
      const dayTotal = weekData[key]?.total_duration || 0;
      total += dayTotal;
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

  function openNewEntryModal(date, event = null) {
    let clickedDate = new Date(date);
    
    // If click event provided, calculate the time based on click position
    if (event) {
      const rect = event.currentTarget.getBoundingClientRect();
      const clickY = event.clientY - rect.top;
      const minutes = Math.round(clickY / 60 * 60); // Convert pixel position to minutes
      clickedDate.setHours(Math.floor(minutes / 60), minutes % 60, 0);
    }
    
    selectedDate = clickedDate;
    selectedTime = clickedDate;
    selectedEntry = null;
    modalOpen = true;
  }

  function openEntryModal(entry) {
    selectedEntry = entry;
    selectedDate = null;
    modalOpen = true;
  }

  function handleModalClose() {
    modalOpen = false;
    selectedDate = null;
    selectedEntry = null;
  }

  function handleEntryCreated() {
    loadWeekData();
  }

  function handleEntryUpdated() {
    loadWeekData();
  }

  function handleEntryDeleted() {
    loadWeekData();
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
    setInterval(updateCurrentTime, 60000);
  });

  $: weekTotal = weekData ? getWeekTotalSeconds() : 0; // Reactively recalculate when weekData changes
</script>

<div class="calendar-container">
  <div class="top-bar">
    <div class="week-selector">
      <button on:click={previousWeek}>
        <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-chevron-left-icon lucide-chevron-left"><path d="m15 18-6-6 6-6"/></svg>
      </button>
      <span>This week - W{getWeekNumber(weekStart)}</span>
      <button on:click={nextWeek}>
        <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-chevron-right-icon lucide-chevron-right"><path d="m9 18 6-6-6-6"/></svg>
      </button>
    </div>

    <div class="week-total">
      WEEK TOTAL: {formatDuration(weekTotal)}
    </div>

    <div class="view-selector">
      <select>
        <option>Week view</option>
      </select>
      <button class="calendar-btn">Calendar</button>
    </div>
  </div>

  <div class="timeline-container">
    <div class="timer-section-inline">
      <Timer activeDay={formatDate(new Date())} on:timerAdded={() => loadWeekData()} />
    </div>

    <div class="timeline-wrapper">
      <div class="day-headers-row">
        <div class="day-header-placeholder"></div>
        {#each getWeekDays() as date (formatDate(date))}
          <div class="day-header">
            <div class="day-name">{getDayName(date)}</div>
            <div class="day-number">{getFormattedDate(date)}</div>
            <div class="day-time">
              {weekData[formatDate(date)]?.total_duration
                ? formatDuration(weekData[formatDate(date)].total_duration)
                : '0:00:00'}
            </div>
          </div>
        {/each}
      </div>

      <div class="timeline-scroll-container">
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
              <div class="day-timeline" on:click={(e) => openNewEntryModal(date, e)}>
                {#each timelineHours as hour}
                  <div class="hour-row"></div>
                {/each}

                {#if weekData[formatDate(date)]?.entries}
                  {#each weekData[formatDate(date)].entries as entry (entry.id)}
                    {#if entry.duration >= MIN_ENTRY_DURATION}
                      {@const projectColor = colors.project_colors[entry.project] || '#808080'}
                      {@const categoryColor = colors.category_colors[entry.category] || '#808080'}
                      <div
                      class="time-entry"
                      style="
                        top: {getTimePosition(entry.start_time)}px;
                        height: {getDurationMinutes(entry.duration)}px;
                        background: linear-gradient(135deg, {projectColor} 0%, {categoryColor} 100%);
                      "
                      title="{entry.project} - {entry.category} ({formatDuration(entry.duration)})"
                      on:click={(e) => {
                        e.stopPropagation();
                        openEntryModal(entry);
                      }}
                    >
                      <div class="entry-content">
                        <div class="entry-project">{entry.project}</div>
                        <div class="entry-category">{entry.category}</div>
                        <div class="entry-duration">{formatDuration(entry.duration)}</div>
                      </div>
                    </div>
                    {/if}
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
</div>

<Modal
  isOpen={modalOpen}
  entry={selectedEntry}
  selectedDate={selectedDate}
  selectedTime={selectedTime}
  on:close={handleModalClose}
  on:entryCreated={handleEntryCreated}
  on:entryUpdated={handleEntryUpdated}
  on:entryDeleted={handleEntryDeleted}
/>
