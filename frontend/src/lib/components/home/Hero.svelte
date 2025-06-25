<script lang="ts">
	import { onMount } from 'svelte';

	let isVisible = $state(false);

	onMount(() => {
		isVisible = true;
	});
</script>

<section class="min-h-screen flex items-center justify-center bg-gray-900">
	<div class="max-w-4xl mx-auto px-4 text-center">
		<h1 class="text-6xl font-bold text-white mb-4">
			<span class="text-pink-500">Peer</span>less
		</h1>

		<p class="text-xl text-gray-300 mb-8">
			discord bot for roblox sports leagues
		</p>

		<div class="flex gap-4 justify-center mb-12">
			<a href="https://discord.com/application-directory/1105640024113954829"
			   class="bg-pink-600 hover:bg-pink-700 text-white px-6 py-3 rounded font-medium">
				invite bot
			</a>
			<a href="https://discord.gg/FsNK9y7MPg"
			   class="border border-gray-600 hover:border-gray-400 text-white px-6 py-3 rounded font-medium">
				support
			</a>
		</div>

		<div class="grid grid-cols-3 gap-8 max-w-2xl mx-auto">
			<div class="text-center">
				<div class="text-2xl font-bold text-pink-500">14k+</div>
				<div class="text-gray-400 text-sm">servers</div>
			</div>
			<div class="text-center">
				<div class="text-2xl font-bold text-purple-500">1m+</div>
				<div class="text-gray-400 text-sm">users</div>
			</div>
			<div class="text-center">
				<div class="text-2xl font-bold text-blue-500">99.9%</div>
				<div class="text-gray-400 text-sm">uptime</div>
			</div>
		</div>
	</div>
</section>
