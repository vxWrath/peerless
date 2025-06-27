<script lang="ts">
	import Header from '$lib/components/nav.svelte';

	const { data } = $props();
</script>

<svelte:head>
	<title>Peerless</title>
	<meta name="description" content="Peerless is an advanced Discord bot designed to make managing Roblox sports leagues effortless. Join 14,000+ servers and 1M+ users." />
</svelte:head>

<div class="bg-gray-800 text-gray-200 min-h-screen flex flex-col">
	<Header {data} />
</div>