<script lang="ts">
	import { onMount } from 'svelte';
	
	let heroRef: HTMLElement;
	let isVisible = $state(false);
	
	onMount(() => {
		isVisible = true;
	});

    let count = $state(0);

    function increment() {
        count += 1;
    }
</script>

<style>
  button {
    padding: 0.5rem 1rem;
    font-size: 1rem;
  }
</style>

<h1>Count: {count}</h1>
<button onclick={increment}>Increment</button>