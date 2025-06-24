<script lang="ts">
	import { onMount } from 'svelte';
	import Test from '$lib/components/home/test.svelte';

	let mounted = $state(false);
	
	onMount(() => {
		mounted = true;
	});
</script>

<svelte:head>
	<title>Peerless - Advanced Discord Bot for Roblox Sports Leagues</title>
	<meta name="description" content="Peerless is an advanced Discord bot designed to make managing Roblox sports leagues effortless. Join 14,000+ servers and 1M+ users." />
</svelte:head>

<div class="bg-gray-900 text-gray-200 min-h-screen flex flex-col">
	<Test/>
</div>