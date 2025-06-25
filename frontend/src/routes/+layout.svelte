<script>
  import { onMount } from 'svelte';
  import { checkAuth } from '$lib/stores/auth';
  import "../app.css";

  let { children } = $props();

  onMount(() => {
    checkAuth();
  });
</script>

{@render children()}