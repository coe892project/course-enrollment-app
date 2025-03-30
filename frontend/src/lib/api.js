import { ENDPOINTS } from './config.js';
import { token, user } from './stores.js';
import { get } from 'svelte/store';
import { goto } from '$app/navigation';

/**
 * Login with username and password
 * @param {string} username - The username
 * @param {string} password - The password
 * @returns {Promise<{access_token: string, token_type: string}>} - The token response
 */
export async function login(username, password) {
  try {
    console.log(`Attempting to login with username: ${username}`);

    // Create form data for the backend API
    const formData = new URLSearchParams();
    formData.append('username', username);
    formData.append('password', password);

    // Make a POST request to the backend login API
    const response = await fetch(ENDPOINTS.LOGIN, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded'
      },
      body: formData
    });

    console.log(`Login response status: ${response.status}`);

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || 'Invalid credentials');
    }

    // Return the token response
    const tokenData = await response.json();
    console.log('Login successful, token received');
    return tokenData;
  } catch (error) {
    console.error('Login error:', error);
    throw error;
  }
}

/**
 * Make an authenticated API request
 * @param {string} url - The API endpoint URL
 * @param {RequestInit} options - Fetch options
 * @returns {Promise<Response>} - The fetch response
 */
export async function apiRequest(url, options = {}) {
  const authToken = get(token);

  // Set up headers with authentication token
  const headers = new Headers(options.headers || {});
  headers.set('Authorization', authToken ? `Bearer ${authToken}` : '');

  // Make the request
  const response = await fetch(url, {
    ...options,
    headers
  });

  // Handle authentication errors
  if (response.status === 401) {
    // Clear user and token
    user.set(null);
    token.set(null);

    // Redirect to login
    goto('/login');
  }

  return response;
}

/**
 * Get all courses
 * @returns {Promise<any[]>} - Array of courses
 */
export async function getCourses() {
  // Make a direct request to the backend API with the token
  const authToken = get(token);

  const response = await fetch(ENDPOINTS.COURSES, {
    headers: {
      'Authorization': authToken ? `Bearer ${authToken}` : ''
    }
  });

  if (!response.ok) {
    if (response.status === 401) {
      // Clear user and token
      user.set(null);
      token.set(null);

      // Redirect to login
      goto('/login');
    }
    throw new Error(`API error: ${response.status}`);
  }

  return await response.json();
}

/**
 * Get all departments
 * @returns {Promise<any[]>} - Array of departments
 */
export async function getDepartments() {
  // Make a direct request to the backend API with the token
  const authToken = get(token);

  const response = await fetch(ENDPOINTS.DEPARTMENTS, {
    headers: {
      'Authorization': authToken ? `Bearer ${authToken}` : ''
    }
  });

  if (!response.ok) {
    if (response.status === 401) {
      // Clear user and token
      user.set(null);
      token.set(null);

      // Redirect to login
      goto('/login');
    }
    throw new Error(`API error: ${response.status}`);
  }

  return await response.json();
}

/**
 * Get all faculties
 * @returns {Promise<any[]>} - Array of faculties
 */
export async function getFaculties() {
  // Make a direct request to the backend API with the token
  const authToken = get(token);

  const response = await fetch(ENDPOINTS.FACULTIES, {
    headers: {
      'Authorization': authToken ? `Bearer ${authToken}` : ''
    }
  });

  if (!response.ok) {
    if (response.status === 401) {
      // Clear user and token
      user.set(null);
      token.set(null);

      // Redirect to login
      goto('/login');
    }
    throw new Error(`API error: ${response.status}`);
  }

  return await response.json();
}

/**
 * Get all instructors
 * @returns {Promise<any[]>} - Array of instructors
 */
export async function getInstructors() {
  // Make a direct request to the backend API with the token
  const authToken = get(token);

  const response = await fetch(ENDPOINTS.INSTRUCTORS, {
    headers: {
      'Authorization': authToken ? `Bearer ${authToken}` : ''
    }
  });

  if (!response.ok) {
    if (response.status === 401) {
      // Clear user and token
      user.set(null);
      token.set(null);

      // Redirect to login
      goto('/login');
    }
    throw new Error(`API error: ${response.status}`);
  }

  return await response.json();
}

/**
 * Get all locations
 * @returns {Promise<any[]>} - Array of locations
 */
export async function getLocations() {
  // Make a direct request to the backend API with the token
  const authToken = get(token);

  const response = await fetch(ENDPOINTS.LOCATIONS, {
    headers: {
      'Authorization': authToken ? `Bearer ${authToken}` : ''
    }
  });

  if (!response.ok) {
    if (response.status === 401) {
      // Clear user and token
      user.set(null);
      token.set(null);

      // Redirect to login
      goto('/login');
    }
    throw new Error(`API error: ${response.status}`);
  }

  return await response.json();
}

/**
 * Get all programs
 * @returns {Promise<any[]>} - Array of programs
 */
