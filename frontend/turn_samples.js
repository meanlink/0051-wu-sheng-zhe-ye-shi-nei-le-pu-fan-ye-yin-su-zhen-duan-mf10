import {table} from './readout.js';
import {samples} from './folio_scope.js';
export const sessionTables=events=>Object.entries(samples).map(([id,label])=>
 table(label,['事件','提前 / 秒','手位','结果'],events.filter(r=>r.sample===id).map(r=>[r.event,r.lead,r.hands_busy?'双手占用':'可腾手',r.missed?'失误':'成功']))).join('');
