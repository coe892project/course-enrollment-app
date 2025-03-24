<script>
  export let course;
</script>

<div class="course-card border rounded-lg p-4 shadow-sm">
  <h2 class="text-xl font-bold mb-2">{course.title}</h2>
  <p class="text-gray-600 mb-3">{course.description}</p>

  <div class="flex justify-between items-center text-sm text-gray-500">
    <span>Instructor: {course.instructor}</span>
    <span>Available Seats: {course.seats}</span>
  </div>

  <slot></slot>
</div>

<style>
  .course-card {
    transition: transform 0.2s, box-shadow 0.2s;
  }

  .course-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  }
</style>
