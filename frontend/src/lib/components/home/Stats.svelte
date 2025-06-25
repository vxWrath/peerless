<script lang="ts">
	const stats = [
		{ value: '14k+', label: 'servers' },
		{ value: '1m+', label: 'users' },
		{ value: '99.9%', label: 'uptime' },
		{ value: '500+', label: 'leagues' }
	];
</script>

<section id="stats" class="py-16 bg-gray-800">
	<div class="max-w-6xl mx-auto px-4">
		<h2 class="text-3xl font-bold text-white text-center mb-12">trusted by</h2>

		<div class="grid grid-cols-2 md:grid-cols-4 gap-8 mb-12">
			{#each stats as stat}
				<div class="text-center">
					<div class="text-2xl font-bold text-pink-500 mb-1">{stat.value}</div>
					<div class="text-gray-400 text-sm">{stat.label}</div>
				</div>
			{/each}
		</div>

		<div class="text-center">
			<div class="bg-gray-900 rounded-lg p-6 border border-gray-700 max-w-2xl mx-auto">
				<h3 class="text-xl font-bold text-white mb-3">ready to start?</h3>
				<div class="flex gap-4 justify-center">
					<a href="https://discord.com/application-directory/1105640024113954829"
					   class="bg-pink-600 hover:bg-pink-700 text-white px-6 py-3 rounded font-medium">
						invite bot
					</a>
					<a href="https://discord.gg/FsNK9y7MPg"
					   class="border border-gray-600 hover:border-gray-400 text-white px-6 py-3 rounded font-medium">
						support
					</a>
				</div>
			</div>
		</div>
	</div>
</section>
