<script lang="ts">
	import Navigation from '$lib/components/Navigation.svelte';
	import Hero from '$lib/components/home/Hero.svelte';
	import Features from '$lib/components/home/Features.svelte';
	import Stats from '$lib/components/home/Stats.svelte';
	import Footer from '$lib/components/Footer.svelte';
</script>

<svelte:head>
	<title>Peerless - Advanced Discord Bot for Roblox Sports Leagues</title>
	<meta name="description" content="Peerless is an advanced Discord bot designed to make managing Roblox sports leagues effortless. Join 14,000+ servers and 1M+ users." />
	<meta name="keywords" content="Discord bot, Roblox, sports leagues, team management, tournaments, statistics" />
	<meta property="og:title" content="Peerless - Advanced Discord Bot for Roblox Sports Leagues" />
	<meta property="og:description" content="Make managing your Roblox sports league effortless with teams, coaches, seasons, transactions, and much more." />
	<meta property="og:type" content="website" />
	<meta name="twitter:card" content="summary_large_image" />
</svelte:head>

<div class="bg-gray-900 text-gray-200">
	<Navigation />
	<Hero />
	<Features />
	<Stats />
	<Footer />
</div>