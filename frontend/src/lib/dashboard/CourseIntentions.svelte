<script lang="ts">
  import { onMount } from 'svelte';
  import { getCourseIntentions, getCourses, getStudents, processIntentions as apiProcessIntentions, updateEntity } from '$lib/api';
  import { ENDPOINTS } from '$lib/config';

  // Define interfaces for our data types
  interface CourseIntention {
    intention_id: string;
    student_id: string;
    course_code: string;
    semester: string;
    timestamp: string;
    status: 'pending' | 'enrolled' | 'failed';
    error?: string;
  }

  interface Course {
    course_code: string;
    course_name: string;
    [key: string]: any; // For other properties
  }

  interface Student {
    student_id: string;
    first_name: string;
    last_name: string;
    [key: string]: any; // For other properties
  }

  // Data state
  let courseIntentions: CourseIntention[] = [];
  let courses: Course[] = [];
  let students: Student[] = [];
  let loading = true;
  let error = '';

  // Filter state
  let statusFilter: 'all' | 'pending' | 'enrolled' | 'failed' = 'all';
  let searchQuery = '';

  // Fetch data on component mount
  onMount(async () => {
    try {
      loading = true;

      // Fetch all required data in parallel
      const [intentionsData, coursesData, studentsData] = await Promise.all([
        getCourseIntentions(),
        getCourses(),
        getStudents()
      ]);

      courseIntentions = intentionsData;
      courses = coursesData;
      students = studentsData;

      loading = false;
    } catch (err) {
      error = err instanceof Error ? err.message : String(err);
      loading = false;
    }
  });

  // Get course name by code
  function getCourseName(courseCode: string): string {
    const course = courses.find(c => c.course_code === courseCode);
    return course ? course.course_name : courseCode;
  }

  // Get student name by ID
  function getStudentName(studentId: string): string {
    const student = students.find(s => s.student_id === studentId);
    return student ? `${student.first_name} ${student.last_name}` : studentId;
  }

  // Format timestamp
  function formatTimestamp(timestamp: string): string {
    return new Date(timestamp).toLocaleString();
  }

  // Filter intentions based on status and search query
  $: filteredIntentions = courseIntentions.filter(intention => {
    // Filter by status
    if (statusFilter !== 'all' && intention.status !== statusFilter) {
      return false;
    }

    // Filter by search query (course code, student ID, or intention ID)
    if (searchQuery) {
      const query = searchQuery.toLowerCase();
      const courseCode = intention.course_code.toLowerCase();
      const studentId = intention.student_id.toLowerCase();
      const intentionId = intention.intention_id.toLowerCase();

      return courseCode.includes(query) ||
             studentId.includes(query) ||
             intentionId.includes(query);
    }

    return true;
  });

  // Handle status change
  async function updateIntentionStatus(intention: CourseIntention, newStatus: 'pending' | 'enrolled' | 'failed'): Promise<void> {
    try {
      // Update the status locally first for immediate feedback
      intention.status = newStatus;
      courseIntentions = [...courseIntentions];

      // Call the API to update the status on the backend
      await updateEntity(ENDPOINTS.COURSE_INTENTIONS, intention.intention_id, {
        ...intention,
        status: newStatus
      });

      // Refresh the list to get the latest data
      courseIntentions = await getCourseIntentions();
    } catch (err) {
      error = err instanceof Error ? err.message : String(err);

      // Refresh the list to revert any local changes if the API call failed
      courseIntentions = await getCourseIntentions();
    }
  }

  // Process all pending intentions to enroll students
  async function processIntentions(): Promise<void> {
    try {
      loading = true;
      error = '';

      // Call the API to process intentions
      const result = await apiProcessIntentions();
      console.log('Process intentions result:', result);

      // Refresh the intentions list to get updated statuses
      courseIntentions = await getCourseIntentions();

      loading = false;
    } catch (err) {
      error = err instanceof Error ? err.message : String(err);
      loading = false;
    }
  }
</script>

