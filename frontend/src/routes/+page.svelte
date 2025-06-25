<script lang="ts">
	import { onMount } from 'svelte';
	import Header from '$lib/components/home/nav.svelte';

	let mounted = $state(false);

	onMount(() => {
		mounted = true;
	});

	const stats = [
		{ number: '14,000+', label: 'Discord Servers' },
		{ number: '1M+', label: 'Unique Users' },
		{ number: '99.9%', label: 'Uptime' }
	];

	const pricing_plans = [
		{
			name: 'Pro Bot',
			price: '$2.99',
			description: 'Perfect for growing leagues',
			features: [
				'Custom profile picture & name',
				'Increased limits (teams, coaches, roles)',
				'Lowered cooldowns',
				'Schedule generation',
				'Auto stats & standings',
				'League slots'
			],
			popular: false
		},
		{
			name: 'Premium Bot',
			price: '$3.99',
			description: 'For serious league management',
			features: [
				'No limits or cooldowns',
				'All Premium features',
				'Advanced analytics',
				'Up to 5-10 custom commands',
				'Priority support',
				'Beta feature access'
			],
			popular: true
		},
		{
			name: 'Custom Bot',
			price: '$9.99',
			description: 'Completely tailored solution',
			features: [
				'Fully customized bot',
				'Up to 25-50 custom commands',
				'Unlimited everything',
				'Custom integrations',
				'Dedicated support',
				'Anything you want within reason'
			],
			popular: false
		}
	];

	const features = [
		{
			icon: 'fas fa-users',
			title: 'Team Management',
			description: 'Effortlessly manage teams, rosters, and player assignments with intuitive commands.'
		},
		{
			icon: 'fas fa-calendar-alt',
			title: 'Season Planning',
			description: 'Create and manage seasons with automated scheduling and bracket generation.'
		},
		{
			icon: 'fas fa-chart-line',
			title: 'Statistics Tracking',
			description: 'Comprehensive stats tracking with automated data collection and reporting.'
		},
		{
			icon: 'fas fa-exchange-alt',
			title: 'Transaction System',
			description: 'Handle trades, transfers, and player movements with built-in approval workflows.'
		},
		{
			icon: 'fas fa-trophy',
			title: 'Standings & Rankings',
			description: 'Real-time standings updates with customizable point systems and tiebreakers.'
		},
		{
			icon: 'fas fa-cog',
			title: 'Highly Customizable',
			description: 'Tailor every aspect of your league management to fit your specific needs.'
		}
	];
</script>

<svelte:head>
	<title>Peerless - Advanced Discord Bot for Roblox Sports Leagues</title>
	<meta name="description" content="Peerless is an advanced Discord bot designed to make managing Roblox sports leagues effortless. Join 14,000+ servers and 1M+ users with 99.9% uptime." />
	<meta name="keywords" content="Discord bot, Roblox, sports leagues, team management, statistics, tournaments" />
</svelte:head>

