<script lang="ts">
	const features = [
		{ icon: 'fas fa-users', title: 'teams', description: 'manage rosters and players' },
		{ icon: 'fas fa-user-tie', title: 'coaches', description: 'assign staff roles' },
		{ icon: 'fas fa-calendar-alt', title: 'seasons', description: 'schedule games and playoffs' },
		{ icon: 'fas fa-exchange-alt', title: 'trades', description: 'player transactions' },
		{ icon: 'fas fa-chart-line', title: 'stats', description: 'track performance' },
		{ icon: 'fas fa-trophy', title: 'tournaments', description: 'run competitions' }
	];
</script>

<section id="features" class="py-16 bg-gray-800">
	<div class="max-w-6xl mx-auto px-4">
		<h2 class="text-3xl font-bold text-white text-center mb-12">features</h2>

		<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
			{#each features as feature}
				<div class="bg-gray-900 rounded-lg p-6 border border-gray-700">
					<div class="flex items-center mb-3">
						<i class="{feature.icon} text-pink-500 text-lg mr-3"></i>
						<h3 class="text-lg font-medium text-white">{feature.title}</h3>
					</div>
					<p class="text-gray-400 text-sm">{feature.description}</p>
				</div>
			{/each}
		</div>
	</div>
</section>
