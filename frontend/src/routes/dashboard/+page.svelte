<script>
  import { user, token } from '$lib/stores';
  import CourseCard from '$lib/CourseCard.svelte';
  import { onMount } from 'svelte';
  import { get } from 'svelte/store';
    import { getCourseOfferings, getCourses, getDepartments, getEnrollments, getStudents } from '$lib/api';

  // Form state for creating a new instructor
  let showInstructorForm = false;
  /** @type {{instructor_id: string, first_name: string, last_name: string, department_id: string, title: string, courses_teachable: string[]}} */
  let newInstructor = {
    instructor_id: '',
    first_name: '',
    last_name: '',
    department_id: '',
    title: '',
    courses_teachable: []
  };
  let courseTeachableInput = '';
  let instructorCreationSuccess = '';
  let instructorCreationError = '';

  /** @type {Array<{department_id: string, department_name: string, faculty_id: string}>} */
  let departments = [];

  // Form state for creating a new course
  let showCourseForm = false;
  /** @type {{course_code: string, course_name: string, section: string, semester: string, prerequisites: string[], corequisites: string[], available_seats: number, instructor: string, course_time: string[]}} */
  let newCourse = {
    course_code: '',
    course_name: '',
    section: '',
    semester: 'Fall',
    prerequisites: [],
    corequisites: [],
    available_seats: 30,
    instructor: '',
    course_time: []
  };
  let prerequisiteInput = '';
  let corequisiteInput = '';
  let courseTimeInput = '';
  let courseCreationSuccess = '';
  let courseCreationError = '';

  // Form state for creating a new location
  let showLocationForm = false;
  /** @type {{room_id: string, room_name: string, available_seats: number, available_times: string[]}} */
  let newLocation = {
    room_id: '',
    room_name: '',
    available_seats: 30,
    available_times: []
  };
  let availableTimeInput = '';
  let locationCreationSuccess = '';
  let locationCreationError = '';

  /**
   * @typedef {Object} Student
   * @property {string} student_id
   * @property {string} first_name
   * @property {string} last_name
   * @property {string} status
   * @property {string} program_id
   * @property {string[]} enrolled_courses
   * @property {string[]} completed_courses
   */

  /**
   * @typedef {Object} Enrollment
   * @property {string} enrollment_id
   * @property {string} student_id
   * @property {string} offering_id
   * @property {string} enrollment_date
   * @property {string|null} grade
   */

  /**
   * @typedef {Object} CourseOffering
   * @property {string} offering_id
   * @property {string} course_code
   * @property {string} course_name
   * @property {string} instructor
   * @property {string} semester
   * @property {number} year
   * @property {number} available_seats
   */

  /**
   * @typedef {Object} EnrolledCourse
   * @property {string} id
   * @property {string} title
   * @property {string} description
   * @property {string} instructor
   * @property {number} seats
   * @property {string} enrollmentDate
   * @property {string|null} grade
   */

  /** @type {Student[]} */
  let students = [];
  /** @type {string} */
  let selectedStudentId = '';
  /** @type {Enrollment[]} */
  let enrollments = [];
  /** @type {CourseOffering[]} */
  let courseOfferings = [];
  /** @type {EnrolledCourse[]} */
  let enrolledCourses = [];
  let isLoading = true;
  let error = '';
  let unenrollSuccess = '';

  /**
   * Add a course teachable to the new instructor
   */
  function addCourseTeachable() {
    if (courseTeachableInput.trim()) {
      newInstructor.courses_teachable = [...newInstructor.courses_teachable, courseTeachableInput.trim()];
      courseTeachableInput = '';
    }
  }

  /**
   * Remove a course teachable from the new instructor
   * @param {string} course - The course to remove
   */
  function removeCourseTeachable(course) {
    newInstructor.courses_teachable = newInstructor.courses_teachable.filter(c => c !== course);
  }

  /**
   * Reset the instructor creation form
   */
  function resetInstructorForm() {
    newInstructor = {
      instructor_id: '',
      first_name: '',
      last_name: '',
      department_id: '',
      title: '',
      courses_teachable: []
    };
    courseTeachableInput = '';
    instructorCreationError = '';
    instructorCreationSuccess = '';
  }

  /**
   * Submit the instructor creation form
   */
  async function handleUnenroll(courseId) {
    if (!selectedStudentId) {
      error = 'No student selected';
      return;
    }

    unenrollSuccess = '';
    error = '';
    isLoading = true;

    try {
      const authToken = get(token);
      const response = await fetch('/api/unenroll', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${authToken}`
        },
        body: JSON.stringify({
          userId: selectedStudentId,
          courseId
        })
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Failed to unenroll student');
      }

      // Get the created instructor
      const createdInstructor = await response.json();

      // Show success message
      instructorCreationSuccess = `Successfully created instructor: ${createdInstructor.first_name} ${createdInstructor.last_name}`;

      // Reset the form
      resetInstructorForm();

      // Reload data
      await loadData();
    } catch (error_) {
      instructorCreationError = error_ instanceof Error ? error_.message : String(error_);
    }
  }

  /**
   * Load all data from the backend
   */
  async function loadData() {
    isLoading = true;
    error = '';

    try {
      // Load all data in parallel
      const [studentsResponse, enrollmentsResponse, offeringsResponse, departmentsResponse] = await Promise.all([
        getStudents(),
        getEnrollments(),
        getCourseOfferings(),
        getDepartments()
      ]);

      students = studentsResponse;
      enrollments = enrollmentsResponse;
      courseOfferings = offeringsResponse;
      departments = departmentsResponse;

      // Set default selected student if not already set
      if (!selectedStudentId && students.length > 0) {
        selectedStudentId = students[0].student_id;
      }

      // Update enrolled courses for the selected student
      if (selectedStudentId) {
        updateEnrolledCourses();
      }
    } catch (error_) {
      error = error_ instanceof Error ? error_.message : String(error_);
    } finally {
      isLoading = false;
    }
  }

  // Initial data load
  onMount(loadData);

  /**
   * Update enrolled courses when student selection changes
   */
  function updateEnrolledCourses() {
    // Filter enrollments for the selected student
    const studentEnrollments = enrollments.filter(
      enrollment => enrollment.student_id === selectedStudentId
    );

    // Map enrollments to course details
    const mappedCourses = studentEnrollments
      .map(enrollment => {
        const offering = courseOfferings.find(
          offering => offering.offering_id === enrollment.offering_id
        );

        if (!offering) {
          return null;
        }

        return {
          id: offering.course_code,
          title: offering.course_name,
          description: `${offering.course_code} - ${offering.semester} ${offering.year}`,
          instructor: offering.instructor,
          seats: offering.available_seats,
          enrollmentDate: enrollment.enrollment_date,
          grade: enrollment.grade
        };
      });

    // Filter out null values
    /** @type {EnrolledCourse[]} */
    enrolledCourses = mappedCourses.filter(course => course !== null);
  }

  /**
   * Handle unenrolling a student from a course
   * @param {string} courseId - The course ID to unenroll from
   */
  async function handleUnenroll(courseId) {
    if (!selectedStudentId) {
      error = 'No student selected';
      return;
    }

    unenrollSuccess = '';
    error = '';
    isLoading = true;

    try {
      const authToken = get(token);
      const response = await fetch('/api/unenroll', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${authToken}`
        },
        body: JSON.stringify({
          userId: selectedStudentId,
          courseId
        })
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Failed to unenroll student');
      }

      // Show success message
      unenrollSuccess = `Successfully unenrolled student from ${courseId}`;

      // Reload data to update the UI
      await loadData();
    } catch (error_) {
      error = error_ instanceof Error ? error_.message : String(error_);
      isLoading = false;
    }
  }

  // This function will be called when the user manually selects a student
  function handleStudentChange() {
    if (selectedStudentId && !isLoading) {
      loadData();
    }
  }

  /**
   * Add a prerequisite to the new course
   */
  function addPrerequisite() {
    if (prerequisiteInput.trim()) {
      newCourse.prerequisites = [...newCourse.prerequisites, prerequisiteInput.trim()];
      prerequisiteInput = '';
    }
  }

  /**
   * Remove a prerequisite from the new course
   * @param {string} prereq - The prerequisite to remove
   */
  function removePrerequisite(prereq) {
    newCourse.prerequisites = newCourse.prerequisites.filter(p => p !== prereq);
  }

  /**
   * Add a corequisite to the new course
   */
  function addCorequisite() {
    if (corequisiteInput.trim()) {
      newCourse.corequisites = [...newCourse.corequisites, corequisiteInput.trim()];
      corequisiteInput = '';
    }
  }

  /**
   * Remove a corequisite from the new course
   * @param {string} coreq - The corequisite to remove
   */
  function removeCorequisite(coreq) {
    newCourse.corequisites = newCourse.corequisites.filter(c => c !== coreq);
  }

  /**
   * Add a course time to the new course
   */
  function addCourseTime() {
    if (courseTimeInput.trim()) {
      newCourse.course_time = [...newCourse.course_time, courseTimeInput.trim()];
      courseTimeInput = '';
    }
  }

  /**
   * Remove a course time from the new course
   * @param {string} time - The course time to remove
   */
  function removeCourseTime(time) {
    newCourse.course_time = newCourse.course_time.filter(t => t !== time);
  }

  /**
   * Reset the course creation form
   */
  function resetCourseForm() {
    newCourse = {
      course_code: '',
      course_name: '',
      section: '',
      semester: 'Fall',
      prerequisites: [],
      corequisites: [],
      available_seats: 30,
      instructor: '',
      course_time: []
    };
    prerequisiteInput = '';
    corequisiteInput = '';
    courseTimeInput = '';
    courseCreationError = '';
    courseCreationSuccess = '';
  }

  /**
   * Submit the course creation form
   */
  async function createCourse() {
    courseCreationError = '';
    courseCreationSuccess = '';

    try {
      // Validate required fields
      if (!newCourse.course_code || !newCourse.course_name || !newCourse.section ||
        !newCourse.semester || !newCourse.instructor) {
        courseCreationError = 'Please fill in all required fields';
        return;
      }

      const authToken = get(token);
      // Send the course data to the API
      const response = await fetch('/api/courses', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${authToken}`
        },
        body: JSON.stringify(newCourse)
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Failed to create course');
      }

      // Get the created course
      const createdCourse = await response.json();

      // Show success message
      courseCreationSuccess = `Successfully created course: ${createdCourse.course_code} - ${createdCourse.course_name}`;

      // Reset the form
      resetCourseForm();

      // Reload data
      await loadData();
    } catch (error_) {
      courseCreationError = error_ instanceof Error ? error_.message : String(error_);
    }
  }

  /**
   * Add an available time to the new location
   */
  function addAvailableTime() {
    if (availableTimeInput.trim()) {
      newLocation.available_times = [...newLocation.available_times, availableTimeInput.trim()];
      availableTimeInput = '';
    }
  }

  /**
   * Remove an available time from the new location
   * @param {string} time - The time to remove
   */
  function removeAvailableTime(time) {
    newLocation.available_times = newLocation.available_times.filter(t => t !== time);
  }

  /**
   * Reset the location creation form
   */
  function resetLocationForm() {
    newLocation = {
      room_id: '',
      room_name: '',
      available_seats: 30,
      available_times: []
    };
    availableTimeInput = '';
    locationCreationError = '';
    locationCreationSuccess = '';
  }

  /**
   * Submit the location creation form
   */
  async function createLocation() {
    locationCreationError = '';
    locationCreationSuccess = '';

    try {
      // Validate required fields
      if (!newLocation.room_id || !newLocation.room_name) {
        locationCreationError = 'Please fill in all required fields';
        return;
      }

      const authToken = get(token);
      // Send the location data to the API
      const response = await fetch('/api/locations', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${authToken}`
        },
        body: JSON.stringify(newLocation)
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Failed to create location');
      }

      // Get the created location
      const createdLocation = await response.json();

      // Show success message
      locationCreationSuccess = `Successfully created location: ${createdLocation.room_name} (${createdLocation.room_id})`;

      // Reset the form
      resetLocationForm();

      // Reload data
      await loadData();
    } catch (error_) {
      locationCreationError = error_ instanceof Error ? error_.message : String(error_);
    }
  }
