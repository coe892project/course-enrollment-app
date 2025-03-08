<script>
    import { user } from '$lib/stores';
    import CourseCard from '$lib/CourseCard.svelte';
    import { goto } from '$app/navigation';
    import { onMount } from 'svelte';
  
    let courses = [];
    let enrolledCourses = [];
    let isLoading = true;
    let error = '';
  
    onMount(async () => {
      if (!$user) {
        goto('/login');
        return;
      }
  
      try {
        // Load all courses
        const coursesResponse = await fetch('/api/courses');
        if (!coursesResponse.ok) throw new Error('Failed to load courses');
        courses = await coursesResponse.json();
  
        // Load user's enrollments
        const enrollmentsResponse = await fetch(`/api/enrollments?userId=${$user.id}`);
        if (!enrollmentsResponse.ok) throw new Error('Failed to load enrollments');
        enrolledCourses = await enrollmentsResponse.json();
  
      } catch (err) {
        error = err.message;
      } finally {
        isLoading = false;
      }
    });
  
    async function handleEnrollment(courseId) {
      try {
        const response = await fetch('/api/enroll', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            userId: $user.id,
            courseId
          })
        });
  
        if (!response.ok) throw new Error('Enrollment failed');
  
        // Update local state
        const newEnrollment = await response.json();
        enrolledCourses = [...enrolledCourses, newEnrollment];
  
      } catch (err) {
        error = err.message;
      }
    }
  </script>
  
  <svelte:head>
    <title>All Courses - Course Enrollment</title>
  </svelte:head>
  
  <main class="container mx-auto p-4">
    <h1 class="text-3xl font-bold mb-6">Available Courses</h1>
  
    {#if error}
      <div class="bg-red-100 text-red-700 p-4 rounded mb-4">{error}</div>
    {/if}
  
    {#if isLoading}
      <div class="animate-pulse space-y-4">
        <div class="h-16 bg-gray-200 rounded"></div>
        <div class="h-16 bg-gray-200 rounded"></div>
      </div>
    {:else}
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {#each courses as course}
          <div class="border rounded-lg p-4 shadow-sm">
            <CourseCard {course} />
  
            <div class="mt-4 text-sm text-gray-600">
              <div class="flex justify-between items-center mb-2">
                <span>Seats available: {course.seats}</span>
                <span class="text-xs">
                  {course.instructor}
                </span>
              </div>
  
              {#if enrolledCourses.some(ec => ec.id === course.id)}
                <div class="text-green-600 font-medium">
                  ✓ Enrolled
                </div>
              {:else}
                <button
                  on:click={() => handleEnrollment(course.id)}
                  class="w-full bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600 disabled:bg-gray-400"
                  disabled={course.seats <= 0 || !$user}
                >
                  {course.seats > 0 ? 'Enroll Now' : 'Course Full'}
                </button>
              {/if}
            </div>
          </div>
        {/each}
      </div>
    {/if}
  </main>
  