import { writable } from 'svelte/store';

export const courses = writable([]);

// Auto-login as admin
export const user = writable({
  id: 'admin',
  name: 'Admin User',
  email: 'admin@example.com',
  role: 'admin'
});
