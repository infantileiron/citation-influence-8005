import {useEffect,useState} from 'react';import * as runs from '../api/runs';import type {Ledger,LedgerRow} from '../types/entities';import {number} from '../utils/format';
const SEGS=[['jump','跳转','seg-jump'],['direct','直接引用','seg-direct'],['multihop','多跳传播','seg-multihop'],['dangling','悬空回流','seg-dangling']] as const;
function Bar({r}:{r:LedgerRow}){const den=r.jump+r.direct+r.multihop+r.dangling+Math.abs(r.gap)||1;return <div className="ledger-bar" aria-hidden="true">{SEGS.map(([k,,c])=><i key={k} className={c} style={{width:100*r[k]/den+'%'}}/>)}{r.gap!==0&&<i className="seg-gap" style={{width:100*Math.abs(r.gap)/den+'%'}}/>}</div>}
export default function SourceLedger({runId}:{runId:string}){
 const[ledger,setLedger]=useState<Ledger|null>(null),[error,setError]=useState(''),[id,setId]=useState('');
 useEffect(()=>{let on=true;setLedger(null);setError('');runs.ledger(runId).then(l=>{if(on){setLedger(l);setId(l.rows[0]?.id??'')}}).catch(e=>{if(on)setError(e.message)});return()=>{on=false}},[runId]);
 if(error)return <section className="paper ledger"><h2>来源账本 / SOURCE LEDGER</h2><p className="notice">{error}</p></section>;
 if(!ledger)return <section className="paper ledger"><h2>来源账本 / SOURCE LEDGER</h2><p className="notice">正在按锁定研究生成来源账本…</p></section>;
 const sel=ledger.rows.find(r=>r.id===id)??ledger.rows[0],rec=ledger.reconciliation;
 return <section className="paper table-scroll ledger"><h2>来源账本 / SOURCE LEDGER</h2>
 <p className="ledger-method">{ledger.method}。阻尼 d={ledger.damping}，悬空质量 {number(ledger.dangling_mass,6)}，{ledger.converged?`已收敛（${ledger.iterations}轮）`:'未收敛，差额见对账差列'}。点击任一行追查该文献的主要来源与路径。</p>
 <div className="ledger-summary">
  <div><small>PageRank概率和</small><strong>{number(rec.probability_sum,8)}</strong></div>
  <div><small>跳转 + 悬空回流</small><strong>{number(rec.jump+rec.dangling,6)}</strong></div>
  <div><small>直接引用 + 多跳传播</small><strong>{number(rec.direct+rec.multihop,6)}</strong></div>
  <div><small>对账差 |Σgap| / 单篇最大</small><strong>{rec.gap_abs.toExponential(2)}</strong><span>{rec.gap_max.toExponential(2)}</span></div>
 </div>
 {ledger.notes.length>0&&<p className="method-note">{ledger.notes.join('；')}</p>}
 <table><thead><tr><th>文献</th><th>跳转</th><th>直接引用</th><th>多跳传播</th><th>悬空回流</th><th>对账差</th><th>合计 = PageRank</th><th>账本构成</th></tr></thead><tbody>
  {ledger.rows.map(r=><tr key={r.id} className={sel&&r.id===sel.id?'selected':''} onClick={()=>setId(r.id)}><td><b>{r.id}</b><small>{r.title}</small></td><td>{number(r.jump,6)}</td><td>{number(r.direct,6)}</td><td>{number(r.multihop,6)}</td><td>{number(r.dangling,6)}</td><td>{r.gap.toExponential(1)}</td><td>{number(r.total,6)}</td><td><Bar r={r}/></td></tr>)}
 </tbody></table>
 {sel&&<div className="ledger-detail">
  <div>
   <h3>{sel.id} · 账本明细</h3>
   <div className="ledger-legend">{SEGS.map(([k,label,c])=><span key={k}><i className={c}/>{label} {number(sel[k],6)}</span>)}<span><i className="seg-gap"/>对账差 {sel.gap.toExponential(2)}</span></div>
   <Bar r={sel}/>
   <small>合计 {number(sel.total,7)}；引用边流入（直接+多跳）{number(sel.citation_inflow,7)}，与右侧主要来源流量逐条对账。</small>
   {sel.notes.map(n=><small className="ledger-note" key={n}>{n}</small>)}
  </div>
  <div>
   <h3>主要来源与路径</h3>
   {sel.sources.length===0&&<small>无引用流入：该文献概率全部来自跳转与悬空回流。</small>}
   {sel.sources.map(s=><div className="ledger-source" key={s.id}><b>{s.id}</b><span style={{width:Math.max(2,100*s.share)+'%'}}/><em>{number(s.flow,6)} · {(100*s.share).toFixed(1)}%</em></div>)}
   {sel.paths.length>0&&<><small>主要二跳路径（更深层已并入多跳传播合计）</small>{sel.paths.map(p=><p className="ledger-path" key={p.origin+'→'+p.via}>{p.origin} → {p.via} → {sel.id}<em>{p.mass.toExponential(2)}</em></p>)}</>}
   {sel.cycle_return>0&&<small>经回路返回自身 {sel.cycle_return.toExponential(2)}，已计入多跳传播，未重复列为来源。</small>}
  </div>
 </div>}
 </section>;
}
