import {h} from './base.js';
import {intro,table} from './readout.js';
import {feedback,onSubmit,options} from './submit.js';
import {pieces,read,write} from './turn_client.js';
import {choose} from './folio_scope.js';

const riskText = value => (100 * Number(value)).toFixed(1) + '%';

function signCard(signability){
 const tone = signability.can_sign ? 'ok' : 'blocked';
 const title = signability.can_sign ? '当前可以签发' : '当前不能签发';
 const reasons = (signability.reasons ?? []).map(line => `<li>${h(line)}</li>`).join('');
 return `<section class="sign-card ${tone}" aria-live="polite">
  <h2>${h(title)}<small>证据批次第 ${h(signability.evidence_version)} 批</small></h2>
  ${reasons ? `<ul class="sign-reasons">${reasons}</ul>` : '<p class="muted">暂无校样，先登记分页改版。</p>'}
 </section>`;
}

function revisionTable(revisions, currentVersion){
 const rows = revisions.map(r => {
  const stale = r.basis_version < currentVersion;
  const basis = `${h(r.basis_version)} 批${stale ? '（已失效）' : ''}`;
  return [r.code, r.target_page, r.hands_busy ? '双手占用' : '可腾手',
    `${r.trial_passes}/3`, riskText(r.failure_probability), basis];
 });
 return table('分页改版',['校样','新页次','留出手位','模拟试翻','失误风险','依据批次'],rows);
}

function correctionForm(){
 return `<form class="entry correction-entry"><h2>按原编号补更正</h2>
  <p class="muted">封存后更正原翻页事件；同一请求编号重试不会重复排队。</p>
  <label>原事件编号<input name="event" required pattern="[A-Z0-9-]{2,20}"></label>
  <label>请求编号（幂等）<input name="request_id" required pattern="[A-Za-z0-9-]{6,40}" placeholder="REQ-0001"></label>
  <label>排练用途<select name="sample"><option value="fit">拟合排练批</option><option value="check">留出回验批</option></select></label>
  <label>提前量 / 秒<input name="lead" type="number" min="0" max="30" step=".1" required></label>
  <label><span><input name="hands_busy" type="checkbox"> 双手占用</span></label>
  <label><span><input name="missed" type="checkbox"> 本次失误</span></label>
  <button>提交更正并重算</button>${feedback}</form>`;
}

export async function render(outlet,user){
 const list=(await pieces()).filter(x=>['frozen','graded','released'].includes(x.stage));
 outlet.innerHTML=`${intro('演出用谱','更正按原事件编号进入新证据批次，待签校样的风险结论立即失效并重算；已发演出用谱保留原签核和依据。')}<div class="toolrow">${choose(list)}</div>
 <div class="split"><section class="revisions stack band"></section><div class="actions stack"></div></div>`;
 const pick=outlet.querySelector('[name=piece]');
 async function draw(){
  const district=outlet.querySelector('.actions');
  const area=outlet.querySelector('.revisions');
  district.innerHTML='';
  if(!pick.value){area.innerHTML='<p>尚无可供改谱的回验批。</p>';return;}
  const data=await read(pick.value,'revisions');
  const current=data.signability.evidence_version;
  const releaseNote=data.release?`<p class="callout">演出 ${h(data.release.programme)} · 用谱 ${h(data.release.revision)} · ${h(data.release.signer)}
   <br>签核依据第 ${h(data.release.basis_version)} 批 · 风险 ${h(riskText(data.release.signed_risk))} · 模型 ${h(data.release.model_method ?? '—')}（历史签核已冻结）</p>`:'';
  area.innerHTML=releaseNote+signCard(data.signability)+
   (data.revisions.length?revisionTable(data.revisions,current):'<p class="empty-state">当前没有符合条件的记录。</p>');
  if(data.release){
   district.innerHTML=`<section class="entry"><h2>已发演出用谱</h2><p class="muted">后续更正只更新证据与留痕，不改变这张谱的历史签核。</p>
    ${user.role==='operator'?correctionForm():''}</section>`;
  } else if(user.role==='operator'){
   const selected=list.find(x=>x.code===pick.value);
   const revisionForm=selected&&selected.stage==='graded'?`<form class="entry"><h2>登记校样</h2><label>版号<input name="code" required></label>
   <label>新页次<input name="target_page" type="number" min="2" max="200" required></label><label>提前 / 秒<input name="lead" type="number" min="0" max="30" step=".1" required></label>
   <label><span><input name="hands_busy" type="checkbox"> 双手占用</span></label><label>连续成功<input name="trial_passes" type="number" min="0" max="3" required></label>
   <button>提交改版</button>${feedback}</form>`:'';
   district.innerHTML=revisionForm+(user.role==='operator'?correctionForm():'');
  } else if(user.role==='reviewer'){
   district.innerHTML=data.revisions.length?`<form class="entry"><h2>签演出曲谱</h2>
   <p class="muted">仅当校样依据与当前证据批次一致且满足全部门槛时可签。</p>
   <label>校样<select name="revision">${options(data.revisions.map(r=>[r.code,r.code+(r.basis_version<current?'（依据已过期）':'')]))}</select></label>
   <label>演出节目名<input name="programme" required minlength="5"></label>
   <button ${data.signability.can_sign?'':'disabled'}>批准用谱</button>${feedback}</form>`
   :'<p class="music-key">等待谱务员提交重新分页与试翻凭据。</p>';
  }
  const forms=[...district.querySelectorAll('form')];
  for(const form of forms){
   onSubmit(form,async body=>{
    if(form.classList.contains('correction-entry')){
     const result=await write(pick.value,'corrections',{...body,lead:+body.lead,hands_busy:!!body.hands_busy,missed:!!body.missed});
     await draw();
     return result.duplicate?'该更正已接收，未重复排队':`已进入第 ${result.evidence_version} 批证据，回验已排队`;
    }
    if(user.role==='operator'){
     await write(pick.value,'revisions',{...body,target_page:+body.target_page,lead:+body.lead,hands_busy:!!body.hands_busy,trial_passes:+body.trial_passes});
     await draw();return '谱页记录已保存';
    }
    await write(pick.value,'revisions/release',body);
    await draw();return '演出用谱已签核';
   });
  }
 }
 pick.onchange=draw;await draw();
}
