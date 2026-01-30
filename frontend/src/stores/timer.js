import { writable, get } from 'svelte/store';
import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

function createTimerStore() {
  const { subscribe, set, update } = writable({
    isRunning: false,
    startTime: null,
    elapsedSeconds: 0,
    stoppedTime: null,
    project: '',
    category: '',
    description: '',
    backendId: null,
    synced: false,
  });

  return {
    subscribe,
    
    // Sync with backend on startup
    syncWithBackend: async () => {
      try {
        const response = await axios.get(`${API_URL}/timer/active`);
        if (response.data.active && response.data.timer) {
          const timer = response.data.timer;
          const startTime = new Date(timer.start_time).getTime();
          set({
            isRunning: true,
            startTime: startTime,
            elapsedSeconds: timer.elapsed,
            stoppedTime: null,
            project: timer.project || '',
            category: timer.category || '',
            description: timer.description || '',
            backendId: timer.id,
            synced: true,
          });
          return true;
        }
        return false;
      } catch (error) {
        console.error('Error syncing with backend timer:', error);
        return false;
      }
    },
    
    startTimer: async () => {
      const state = get({ subscribe });
      try {
        const response = await axios.post(`${API_URL}/timer/start`, null, {
          params: {
            project: state.project,
            category: state.category,
            description: state.description,
          }
        });
        const timer = response.data.timer;
        const startTime = new Date(timer.start_time).getTime();
        update(s => ({
          ...s,
          isRunning: true,
          startTime: startTime,
          stoppedTime: null,
          backendId: timer.id,
          synced: true,
        }));
      } catch (error) {
        console.error('Error starting timer on backend:', error);
        // Fall back to local-only timer
        update(s => ({
          ...s,
          isRunning: true,
          startTime: Date.now(),
          stoppedTime: null,
          synced: false,
        }));
      }
    },
    
    stopTimer: () => update(state => ({
      ...state,
      isRunning: false,
      stoppedTime: new Date(),
    })),
    
    resetTimer: async () => {
      try {
        await axios.delete(`${API_URL}/timer/discard`);
      } catch (error) {
        // Timer might not exist on backend, that's ok
      }
      set({
        isRunning: false,
        startTime: null,
        elapsedSeconds: 0,
        stoppedTime: null,
        project: '',
        category: '',
        description: '',
        backendId: null,
        synced: false,
      });
    },
    
    setElapsed: (seconds) => update(state => ({
      ...state,
      elapsedSeconds: seconds,
    })),
    
    setProject: async (project) => {
      update(state => ({ ...state, project }));
      const state = get({ subscribe });
      if (state.isRunning && state.synced) {
        try {
          await axios.put(`${API_URL}/timer/update`, null, {
            params: { project }
          });
        } catch (error) {
          console.error('Error updating timer project:', error);
        }
      }
    },
    
    setCategory: async (category) => {
      update(state => ({ ...state, category }));
      const state = get({ subscribe });
      if (state.isRunning && state.synced) {
        try {
          await axios.put(`${API_URL}/timer/update`, null, {
            params: { category }
          });
        } catch (error) {
          console.error('Error updating timer category:', error);
        }
      }
    },
    
    setDescription: async (description) => {
      update(state => ({ ...state, description }));
      const state = get({ subscribe });
      if (state.isRunning && state.synced) {
        try {
          await axios.put(`${API_URL}/timer/update`, null, {
            params: { description }
          });
        } catch (error) {
          console.error('Error updating timer description:', error);
        }
      }
    },
    
    // Submit and stop via backend
    submitToBackend: async () => {
      try {
        const response = await axios.post(`${API_URL}/timer/stop`);
        set({
          isRunning: false,
          startTime: null,
          elapsedSeconds: 0,
          stoppedTime: null,
          project: '',
          category: '',
          description: '',
          backendId: null,
          synced: false,
        });
        return response.data.entry;
      } catch (error) {
        console.error('Error stopping timer on backend:', error);
        throw error;
      }
    },
  };
}

export const timerStore = createTimerStore();
