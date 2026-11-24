import {h} from './base.js';
import {stats} from './readout.js';
import {stages} from './folio_scope.js';
export function comparison({stage,model,baseline_risk}){
 return stats([['阶段',stages[stage]],['旧谱风险',baseline_risk===null?'待回验':(100*baseline_risk).toFixed(1)+'%']])+
  (model?`<div class="signal"><p>仅提前量<br><strong>${h(model.lead_loss)}</strong> log loss</p><p>提前量与手位<br><strong>${h(model.combined_loss)}</strong> log loss</p></div>
 <p>采用${model.method==='lead_hands'?'提前量与手位':'仅提前量'}。拟合 ${h(model.learned)} 笔，回验 ${h(model.checked)} 笔。</p>`:'<p class="callout">先独立记录拟合和留出批。</p>');
}
