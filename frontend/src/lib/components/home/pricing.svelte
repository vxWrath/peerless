<script lang="ts">
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
</script>

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
