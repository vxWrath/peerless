<script lang="ts">
	import { onMount } from 'svelte';
	import { user, fetchUserGuilds } from '$lib/stores/auth';
	import { goto } from '$app/navigation';
	import Navigation from '$lib/components/Navigation.svelte';

	let guilds = $state([]);
	let loading = $state(true);
	
	onMount(async () => {
		if (!$user) {
			goto('/');
			return;
		}
		
		guilds = await fetchUserGuilds();
		loading = false;
	});
	
	function selectGuild(guildId: string) {
		goto(`/dashboard/${guildId}`);
	}
</script>

<svelte:head>
	<title>Dashboard - Peerless</title>
</svelte:head>

<Navigation />

<div class="min-h-screen bg-gray-900 pt-20">
	<div class="max-w-6xl mx-auto px-4 py-8">
		<div class="text-center mb-8">
			<h1 class="text-3xl font-bold text-white mb-2">
				hey {$user?.username}
			</h1>
			<p class="text-gray-400">select a server to manage</p>
		</div>

		{#if loading}
			<div class="flex justify-center">
				<div class="animate-spin rounded-full h-8 w-8 border-b-2 border-pink-500"></div>
			</div>
		{:else if guilds.length === 0}
			<div class="text-center">
				<div class="bg-gray-800 rounded-lg p-6 max-w-md mx-auto">
					<h3 class="text-lg font-medium text-white mb-2">no servers found</h3>
					<p class="text-gray-400 mb-4 text-sm">
						you need manage server permissions to configure settings
					</p>
					<a href="https://discord.com/application-directory/1105640024113954829"
					   class="bg-pink-600 hover:bg-pink-700 text-white px-4 py-2 rounded font-medium">
						invite peerless
					</a>
				</div>
			</div>
		{:else}
			<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
				{#each guilds as guild}
					<button onclick={() => selectGuild(guild.id)}
							class="bg-gray-800 hover:bg-gray-700 rounded-lg p-4 text-left border border-gray-700">
						<div class="flex items-center mb-3">
							{#if guild.icon}
								<img src="https://cdn.discordapp.com/icons/{guild.id}/{guild.icon}.png"
									 alt="{guild.name}"
									 class="w-10 h-10 rounded-full mr-3">
							{:else}
								<div class="w-10 h-10 bg-gray-600 rounded-full flex items-center justify-center mr-3">
									<i class="fas fa-server text-gray-300 text-sm"></i>
								</div>
							{/if}
							<div>
								<h3 class="font-medium text-white">{guild.name}</h3>
								<span class="text-xs text-gray-400">
									{guild.owner ? 'owner' : 'admin'}
								</span>
							</div>
						</div>
						<div class="text-xs text-gray-400">click to manage →</div>
					</button>
				{/each}
			</div>
		{/if}
	</div>
</div>
