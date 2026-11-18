// News-image entry for make.fun news-image-20261118 (Node 22, stdlib
// only). The image is entry.png beside this file: a newspaper front page
// drawn by draw.py in this repository, summing up the world news of
// Wednesday 18 November 2026. The program copies it to the output
// directory as entry.png; the grader runs it twice and both runs must
// produce the same bytes, which a plain copy guarantees.
//
// Local run:  mkdir -p out && MAKEFUN_OUTPUT_DIR=out node main.ts

import { copyFileSync } from "node:fs";
import { join } from "node:path";

const outDir = process.env.MAKEFUN_OUTPUT_DIR ?? "/output";
const src = new URL("./entry.png", import.meta.url);
copyFileSync(src, join(outDir, "entry.png"));
console.log("entry.png copied to", join(outDir, "entry.png"));
