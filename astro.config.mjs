import { defineConfig } from 'astro/config';
import react from '@astrojs/react';

export default defineConfig({
  site: process.env.PUBLIC_SITE_URL || 'https://yunhetech.net',
  base: '/',
  output: 'static',
  integrations: [react()],
});
