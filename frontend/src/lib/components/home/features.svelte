<script lang="ts">
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
