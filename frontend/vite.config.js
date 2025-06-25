import devtoolsJson from 'vite-plugin-devtools-json';
import { sveltekit } from '@sveltejs/kit/vite';
import { defineConfig } from 'vite';
import tailwindcss from '@tailwindcss/vite';

export default defineConfig({
	plugins: [sveltekit(), devtoolsJson(), tailwindcss()],
	server: {
		host: true,
		strictPort: true,
		watch: {
			usePolling: true,
		},
		proxy: {
			'/account': {
				target: 'http://api:8000',
				changeOrigin: true,
			},
		},
	},
});
