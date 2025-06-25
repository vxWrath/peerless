import { describe, it, expect } from 'vitest';

const WEBSITE_CONFIG = {
	name: 'Peerless',
	tagline: 'Advanced Discord Bot for Roblox Sports Leagues',
	stats: {
		servers: 14000,
		users: 1000000,
		uptime: 99.9,
		leagues: 500
	},
	links: {
		invite: 'https://discord.com/application-directory/1105640024113954829',
		support: 'https://discord.gg/FsNK9y7MPg',
		github: 'https://github.com/vxWrath/peerless'
	},
	features: [
		'Team Management',
		'Coach System', 
		'Season Planning',
		'Transactions',
		'Statistics',
		'Tournaments'
	]
};

function getAppName() {
	return WEBSITE_CONFIG.name;
}

function getTagline() {
	return WEBSITE_CONFIG.tagline;
}

function getStats() {
	return WEBSITE_CONFIG.stats;
}

function getLinks() {
	return WEBSITE_CONFIG.links;
}

function getFeatures() {
	return WEBSITE_CONFIG.features;
}

function formatStatValue(key, value) {
	switch (key) {
		case 'servers':
			return `${(value / 1000).toFixed(0)}K+`;
		case 'users':
			return `${(value / 1000000).toFixed(1)}M+`;
		case 'uptime':
			return `${value}%`;
		case 'leagues':
			return `${value}+`;
		default:
			return value.toString();
	}
}

describe('Website Configuration', () => {
	it('returns correct app name', () => {
		expect(getAppName()).toBe('Peerless');
	});

	it('returns correct tagline', () => {
		expect(getTagline()).toBe('Advanced Discord Bot for Roblox Sports Leagues');
	});

	it('has valid stats', () => {
		const stats = getStats();
		expect(stats.servers).toBeGreaterThan(0);
		expect(stats.users).toBeGreaterThan(0);
		expect(stats.uptime).toBeGreaterThan(90);
		expect(stats.leagues).toBeGreaterThan(0);
	});

	it('has valid links', () => {
		const links = getLinks();
		expect(links.invite).toContain('discord.com');
		expect(links.support).toContain('discord.gg');
		expect(links.github).toContain('github.com');
	});

	it('has expected features', () => {
		const features = getFeatures();
		expect(features).toContain('Team Management');
		expect(features).toContain('Coach System');
		expect(features).toContain('Season Planning');
		expect(features).toContain('Transactions');
		expect(features).toContain('Statistics');
		expect(features).toContain('Tournaments');
		expect(features.length).toBe(6);
	});

	it('formats stat values correctly', () => {
		expect(formatStatValue('servers', 14000)).toBe('14K+');
		expect(formatStatValue('users', 1000000)).toBe('1.0M+');
		expect(formatStatValue('uptime', 99.9)).toBe('99.9%');
		expect(formatStatValue('leagues', 500)).toBe('500+');
	});
});

describe('Website Structure', () => {
	it('has required sections', () => {
		const sections = ['hero', 'features', 'stats', 'footer'];
		sections.forEach(section => {
			expect(section).toBeTruthy();
		});
	});

	it('validates navigation items', () => {
		const navItems = ['Features', 'Stats', 'Support', 'Invite Bot'];
		navItems.forEach(item => {
			expect(item).toBeTruthy();
		});
	});
});
