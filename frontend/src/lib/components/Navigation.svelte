<script lang="ts">
	import { onMount } from 'svelte';
	import { user } from '$lib/stores/auth';

	let isScrolled = $state(false);
	let isMobileMenuOpen = $state(false);

	onMount(() => {
		const handleScroll = () => {
			isScrolled = window.scrollY > 50;
		};

		window.addEventListener('scroll', handleScroll);
		return () => window.removeEventListener('scroll', handleScroll);
	});

	function toggleMobileMenu() {
		isMobileMenuOpen = !isMobileMenuOpen;
	}

	function login() {
		window.location.href = '/api/auth/discord';
	}

	function logout() {
		fetch('/api/auth/logout', { method: 'POST' })
			.then(() => {
				user.set(null);
				window.location.href = '/';
			});
	}
</script>

<nav class="fixed top-0 left-0 right-0 z-50 bg-gray-900 border-b border-gray-800">
	<div class="max-w-6xl mx-auto px-4">
		<div class="flex items-center justify-between h-16">
			<a href="/" class="text-xl font-bold text-white">
				<span class="text-pink-500">peer</span>less
			</a>

			<div class="hidden md:flex items-center gap-6">
				<a href="#features" class="text-gray-300 hover:text-white">features</a>
				<a href="#stats" class="text-gray-300 hover:text-white">stats</a>
				<a href="https://discord.gg/FsNK9y7MPg" class="text-gray-300 hover:text-white">support</a>
				{#if $user}
					<a href="/dashboard" class="text-gray-300 hover:text-white">dashboard</a>
					<button onclick={logout} class="text-gray-300 hover:text-white">logout</button>
				{:else}
					<button onclick={login} class="bg-pink-600 hover:bg-pink-700 text-white px-4 py-2 rounded">
						login
					</button>
				{/if}
			</div>

			<button onclick={toggleMobileMenu} class="md:hidden text-gray-400 hover:text-white">
				<i class="fas {isMobileMenuOpen ? 'fa-times' : 'fa-bars'}"></i>
			</button>
		</div>
	</div>

	{#if isMobileMenuOpen}
		<div class="md:hidden bg-gray-900 border-t border-gray-800">
			<div class="px-4 py-3 space-y-2">
				<a href="#features" class="block text-gray-300 hover:text-white py-2">features</a>
				<a href="#stats" class="block text-gray-300 hover:text-white py-2">stats</a>
				<a href="https://discord.gg/FsNK9y7MPg" class="block text-gray-300 hover:text-white py-2">support</a>
				{#if $user}
					<a href="/dashboard" class="block text-gray-300 hover:text-white py-2">dashboard</a>
					<button onclick={logout} class="block text-gray-300 hover:text-white py-2">logout</button>
				{:else}
					<button onclick={login} class="block bg-pink-600 hover:bg-pink-700 text-white px-4 py-2 rounded mt-2">
						login
					</button>
				{/if}
			</div>
		</div>
	{/if}
</nav>
