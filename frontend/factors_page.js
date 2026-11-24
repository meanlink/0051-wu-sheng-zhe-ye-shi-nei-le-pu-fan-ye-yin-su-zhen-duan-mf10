import {waitJob} from './base.js';
import {intro} from './readout.js';
import {feedback,onSubmit} from './submit.js';
import {pieces,read,write} from './turn_client.js';
import {choose} from './folio_scope.js';
import {comparison} from './model_compare.js';
export async function render(outlet,user){
 const list=await pieces();
 outlet.innerHTML=`${intro('双模型回验','用留出排练记录比较两套拟合结果。验证损失改善到预定量才引入手位作为额外特征。')}
 <form class="toolrow">${choose(list)}${user.role==='reviewer'?'<button>封存并回验</button>':''}${feedback}</form><section class="performance band"></section>`;
 const pick=outlet.querySelector('select');
 async function draw(){if(pick.value)outlet.querySelector('.performance').innerHTML=comparison(await read(pick.value,'grade'));}
 pick.onchange=draw;
 onSubmit(outlet.querySelector('form'),async()=>{const job=await write(pick.value,'grade');await waitJob(job.job_id);await draw();return '模型验证完成';});
 await draw();
}
