import {mount} from './base.js';
import {render as folios} from './folios_page.js';
import {render as turns} from './turns_page.js';
import {render as factors} from './factors_page.js';
import {render as approval} from './approval_page.js';
const pages = {"folios": "曲谱折页", "turns": "翻页实录", "factors": "双模型回验", "approval": "演出用谱"};
const screens = {folios, turns, factors, approval};
mount({title: "无声折页 · 室内乐谱翻页因素诊断", kicker: "谱务室 / 分页与演出用谱", pages, render: (page, outlet, user) => screens[page](outlet, user)});
