<script>
    import { user } from '$lib/stores';
    import CourseCard from '$lib/CourseCard.svelte';
    import { goto } from '$app/navigation';
    import { onMount } from 'svelte';
  
    let enrolledCourses = [];
    let isLoading = true;
    let error = '';
  
    onMount(async () => {
      if (!$user) {
        goto('/login');
        return;
      }
  
      try {
        const response = await fetch(`/api/enrollments?userId=${$user.id}`);
        if (!response.ok) throw new Error('Failed to load enrollments');
        enrolledCourses = await response.json();
      } catch (err) {
        error = err.message;
      } finally {
        isLoading = false;
      }
    });
  </script>
  
  <svelte:head>
    <title>Dashboard - Course Enrollment</title>
  </svelte:head>
  
  <main class="container mx-auto p-4">
    <div class="mb-8">
      <h1 class="text-3xl font-bold mb-2">Welcome back, {$user?.name}!</h1>
      <p class="text-gray-600">Email: {$user?.email}</p>
      <div class="mt-4 flex gap-4">
        <a href="/profile" class="text-blue-500 hover:underline">Edit Profile</a>
        <button on:click={() => user.set(null)} class="text-red-500 hover:underline">
          Logout
        </button>
      </div>
    </div>
  
    {#if error}
      <div class="bg-red-100 text-red-700 p-4 rounded mb-4">{error}</div>
    {/if}
  
    <h2 class="text-2xl font-bold mb-4">Your Enrolled Courses</h2>
  
    {#if isLoading}
      <div class="animate-pulse text-gray-500">Loading your courses...</div>
    {:else if enrolledCourses.length === 0}
      <div class="bg-blue-100 text-blue-700 p-4 rounded">
        You're not enrolled in any courses yet. <a href="/courses" class="font-semibold hover:underline">Browse courses</a>
      </div>
    {:else}
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {#each enrolledCourses as course}
          <CourseCard {course}>
            <div class="mt-4 text-sm text-gray-600">
              Enrolled on: {new Date(course.enrollmentDate).toLocaleDateString()}
            </div>
          </CourseCard>
        {/each}
      </div>
    {/if}
  </main>
  