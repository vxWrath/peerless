<script lang="ts">
	const stats = [
		{ number: '14,000+', label: 'Discord Servers' },
		{ number: '1M+', label: 'Unique Users' },
		{ number: '99.9%', label: 'Uptime' }
	];
</script>

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