</script>

<svelte:head>
  <title>Student Dashboard - Course Enrollment</title>
</svelte:head>

<main>
  <div class="mdc-typography--headline4 dashboard-title">Admin Dashboard</div>
  <p class="mdc-typography--body1">Logged in as: {$user.name}</p>

  <div class="dashboard-nav">
    <a href="/" class="mdc-button">
      <span class="mdc-button__ripple"></span>
      <span class="mdc-button__label">Home</span>
    </a>
    <a href="/courses" class="mdc-button">
      <span class="mdc-button__ripple"></span>
      <span class="mdc-button__label">Manage Enrollments</span>
    </a>
    <button class="mdc-button" on:click={() => showCourseForm = !showCourseForm}>
      <span class="mdc-button__ripple"></span>
      <span class="mdc-button__label">{showCourseForm ? 'Hide Course Form' : 'Create New Course'}</span>
    </button>
    <button class="mdc-button" on:click={() => showInstructorForm = !showInstructorForm}>
      <span class="mdc-button__ripple"></span>
      <span class="mdc-button__label">{showInstructorForm ? 'Hide Instructor Form' : 'Create New Instructor'}</span>
    </button>
    <button class="mdc-button" on:click={() => showLocationForm = !showLocationForm}>
      <span class="mdc-button__ripple"></span>
      <span class="mdc-button__label">{showLocationForm ? 'Hide Location Form' : 'Create New Location'}</span>
    </button>
  </div>

  {#if showInstructorForm}
    <div class="mdc-card course-form-card">
      <div class="mdc-card__content">
        <h2 class="mdc-typography--headline6">Create New Instructor</h2>

        {#if instructorCreationSuccess}
          <div class="success-message">
            <p class="mdc-typography--body2">{instructorCreationSuccess}</p>
          </div>
        {/if}

        {#if instructorCreationError}
          <div class="error-message">
            <p class="mdc-typography--body2">{instructorCreationError}</p>
          </div>
        {/if}

        <form on:submit|preventDefault={createInstructor}>
          <div class="form-row">
            <div class="form-field">
              <label class="mdc-typography--subtitle2" for="instructor-id">Instructor ID*</label>
              <input
                id="instructor-id"
                class="mdc-text-field__input"
                type="text"
                bind:value={newInstructor.instructor_id}
                required
              />
            </div>

            <div class="form-field">
              <label class="mdc-typography--subtitle2" for="title">Title*</label>
              <input
                id="title"
                class="mdc-text-field__input"
                type="text"
                bind:value={newInstructor.title}
                required
              />
            </div>
          </div>

          <div class="form-row">
            <div class="form-field">
              <label class="mdc-typography--subtitle2" for="first-name">First Name*</label>
              <input
                id="first-name"
                class="mdc-text-field__input"
                type="text"
                bind:value={newInstructor.first_name}
                required
              />
            </div>

            <div class="form-field">
              <label class="mdc-typography--subtitle2" for="last-name">Last Name*</label>
              <input
                id="last-name"
                class="mdc-text-field__input"
                type="text"
                bind:value={newInstructor.last_name}
                required
              />
            </div>
          </div>

          <div class="form-row">
            <div class="form-field">
              <label class="mdc-typography--subtitle2" for="department">Department*</label>
              <select
                id="department"
                class="mdc-select__native-control"
                bind:value={newInstructor.department_id}
                required
              >
                <option value="">Select a department</option>
                {#each departments as department}
                  <option value={department.department_id}>{department.department_name}</option>
                {/each}
              </select>
            </div>
          </div>

          <div class="form-section">
            <label class="mdc-typography--subtitle2">Courses Teachable</label>
            <div class="array-input">
              <input
                class="mdc-text-field__input"
                type="text"
                placeholder="Enter course code"
                bind:value={courseTeachableInput}
              />
              <button
                type="button"
                class="mdc-button mdc-button--raised"
                on:click={addCourseTeachable}
              >
                <span class="mdc-button__ripple"></span>
                <span class="mdc-button__label">Add</span>
              </button>
            </div>

            {#if newInstructor.courses_teachable.length > 0}
              <div class="array-items">
                {#each newInstructor.courses_teachable as course}
                  <div class="array-item">
                    <span>{course}</span>
                    <button
                      type="button"
                      class="mdc-button mdc-button--small"
                      on:click={() => removeCourseTeachable(course)}
                    >
                      <span class="mdc-button__ripple"></span>
                      <span class="mdc-button__label">Remove</span>
                    </button>
                  </div>
                {/each}
              </div>
            {/if}
          </div>

          <div class="form-actions">
            <button
              type="button"
              class="mdc-button"
              on:click={resetInstructorForm}
            >
              <span class="mdc-button__ripple"></span>
              <span class="mdc-button__label">Reset</span>
            </button>

            <button
              type="submit"
              class="mdc-button mdc-button--raised"
            >
              <span class="mdc-button__ripple"></span>
              <span class="mdc-button__label">Create Instructor</span>
            </button>
          </div>
        </form>
      </div>
    </div>
  {/if}

  {#if showCourseForm}
    <div class="mdc-card course-form-card">
      <div class="mdc-card__content">
        <h2 class="mdc-typography--headline6">Create New Course</h2>

        {#if courseCreationSuccess}
          <div class="success-message">
            <p class="mdc-typography--body2">{courseCreationSuccess}</p>
          </div>
        {/if}

        {#if courseCreationError}
          <div class="error-message">
            <p class="mdc-typography--body2">{courseCreationError}</p>
          </div>
        {/if}

        <form on:submit|preventDefault={createCourse}>
          <div class="form-row">
            <div class="form-field">
              <label class="mdc-typography--subtitle2" for="course-code">Course Code*</label>
              <input
                id="course-code"
                class="mdc-text-field__input"
                type="text"
                bind:value={newCourse.course_code}
                required
              />
            </div>

            <div class="form-field">
              <label class="mdc-typography--subtitle2" for="course-name">Course Name*</label>
              <input
                id="course-name"
                class="mdc-text-field__input"
                type="text"
                bind:value={newCourse.course_name}
                required
              />
            </div>
          </div>

          <div class="form-row">
            <div class="form-field">
              <label class="mdc-typography--subtitle2" for="section">Section*</label>
              <input
                id="section"
                class="mdc-text-field__input"
                type="text"
                bind:value={newCourse.section}
                required
              />
            </div>

            <div class="form-field">
              <label class="mdc-typography--subtitle2" for="semester">Semester*</label>
              <select
                id="semester"
                class="mdc-select__native-control"
                bind:value={newCourse.semester}
                required
              >
                <option value="Fall">Fall</option>
                <option value="Winter">Winter</option>
                <option value="Spring">Spring</option>
                <option value="Summer">Summer</option>
              </select>
            </div>
          </div>

          <div class="form-row">
            <div class="form-field">
              <label class="mdc-typography--subtitle2" for="instructor">Instructor*</label>
              <input
                id="instructor"
                class="mdc-text-field__input"
                type="text"
                bind:value={newCourse.instructor}
                required
              />
            </div>

            <div class="form-field">
              <label class="mdc-typography--subtitle2" for="available-seats">Available Seats*</label>
              <input
                id="available-seats"
                class="mdc-text-field__input"
                type="number"
                min="1"
                bind:value={newCourse.available_seats}
                required
              />
            </div>
          </div>

          <div class="form-section">
            <label class="mdc-typography--subtitle2">Prerequisites</label>
            <div class="array-input">
              <input
                class="mdc-text-field__input"
                type="text"
                placeholder="Enter prerequisite course code"
                bind:value={prerequisiteInput}
              />
              <button
                type="button"
                class="mdc-button mdc-button--raised"
                on:click={addPrerequisite}
              >
                <span class="mdc-button__ripple"></span>
                <span class="mdc-button__label">Add</span>
              </button>
            </div>

            {#if newCourse.prerequisites.length > 0}
              <div class="array-items">
                {#each newCourse.prerequisites as prereq}
                  <div class="array-item">
                    <span>{prereq}</span>
                    <button
                      type="button"
                      class="mdc-button mdc-button--small"
                      on:click={() => removePrerequisite(prereq)}
                    >
                      <span class="mdc-button__ripple"></span>
                      <span class="mdc-button__label">Remove</span>
                    </button>
                  </div>
                {/each}
              </div>
            {/if}
          </div>

          <div class="form-section">
            <label class="mdc-typography--subtitle2">Corequisites</label>
            <div class="array-input">
              <input
                class="mdc-text-field__input"
                type="text"
                placeholder="Enter corequisite course code"
                bind:value={corequisiteInput}
              />
              <button
                type="button"
                class="mdc-button mdc-button--raised"
                on:click={addCorequisite}
              >
                <span class="mdc-button__ripple"></span>
                <span class="mdc-button__label">Add</span>
              </button>
            </div>

            {#if newCourse.corequisites.length > 0}
              <div class="array-items">
                {#each newCourse.corequisites as coreq}
                  <div class="array-item">
                    <span>{coreq}</span>
                    <button
                      type="button"
                      class="mdc-button mdc-button--small"
                      on:click={() => removeCorequisite(coreq)}
                    >
                      <span class="mdc-button__ripple"></span>
                      <span class="mdc-button__label">Remove</span>
                    </button>
                  </div>
                {/each}
              </div>
            {/if}
          </div>

          <div class="form-section">
            <label class="mdc-typography--subtitle2">Course Times</label>
            <div class="array-input">
              <input
                class="mdc-text-field__input"
                type="text"
                placeholder="Enter course time (e.g., 'Mon 10:00-11:30')"
                bind:value={courseTimeInput}
              />
              <button
                type="button"
                class="mdc-button mdc-button--raised"
                on:click={addCourseTime}
              >
                <span class="mdc-button__ripple"></span>
                <span class="mdc-button__label">Add</span>
              </button>
            </div>

            {#if newCourse.course_time.length > 0}
              <div class="array-items">
                {#each newCourse.course_time as time}
                  <div class="array-item">
                    <span>{time}</span>
                    <button
                      type="button"
                      class="mdc-button mdc-button--small"
                      on:click={() => removeCourseTime(time)}
                    >
                      <span class="mdc-button__ripple"></span>
                      <span class="mdc-button__label">Remove</span>
                    </button>
                  </div>
                {/each}
              </div>
            {/if}
          </div>

          <div class="form-actions">
            <button
              type="button"
              class="mdc-button"
              on:click={resetCourseForm}
            >
              <span class="mdc-button__ripple"></span>
              <span class="mdc-button__label">Reset</span>
            </button>

            <button
              type="submit"
              class="mdc-button mdc-button--raised"
            >
              <span class="mdc-button__ripple"></span>
              <span class="mdc-button__label">Create Course</span>
            </button>
          </div>
        </form>
      </div>
    </div>
  {/if}

  {#if showLocationForm}
    <div class="mdc-card course-form-card">
      <div class="mdc-card__content">
        <h2 class="mdc-typography--headline6">Create New Location</h2>

        {#if locationCreationSuccess}
          <div class="success-message">
            <p class="mdc-typography--body2">{locationCreationSuccess}</p>
          </div>
        {/if}

        {#if locationCreationError}
          <div class="error-message">
            <p class="mdc-typography--body2">{locationCreationError}</p>
          </div>
        {/if}

        <form on:submit|preventDefault={createLocation}>
          <div class="form-row">
            <div class="form-field">
              <label class="mdc-typography--subtitle2" for="room-id">Room ID*</label>
              <input
                id="room-id"
                class="mdc-text-field__input"
                type="text"
                bind:value={newLocation.room_id}
                required
              />
            </div>

            <div class="form-field">
              <label class="mdc-typography--subtitle2" for="room-name">Room Name*</label>
              <input
                id="room-name"
                class="mdc-text-field__input"
                type="text"
                bind:value={newLocation.room_name}
                required
              />
            </div>
          </div>

          <div class="form-row">
            <div class="form-field">
              <label class="mdc-typography--subtitle2" for="available-seats-location">Available Seats*</label>
              <input
                id="available-seats-location"
                class="mdc-text-field__input"
                type="number"
                min="1"
                bind:value={newLocation.available_seats}
                required
              />
            </div>
          </div>

          <div class="form-section">
            <label class="mdc-typography--subtitle2">Available Times</label>
            <div class="array-input">
              <input
                class="mdc-text-field__input"
                type="text"
                placeholder="Enter available time (e.g., 'Mon 10:00-11:30')"
                bind:value={availableTimeInput}
              />
              <button
                type="button"
                class="mdc-button mdc-button--raised"
                on:click={addAvailableTime}
              >
                <span class="mdc-button__ripple"></span>
                <span class="mdc-button__label">Add</span>
              </button>
            </div>

            {#if newLocation.available_times.length > 0}
              <div class="array-items">
                {#each newLocation.available_times as time}
                  <div class="array-item">
                    <span>{time}</span>
                    <button
                      type="button"
                      class="mdc-button mdc-button--small"
                      on:click={() => removeAvailableTime(time)}
                    >
                      <span class="mdc-button__ripple"></span>
                      <span class="mdc-button__label">Remove</span>
                    </button>
                  </div>
                {/each}
              </div>
            {/if}
          </div>

          <div class="form-actions">
            <button
              type="button"
              class="mdc-button"
              on:click={resetLocationForm}
            >
              <span class="mdc-button__ripple"></span>
              <span class="mdc-button__label">Reset</span>
            </button>

            <button
              type="submit"
              class="mdc-button mdc-button--raised"
            >
              <span class="mdc-button__ripple"></span>
              <span class="mdc-button__label">Create Location</span>
            </button>
          </div>
        </form>
      </div>
    </div>
  {/if}

  {#if error}
    <div class="mdc-card error-card">
      <div class="mdc-card__content">
        <p class="mdc-typography--body2">{error}</p>
      </div>
    </div>
  {/if}

  {#if unenrollSuccess}
    <div class="mdc-card success-card">
      <div class="mdc-card__content">
        <p class="mdc-typography--body2">{unenrollSuccess}</p>
      </div>
    </div>
  {/if}

  <div class="student-select-container">
    <label class="mdc-typography--subtitle1" for="student-select">
      Select Student to View Enrollments
    </label>
    <div class="mdc-select">
      <select
        id="student-select"
        class="mdc-select__native-control"
        bind:value={selectedStudentId}
        on:change={handleStudentChange}
      >
        {#each students as student}
          <option value={student.student_id}>
            {student.first_name} {student.last_name} ({student.student_id})
          </option>
        {/each}
      </select>
      <div class="mdc-select__dropdown-icon"></div>
      <div class="mdc-line-ripple"></div>
    </div>
  </div>

  <h2 class="mdc-typography--headline5 courses-title">
    {#if selectedStudentId}
      {students.find(s => s.student_id === selectedStudentId)?.first_name || ''}'s Enrolled Courses
    {:else}
      Student Enrollments
    {/if}
  </h2>

  {#if isLoading}
    <div class="loading-indicator">
      <div class="mdc-typography--body1 animate-pulse">Loading courses...</div>
    </div>
  {:else if !selectedStudentId}
    <div class="mdc-card info-card">
      <div class="mdc-card__content">
        <p class="mdc-typography--body1">Please select a student to view their enrollments</p>
      </div>
    </div>
  {:else if enrolledCourses.length === 0}
    <div class="mdc-card info-card">
      <div class="mdc-card__content">
        <p class="mdc-typography--body1">This student is not enrolled in any courses yet.</p>
      </div>
    </div>
  {:else}
    <div class="courses-grid">
      {#each enrolledCourses as course}
        <div class="course-container">
          <CourseCard {course} />

          <div class="enrollment-details">
            <div class="mdc-typography--caption">
              Enrolled on: {new Date(course.enrollmentDate).toLocaleDateString()}
            </div>
            {#if course.grade}
              <div class="mdc-typography--subtitle2">Grade: {course.grade}</div>
            {/if}

            <button
              class="mdc-button mdc-button--raised mdc-button--danger"
              on:click={() => handleUnenroll(course.id)}
            >
              <span class="mdc-button__ripple"></span>
              <span class="mdc-button__label">Unenroll</span>
            </button>
          </div>
        </div>
      {/each}
    </div>
  {/if}
</main>

<style>
  main {
    padding: 1rem;
    max-width: 1200px;
    margin: 0 auto;
  }

  .dashboard-title {
    margin-bottom: 0.5rem;
    color: var(--mdc-theme-primary);
  }

  .dashboard-nav {
    margin: 1rem 0;
    display: flex;
    gap: 1rem;
  }

  .student-select-container {
    margin: 1.5rem 0;
  }

  .courses-title {
    margin: 1.5rem 0 1rem;
    color: var(--mdc-theme-primary);
  }

  .courses-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
    gap: 1rem;
  }

  .course-container {
    margin-bottom: 1rem;
  }

  .enrollment-details {
    margin-top: 0.5rem;
    padding: 0.5rem;
  }

  .error-card {
    background-color: #ffebee;
    margin-bottom: 1rem;
  }

  .success-card {
    background-color: #e8f5e9;
    margin-bottom: 1rem;
  }

  .info-card {
    background-color: #e3f2fd;
    margin-bottom: 1rem;
  }

  .mdc-card__content {
    padding: 1rem;
  }

  .loading-indicator {
    padding: 1rem;
    text-align: center;
  }

  .mdc-button--danger {
    background-color: var(--mdc-theme-error);
    color: white;
    width: 100%;
    margin-top: 0.5rem;
  }

  /* Course form styles */
  .course-form-card {
    margin-bottom: 1.5rem;
  }

  .form-row {
    display: flex;
    gap: 1rem;
    margin-bottom: 1rem;
  }

  .form-field {
    flex: 1;
    display: flex;
    flex-direction: column;
  }

  .form-field label {
    margin-bottom: 0.25rem;
  }

  .form-section {
    margin-bottom: 1rem;
  }

  .array-input {
    display: flex;
    gap: 0.5rem;
    margin-top: 0.25rem;
    margin-bottom: 0.5rem;
  }

  .array-input input {
    flex: 1;
  }

  .array-items {
    display: flex;
    flex-wrap: wrap;
    gap: 0.5rem;
    margin-top: 0.5rem;
  }

  .array-item {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    background-color: #f5f5f5;
    padding: 0.25rem 0.5rem;
    border-radius: 4px;
  }

  .mdc-button--small {
    padding: 0 0.5rem;
    min-width: auto;
    height: 24px;
    line-height: 24px;
    font-size: 0.75rem;
  }

  .form-actions {
    display: flex;
    justify-content: flex-end;
    gap: 1rem;
    margin-top: 1.5rem;
  }

  .success-message {
    background-color: #e8f5e9;
    padding: 0.5rem 1rem;
    border-radius: 4px;
    margin-bottom: 1rem;
  }

  .error-message {
    background-color: #ffebee;
    padding: 0.5rem 1rem;
    border-radius: 4px;
    margin-bottom: 1rem;
  }

  /* Add Material Design ripple effect to buttons */
  .mdc-button__ripple {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    overflow: hidden;
  }
</style>
