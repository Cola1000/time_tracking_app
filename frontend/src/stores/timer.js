import { writable } from 'svelte/store';

function createTimerStore() {
  const { subscribe, set, update } = writable({
    isRunning: false,
    startTime: null,
    elapsedSeconds: 0,
    stoppedTime: null,
    project: '',
    category: '',
    description: '',
  });

  return {
    subscribe,
    startTimer: () => update(state => ({
      ...state,
      isRunning: true,
      startTime: Date.now(),
      stoppedTime: null,
    })),
    stopTimer: () => update(state => ({
      ...state,
      isRunning: false,
      stoppedTime: new Date(),
    })),
    resetTimer: () => set({
      isRunning: false,
      startTime: null,
      elapsedSeconds: 0,
      stoppedTime: null,
      project: '',
      category: '',
      description: '',
    }),
    setElapsed: (seconds) => update(state => ({
      ...state,
      elapsedSeconds: seconds,
    })),
    setProject: (project) => update(state => ({
      ...state,
      project,
    })),
    setCategory: (category) => update(state => ({
      ...state,
      category,
    })),
    setDescription: (description) => update(state => ({
      ...state,
      description,
    })),
  };
}

export const timerStore = createTimerStore();
