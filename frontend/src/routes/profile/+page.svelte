<script>
    import { user } from '$lib/stores';
  
    let name = $user?.name || '';
    let email = $user?.email || '';
  
    function saveProfile() {
      user.update(u => ({ ...u, name, email }));
    }
  </script>
  
  <main class="max-w-md mx-auto mt-20 p-6 bg-white rounded-lg shadow-md">
    <h1 class="text-2xl font-bold mb-6">Edit Profile</h1>
  
    <form on:submit|preventDefault={saveProfile} class="space-y-4">
      <div>
        <label class="block text-sm font-medium mb-1">Name</label>
        <input bind:value={name} class="w-full p-2 border rounded">
      </div>
  
      <div>
        <label class="block text-sm font-medium mb-1">Email</label>
        <input type="email" bind:value={email} class="w-full p-2 border rounded">
      </div>
  
      <button class="w-full bg-blue-500 text-white p-2 rounded hover:bg-blue-600">
        Save Changes
      </button>
    </form>
  </main>
  