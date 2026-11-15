import { defineConfig } from 'astro/config';
import react from '@astrojs/react';

const githubPages = process.env.GITHUB_PAGES === '1';

export default defineConfig({
  site: githubPages ? 'https://rosem-5.github.io' : process.env.PUBLIC_SITE_URL || undefined,
  base: githubPages ? '/YH/' : '/',
  output: 'static',
  integrations: [react()],
});
