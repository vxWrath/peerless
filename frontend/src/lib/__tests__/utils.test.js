import { describe, it, expect } from 'vitest';

// Frontend utility functions for testing
function add(a, b) {
	return a + b;
}

function multiply(a, b) {
	return a * b;
}

function formatMessage(name) {
	return `Hello, ${name}!`;
}

function validateEmail(email) {
	const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
	return emailRegex.test(email);
}

function capitalizeWords(str) {
	return str.replace(/\b\w/g, l => l.toUpperCase());
}

describe('Frontend Utility Functions', () => {
	it('adds two numbers correctly', () => {
		expect(add(2, 3)).toBe(5);
		expect(add(-1, 1)).toBe(0);
		expect(add(0, 0)).toBe(0);
	});

	it('multiplies two numbers correctly', () => {
		expect(multiply(2, 3)).toBe(6);
		expect(multiply(-1, 5)).toBe(-5);
		expect(multiply(0, 10)).toBe(0);
	});

	it('formats messages correctly', () => {
		expect(formatMessage('World')).toBe('Hello, World!');
		expect(formatMessage('Peerless')).toBe('Hello, Peerless!');
	});

	it('validates email addresses', () => {
		expect(validateEmail('test@example.com')).toBe(true);
		expect(validateEmail('user@domain.org')).toBe(true);
		expect(validateEmail('invalid-email')).toBe(false);
		expect(validateEmail('test@')).toBe(false);
		expect(validateEmail('@domain.com')).toBe(false);
	});

	it('capitalizes words correctly', () => {
		expect(capitalizeWords('hello world')).toBe('Hello World');
		expect(capitalizeWords('peerless discord bot')).toBe('Peerless Discord Bot');
		expect(capitalizeWords('a')).toBe('A');
	});
});
