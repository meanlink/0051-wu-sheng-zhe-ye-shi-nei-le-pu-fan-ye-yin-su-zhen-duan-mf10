import {intro, table} from './readout.js';
import {feedback,onSubmit,options} from './submit.js';
import {pieces,read,write} from './turn_client.js';
import {choose,samples,stages} from './folio_scope.js';
import {sessionTables} from './turn_samples.js';
import {h} from './base.js';

const correctionForm = `
 <form class="entry correction-entry" hidden><h2>按原编号补更正</h2>
  <p class="muted">封存后仍可更正原翻页事件；同一请求编号重试不重复排队，更正后回验按最新证据重算。</p>
  <label>原事件编号<input name="event" required pattern="[A-Z0-9-]{2,20}"></label>
  <label>请求编号（幂等）<input name="request_id" required pattern="[A-Za-z0-9-]{6,40}" placeholder="REQ-0001"></label>
  <label>排练用途<select name="sample">${options(Object.entries(samples))}</select></label>
  <label>提前量 / 秒<input name="lead" type="number" min="0" max="30" step=".1" required></label>
  <label><span><input name="hands_busy" type="checkbox"> 双手占用</span></label>
  <label><span><input name="missed" type="checkbox"> 本次失误</span></label>
  <button>提交更正</button>${feedback}</form>`;

function correctionTable(rows){
 if(!rows.length) return '<p class="muted">封存后尚无更正记录。</p>';
 return table('更正台账',['原事件','请求编号','提前 / 秒','手位','结果','进入批次'],
  rows.map(r=>[r.event,r.request_id,r.lead,r.hands_busy?'双手占用':'可腾手',
   r.missed?'失误':'成功',`第 ${r.evidence_version} 批`]));
}

export async function render(outlet,user){
 const list=await pieces();
 outlet.innerHTML=`${intro('翻页实录','按排练批记录谱页转换。每个原始事件只能在一个证据分区出现；封存后按原编号补更正并自动重算。')}
 <div class="toolrow">${choose(list)}</div><div class="split"><section class="sessions band stack"></section>
 <div class="side stack">${user.role==='operator'?`<form class="entry event-entry"><h2>登记翻页</h2><label>事件编号<input name="event" required></label><label>排练用途<select name="sample">${options(Object.entries(samples))}</select></label>
 <label>提前量 / 秒<input name="lead" type="number" min="0" max="30" step=".1" required></label>
 <label><span><input name="hands_busy" type="checkbox"> 双手占用</span></label><label><span><input name="missed" type="checkbox"> 本次失误</span></label><button>保存排练事件</button>${feedback}</form>${correctionForm}`:''}</div></div>`;
 const pick=outlet.querySelector('[name=piece]');
 const side=outlet.querySelector('.side');
 const eventForm=side.querySelector('.event-entry');
 const correction=side.querySelector('.correction-entry');
 async function draw(){
  if(!pick.value)return;
  const sheet=list.find(x=>x.code===pick.value);
  const sealed=sheet.stage!=='recording';
  outlet.querySelector('.sessions').innerHTML=
   `<p class="callout">当前阶段：${h(stages[sheet.stage])} · 证据第 ${h(sheet.evidence_version)} 批</p>`
   +sessionTables(await read(pick.value,'events'))
   +(sealed?correctionTable((await read(pick.value,'corrections')).corrections):'');
  if(user.role==='operator'){
   eventForm.hidden=sealed;
   correction.hidden=!sealed;
  }
 }
 onSubmit(correction,async body=>{
  const result=await write(pick.value,'corrections',{...body,lead:+body.lead,hands_busy:!!body.hands_busy,missed:!!body.missed});
  const fresh=await pieces(); list.splice(0,list.length,...fresh);
  await draw();
  return result.duplicate?'该更正已接收，未重复排队':`已进入第 ${result.evidence_version} 批证据，回验已排队`;
 });
 pick.onchange=draw;
 onSubmit(eventForm,async data=>{
  await write(pick.value,'events',{...data,lead:+data.lead,hands_busy:!!data.hands_busy,missed:!!data.missed});
  const fresh=await pieces();list.splice(0,list.length,...fresh);await draw();return '排练事件已保存';});
 await draw();
}
