<script>
  export let course;

  // Determine the title to display (course_name has priority over title)
  const displayTitle = course.course_name || course.title;

  // Create a description if not provided
  const displayDescription = course.description ||
    `${course.course_code || course.id} - ${course.section || 'Main'} - ${course.semester || ''}`;

  // Get available seats
  const availableSeats = course.available_seats || course.seats;
</script>

<div class="mdc-card course-card">
  <div class="mdc-card__primary-action" tabindex="0">
    <div class="mdc-card__content">
      <h2 class="mdc-typography--headline6">{displayTitle}</h2>
      <p class="mdc-typography--body2">{displayDescription}</p>

      <div class="details">
        <span class="mdc-typography--caption"
          >Instructor: {course.instructor}</span
        >
        <span class="mdc-typography--caption"
          >Available Seats: {availableSeats}</span
        >
      </div>
    </div>
  </div>

  <div class="mdc-card__actions">
    <slot></slot>
  </div>
</div>

<style>
  .course-card {
    width: 100%;
    margin-bottom: 16px;
    transition:
      transform 0.2s,
      box-shadow 0.2s;
    border-radius: 4px;
    background-color: var(--mdc-theme-surface);
    box-shadow:
      0 2px 1px -1px rgba(0, 0, 0, 0.2),
      0 1px 1px 0 rgba(0, 0, 0, 0.14),
      0 1px 3px 0 rgba(0, 0, 0, 0.12);
  }

  .course-card:hover {
    transform: translateY(-2px);
    box-shadow:
      0 5px 5px -3px rgba(0, 0, 0, 0.2),
      0 8px 10px 1px rgba(0, 0, 0, 0.14),
      0 3px 14px 2px rgba(0, 0, 0, 0.12);
  }

  .mdc-card__content {
    padding: 16px;
  }

  .details {
    display: flex;
    justify-content: space-between;
    margin-top: 8px;
  }

  .mdc-card__actions {
    padding: 8px;
    border-top: 1px solid rgba(0, 0, 0, 0.12);
  }

  :global(.mdc-typography--headline6) {
    margin: 0 0 8px 0;
    color: var(--mdc-theme-on-surface);
  }

  :global(.mdc-typography--body2) {
    margin: 0 0 16px 0;
    color: rgba(0, 0, 0, 0.6);
  }

  :global(.mdc-typography--caption) {
    color: rgba(0, 0, 0, 0.6);
  }
</style>
