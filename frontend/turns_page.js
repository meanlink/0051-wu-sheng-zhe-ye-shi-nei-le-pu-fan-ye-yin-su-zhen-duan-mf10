import {intro} from './readout.js';
import {feedback,onSubmit,options} from './submit.js';
import {pieces,read,write} from './turn_client.js';
import {choose,samples} from './folio_scope.js';
import {sessionTables} from './turn_samples.js';
export async function render(outlet,user){
 const list=await pieces();
 outlet.innerHTML=`${intro('翻页实录','按排练批记录谱页转换。每个原始事件只能在一个证据分区出现。')}<div class="toolrow">${choose(list)}</div><div class="split"><section class="sessions band stack"></section>
 ${user.role==='operator'?`<form class="entry"><h2>登记翻页</h2><label>事件编号<input name="event" required></label><label>排练用途<select name="sample">${options(Object.entries(samples))}</select></label>
 <label>提前量 / 秒<input name="lead" type="number" min="0" max="30" step=".1" required></label>
 <label><span><input name="hands_busy" type="checkbox"> 双手占用</span></label><label><span><input name="missed" type="checkbox"> 本次失误</span></label><button>保存排练事件</button>${feedback}</form>`:''}</div>`;
 const pick=outlet.querySelector('[name=piece]');
 async function draw(){if(pick.value)outlet.querySelector('.sessions').innerHTML=sessionTables(await read(pick.value,'events'));}
 pick.onchange=draw;
 onSubmit(outlet.querySelector('form'),async data=>{await write(pick.value,'events',{...data,lead:+data.lead,hands_busy:!!data.hands_busy,missed:!!data.missed});await draw();return '排练事件已保存';});
 await draw();
}
