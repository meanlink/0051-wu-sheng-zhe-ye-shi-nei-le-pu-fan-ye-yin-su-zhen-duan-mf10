import {h} from './base.js';
export function layout(piece){
 return `<section class="folio"><article><h2>旧版左页</h2><p>翻页点前预留 ${h(piece.legacy_lead)} 秒</p></article>
 <article><h2>第 ${h(piece.legacy_page)} 页</h2><p>${piece.legacy_hands_busy?'两手继续持奏，需重点核对':'可空出手处理折页'}</p></article></section>`;
}
