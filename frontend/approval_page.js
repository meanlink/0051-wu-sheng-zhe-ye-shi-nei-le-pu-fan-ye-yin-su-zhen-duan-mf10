import {h} from './base.js';
import {intro,table} from './readout.js';
import {feedback,onSubmit,options} from './submit.js';
import {pieces,read,write} from './turn_client.js';
import {choose} from './folio_scope.js';
export async function render(outlet,user){
 const list=(await pieces()).filter(x=>['graded','released'].includes(x.stage));
 outlet.innerHTML=`${intro('演出用谱','改版录入新分页位置和连续试翻成绩。风险低于原版且不高于 45% 才能签给演出场次。')}<div class="toolrow">${choose(list)}</div>
 <div class="split"><section class="revisions stack band"></section><div class="actions"></div></div>`;
 const pick=outlet.querySelector('[name=piece]');
 async function draw(){
  const district=outlet.querySelector('.actions');
  district.innerHTML='';
  const area=outlet.querySelector('.revisions');
  if(!pick.value){area.innerHTML='<p>尚无可供改谱的回验批。</p>';return;}
  const data=await read(pick.value,'revisions');
  area.innerHTML=(data.release?`<p class="callout">演出 ${h(data.release.programme)} · 用谱 ${h(data.release.revision)} · ${h(data.release.signer)}</p>`:'')+
  table('分页改版',['校样','新页次','留出手位','模拟试翻','失误风险'],data.revisions.map(r=>[r.code,r.target_page,r.hands_busy?'双手占用':'可腾手',r.trial_passes+'/3',(100*Number(r.failure_probability)).toFixed(1)+'%']));
  if(data.release)return;
  if(user.role==='operator')district.innerHTML=`<form class="entry"><h2>登记校样</h2><label>版号<input name="code" required></label>
   <label>新页次<input name="target_page" type="number" min="2" max="200" required></label><label>提前 / 秒<input name="lead" type="number" min="0" max="30" step=".1" required></label>
   <label><span><input name="hands_busy" type="checkbox"> 双手占用</span></label><label>连续成功<input name="trial_passes" type="number" min="0" max="3" required></label>
   <button>提交改版</button>${feedback}</form>`;
  if(user.role==='reviewer'&&data.revisions.length)district.innerHTML=`<form class="entry"><h2>签演出曲谱</h2><label>校样<select name="revision">${options(data.revisions.map(r=>[r.code,r.code]))}</select></label><label>演出节目名<input name="programme" required minlength="5"></label><button>批准用谱</button>${feedback}</form>`;
  if(user.role==='reviewer'&&!data.revisions.length)district.innerHTML='<p class="music-key">等待谱务员提交重新分页与试翻凭据。</p>';
  onSubmit(district.querySelector('form'),async body=>{
   if(user.role==='operator')await write(pick.value,'revisions',{...body,target_page:+body.target_page,lead:+body.lead,hands_busy:!!body.hands_busy,trial_passes:+body.trial_passes});
   else await write(pick.value,'revisions/release',body);
   await draw();return '谱页记录已保存';
  });
 }
 pick.onchange=draw;await draw();
}
