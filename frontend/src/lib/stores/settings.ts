import { writable } from 'svelte/store';

export interface Setting {
	name: string;
	key: string;
	default_value: any;
	type: string;
	description: string;
	required: boolean;
	icon?: string;
	minimum?: number;
	maximum?: number;
	options?: Array<{
		name: string;
		description: string;
		icon?: string;
	}>;
}

export interface SettingCategory {
	name: string;
	key: string;
	description: string;
	settings: Setting[];
}

export const settingsConfig = writable<SettingCategory[]>([]);
export const guildSettings = writable<Record<string, any>>({});
export const selectedGuild = writable<string | null>(null);

export async function loadSettingsConfig() {
	try {
		const response = await fetch('https://gist.githubusercontent.com/vxWrath/ace3c7965a881627ae9f91e08ec49dde/raw/43b7e651fedbeadc9b15bf992e5e0bda6a259e9d/settings.json');
		const config = await response.json();
		settingsConfig.set(config);
		return config;
	} catch (error) {
		console.error('Failed to load settings config:', error);
		return [];
	}
}

export async function loadGuildSettings(guildId: string) {
	try {
		const response = await fetch(`/api/guilds/${guildId}/settings`);
		if (response.ok) {
			const settings = await response.json();
			guildSettings.set(settings);
			return settings;
		}
	} catch (error) {
		console.error('Failed to load guild settings:', error);
	}
	return {};
}

export async function saveGuildSetting(guildId: string, key: string, value: any) {
	try {
		const response = await fetch(`/api/guilds/${guildId}/settings`, {
			method: 'PATCH',
			headers: {
				'Content-Type': 'application/json',
			},
			body: JSON.stringify({ [key]: value }),
		});
		
		if (response.ok) {
			guildSettings.update(settings => ({
				...settings,
				[key]: value
			}));
			return true;
		}
	} catch (error) {
		console.error('Failed to save setting:', error);
	}
	return false;
}