export async function getPrograms() {
  // Make a direct request to the backend API with the token
  const authToken = get(token);

  const response = await fetch(ENDPOINTS.PROGRAMS, {
    headers: {
      'Authorization': authToken ? `Bearer ${authToken}` : ''
    }
  });

  if (!response.ok) {
    if (response.status === 401) {
      // Clear user and token
      user.set(null);
      token.set(null);

      // Redirect to login
      goto('/login');
    }
    throw new Error(`API error: ${response.status}`);
  }

  return await response.json();
}

/**
 * Get all prerequisites
 * @returns {Promise<any[]>} - Array of prerequisites
 */
export async function getPrerequisites() {
  // Make a direct request to the backend API with the token
  const authToken = get(token);

  const response = await fetch(ENDPOINTS.PREREQUISITES, {
    headers: {
      'Authorization': authToken ? `Bearer ${authToken}` : ''
    }
  });

  if (!response.ok) {
    if (response.status === 401) {
      // Clear user and token
      user.set(null);
      token.set(null);

      // Redirect to login
      goto('/login');
    }
    throw new Error(`API error: ${response.status}`);
  }

  return await response.json();
}

/**
 * Get all enrollments
 * @returns {Promise<any[]>} - Array of enrollments
 */
export async function getEnrollments() {
  // Make a direct request to the backend API with the token
  const authToken = get(token);

  const response = await fetch(ENDPOINTS.ENROLLMENTS, {
    headers: {
      'Authorization': authToken ? `Bearer ${authToken}` : ''
    }
  });

  if (!response.ok) {
    if (response.status === 401) {
      // Clear user and token
      user.set(null);
      token.set(null);

      // Redirect to login
      goto('/login');
    }
    throw new Error(`API error: ${response.status}`);
  }

  return await response.json();
}

/**
 * Get all course offerings
 * @returns {Promise<any[]>} - Array of course offerings
 */
export async function getCourseOfferings() {
  // Make a direct request to the backend API with the token
  const authToken = get(token);

  const response = await fetch(ENDPOINTS.COURSE_OFFERINGS, {
    headers: {
      'Authorization': authToken ? `Bearer ${authToken}` : ''
    }
  });

  if (!response.ok) {
    if (response.status === 401) {
      // Clear user and token
      user.set(null);
      token.set(null);

      // Redirect to login
      goto('/login');
    }
    throw new Error(`API error: ${response.status}`);
  }

  return await response.json();
}

/**
 * Get all students
 * @returns {Promise<any[]>} - Array of students
 */
export async function getStudents() {
  // Make a direct request to the backend API with the token
  const authToken = get(token);

  const response = await fetch(ENDPOINTS.STUDENTS, {
    headers: {
      'Authorization': authToken ? `Bearer ${authToken}` : ''
    }
  });

  if (!response.ok) {
    if (response.status === 401) {
      // Clear user and token
      user.set(null);
      token.set(null);

      // Redirect to login
      goto('/login');
    }
    throw new Error(`API error: ${response.status}`);
  }

  return await response.json();
}

/**
 * Create a new entity
 * @param {string} endpoint - The API endpoint
 * @param {any} data - The data to create
 * @returns {Promise<any>} - The created entity
 */
export async function createEntity(endpoint, data) {
  // Make a direct request to the backend API with the token
  const authToken = get(token);

  const response = await fetch(endpoint, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': authToken ? `Bearer ${authToken}` : ''
    },
    body: JSON.stringify(data)
  });

  if (!response.ok) {
    if (response.status === 401) {
      // Clear user and token
      user.set(null);
      token.set(null);

      // Redirect to login
      goto('/login');
    }
    const errorData = await response.json();
    throw new Error(errorData.detail || `API error: ${response.status}`);
  }

  return await response.json();
}

/**
 * Update an entity
 * @param {string} endpoint - The API endpoint
 * @param {string} id - The entity ID
 * @param {any} data - The data to update
 * @returns {Promise<any>} - The updated entity
 */
export async function updateEntity(endpoint, id, data) {
  // Make a direct request to the backend API with the token
  const authToken = get(token);

  const response = await fetch(`${endpoint}${id}`, {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': authToken ? `Bearer ${authToken}` : ''
    },
    body: JSON.stringify(data)
  });

  if (!response.ok) {
    if (response.status === 401) {
      // Clear user and token
      user.set(null);
      token.set(null);

      // Redirect to login
      goto('/login');
    }
    const errorData = await response.json();
    throw new Error(errorData.detail || `API error: ${response.status}`);
  }

  return await response.json();
}

/**
 * Delete an entity
 * @param {string} endpoint - The API endpoint
 * @param {string} id - The entity ID
 * @returns {Promise<void>}
 */
export async function deleteEntity(endpoint, id) {
  // Make a direct request to the backend API with the token
  const authToken = get(token);

  const response = await fetch(`${endpoint}${id}`, {
    method: 'DELETE',
    headers: {
      'Authorization': authToken ? `Bearer ${authToken}` : ''
    }
  });

  if (!response.ok) {
    if (response.status === 401) {
      // Clear user and token
      user.set(null);
      token.set(null);

      // Redirect to login
      goto('/login');
    }
    const errorData = await response.json();
    throw new Error(errorData.detail || `API error: ${response.status}`);
  }
}
