const $ = selector => document.querySelector(selector);
const canonicalAssets = 'https://raw.githubusercontent.com/Jeromelll/AlphaKit/main/dist/';
const siteMirror = location.hostname.endsWith('.chatgpt.site');
let catalogAssets = new URL('./', location.href).href;
let usingSnapshot = false;
const messages = {
  zh: {
    brand:'AlphaKit',brandDescriptor:'投研技能库',skip:'跳到技能目录',catalogNav:'技能目录',workflowNav:'任务组合',guideNav:'使用指南',myList:'我的清单',
    heroContext:'面向金融与投研工作的 AI 技能目录',heroTitle:'把 AI 技能用进<br>你的研究工作。',
    heroDescription:'从财报拆解到模型搭建，找到有具体方法的技能。看清来源、输入与依赖，再决定怎么用。',heroCta:'查找适合的技能',
    principleSource:'原始来源可追溯',principleLicense:'开源许可可核对',principleDependencies:'环境依赖说清楚',
    sheetTitle:'一次公司研究',sheetSubtitle:'从材料到可复核的产物',sheetInputLabel:'研究输入',sheetInput:'公开披露 · 财务数据 · 研究问题',
    flowBusiness:'拆分业务',flowBusinessNote:'理解收入与利润来源',flowModel:'建立模型',flowModelNote:'把假设接进财务预测',flowVerify:'检验判断',flowVerifyNote:'核对证据与情景边界',
    sheetOutputLabel:'研究产物',sheetOutput:'模型、研究提纲与验证清单',sheetFootnote:'技能提供方法，证据与判断仍需核验。',
    workflowContext:'先从你手上的任务出发',workflowTitle:'这次研究要完成什么？',firstUse:'第一次使用技能？',
    bundleEarnings:'做好一次财报研究',bundleEarningsNote:'财报分析、预测更新、情景检验',
    bundleValuation:'搭一份可复核的模型',bundleValuationNote:'财务建模、估值方法、假设校验',
    bundlePortfolio:'检查组合与企业风险',bundlePortfolioNote:'组合敞口、经营偏离、风险信号',viewBundle:'查看这组技能',
    catalogContext:'按场景选择，按证据判断',catalogTitle:'金融投研技能目录',scenario:'工作场景',
    verifiedQuestion:'“来源核验”核验什么？',verifiedAnswer:'核对原作者仓库、技能文件和开源许可。实际执行与产物质量须在使用环境中验证。',
    standards:'查看收录标准',standardsShort:'收录标准',search:'搜索技能',searchPlaceholder:'搜索财报、DCF、信用风险或一个研究任务…',
    reset:'重置',savedOnly:'只看我的清单',sort:'排序',sortCurated:'目录顺序',sortName:'技能名称',loading:'正在载入技能目录…',
    catalogBottom:'每条技能保留原作者与许可信息。下载与安装以原仓库说明为准。',
    guideContext:'先做一个能验证的小任务',guideTitle:'把技能接进工作，<br>从一次公开材料试跑开始。',
    guideDescription:'一个好的技能应说清楚要什么、怎么做、交付什么。先确认这些，再逐步扩大使用范围。',
    guideOne:'确认输入与产物',guideOneNote:'看技能需要公告、财务报表还是模型文件，检查产物是否对应当前的研究问题。',
    guideTwo:'获取完整原始包',guideTwoNote:'打开原仓库安装说明，保留配套脚本和参考文件。需要连接器或商业数据时，按原作者要求配置。',
    guideThree:'用公开资料试跑并复核',guideThreeNote:'检查来源、时点、币种、年度口径和计算结果。把能重复完成任务的技能加入自己的清单。',
    footerNote:'为研究工作选方法，让来源与边界看得见。',githubRepo:'GitHub · 贡献技能',snapshotAt:'当前显示随站副本，来源核验于 {date}',about:'关于目录',attribution:'技能归原作者所有，遵守各自开源许可。',
    clear:'清空',compareThese:'比较这些技能',all:'全部技能',research:'公司与行业研究',earnings:'财报分析',valuation:'估值与建模',portfolio:'组合与风险',deals:'交易与尽调',operations:'研究流程',data:'金融数据',macro:'宏观与市场',quant:'量化与技术研究',fixedincome:'固收与信用',
    sourceFilter:'来源仓库',allSources:'全部来源',sourceCount:'来自 {n} 个原始仓库',browseSources:'浏览来源仓库',sourcesContext:'回到完整原作',sourcesTitle:'原始技能仓库',sourcesNote:'按原仓库获取完整技能包；每条目录介绍都保留固定版本、许可与依赖。',includedCount:'已收录 {n} 个技能',openRepository:'打开固定版本仓库',filterSource:'查看这组技能',
    results:'{n} 个技能',savedResults:'{n} 个已收藏技能',verifiedAt:'来源核验于 {date}',verified:'✓ 来源已核验',verifiedHint:'原仓库、文件路径与许可证已核对；实际执行未验证',
    viewDetail:'查看方法与依赖',save:'收藏',saved:'已收藏',removeSaved:'从清单移除',addSaved:'加入清单',compare:'比较',selected:'已选 {n} 个技能',
    emptyTitle:'没有找到匹配的技能',emptyNote:'换一个工作场景或更短的关键词，也可以清除筛选。',emptySaved:'清单里还没有匹配的技能',emptySavedNote:'点击技能旁的“收藏”，在这台浏览器中建立自己的清单。',
    clearFilters:'清除筛选',workflowActive:'任务组合：{name}',workflowEarnings:'财报研究',workflowValuation:'模型搭建',workflowPortfolio:'组合与企业风险',
    saveDone:'已加入我的清单，保存在当前浏览器',removeDone:'已从我的清单移除',saveUnavailable:'当前浏览器无法保存清单，已在本次页面中保留。',compareLimit:'最多比较三个技能，请先移除一个。',
    author:'原作者',license:'许可',verifiedDate:'来源核验',method:'它用什么方法？',inputs:'需要哪些输入',outputs:'得到什么产物',dependencies:'环境与依赖',
    execution:'执行验证',executionPending:'实际执行尚未验证。请先按原仓库说明，在你的工具与数据环境中试跑。',executionVerified:'有执行验证记录。',
    example:'从这个问题开始',boundary:'使用边界',source:'原始来源',openSkill:'打开原始技能',copyExample:'复制使用示例',addList:'加入我的清单',removeList:'移出我的清单',
    repositoryIntro:'获取配套文件与安装说明：',repository:'原作者完整仓库',copyDone:'使用示例已复制',copyFailed:'当前浏览器无法自动复制，已选中示例，可手动复制。',
    compareTitle:'比较这些技能',compareNote:'先比较输入、产物与依赖，选择适合当前任务的技能。',compareItem:'比较项',methodShort:'方法',inputsShort:'输入',outputsShort:'产物',licenseFull:'开源许可',notExecuted:'尚未执行验证',
    aboutTitle:'关于 AlphaKit',aboutOne:'AlphaKit 把公开的金融投研 AI 技能按研究任务组织，帮助使用者判断方法、输入、产物和依赖是否适合自己的工作。',
    aboutTwo:'目录由公开 GitHub 仓库持续维护。新条目经过双语内容审核、原始文件与许可证核验后发布。所有收录条目保留原作者与开源许可，不代表原作者或任何技能平台的官方认证。',
    aboutThree:'我的清单保存在当前浏览器。网站不接收研究材料，不要求填写券商、数据平台或模型服务的密钥。',
    aboutCredits:'技能来自多个原作者仓库，分别保留 MIT、Apache-2.0 等开源许可。中英文介绍、分类和示例由本目录整理，并非原作者原文。',licenseCopy:'随附的原始许可证',
    standardsTitle:'我们的收录标准',standardOne:'有具体金融或投研用途，能够说明输入、方法与产物。',standardTwo:'能回到原作者仓库与固定版本的技能文件。',
    standardThree:'核对明确的开源许可，并保留原作者归属。',standardFour:'说明实际依赖，区分用户材料、公开数据与需另配置的连接器。',standardFive:'来源核验与执行验证分别记录，未经试跑不标为“实测可用”。',
    standardsNote:'当前“来源已核验”只表示原始文件、版本和许可证已核对。请按原仓库的完整安装说明使用配套资源。',
    unavailable:'目录暂时不可用',loadError:'技能目录暂时无法载入',loadErrorNote:'请刷新页面重试，或稍后再来查看。',retry:'重新载入',close:'关闭',clearWorkflow:'取消任务组合筛选'
  },
  en: {
    brand:'AlphaKit',brandDescriptor:'Research Skills',skip:'Skip to the skill directory',catalogNav:'Directory',workflowNav:'Workflows',guideNav:'Getting started',myList:'My shortlist',
    heroContext:'AI skills for finance and investment research',heroTitle:'Put AI skills<br>to work in research.',
    heroDescription:'Find a concrete method for your next earnings review or financial model. Check the source, inputs and dependencies before you use it.',heroCta:'Find a research skill',
    principleSource:'Traceable sources',principleLicense:'Clear licenses',principleDependencies:'Explicit dependencies',
    sheetTitle:'A company research task',sheetSubtitle:'From evidence to a reviewable output',sheetInputLabel:'Research inputs',sheetInput:'Public filings, financial data, a research question',
    flowBusiness:'Understand',flowBusinessNote:'Map the business drivers',flowModel:'Model',flowModelNote:'Connect assumptions to forecasts',flowVerify:'Verify',flowVerifyNote:'Check evidence and scenarios',
    sheetOutputLabel:'Research outputs',sheetOutput:'Models, research outlines and verification lists',sheetFootnote:'Skills provide a method. Evidence and judgment need review.',
    workflowContext:'Start with the task on your desk',workflowTitle:'What are you working on?',firstUse:'New to AI skills?',
    bundleEarnings:'Review an earnings release',bundleEarningsNote:'Results analysis, forecast updates, scenarios',
    bundleValuation:'Build a reviewable model',bundleValuationNote:'Financial modeling, valuation, assumptions',
    bundlePortfolio:'Review portfolio and operating risk',bundlePortfolioNote:'Exposures, operating variances, risk signals',viewBundle:'Explore these skills',
    catalogContext:'Choose by task. Evaluate the evidence.',catalogTitle:'The finance skills directory',scenario:'Work scenario',
    verifiedQuestion:'What is source verification?',verifiedAnswer:'We check the original repository, skill file and license. Execution and output quality still need testing in your environment.',
    standards:'Our inclusion criteria',standardsShort:'Inclusion criteria',search:'Search skills',searchPlaceholder:'Search earnings, DCF, credit risk or a research task…',
    reset:'Reset',savedOnly:'My shortlist only',sort:'Sort',sortCurated:'Directory order',sortName:'Skill name',loading:'Loading the skill directory…',
    catalogBottom:'Every skill retains its original author and license. Follow the source repository for installation.',
    guideContext:'Start with a small task you can verify',guideTitle:'Bring skills into your work.<br>Try public evidence first.',
    guideDescription:'A useful skill explains its inputs, method and outputs. Check those first, then expand its role in your workflow.',
    guideOne:'Match the inputs and outputs',guideOneNote:'Check whether the skill needs filings, financial statements or a model, and whether its output answers your research question.',
    guideTwo:'Get the complete source package',guideTwoNote:'Follow the original installation instructions and retain supporting scripts and references. Configure connectors or licensed data when required.',
    guideThree:'Test with public materials and review',guideThreeNote:'Check sources, dates, currencies, fiscal periods and calculations. Shortlist skills that can repeat the task reliably.',
    footerNote:'Find a method for the task, with its source and boundaries in view.',githubRepo:'GitHub · Contribute',snapshotAt:'Bundled copy; sources checked {date}',about:'About the directory',attribution:'Skills belong to their original authors and retain their open-source licenses.',
    clear:'Clear',compareThese:'Compare selected',all:'All skills',research:'Company research',earnings:'Earnings analysis',valuation:'Valuation & models',portfolio:'Portfolio & risk',deals:'Deals & diligence',operations:'Research operations',data:'Financial data',macro:'Macro & markets',quant:'Quant & technical research',fixedincome:'Fixed income & credit',
    sourceFilter:'Source repository',allSources:'All sources',sourceCount:'From {n} original repositories',browseSources:'Browse source repositories',sourcesContext:'Get the complete original',sourcesTitle:'Original skill repositories',sourcesNote:'Use the original repository for the complete package. Each entry retains its revision, license and dependencies.',includedCount:'{n} skills included',openRepository:'Open pinned repository',filterSource:'Explore these skills',
    results:'{n} skills',savedResults:'{n} shortlisted skills',verifiedAt:'Sources checked {date}',verified:'✓ Source checked',verifiedHint:'Repository, file path and license checked. Execution has not been verified.',
    viewDetail:'Method & dependencies',save:'Save',saved:'Saved',removeSaved:'Remove from shortlist',addSaved:'Add to shortlist',compare:'Compare',selected:'{n} skills selected',
    emptyTitle:'No matching skills',emptyNote:'Try a different scenario or a shorter query, or clear the filters.',emptySaved:'No matching skills in your shortlist',emptySavedNote:'Use “Save” beside a skill to build a shortlist in this browser.',
    clearFilters:'Clear filters',workflowActive:'Workflow: {name}',workflowEarnings:'Earnings research',workflowValuation:'Financial modeling',workflowPortfolio:'Portfolio and operating risk',
    saveDone:'Added to your shortlist in this browser',removeDone:'Removed from your shortlist',saveUnavailable:'Browser storage is unavailable. Your shortlist is retained for this visit.',compareLimit:'Compare up to three skills. Remove one first.',
    author:'Author',license:'License',verifiedDate:'Source check',method:'What is the method?',inputs:'Inputs you need',outputs:'Outputs you get',dependencies:'Environment & dependencies',
    execution:'Execution check',executionPending:'Execution has not been verified. Follow the original instructions and test with your own tools and data environment.',executionVerified:'An execution verification record is available.',
    example:'Start with this task',boundary:'Scope and limits',source:'Original source',openSkill:'Open original skill',copyExample:'Copy example task',addList:'Add to shortlist',removeList:'Remove from shortlist',
    repositoryIntro:'Supporting files and installation instructions: ',repository:'Complete original repository',copyDone:'Example task copied',copyFailed:'Automatic copy is unavailable. The example is selected for manual copying.',
    compareTitle:'Compare these skills',compareNote:'Compare inputs, outputs and dependencies to choose a skill for the task.',compareItem:'Compare',methodShort:'Method',inputsShort:'Inputs',outputsShort:'Outputs',licenseFull:'Open-source license',notExecuted:'Not execution-verified',
    aboutTitle:'About AlphaKit',aboutOne:'AlphaKit organizes public finance and research AI skills around working tasks, helping you evaluate methods, inputs, outputs and dependencies.',
    aboutTwo:'The directory is maintained in a public GitHub repository. New entries pass bilingual content review and original-file and license checks before publication. Entries retain the original author and license. Inclusion is not an official endorsement by an author or a skill platform.',
    aboutThree:'Your shortlist stays in this browser. This site does not receive research materials or request broker, data-platform or model-service keys.',
    aboutCredits:'Skills come from several original repositories and retain their MIT, Apache-2.0 or other stated licenses. Bilingual descriptions, categories and examples are edited by this directory and are not verbatim author text.',licenseCopy:'Included original licenses',
    standardsTitle:'Our inclusion criteria',standardOne:'A specific finance or research use case with clear inputs, method and outputs.',standardTwo:'Traceable to an original repository and a skill file at a fixed revision.',
    standardThree:'An explicit open-source license and retained author attribution.',standardFour:'Dependencies distinguish user materials, public data and connectors that need configuration.',standardFive:'Source and execution checks are recorded separately. Unexecuted skills are not labeled tested.',
    standardsNote:'“Source checked” means the original file, revision and license were checked. Use supporting resources as instructed by the original repository.',
    unavailable:'Directory unavailable',loadError:'The skill directory could not be loaded',loadErrorNote:'Refresh to try again, or return later.',retry:'Reload directory',close:'Close',clearWorkflow:'Clear workflow filter'
  }
};
const categoryDefs = [
  {id:'all',symbol:'⌘'},{id:'research',symbol:'⌕'},{id:'earnings',symbol:'≋'},
  {id:'valuation',symbol:'ƒ'},{id:'portfolio',symbol:'⊞'},{id:'deals',symbol:'◇'},{id:'operations',symbol:'▤'},
  {id:'data',symbol:'▦'},{id:'macro',symbol:'◎'},{id:'quant',symbol:'∑'},{id:'fixedincome',symbol:'⇌'}
];
const workflows = {
  earnings:{label:'workflowEarnings',categories:['earnings','research','valuation']},
  valuation:{label:'workflowValuation',categories:['valuation','earnings']},
  portfolio:{label:'workflowPortfolio',categories:['portfolio']}
};
const params = new URLSearchParams(location.search);
let language = params.get('lang') === 'en' ? 'en' : 'zh';
if(!params.has('lang')){try{language = localStorage.getItem('finskills:language') === 'en' ? 'en' : 'zh';}catch{}}
const state = {q:params.get('q')||'',category:params.get('category')||'all',repository:params.get('repo')||'all',workflow:params.get('workflow')||'',savedOnly:params.get('saved')==='1',sort:'curated',compare:[]};
if(!categoryDefs.some(c=>c.id===state.category))state.category='all';
if(!workflows[state.workflow])state.workflow='';
let catalog=null,skills=[],currentDetail=null,toastTimer=null,saved=new Set(),infoMode='standards';
try{const value=JSON.parse(localStorage.getItem('finskills:saved:v1')||'[]');if(Array.isArray(value))saved=new Set(value.filter(v=>typeof v==='string'));}catch{}
const esc = value => String(value??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const t = (key,variables={}) => Object.entries(variables).reduce((text,[name,value])=>text.replaceAll('{'+name+'}',String(value)),messages[language][key]||key);
const field = (skill,key) => language==='en' && skill[key+'En']!==undefined ? skill[key+'En'] : skill[key];
const listHTML = values => '<ul>'+(values||[]).map(value=>'<li>'+esc(value)+'</li>').join('')+'</ul>';
const iconBookmark = '<svg viewBox="0 0 14 18" aria-hidden="true"><path d="M2 2h10v14l-5-3-5 3Z" fill="none" stroke="currentColor" stroke-width="1.3"/></svg>';
function sourceLink(value){try{const url=new URL(value);return url.protocol==='https:'&&url.hostname==='github.com'?url.href:'#';}catch{return '#';}}
function notify(message){clearTimeout(toastTimer);$('#toast').textContent=message;$('#toast').hidden=false;toastTimer=setTimeout(()=>$('#toast').hidden=true,2500);}
function persistSaved(){try{localStorage.setItem('finskills:saved:v1',JSON.stringify([...saved]));}catch{notify(t('saveUnavailable'));}}
function syncURL(){const p=new URLSearchParams();if(language==='en')p.set('lang','en');if(state.q)p.set('q',state.q);if(state.category!=='all')p.set('category',state.category);if(state.repository!=='all')p.set('repo',state.repository);if(state.workflow)p.set('workflow',state.workflow);if(state.savedOnly)p.set('saved','1');history.replaceState(null,'',location.pathname+(p.size?'?'+p.toString():'')+location.hash);}
function applyLanguage(){
  document.documentElement.lang=language==='en'?'en':'zh-CN';
  document.title=language==='en'?'AlphaKit — Finance & Investment Research Skills':'AlphaKit · 投研技能库';
  document.querySelectorAll('[data-i18n]').forEach(element=>element.textContent=t(element.dataset.i18n));
  document.querySelectorAll('[data-i18n-html]').forEach(element=>element.innerHTML=t(element.dataset.i18nHtml));
  document.querySelectorAll('.dialog-close').forEach(element=>element.setAttribute('aria-label',t('close')));
  $('#search').placeholder=t('searchPlaceholder');$('#language-toggle').textContent=language==='en'?'中文':'EN';
  $('#language-toggle').setAttribute('aria-label',language==='en'?'Switch to Chinese':'切换到英文');
  $('#clear-workflow').setAttribute('aria-label',t('clearWorkflow'));
  if(catalog)$('#catalog-updated').textContent=t(usingSnapshot?'snapshotAt':'verifiedAt',{date:catalog.updatedAt});
}
function searchText(skill){
  const values=['name','nameEn','originalName','summary','summaryEn','method','methodEn','author','repository'].map(k=>skill[k]||'');
  for(const key of ['tags','tagsEn','inputs','inputsEn','outputs','outputsEn','dependencies','dependenciesEn'])values.push(...(skill[key]||[]));
  values.push(messages.zh[skill.category],messages.en[skill.category]);return values.join(' ').toLocaleLowerCase();
}
function filteredSkills(){
  let rows=skills.filter(s=>(state.category==='all'||s.category===state.category)&&(state.repository==='all'||s.repository===state.repository)&&(!state.workflow||workflows[state.workflow].categories.includes(s.category))&&(!state.savedOnly||saved.has(s.id)));
  const terms=state.q.toLocaleLowerCase().trim().split(/\s+/).filter(Boolean);
  if(terms.length)rows=rows.filter(s=>terms.every(term=>searchText(s).includes(term)));
  if(state.sort==='name')rows.sort((a,b)=>field(a,'name').localeCompare(field(b,'name'),language==='en'?'en':'zh-CN'));
  if(state.sort==='category')rows.sort((a,b)=>categoryDefs.findIndex(c=>c.id===a.category)-categoryDefs.findIndex(c=>c.id===b.category));
  return rows;
}
function renderCategories(){
  $('#categories').innerHTML=categoryDefs.filter(c=>c.id==='all'||skills.some(s=>s.category===c.id)).map(c=>'<button class="category-button'+(c.id===state.category?' active':'')+'" data-category="'+c.id+'" type="button" aria-pressed="'+(c.id===state.category)+'"><span class="category-symbol" aria-hidden="true">'+esc(c.symbol)+'</span><span>'+esc(t(c.id))+'</span><span class="category-count">'+(c.id==='all'?skills.length:skills.filter(s=>s.category===c.id).length)+'</span></button>').join('');
}
function sourceGroups(){
  return [...new Set(skills.map(s=>s.repository))].map(repository=>{
    const first=skills.find(s=>s.repository===repository),source=(catalog.sources||[]).find(s=>s.repository===repository)||{};
    return {...source,repository,commit:source.commit||first.commit,license:source.license||first.license,count:skills.filter(s=>s.repository===repository).length};
  });
}
function renderSources(){
  const sources=sourceGroups();
  $('#source-filter').innerHTML='<option value="all">'+esc(t('allSources'))+'</option>'+sources.map(s=>'<option value="'+esc(s.repository)+'">'+esc(s.repository.replace('https://github.com/',''))+' ('+s.count+')</option>').join('');
  $('#source-filter').value=state.repository;$('#source-summary').textContent=t('sourceCount',{n:sources.length});
  $('#source-list').innerHTML=sources.map(s=>'<article class="source-card"><p class="source-license">'+esc(s.license)+'</p><h3>'+esc(s.repository.replace('https://github.com/',''))+'</h3><p>'+esc(field(s,'description')||'')+'</p><div class="source-card-bottom"><span>'+esc(t('includedCount',{n:s.count}))+'</span><button class="text-link" type="button" data-repository="'+esc(s.repository)+'">'+esc(t('filterSource'))+'</button></div><a class="source-repository-link" href="'+sourceLink(s.repository+'/tree/'+s.commit)+'" target="_blank" rel="noopener noreferrer">'+esc(t('openRepository'))+' ↗</a></article>').join('');
}
function skillRow(s){
  const glyph=categoryDefs.find(c=>c.id===s.category)?.symbol||'研',name=field(s,'name');
  const badge=s.sourceVerified?'<span class="verified-badge" title="'+esc(t('verifiedHint'))+'">'+esc(t('verified'))+'</span>':'';
  return '<article class="skill-row" data-skill-id="'+esc(s.id)+'">'+
    '<span class="skill-tile category-'+esc(s.category)+'" aria-hidden="true">'+esc(glyph)+'</span><div class="skill-content">'+
    '<div class="skill-title-line"><button class="skill-title" data-open="'+esc(s.id)+'" type="button">'+esc(name)+'</button>'+badge+'</div>'+
    '<p class="skill-original-name">'+esc(s.originalName)+'</p><p class="skill-summary">'+esc(field(s,'summary'))+'</p>'+
    '<div class="skill-tags">'+(field(s,'tags')||[]).slice(0,4).map(tag=>'<span class="tag">'+esc(tag)+'</span>').join('')+'</div>'+
    '<div class="skill-meta"><span>'+esc(s.author)+'</span><span class="license">'+esc(s.license)+'</span></div></div>'+
    '<div class="skill-actions"><button class="button" data-open="'+esc(s.id)+'" type="button">'+esc(t('viewDetail'))+'</button><div class="skill-sub-actions">'+
    '<button class="save-button" data-save="'+esc(s.id)+'" type="button" aria-pressed="'+saved.has(s.id)+'" aria-label="'+esc(t(saved.has(s.id)?'removeSaved':'addSaved')+': '+name)+'">'+iconBookmark+esc(t(saved.has(s.id)?'saved':'save'))+'</button>'+
    '<button class="compare-button" data-compare="'+esc(s.id)+'" type="button" aria-pressed="'+state.compare.includes(s.id)+'" aria-label="'+esc(t('compare')+': '+name)+'"><span class="compare-symbol">'+(state.compare.includes(s.id)?'✓':'')+'</span>'+esc(t('compare'))+'</button></div></div></article>';
}
function render(){
  renderCategories();renderSources();const rows=filteredSkills();$('#result-count').textContent=t(state.savedOnly?'savedResults':'results',{n:rows.length});
  $('#saved-count').textContent=String(skills.filter(s=>saved.has(s.id)).length);$('#saved-filter').setAttribute('aria-pressed',String(state.savedOnly));
  $('#skills-list').innerHTML=rows.length?rows.map(skillRow).join(''):'<div class="empty-state"><h3>'+esc(t(state.savedOnly?'emptySaved':'emptyTitle'))+'</h3><p>'+esc(t(state.savedOnly?'emptySavedNote':'emptyNote'))+'</p><button class="button button-quiet" type="button" data-reset>'+esc(t('clearFilters'))+'</button></div>';
  $('#active-workflow').hidden=!state.workflow;if(state.workflow)$('#active-workflow span').textContent=t('workflowActive',{name:t(workflows[state.workflow].label)});
  renderCompareBar();syncURL();
}
function toggleSaved(id){
  if(saved.has(id)){saved.delete(id);notify(t('removeDone'));}else{saved.add(id);notify(t('saveDone'));}
  persistSaved();render();if(currentDetail?.id===id&&$('#detail-dialog').open)renderDetail(currentDetail);
}
function toggleCompare(id){
  if(state.compare.includes(id))state.compare=state.compare.filter(x=>x!==id);
  else{if(state.compare.length>=3){notify(t('compareLimit'));return;}state.compare.push(id);}render();
}
function renderCompareBar(){
  const rows=state.compare.map(id=>skills.find(s=>s.id===id)).filter(Boolean);$('#compare-bar').hidden=!rows.length;
  $('#compare-count').textContent=t('selected',{n:rows.length});$('#compare-names').textContent=rows.map(s=>field(s,'name')).join(language==='en'?', ':'、');$('#compare-open').disabled=rows.length<2;
}
function detailSection(label,body){return '<section class="detail-section"><h3>'+esc(t(label))+'</h3>'+body+'</section>';}
function renderDetail(s){
  const repository=sourceLink(s.repository),source=sourceLink(s.sourceUrl),license=sourceLink(s.licenseUrl),packageSource=sourceLink(s.repository+'/tree/'+s.commit);
  $('#detail-content').innerHTML='<div class="detail-header"><p class="detail-eyebrow">'+esc(t(s.category))+'</p><h2 id="detail-title">'+esc(field(s,'name'))+'</h2><p class="skill-original-name">'+esc(s.originalName)+'</p><p class="detail-summary">'+esc(field(s,'summary'))+'</p></div>'+
    '<div class="detail-body"><div class="detail-source"><span>'+esc(t('author'))+' <a href="'+repository+'" target="_blank" rel="noopener noreferrer">'+esc(s.author)+'</a></span><span>'+esc(t('license'))+' <a href="'+license+'" target="_blank" rel="noopener noreferrer">'+esc(s.license)+'</a></span><span>'+esc(t('verifiedDate'))+' '+esc(catalog.updatedAt)+'</span></div>'+
    detailSection('method','<p>'+esc(field(s,'method'))+'</p>')+
    '<section class="detail-section detail-io"><div><h3>'+esc(t('inputs'))+'</h3>'+listHTML(field(s,'inputs'))+'</div><div><h3>'+esc(t('outputs'))+'</h3>'+listHTML(field(s,'outputs'))+'</div></section>'+
    detailSection('dependencies','<p>'+esc(field(s,'environment'))+'</p>'+listHTML(field(s,'dependencies')))+
    '<p class="execution-note">'+esc(t(s.executionVerified?'executionVerified':'executionPending'))+'</p>'+
    detailSection('example','<p class="example-box">'+esc(field(s,'example'))+'</p>')+
    detailSection('boundary','<p>'+esc(field(s,'notes'))+'</p>')+
    '<div class="detail-actions"><a class="button button-primary" href="'+source+'" target="_blank" rel="noopener noreferrer">'+esc(t('openSkill'))+'</a><button class="button button-quiet" id="copy-example" type="button">'+esc(t('copyExample'))+'</button><button class="button button-quiet" data-save="'+esc(s.id)+'" type="button">'+esc(t(saved.has(s.id)?'removeList':'addList'))+'</button></div>'+
    '<section class="detail-section"><p>'+esc(t('repositoryIntro'))+'<a class="text-link" href="'+packageSource+'" target="_blank" rel="noopener noreferrer">'+esc(t('repository'))+'</a></p></section></div>';
}
function openDetail(id){const s=skills.find(s=>s.id===id);if(!s)return;currentDetail=s;renderDetail(s);$('#detail-dialog').showModal();}
async function copyExample(){
  if(!currentDetail)return;try{await navigator.clipboard.writeText(field(currentDetail,'example'));notify(t('copyDone'));}
  catch{const element=$('#detail-content .example-box'),range=document.createRange();range.selectNodeContents(element);const selection=window.getSelection();selection.removeAllRanges();selection.addRange(range);notify(t('copyFailed'));}
}
function renderComparison(){
  const rows=state.compare.map(id=>skills.find(s=>s.id===id)).filter(Boolean);
  const fields=[['scenario',s=>esc(t(s.category))],['methodShort',s=>esc(field(s,'method'))],['inputsShort',s=>listHTML(field(s,'inputs'))],['outputsShort',s=>listHTML(field(s,'outputs'))],['dependencies',s=>'<p>'+esc(field(s,'environment'))+'</p>'+listHTML(field(s,'dependencies'))],['licenseFull',s=>esc(s.license)],['execution',s=>esc(t(s.executionVerified?'executionVerified':'notExecuted'))],['source',s=>'<a href="'+sourceLink(s.sourceUrl)+'" target="_blank" rel="noopener noreferrer">'+esc(t('openSkill'))+'</a>']];
  $('#compare-content').innerHTML='<h2 id="compare-title">'+esc(t('compareTitle'))+'</h2><p>'+esc(t('compareNote'))+'</p><div class="comparison-scroll"><table class="comparison-table"><thead><tr><th scope="col">'+esc(t('compareItem'))+'</th>'+rows.map(s=>'<th scope="col">'+esc(field(s,'name'))+'</th>').join('')+'</tr></thead><tbody>'+
    fields.map(([label,value])=>'<tr><th scope="row">'+esc(t(label))+'</th>'+rows.map(s=>'<td>'+value(s)+'</td>').join('')+'</tr>').join('')+'</tbody></table></div>';
}
function openCompare(){if(state.compare.length<2)return;renderComparison();$('#compare-dialog').showModal();}
function renderInfo(){
  const licenses=(catalog.sources||[]).filter(s=>s.licenseFile&&/^\/licenses\/[\w.-]+$/.test(s.licenseFile));
  $('#info-content').innerHTML=infoMode==='about'?'<h2 id="info-title">'+esc(t('aboutTitle'))+'</h2>'+['aboutOne','aboutTwo','aboutThree','aboutCredits'].map(key=>'<p>'+esc(t(key))+'</p>').join('')+'<h3>'+esc(t('licenseCopy'))+'</h3><ul>'+licenses.map(s=>'<li><a href="'+esc(new URL(s.licenseFile.replace(/^\//,''),catalogAssets).href)+'" target="_blank" rel="noopener noreferrer">'+esc(s.repository.replace('https://github.com/',''))+' · '+esc(s.license)+'</a></li>').join('')+'</ul>':
    '<h2 id="info-title">'+esc(t('standardsTitle'))+'</h2><ul>'+['standardOne','standardTwo','standardThree','standardFour','standardFive'].map(key=>'<li>'+esc(t(key))+'</li>').join('')+'</ul><p>'+esc(t('standardsNote'))+'</p>';
}
function openInfo(mode='standards'){infoMode=mode;renderInfo();$('#info-dialog').showModal();}
function resetFilters(){state.q='';state.category='all';state.repository='all';state.workflow='';state.savedOnly=false;$('#search').value='';render();}
function moveToCatalog(){$('#catalog').scrollIntoView({behavior:matchMedia('(prefers-reduced-motion: reduce)').matches?'auto':'smooth'});}
function switchLanguage(){
  language=language==='en'?'zh':'en';try{localStorage.setItem('finskills:language',language);}catch{}
  applyLanguage();if(catalog)render();if($('#detail-dialog').open&&currentDetail)renderDetail(currentDetail);if($('#compare-dialog').open)renderComparison();if($('#info-dialog').open)renderInfo();
}
document.addEventListener('click',event=>{
  const button=event.target.closest('button');if(!button)return;
  if(button.dataset.open)openDetail(button.dataset.open);
  if(button.dataset.save)toggleSaved(button.dataset.save);
  if(button.dataset.compare)toggleCompare(button.dataset.compare);
  if(button.dataset.category){state.category=button.dataset.category;state.workflow='';render();}
  if(button.dataset.workflow){state.workflow=button.dataset.workflow;state.category='all';state.repository='all';state.q='';state.savedOnly=false;$('#search').value='';render();moveToCatalog();}
  if(button.dataset.repository){state.repository=button.dataset.repository;state.category='all';state.workflow='';state.q='';state.savedOnly=false;$('#search').value='';render();moveToCatalog();}
  if(button.hasAttribute('data-reset'))resetFilters();
});
$('#search').value=state.q;$('#search').addEventListener('input',event=>{state.q=event.target.value;render();});
$('#sort').addEventListener('change',event=>{state.sort=event.target.value;render();});
$('#source-filter').addEventListener('change',event=>{state.repository=event.target.value;render();});
$('#clear-filters').addEventListener('click',resetFilters);
$('#saved-filter').addEventListener('click',()=>{state.savedOnly=!state.savedOnly;render();});
$('#saved-header').addEventListener('click',()=>{state.savedOnly=true;state.q='';state.category='all';state.repository='all';state.workflow='';$('#search').value='';render();moveToCatalog();});
$('#clear-workflow').addEventListener('click',()=>{state.workflow='';render();});
$('#compare-clear').addEventListener('click',()=>{state.compare=[];render();});
$('#compare-open').addEventListener('click',openCompare);
$('#detail-content').addEventListener('click',event=>{if(event.target.closest('#copy-example'))copyExample();});
$('#standards-button').addEventListener('click',()=>openInfo());$('#standards-bottom').addEventListener('click',()=>openInfo());$('#about-button').addEventListener('click',()=>openInfo('about'));
$('#language-toggle').addEventListener('click',switchLanguage);
for(const dialog of document.querySelectorAll('dialog')){
  dialog.querySelector('.dialog-close').addEventListener('click',()=>dialog.close());
  dialog.addEventListener('click',event=>{if(event.target===dialog){const rect=dialog.getBoundingClientRect();if(event.clientX<rect.left||event.clientX>rect.right||event.clientY<rect.top||event.clientY>rect.bottom)dialog.close();}});
  dialog.addEventListener('close',()=>{if(dialog.id==='detail-dialog')currentDetail=null;});
}
document.addEventListener('keydown',event=>{if(event.key==='/'&&!document.querySelector('dialog[open]')&&!/input|textarea|select/i.test(document.activeElement?.tagName)){event.preventDefault();$('#search').focus();}});
async function loadCatalog(){
  try{
    async function readCatalog(assets){
      const url=new URL('data/catalog.json',assets);
      if(assets===canonicalAssets)url.searchParams.set('v',Math.floor(Date.now()/60000));
      const response=await fetch(url,{cache:'no-cache',signal:AbortSignal.timeout(8000)});
      if(!response.ok)throw new Error('catalog unavailable');
      const data=await response.json();
      if(!Array.isArray(data.skills)||!data.skills.length||!Array.isArray(data.sources))throw new Error('invalid catalog');
      catalogAssets=assets;return data;
    }
    usingSnapshot=false;
    if(siteMirror){
      try{catalog=await readCatalog(canonicalAssets);}
      catch{catalog=await readCatalog(new URL('./',location.href).href);usingSnapshot=true;}
    }else{catalog=await readCatalog(new URL('./',location.href).href);}
    if(!Array.isArray(catalog.skills)||!catalog.skills.length)throw new Error('empty catalog');skills=catalog.skills;if(state.repository!=='all'&&!skills.some(s=>s.repository===state.repository))state.repository='all';applyLanguage();render();
  }catch{
    $('#result-count').textContent=t('unavailable');$('#skills-list').innerHTML='<div class="empty-state"><h3>'+esc(t('loadError'))+'</h3><p>'+esc(t('loadErrorNote'))+'</p><button id="retry-catalog" class="button button-quiet" type="button">'+esc(t('retry'))+'</button></div>';
    $('#retry-catalog').addEventListener('click',loadCatalog);
  }
}
applyLanguage();loadCatalog();
