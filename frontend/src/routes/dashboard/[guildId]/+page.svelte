<script lang="ts">
	import { onMount } from 'svelte';
	import { page } from '$app/stores';
	import { user } from '$lib/stores/auth';
	import { settingsConfig, guildSettings, loadSettingsConfig, loadGuildSettings, saveGuildSetting } from '$lib/stores/settings';
	import { goto } from '$app/navigation';
	import Navigation from '$lib/components/Navigation.svelte';
	import SettingInput from '$lib/components/settings/SettingInput.svelte';
	
	let guildId = $page.params.guildId;
	let loading = $state(true);
	let selectedCategory = $state('customization');
	let guild = $state(null);
	let saving = $state(false);
	
	onMount(async () => {
		if (!$user) {
			goto('/');
			return;
		}
		
		guild = $user.guilds?.find(g => g.id === guildId);
		if (!guild) {
			goto('/dashboard');
			return;
		}
		
		await loadSettingsConfig();
		await loadGuildSettings(guildId);
		loading = false;
	});
	
	async function saveSetting(key: string, value: any): Promise<boolean> {
		return await saveGuildSetting(guildId, key, value);
	}
</script>

<svelte:head>
	<title>{guild?.name || 'Server'} Settings - Peerless</title>
</svelte:head>

<Navigation />

<div class="min-h-screen bg-gray-900 pt-20">
	<div class="max-w-6xl mx-auto px-4 py-8">
		{#if loading}
			<div class="flex justify-center">
				<div class="animate-spin rounded-full h-8 w-8 border-b-2 border-pink-500"></div>
			</div>
		{:else}
			<div class="mb-6">
				<div class="flex items-center mb-4">
					<a href="/dashboard" class="text-gray-400 hover:text-white mr-3">
						← back
					</a>
					{#if guild?.icon}
						<img src="https://cdn.discordapp.com/icons/{guild.id}/{guild.icon}.png"
							 alt="{guild.name}"
							 class="w-8 h-8 rounded-full mr-3">
					{:else}
						<div class="w-8 h-8 bg-gray-600 rounded-full flex items-center justify-center mr-3">
							<i class="fas fa-server text-gray-300 text-sm"></i>
						</div>
					{/if}
					<div>
						<h1 class="text-2xl font-bold text-white">{guild?.name}</h1>
						<p class="text-gray-400 text-sm">settings</p>
					</div>
				</div>
			</div>

			<div class="grid grid-cols-1 lg:grid-cols-4 gap-6">
				<div class="lg:col-span-1">
					<div class="bg-gray-800 rounded-lg p-4">
						<h3 class="font-medium text-white mb-3">categories</h3>
						<nav class="space-y-1">
							{#each $settingsConfig as category}
								<button onclick={() => selectedCategory = category.key}
										class="w-full text-left px-3 py-2 rounded text-sm
											   {selectedCategory === category.key ? 'bg-pink-600 text-white' : 'text-gray-300 hover:text-white hover:bg-gray-700'}">
									{category.name.toLowerCase()}
								</button>
							{/each}
						</nav>
					</div>
				</div>

				<div class="lg:col-span-3">
					{#each $settingsConfig as category}
						{#if selectedCategory === category.key}
							<div class="bg-gray-800 rounded-lg p-6">
								<div class="mb-6">
									<h2 class="text-xl font-bold text-white mb-2">{category.name.toLowerCase()}</h2>
									<p class="text-gray-400 text-sm">{category.description}</p>
								</div>

								{#if category.settings.length === 0}
									<div class="text-center py-8">
										<p class="text-gray-400">no settings available yet</p>
									</div>
								{:else}
									<div class="space-y-6">
										{#each category.settings as setting}
											<div class="border-b border-gray-700 pb-4 last:border-b-0 last:pb-0">
												<div class="mb-3">
													<div class="flex items-center mb-1">
														{#if setting.icon}
															<i class="{setting.icon} text-pink-500 mr-2 text-sm"></i>
														{/if}
														<h4 class="font-medium text-white">{setting.name}</h4>
														{#if setting.required}
															<span class="ml-2 text-xs bg-red-600 text-white px-2 py-1 rounded">required</span>
														{/if}
													</div>
													<p class="text-gray-400 text-sm">{setting.description}</p>
												</div>

												<SettingInput
													{setting}
													value={$guildSettings[setting.key] ?? setting.default_value}
													onSave={(value) => saveSetting(setting.key, value)}
													saving={false}
												/>
											</div>
										{/each}
									</div>
								{/if}
							</div>
						{/if}
					{/each}
				</div>
			</div>
		{/if}
	</div>
</div>
