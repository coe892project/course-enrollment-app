import { writable } from 'svelte/store';
import { browser } from '$app/environment';

// Define the course type to match the API response
export const courses = writable(/** @type {any[]} */ ([]));

// User store with persistence
const storedUser = browser && localStorage.getItem('user');
export const user = writable(storedUser ? JSON.parse(storedUser) : null);

// Subscribe to user changes and update localStorage
if (browser) {
  user.subscribe(value => {
    if (value) {
      localStorage.setItem('user', JSON.stringify(value));
    } else {
      localStorage.removeItem('user');
    }
  });
}

// Auth token store with persistence
const storedToken = browser && localStorage.getItem('token');
export const token = writable(storedToken || null);

// Subscribe to token changes and update localStorage
if (browser) {
  token.subscribe(value => {
    if (value) {
      localStorage.setItem('token', value);
    } else {
      localStorage.removeItem('token');
    }
  });
}
