import {options} from './submit.js';
export const stages={recording:'实录中',frozen:'验证中',graded:'待改谱',released:'已发谱'};
export const samples={fit:'拟合排练批',check:'留出回验批'};
export const choose=list=>`<label>分谱<select name="piece">${options(list.map(x=>[x.code,x.code+' · '+x.title]))}</select></label>`;
