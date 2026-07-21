#!/usr/bin/env node
/* Export every build as a standalone SVG. PNG/GIF conversion is performed by
   export_frames.sh so the editable SVG remains the source asset. */
const fs=require('fs');
const path=require('path');
const {sequences,renderers}=require('./app.js');
const out=path.join(__dirname,'exports');
fs.mkdirSync(out,{recursive:true});
const realAnchorPath=path.join(__dirname,'../../claude-design-package/figures/eavail_marginal_vs_paper_pull_full.png');
const realAnchorData=`data:image/png;base64,${fs.readFileSync(realAnchorPath).toString('base64')}`;

const escapeXml=s=>s.replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;');
for(let i=0;i<sequences.length;i++){
  const seq=sequences[i];
  const dir=path.join(out,`${String(i+1).padStart(2,'0')}-${seq.key}`);
  fs.mkdirSync(dir,{recursive:true});
  for(let step=0;step<seq.steps;step++){
    let body=renderers[seq.key](step);
    // The browser can load the real-result PNG by relative path. Standalone
    // SVG rasterizers are less consistent, so embed it for exported frames.
    body=body.replace('../../claude-design-package/figures/eavail_marginal_vs_paper_pull_full.png',realAnchorData);
    const svg=`<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="1440" height="810" viewBox="0 0 1440 810">
<rect width="1440" height="810" fill="#fffefa"/>
<style>text{font-family:Arial,Helvetica,sans-serif}</style>
${body}
</svg>\n`;
    fs.writeFileSync(path.join(dir,`build-${String(step+1).padStart(2,'0')}.svg`),svg);
  }
  fs.writeFileSync(path.join(dir,'speaker-notes.txt'),seq.builds.map((b,j)=>
    `BUILD ${j+1}\nSpeaker move: ${b[0]}\nPurpose: ${b[1]}\n`).join('\n'));
}
console.log(`Exported ${sequences.reduce((n,s)=>n+s.steps,0)} SVG builds to ${out}`);
