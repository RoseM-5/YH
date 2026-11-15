import { readdir, readFile, writeFile } from 'node:fs/promises';
import { join, extname } from 'node:path';
import { fileURLToPath } from 'node:url';

const outputDir = fileURLToPath(new URL('../dist/', import.meta.url));
const base = '/YH';
const textExtensions = new Set(['.html', '.js', '.css', '.json', '.xml', '.webmanifest']);
const rootPath = /(^|[\s"'`(=,:])\/(media|products|solutions|news|about|contact|_astro)(?=\/)/gm;
let updatedFiles = 0;

async function visit(directory) {
  for (const entry of await readdir(directory, { withFileTypes: true })) {
    const location = join(directory, entry.name);
    if (entry.isDirectory()) {
      await visit(location);
      continue;
    }
    if (!textExtensions.has(extname(entry.name))) continue;

    const original = await readFile(location, 'utf8');
    const changed = original
      .replace(rootPath, (_, boundary, segment) => `${boundary}${base}/${segment}`)
      .replaceAll('href="/"', `href="${base}/"`)
      .replaceAll("href='/'", `href='${base}/'`);

    if (rootPath.test(changed) || changed.includes('href="/"') || changed.includes("href='/'")) {
      throw new Error(`Unprefixed local URL remains in ${location}`);
    }
    rootPath.lastIndex = 0;
    if (changed === original) continue;
    await writeFile(location, changed);
    updatedFiles += 1;
  }
}

await visit(outputDir);
console.log(`Prefixed local URLs with ${base}/ in ${updatedFiles} built files.`);
