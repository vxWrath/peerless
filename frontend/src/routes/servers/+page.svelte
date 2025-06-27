<script lang="ts">
	import Header from '$lib/components/nav.svelte';

	const { data } = $props();

	const authenticated = data.authenticated;
	const user = data.user;
</script>

<svelte:head>
	<title>Peerless</title>
	<meta name="description" content="Peerless is an advanced Discord bot designed to make managing Roblox sports leagues effortless. Join 14,000+ servers and 1M+ users." />
</svelte:head>

<div class="bg-gray-800 text-gray-200 min-h-screen flex flex-col">
	<Header {data} />

	{#if authenticated}
		<h1 class="text-xl font-bold mb-4">Welcome, {user.global_name}</h1>

		<h2 class="text-lg mb-2">Your Servers:</h2>

		{#each Object.values(user.guilds) as guild (guild.id)}
			<div class="bg-gray-700 rounded-xl p-4 mb-3 flex items-center gap-4 shadow">
				<img src={guild.icon_url} alt={guild.name} class="w-6 h-6 rounded-full object-cover" />
				<div>
					<p class="text-lg font-semibold">{guild.name}</p>
					<p class="text-sm text-gray-400">
						{guild.owner ? 'Owner' : 'Member'}
					</p>
				</div>
			</div>
		{/each}
	{:else}
		<p class="text-gray-400">You are not logged in.</p>
	{/if}
</div>