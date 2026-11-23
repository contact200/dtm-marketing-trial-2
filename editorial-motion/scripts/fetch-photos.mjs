import fs from 'node:fs/promises';
import path from 'node:path';
const basedir=process.cwd();
const src=JSON.parse(await fs.readFile(path.join(basedir,'photo-sources.json'),'utf8'));
const outDir=path.join(basedir,'public','photos');
await fs.mkdir(outDir,{recursive:true});
const success=[];
for(let i=0;i<src.photos.length;i++){
  const target=path.join(outDir,String(i+1).padStart(2,'0')+'.jpg');
  try{
    const r=await fetch(src.photos[i],{headers:{'User-Agent':'Mozilla/5.0 (compatible; DateTheMomentRender/1.0)'},signal:AbortSignal.timeout(45000)});
    if(!r.ok)throw Error('HTTP '+r.status);
    const bytes=Buffer.from(await r.arrayBuffer());
    if(bytes.length<2000)throw Error('Image unexpectedly small');
    await fs.writeFile(target,bytes);
    success.push(target);
    console.log('Image',i+1,'fetched,',bytes.length,'bytes');
  }catch(err){
    console.warn('Image',i+1,'download failed:',String(err));
  }
}
if(success.length<4)throw Error('Not enough DateTheMoment source photos downloaded to render safely ('+success.length+'/10)');
for(let i=0;i<src.photos.length;i++){
  const target=path.join(outDir,String(i+1).padStart(2,'0')+'.jpg');
  try{await fs.access(target)}catch{await fs.copyFile(success[i%success.length],target)}
}
console.log('Photo set ready:',src.photos.length);
