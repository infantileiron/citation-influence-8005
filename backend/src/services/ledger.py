TOP_SOURCES=5
TOP_PATHS=5
def source_ledger(result):
    """按锁定研究与运行存储的PageRank概率，生成每篇文献的来源账本。

    不动点方程 x=(1-d)p+d·Ex+d·DM·p 代入自身一次，得到收敛点上精确成立的互斥分解：
      x_j = (1-d)·p_j                  跳转：随机跳转直接落在j
          + (1-d)·d·(Ep)_j             直接引用：跳转后沿一条引用边到达j
          + d²·(E²x)_j + d²·DM·(Ep)_j  多跳传播：两条及以上引用边，含悬空回流后再走边
          + d·DM·p_j                   悬空回流：悬空质量按锁定个性化向量回流到j
    其中 (Ev)_j=Σ_{i→j} v_i/out_i，DM=悬空节点概率和。循环引用质量按跳数归入唯一桶，
    不重复计入；经回路返回自身的质量单独标注。未收敛时差额单列对账差，不并入任何桶。
    """
    pr=result['pagerank'];d=result['policy']['damping']
    ids=[r['id'] for r in result['rows']];title={r['id']:r['title'] for r in result['rows']}
    x={i:pr['scores'][i] for i in ids};p={i:pr['personalization'][i] for i in ids}
    outs={i:[] for i in ids};ins={i:[] for i in ids}
    for s,t in result['edges']:outs[s].append(t);ins[t].append(s)
    outdeg={i:len(outs[i]) for i in ids}
    dm=sum(x[i] for i in ids if outdeg[i]==0)
    def propagate(v):
        w={j:0. for j in ids}
        for i in ids:
            if outdeg[i]:
                share=v[i]/outdeg[i]
                for j in outs[i]:w[j]+=share
        return w
    Ep=propagate(p);Ex=propagate(x);E2x=propagate(Ex)
    rows=[]
    for j in ids:
        jump=(1-d)*p[j];direct=(1-d)*d*Ep[j];backflow=d*dm*p[j];multihop=d*d*(E2x[j]+dm*Ep[j])
        gap=x[j]-(jump+direct+multihop+backflow)
        sources=sorted(({'id':i,'flow':d*x[i]/outdeg[i],'share':(x[i]/outdeg[i])/Ex[j] if Ex[j]>0 else 0.} for i in ins[j]),key=lambda s:(-s['flow'],s['id']))[:TOP_SOURCES]
        paths={};cycle=0.
        for k in ins[j]:
            for o in ins[k]:
                mass=d*d*x[o]/outdeg[o]/outdeg[k]
                if o==j:cycle+=mass
                else:paths[(o,k)]=paths.get((o,k),0.)+mass
        paths=[{'origin':o,'via':k,'mass':m} for (o,k),m in sorted(paths.items(),key=lambda kv:(-kv[1],kv[0]))[:TOP_PATHS]]
        notes=[]
        if p[j]==0:notes.append('个性化权重为零：跳转与悬空回流为0，概率全部来自引用传播')
        if outdeg[j]==0:notes.append('悬空文献：自身概率按锁定个性化向量向全网回流')
        if not ins[j] and not outs[j]:notes.append('孤立文献：无引用进出，账本仅含跳转与悬空回流')
        if cycle>0:notes.append('经回路返回自身的质量已计入多跳传播，不重复列为外部来源')
        rows.append({'id':j,'title':title[j],'total':x[j],'jump':jump,'direct':direct,'multihop':multihop,'dangling':backflow,'gap':gap,'citation_inflow':d*Ex[j],'sources':sources,'paths':paths,'cycle_return':cycle,'notes':notes})
    recon={'probability_sum':sum(x.values()),'jump':sum(r['jump'] for r in rows),'direct':sum(r['direct'] for r in rows),'multihop':sum(r['multihop'] for r in rows),'dangling':sum(r['dangling'] for r in rows),'gap_abs':sum(abs(r['gap']) for r in rows),'gap_max':max(abs(r['gap']) for r in rows)}
    notes=[]
    if not pr['converged']:notes.append('运行未收敛：各篇差额单列于对账差，未并入任何来源桶，需人工复核')
    if len(result['components'])>1:notes.append(f"网络含{len(result['components'])}个弱连通分量：引用传播不跨分量，跨分量影响仅来自跳转与悬空回流")
    zero=sum(1 for i in ids if p[i]==0)
    if zero:notes.append(f'{zero}篇文献个性化权重为零：其跳转与悬空回流均为0')
    if dm>0:notes.append('悬空质量按锁定个性化向量回流，与跳转同向量')
    return {'damping':d,'converged':pr['converged'],'iterations':pr['iterations'],'residual':pr['residual'],'dangling_mass':dm,'reconciliation':recon,'rows':rows,'notes':notes,'method':'x_j=跳转(1-d)p_j+直接引用(1-d)d(Ep)_j+多跳传播d²(E²x+DM·Ep)_j+悬空回流d·DM·p_j+对账差；引用流入按边流量d·x_i/out_i逐条对账'}
