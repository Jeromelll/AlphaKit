// Check the hosted mirror's fresh-data and unavailable-source behavior in isolated contexts.
const {chromium}=require('playwright');
const fs=require('node:fs');
const path=require('node:path');
const assert=require('node:assert/strict');
const root=path.resolve(__dirname,'../dist');
const bundled=JSON.parse(fs.readFileSync(path.join(root,'data/catalog.json'),'utf8'));
const fresh=structuredClone(bundled);
fresh.skills.push({...fresh.skills[0],id:'qa-fresh-remote-entry',name:'远程新增条目',nameEn:'Fresh remote entry'});
const mirror='https://finskills-hub.fit-lemon-8083.chatgpt.site';
const canonical='https://raw.githubusercontent.com/Jeromelll/AlphaKit/main/dist/';

(async()=>{
  const options={headless:true};
  const mac='/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
  if(process.env.BROWSER_EXECUTABLE_PATH)options.executablePath=process.env.BROWSER_EXECUTABLE_PATH;
  else if(process.platform==='darwin'&&fs.existsSync(mac))options.executablePath=mac;
  const browser=await chromium.launch(options);
  try{
    const checks=[];
    for(const available of [true,false]){
      const context=await browser.newContext();
      const requests=[];
      await context.route(mirror+'/**',async route=>{
        const url=new URL(route.request().url());
        const relative=url.pathname==='/'?'index.html':url.pathname.slice(1);
        if(!['index.html','app.js','styles.css','favicon.svg','data/catalog.json'].includes(relative))return route.abort();
        const types={'index.html':'text/html','app.js':'text/javascript','styles.css':'text/css','favicon.svg':'image/svg+xml','data/catalog.json':'application/json'};
        await route.fulfill({status:200,contentType:types[relative],body:fs.readFileSync(path.join(root,relative))});
      });
      await context.route(canonical+'**',async route=>{
        requests.push(new URL(route.request().url()));
        await route.fulfill({status:available?200:503,contentType:'application/json',
          headers:{'Access-Control-Allow-Origin':'*'},body:JSON.stringify(available?fresh:{})});
      });
      const page=await context.newPage();
      await page.goto(mirror+'/',{waitUntil:'networkidle'});
      const expected=available?fresh.skills.length:bundled.skills.length;
      await page.waitForFunction(n=>document.querySelectorAll('.skill-row').length===n,expected);
      assert.equal(requests.length,1);
      assert(/^\d+$/.test(requests[0].searchParams.get('v')),'Fresh canonical fetch must bypass a previous CDN cache key');
      if(available){
        assert.equal(await page.locator('[data-skill-id="qa-fresh-remote-entry"]').count(),1);
        assert(!/随站副本/.test(await page.locator('#catalog-updated').textContent()));
        checks.push('A hosted mirror displays newly published canonical entries');
      }else{
        assert(/随站副本/.test(await page.locator('#catalog-updated').textContent()));
        assert.equal(await page.locator('[data-skill-id="qa-fresh-remote-entry"]').count(),0);
        checks.push('An unavailable canonical source displays the dated bundled copy');
      }
      await context.close();
    }
    fs.mkdirSync('.site-qa',{recursive:true});
    const report={status:'passed',checks};
    fs.writeFileSync('.site-qa/mirror-report.json',JSON.stringify(report,null,2));
    console.log(JSON.stringify(report,null,2));
  }finally{await browser.close();}
})().catch(error=>{console.error(error);process.exitCode=1;});
