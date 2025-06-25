import { describe, it, expect } from 'vitest';

const APP_CONFIG = {
	name: 'Peerless',
	version: '0.0.1',
	description: 'Advanced Discord Bot for Roblox Sports Leagues',
	features: ['teams', 'coaches', 'seasons', 'transactions']
};

function getAppName() {
	return APP_CONFIG.name;
}

function getVersion() {
	return APP_CONFIG.version;
}

function hasFeature(feature) {
	return APP_CONFIG.features.includes(feature);
}

describe('Application Configuration', () => {
	it('returns correct app name', () => {
		expect(getAppName()).toBe('Peerless');
	});

	it('returns correct version', () => {
		expect(getVersion()).toBe('0.0.1');
	});

	it('checks features correctly', () => {
		expect(hasFeature('teams')).toBe(true);
		expect(hasFeature('coaches')).toBe(true);
		expect(hasFeature('nonexistent')).toBe(false);
	});

	it('has all expected features', () => {
		const expectedFeatures = ['teams', 'coaches', 'seasons', 'transactions'];
		expectedFeatures.forEach(feature => {
			expect(hasFeature(feature)).toBe(true);
		});
	});
});
