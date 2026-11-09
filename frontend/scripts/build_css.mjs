import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";
import { compile } from "tailwindcss";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const rootDir = path.resolve(__dirname, "..");

// Scan all source files in app and components
function getAllFiles(dir, exts = [".tsx", ".ts", ".jsx", ".js"]) {
  let files = [];
  if (!fs.existsSync(dir)) return files;
  for (const item of fs.readdirSync(dir, { withFileTypes: true })) {
    const full = path.join(dir, item.name);
    if (item.isDirectory()) {
      if (item.name !== "node_modules" && item.name !== ".next") {
        files = files.concat(getAllFiles(full, exts));
      }
    } else if (exts.includes(path.extname(item.name))) {
      files.push(full);
    }
  }
  return files;
}

const sourceFiles = [
  ...getAllFiles(path.join(rootDir, "app")),
  ...getAllFiles(path.join(rootDir, "components")),
];

console.log(`Found ${sourceFiles.length} template source files to scan.`);

// Extract all candidate class strings from source files
const candidateSet = new Set();
const classRegex = /(?:className|class)\s*=\s*["'`]([^"'`]+)["'`]/g;
const templateRegex = /(?:className|class)\s*=\s*\{`([^`]+)`\}/g;
const stringRegex = /["'`]([a-zA-Z0-9_\-\/:\.\[\]#%]+)["'`]/g;

for (const file of sourceFiles) {
  const content = fs.readFileSync(file, "utf8");
  let match;
  while ((match = classRegex.exec(content)) !== null) {
    match[1].split(/\s+/).forEach((c) => c && candidateSet.add(c.trim()));
  }
  while ((match = templateRegex.exec(content)) !== null) {
    match[1].split(/\s+/).forEach((c) => c && candidateSet.add(c.trim()));
  }
  // Also collect common tailwind tokens
  const words = content.match(/[a-zA-Z0-9_\-\/:\.\[\]#%]+/g) || [];
  for (const w of words) {
    if (w.includes("-") || w.includes(":") || w.startsWith("p") || w.startsWith("m") || w.startsWith("text") || w.startsWith("bg") || w.startsWith("flex") || w.startsWith("grid") || w.startsWith("rounded") || w.startsWith("border")) {
      candidateSet.add(w.trim());
    }
  }
}

const candidates = Array.from(candidateSet);
console.log(`Extracted ${candidates.length} potential class candidates.`);

const cssInput = fs.readFileSync(path.join(rootDir, "styles", "globals.css"), "utf8");

const compiler = await compile(cssInput, {
  base: path.join(rootDir, "styles"),
  loadStylesheet: async (id, base) => {
    if (id === "tailwindcss") {
      const p = path.resolve(rootDir, "node_modules", "tailwindcss", "index.css");
      return { content: fs.readFileSync(p, "utf8"), base: path.dirname(p) };
    }
    const full = path.resolve(base, id);
    if (fs.existsSync(full)) {
      return { content: fs.readFileSync(full, "utf8"), base: path.dirname(full) };
    }
    const nm = path.resolve(rootDir, "node_modules", id);
    if (fs.existsSync(nm)) {
      return { content: fs.readFileSync(nm, "utf8"), base: path.dirname(nm) };
    }
    throw new Error(`Cannot resolve stylesheet: ${id}`);
  },
});

const compiledCss = compiler.build(candidates);
const outPath = path.join(rootDir, "styles", "compiled.css");
fs.writeFileSync(outPath, compiledCss);
console.log(`[SUCCESS] Compiled CSS written to ${outPath} (${compiledCss.length} bytes / ${(compiledCss.length / 1024).toFixed(1)} KB)`);
