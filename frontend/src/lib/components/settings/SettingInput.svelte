<script lang="ts">
	import type { Setting } from '$lib/stores/settings';

	interface Props {
		setting: Setting;
		value: any;
		onSave: (value: any) => Promise<boolean>;
		saving: boolean;
	}

	let { setting, value, onSave, saving }: Props = $props();

	let currentValue = $state(value);
	let originalValue = $state(value);
	let hasChanges = $state(false);
	let saveStatus = $state<'idle' | 'saving' | 'success' | 'error'>('idle');

	$effect(() => {
		currentValue = value;
		originalValue = value;
		hasChanges = false;
		saveStatus = 'idle';
	});

	function handleChange(newValue: any) {
		currentValue = newValue;
		hasChanges = JSON.stringify(newValue) !== JSON.stringify(originalValue);
		saveStatus = 'idle';
	}

	async function save() {
		saveStatus = 'saving';
		const success = await onSave(currentValue);
		if (success) {
			originalValue = currentValue;
			hasChanges = false;
			saveStatus = 'success';
			setTimeout(() => saveStatus = 'idle', 2000);
		} else {
			saveStatus = 'error';
			setTimeout(() => saveStatus = 'idle', 3000);
		}
	}

	function revert() {
		currentValue = originalValue;
		hasChanges = false;
		saveStatus = 'idle';
	}
</script>

<div class="space-y-3">
	{#if setting.type === 'status'}
		<div class="flex items-center justify-between">
			<label class="flex items-center cursor-pointer">
				<input type="checkbox" 
					   checked={currentValue} 
					   onchange={(e) => handleChange(e.target.checked)}
					   class="sr-only">
				<div class="relative">
					<div class="w-10 h-6 bg-gray-600 rounded-full shadow-inner transition-colors duration-300 {currentValue ? 'bg-pink-600' : ''}"></div>
					<div class="absolute w-4 h-4 bg-white rounded-full shadow top-1 transition-transform duration-300 {currentValue ? 'translate-x-5' : 'translate-x-1'}"></div>
				</div>
				<span class="ml-3 text-white">{currentValue ? 'Enabled' : 'Disabled'}</span>
			</label>
		</div>
	{:else if setting.type === 'number' || setting.type === 'day'}
		<div class="flex items-center space-x-3">
			<input type="number" 
				   bind:value={currentValue}
				   min={setting.minimum}
				   max={setting.maximum}
				   onchange={() => handleChange(currentValue)}
				   class="bg-gray-700 border border-gray-600 rounded-md px-3 py-2 text-white focus:outline-none focus:ring-2 focus:ring-pink-500 focus:border-transparent">
			{#if setting.type === 'day'}
				<span class="text-gray-400">{currentValue === 1 ? 'day' : 'days'}</span>
			{/if}
		</div>
	{:else if setting.type === 'option'}
		<select bind:value={currentValue} 
				onchange={() => handleChange(currentValue)}
				class="bg-gray-700 border border-gray-600 rounded-md px-3 py-2 text-white focus:outline-none focus:ring-2 focus:ring-pink-500 focus:border-transparent">
			{#each setting.options || [] as option, index}
				<option value={index}>{option.name}</option>
			{/each}
		</select>
		{#if setting.options && setting.options[currentValue]}
			<p class="text-sm text-gray-400 mt-1">{setting.options[currentValue].description}</p>
		{/if}
	{:else if setting.type === 'channel'}
		<div class="flex items-center space-x-3">
			<input type="text" 
				   bind:value={currentValue}
				   placeholder="Channel ID or #channel-name"
				   onchange={() => handleChange(currentValue)}
				   class="flex-1 bg-gray-700 border border-gray-600 rounded-md px-3 py-2 text-white focus:outline-none focus:ring-2 focus:ring-pink-500 focus:border-transparent">
			<i class="fas fa-hashtag text-gray-400"></i>
		</div>
	{:else if setting.type === 'role'}
		<div class="flex items-center space-x-3">
			<input type="text" 
				   bind:value={currentValue}
				   placeholder="Role ID or @role-name"
				   onchange={() => handleChange(currentValue)}
				   class="flex-1 bg-gray-700 border border-gray-600 rounded-md px-3 py-2 text-white focus:outline-none focus:ring-2 focus:ring-pink-500 focus:border-transparent">
			<i class="fas fa-at text-gray-400"></i>
		</div>
	{:else if setting.type === 'timezone'}
		<select bind:value={currentValue} 
				onchange={() => handleChange(currentValue)}
				class="bg-gray-700 border border-gray-600 rounded-md px-3 py-2 text-white focus:outline-none focus:ring-2 focus:ring-pink-500 focus:border-transparent">
			<option value="America/New_York">Eastern Time (ET)</option>
			<option value="America/Chicago">Central Time (CT)</option>
			<option value="America/Denver">Mountain Time (MT)</option>
			<option value="America/Los_Angeles">Pacific Time (PT)</option>
			<option value="Europe/London">Greenwich Mean Time (GMT)</option>
			<option value="Europe/Paris">Central European Time (CET)</option>
			<option value="Asia/Tokyo">Japan Standard Time (JST)</option>
			<option value="Australia/Sydney">Australian Eastern Time (AET)</option>
		</select>
	{:else if setting.type === 'theme'}
		<div class="grid grid-cols-2 gap-3">
			{#each [1, 2, 3, 4] as theme}
				<button onclick={() => handleChange(theme)}
						class="p-3 rounded-md border-2 transition-colors {currentValue === theme ? 'border-pink-500 bg-pink-500/10' : 'border-gray-600 hover:border-gray-500'}">
					<div class="text-white font-medium mb-1">Theme {theme}</div>
					<div class="text-sm text-gray-400">Style variant {theme}</div>
				</button>
			{/each}
		</div>
	{:else}
		<input type="text" 
			   bind:value={currentValue}
			   onchange={() => handleChange(currentValue)}
			   class="w-full bg-gray-700 border border-gray-600 rounded-md px-3 py-2 text-white focus:outline-none focus:ring-2 focus:ring-pink-500 focus:border-transparent">
	{/if}
	
	{#if hasChanges || saveStatus !== 'idle'}
		<div class="flex items-center justify-between pt-3">
			<div class="flex items-center space-x-3">
				{#if hasChanges}
					<button onclick={save}
							disabled={saveStatus === 'saving'}
							class="bg-pink-600 hover:bg-pink-700 disabled:opacity-50 text-white px-4 py-2 rounded text-sm font-medium">
						{saveStatus === 'saving' ? 'saving...' : 'save changes'}
					</button>
					<button onclick={revert}
							disabled={saveStatus === 'saving'}
							class="bg-gray-600 hover:bg-gray-700 disabled:opacity-50 text-white px-4 py-2 rounded text-sm font-medium">
						revert
					</button>
				{/if}
			</div>

			<div class="text-sm">
				{#if saveStatus === 'success'}
					<span class="text-green-400">✓ saved</span>
				{:else if saveStatus === 'error'}
					<span class="text-red-400">✗ failed to save</span>
				{/if}
			</div>
		</div>
	{/if}
</div>
