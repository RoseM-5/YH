import { spawnSync } from 'node:child_process';

const python = process.platform === 'win32' ? 'python' : 'python3';
const result = spawnSync(python, ['scripts/localize_site.py'], { stdio: 'inherit' });
if (result.error) throw result.error;
process.exit(result.status ?? 1);