<div class="bg-gray-800 text-gray-200 min-h-screen">
	<Header/>

	<main class="flex-1">
		<section class="relative py-20 px-4 text-center bg-gradient-to-br from-gray-800 via-gray-900 to-black">
			<div class="max-w-6xl mx-auto">
				<div class="flex flex-col items-center space-y-8">
					<img src="pink.png" alt="Peerless Logo" class="h-32 w-32 filter drop-shadow-2xl animate-pulse">
					<h1 class="text-5xl md:text-7xl font-bold bg-gradient-to-r from-pink-400 to-pink-600 bg-clip-text text-transparent">
						Peerless
					</h1>
					<p class="text-xl md:text-2xl text-gray-300 max-w-3xl leading-relaxed">
						Advanced Discord bot designed to make managing <span class="text-pink-400 font-semibold">Roblox sports leagues</span> effortless
					</p>
					<div class="flex flex-col sm:flex-row gap-4 mt-8">
						<a href="https://discord.com/application-directory/1105640024113954829"
						   class="bg-pink-500 hover:bg-pink-600 text-white px-8 py-4 rounded-lg font-semibold text-lg transition-all duration-300 transform hover:scale-105 shadow-lg">
							<i class="fab fa-discord mr-2"></i>
							Invite to Server
						</a>
						<a href="https://discord.gg/FsNK9y7MPg"
						   class="border-2 border-pink-500 text-pink-400 hover:bg-pink-500 hover:text-white px-8 py-4 rounded-lg font-semibold text-lg transition-all duration-300">
							<i class="fas fa-headset mr-2"></i>
							Support Server
						</a>
					</div>
				</div>
			</div>
		</section>

		<section class="py-16 px-4 bg-gray-900">
			<div class="max-w-6xl mx-auto">
				<div class="grid grid-cols-1 md:grid-cols-3 gap-8 text-center">
					{#each stats as stat}
						<div class="bg-gray-800 p-8 rounded-xl border border-gray-700 hover:border-pink-500 transition-all duration-300">
							<div class="text-4xl md:text-5xl font-bold text-pink-400 mb-2">{stat.number}</div>
							<div class="text-gray-300 text-lg">{stat.label}</div>
						</div>
					{/each}
				</div>
			</div>
		</section>

		<section id="features" class="py-20 px-4 bg-gray-800">
			<div class="max-w-6xl mx-auto">
				<div class="text-center mb-16">
					<h2 class="text-4xl md:text-5xl font-bold text-white mb-4">
						Why Choose <span class="text-pink-400">Peerless</span>?
					</h2>
					<p class="text-xl text-gray-300 max-w-3xl mx-auto">
						From handling teams and coaches to seasons and transactions, Peerless makes running a league smoother than ever
					</p>
				</div>

				<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
					{#each features as feature}
						<div class="bg-gray-900 p-6 rounded-xl border border-gray-700 hover:border-pink-500 transition-all duration-300 hover:transform hover:scale-105">
							<div class="text-pink-400 text-3xl mb-4">
								<i class={feature.icon}></i>
							</div>
							<h3 class="text-xl font-semibold text-white mb-3">{feature.title}</h3>
							<p class="text-gray-300">{feature.description}</p>
						</div>
					{/each}
				</div>
			</div>
		</section>

		<section id="pricing" class="py-20 px-4 bg-gray-900">
			<div class="max-w-6xl mx-auto">
				<div class="text-center mb-16">
					<h2 class="text-4xl md:text-5xl font-bold text-white mb-4">
						Choose Your <span class="text-pink-400">Plan</span>
					</h2>
					<p class="text-xl text-gray-300 max-w-3xl mx-auto">
						All plans include your own dedicated Discord bot. Upgrade your league management experience.
					</p>
				</div>

				<div class="grid grid-cols-1 md:grid-cols-3 gap-8">
					{#each pricing_plans as plan, index}
						<div class="relative bg-gray-800 rounded-xl border-2 {plan.popular ? 'border-pink-500 transform scale-105' : 'border-gray-700'} p-8 hover:border-pink-500 hover:transform hover:scale-110 hover:shadow-2xl hover:shadow-pink-500/20 transition-all duration-500 animate-fade-in-up group"
							 style="animation-delay: {index * 200}ms;">
							{#if plan.popular}
								<div class="absolute -top-4 left-1/2 transform -translate-x-1/2">
									<span class="bg-gradient-to-r from-pink-500 to-pink-600 text-white px-4 py-2 rounded-full text-sm font-semibold shadow-lg">Most Popular</span>
								</div>
							{/if}

							<div class="text-center mb-8">
								<h3 class="text-2xl font-bold text-white mb-2 group-hover:text-pink-400 transition-colors duration-300">{plan.name}</h3>
								<p class="text-gray-300 mb-4 group-hover:text-gray-200 transition-colors duration-300">{plan.description}</p>
								<div class="text-4xl font-bold text-pink-400 mb-2 group-hover:scale-110 transition-transform duration-300">{plan.price}</div>
								<div class="text-gray-400 text-sm">per month</div>
							</div>

							<ul class="space-y-3 mb-8">
								{#each plan.features as feature, featureIndex}
									<li class="flex items-center text-gray-300 animate-fade-in group-hover:text-gray-200 transition-colors duration-300"
										style="animation-delay: {(index * 200) + (featureIndex * 100) + 300}ms;">
										<i class="fas fa-check text-pink-400 mr-3 group-hover:text-pink-300 transition-colors duration-300"></i>
										{feature}
									</li>
								{/each}
							</ul>

							<button class="w-full bg-gradient-to-r from-pink-500 to-pink-600 hover:from-pink-600 hover:to-pink-700 text-white py-3 rounded-lg font-semibold transition-all duration-300 transform hover:scale-105 shadow-lg hover:shadow-xl animate-fade-in group-hover:shadow-pink-500/30"
									style="animation-delay: {(index * 200) + 800}ms;">
								Get Started
							</button>
						</div>
					{/each}
				</div>
			</div>
		</section>

		<section class="py-20 px-4 bg-gradient-to-r from-pink-600 to-pink-800">
			<div class="max-w-4xl mx-auto text-center">
				<h2 class="text-4xl md:text-5xl font-bold text-white mb-6">
					Ready to Transform Your League?
				</h2>
				<p class="text-xl text-pink-100 mb-8 max-w-2xl mx-auto">
					Join thousands of league managers who trust Peerless to handle their Roblox sports leagues.
					Get started today and experience the difference.
				</p>
				<div class="flex flex-col sm:flex-row gap-4 justify-center">
					<a href="https://discord.com/application-directory/1105640024113954829"
					   class="bg-white text-pink-600 hover:bg-gray-100 px-8 py-4 rounded-lg font-semibold text-lg transition-all duration-300 transform hover:scale-105 shadow-lg">
						<i class="fab fa-discord mr-2"></i>
						Add to Discord
					</a>
					<a href="https://discord.gg/FsNK9y7MPg"
					   class="border-2 border-white text-white hover:bg-white hover:text-pink-600 px-8 py-4 rounded-lg font-semibold text-lg transition-all duration-300">
						<i class="fas fa-question-circle mr-2"></i>
						Get Support
					</a>
				</div>
			</div>
		</section>
	</main>

	<footer class="bg-black py-12 px-4">
		<div class="max-w-6xl mx-auto">
			<div class="grid grid-cols-1 md:grid-cols-4 gap-8">
				<div class="col-span-1 md:col-span-2">
					<div class="flex items-center space-x-3 mb-4">
						<img src="pink.png" alt="Peerless Logo" class="h-10 w-10">
						<span class="text-2xl font-bold text-white">Peerless</span>
					</div>
					<p class="text-gray-400 max-w-md">
						The most advanced Discord bot for managing Roblox sports leagues.
						Trusted by 14,000+ servers worldwide.
					</p>
				</div>

				<div>
					<h4 class="text-white font-semibold mb-4">Quick Links</h4>
					<ul class="space-y-2">
						<li><a href="https://discord.com/application-directory/1105640024113954829" class="text-gray-400 hover:text-pink-400 transition-colors">Invite Bot</a></li>
						<li><a href="https://discord.gg/FsNK9y7MPg" class="text-gray-400 hover:text-pink-400 transition-colors">Support Server</a></li>
						<li><a href="#pricing" class="text-gray-400 hover:text-pink-400 transition-colors">Pricing</a></li>
					</ul>
				</div>

				<div>
					<h4 class="text-white font-semibold mb-4">Stats</h4>
					<ul class="space-y-2 text-gray-400">
						<li>14,000+ Servers</li>
						<li>1M+ Users</li>
						<li>99.9% Uptime</li>
					</ul>
				</div>
			</div>

			<div class="border-t border-gray-800 mt-8 pt-8 text-center">
				<p class="text-gray-400">
					© 2025 Peerless. All rights reserved.
				</p>
			</div>
		</div>
	</footer>
</div>