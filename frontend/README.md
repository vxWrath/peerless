# Peerless Website

Official website for Peerless Discord bot.

## Tech Stack

- SvelteKit 2.0
- TailwindCSS 4.0
- Font Awesome
- Vitest
- Vite

## Development

### Prerequisites

- Node.js 18+
- npm

### Getting Started

1. Quick setup:
   ```bash
   ./setup.sh
   ```

2. Manual setup:
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

3. Open `http://localhost:5173`

### Scripts

- `npm run dev` - dev server
- `npm run build` - build for production
- `npm run preview` - preview build
- `npm test` - run tests
- `npm run test:watch` - watch tests

### Structure

```
frontend/
├── src/
│   ├── lib/
│   │   ├── components/
│   │   ├── stores/
│   │   └── __tests__/
│   ├── routes/
│   ├── app.css
│   └── app.html
├── static/
└── package.json
```

## Features

- Discord OAuth authentication
- Guild settings management
- Responsive design
- Modern animations
- SEO optimized

## Testing

```bash
npm test
npm run test:watch
```

## Deployment

```bash
npm run build
npm run preview
```
