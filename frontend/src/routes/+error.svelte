<script lang="ts">
	import { page } from '$app/stores';
	import Navigation from '$lib/components/Navigation.svelte';
</script>

<svelte:head>
	<title>Page Not Found - Peerless</title>
</svelte:head>

<Navigation />

<div class="min-h-screen bg-gray-900 pt-20 flex items-center justify-center">
	<div class="text-center">
		<div class="mb-8">
			<h1 class="text-6xl font-bold text-pink-500 mb-4">404</h1>
			<h2 class="text-2xl font-semibold text-white mb-2">page not found</h2>
			<p class="text-gray-400">the page you're looking for doesn't exist</p>
		</div>
		
		<div class="space-y-4">
			<a href="/" class="inline-block bg-pink-600 hover:bg-pink-700 text-white px-6 py-3 rounded-lg font-medium transition-colors">
				go home
			</a>
			<div>
				<a href="/dashboard" class="text-gray-400 hover:text-white transition-colors">
					dashboard
				</a>
			</div>
		</div>
	</div>
</div>
