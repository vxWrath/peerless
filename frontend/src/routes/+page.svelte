<script lang="ts">

	import Header from '$lib/components/home/nav.svelte';
	import Hero from '$lib/components/home/hero.svelte';
	import Features from '$lib/components/home/features.svelte';
	import Pricing from '$lib/components/home/pricing.svelte';
	import Footer from '$lib/components/home/footer.svelte';

</script>

<svelte:head>
	<title>Peerless - Advanced Discord Bot for Roblox Sports Leagues</title>
	<meta name="description" content="Peerless is an advanced Discord bot designed to make managing Roblox sports leagues effortless. Join 14,000+ servers and 1M+ users with 99.9% uptime." />
	<meta name="keywords" content="Discord bot, Roblox, sports leagues, team management, statistics, tournaments" />
</svelte:head>

<div class="bg-gray-800 text-gray-200 min-h-screen">
	<Header/>

	<main class="flex-1">
		<Hero/>
		<Features/>
		<Pricing/>
	</main>

	<Footer/>
</div>