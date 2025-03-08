<script>
    import { courses, user } from '$lib/stores';
    import CourseCard from '$lib/CourseCard.svelte';
    import { onMount } from 'svelte';
  
    // Fetch courses on component mount
    onMount(async () => {
      try {
        const response = await fetch('/api/courses');
        const data = await response.json();
        courses.set(data);
      } catch (error) {
        console.error('Error loading courses:', error);
      }
    });
  </script>
  
  <svelte:head>
    <title>Course Enrollment</title>
  </svelte:head>
  
  <main class="container mx-auto p-4">
    <div class="flex justify-between items-center mb-8">
      <a href="/courses" class="text-2xl font-bold">Available Courses</a>
      {#if $user}
        <div class="flex gap-4">
          <span>Welcome, {$user.name}!</span>
          <a href="/dashboard" class="btn btn-blue">My Dashboard</a>
        </div>
      {:else}
        <a href="/login" class="btn btn-blue">Login to Enroll</a>
      {/if}
    </div>
  
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      {#each $courses as course}
        <CourseCard {course} />
      {:else}
        <p class="text-gray-500">No courses available at the moment</p>
      {/each}
    </div>
  </main>
  
  <style>
    .btn {
      @apply px-4 py-2 rounded transition-colors;
    }
    .btn-blue {
      @apply bg-blue-500 text-white hover:bg-blue-600;
    }
  </style>
  