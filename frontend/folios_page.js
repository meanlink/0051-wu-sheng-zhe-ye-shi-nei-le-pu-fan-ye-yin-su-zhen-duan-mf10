import {intro,stats} from './readout.js';
import {pieces} from './turn_client.js';
import {choose,stages} from './folio_scope.js';
import {layout} from './folio_layout.js';
export async function render(outlet){
 const list=await pieces();
 outlet.innerHTML=`${intro('曲谱折页','核对原谱及换页前的动作。此处给出回验使用的谱号、乐器和旧翻页点。')}<div class="toolrow">${choose(list)}</div><div class="split"><div class="score"></div><aside class="music-key"><h2>排练与演出</h2><p>一批训练用于拟合，另一批留作回验。通过评估的谱页才会产生可发演出的编号。</p></aside></div>`;
 const selector=outlet.querySelector('select');
 function draw(){const sheet=list.find(x=>x.code===selector.value);if(sheet)outlet.querySelector('.score').innerHTML=stats([['分谱',sheet.part],['阶段',stages[sheet.stage]]])+layout(sheet);}
 selector.onchange=draw;draw();
}