<div class="course-intentions">
  <h2 class="mdc-typography--headline6">Course Intentions</h2>

  {#if error}
    <div class="error-message">
      <p class="mdc-typography--body2">{error}</p>
    </div>
  {/if}

  <div class="filters">
    <div class="search-field">
      <label class="mdc-typography--subtitle2" for="search-intentions">Search</label>
      <input
        id="search-intentions"
        class="mdc-text-field__input"
        type="text"
        placeholder="Search by course code, student ID, or intention ID"
        bind:value={searchQuery}
      />
    </div>

    <div class="status-filter">
      <label class="mdc-typography--subtitle2" for="status-filter">Status</label>
      <select
        id="status-filter"
        class="mdc-select__native-control"
        bind:value={statusFilter}
      >
        <option value="all">All</option>
        <option value="pending">Pending</option>
        <option value="enrolled">Enrolled</option>
        <option value="failed">Failed</option>
      </select>
    </div>
  </div>

  <div class="actions-bar">
    <button
      class="mdc-button process-button"
      on:click={processIntentions}
      disabled={loading || courseIntentions.filter(i => i.status === 'pending').length === 0}
    >
      <span class="mdc-button__ripple"></span>
      <span class="mdc-button__label">Process Intentions</span>
    </button>
  </div>

  {#if loading}
    <div class="loading">
      <p class="mdc-typography--body1">Loading course intentions...</p>
    </div>
  {:else if filteredIntentions.length === 0}
    <div class="empty-state">
      <p class="mdc-typography--body1">No course intentions found.</p>
    </div>
  {:else}
    <div class="intentions-table">
      <table class="mdc-data-table__table">
        <thead>
          <tr class="mdc-data-table__header-row">
            <th class="mdc-data-table__header-cell">Intention ID</th>
            <th class="mdc-data-table__header-cell">Student</th>
            <th class="mdc-data-table__header-cell">Course</th>
            <th class="mdc-data-table__header-cell">Semester</th>
            <th class="mdc-data-table__header-cell">Timestamp</th>
            <th class="mdc-data-table__header-cell">Status</th>
            <th class="mdc-data-table__header-cell">Actions</th>
          </tr>
        </thead>
        <tbody>
          {#each filteredIntentions as intention}
            <tr class="mdc-data-table__row">
              <td class="mdc-data-table__cell">{intention.intention_id}</td>
              <td class="mdc-data-table__cell">{getStudentName(intention.student_id)}</td>
              <td class="mdc-data-table__cell">
                {intention.course_code} - {getCourseName(intention.course_code)}
              </td>
              <td class="mdc-data-table__cell">{intention.semester}</td>
              <td class="mdc-data-table__cell">{formatTimestamp(intention.timestamp)}</td>
              <td class="mdc-data-table__cell">
                <span class="status-badge status-{intention.status}">
                  {intention.status}
                </span>
              </td>
              <td class="mdc-data-table__cell actions">
                {#if intention.status === 'pending'}
                  <button
                    class="mdc-button mdc-button--small enroll-button"
                    on:click={() => updateIntentionStatus(intention, 'enrolled')}
                  >
                    <span class="mdc-button__ripple"></span>
                    <span class="mdc-button__label">Enroll</span>
                  </button>
                  <button
                    class="mdc-button mdc-button--small fail-button"
                    on:click={() => updateIntentionStatus(intention, 'failed')}
                  >
                    <span class="mdc-button__ripple"></span>
                    <span class="mdc-button__label">Fail</span>
                  </button>
                {:else}
                  <button
                    class="mdc-button mdc-button--small reset-button"
                    on:click={() => updateIntentionStatus(intention, 'pending')}
                  >
                    <span class="mdc-button__ripple"></span>
                    <span class="mdc-button__label">Reset</span>
                  </button>
                {/if}
              </td>
            </tr>
          {/each}
        </tbody>
      </table>
    </div>
  {/if}
</div>

<style>
  .course-intentions {
    margin-top: 2rem;
  }

  .filters {
    display: flex;
    gap: 1rem;
    margin-bottom: 1rem;
  }

  .search-field {
    flex: 1;
    display: flex;
    flex-direction: column;
  }

  .status-filter {
    width: 150px;
    display: flex;
    flex-direction: column;
  }

  .intentions-table {
    width: 100%;
    overflow-x: auto;
  }

  table {
    width: 100%;
    border-collapse: collapse;
  }

  th, td {
    padding: 0.75rem;
    text-align: left;
    border-bottom: 1px solid #e0e0e0;
  }

  th {
    font-weight: 600;
    background-color: #f5f5f5;
  }

  .status-badge {
    display: inline-block;
    padding: 0.25rem 0.5rem;
    border-radius: 4px;
    text-transform: capitalize;
    font-size: 0.75rem;
    font-weight: 500;
  }

  .status-pending {
    background-color: #fff8e1;
    color: #ff8f00;
  }

  .status-enrolled {
    background-color: #e8f5e9;
    color: #2e7d32;
  }

  .status-failed {
    background-color: #ffebee;
    color: #c62828;
  }

  .actions {
    display: flex;
    gap: 0.5rem;
  }

  .enroll-button {
    background-color: #e8f5e9;
    color: #2e7d32;
  }

  .fail-button {
    background-color: #ffebee;
    color: #c62828;
  }

  .process-button {
    background-color: #e3f2fd;
    color: #1565c0;
    margin-bottom: 1rem;
  }

  .actions-bar {
    display: flex;
    justify-content: flex-end;
    margin-bottom: 1rem;
  }

  .reset-button {
    background-color: #f5f5f5;
    color: #616161;
  }

  .loading, .empty-state {
    padding: 2rem;
    text-align: center;
    background-color: #f5f5f5;
    border-radius: 4px;
  }

  .error-message {
    background-color: #ffebee;
    padding: 0.5rem 1rem;
    border-radius: 4px;
    margin-bottom: 1rem;
  }
</style>
