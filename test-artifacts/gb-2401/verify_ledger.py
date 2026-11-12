"""来源账本对账验证：跳转/直接引用/多跳传播/悬空回流四桶与运行中PageRank逐篇对账。

运行方式：PYTHONPATH=/workspace/backend python3 verify_ledger.py
覆盖：收敛精确性、零权重、断连/孤立、悬空回流、循环引用不重复计入、未收敛差额。
"""
import random, sys
from src.services.pagerank import pagerank
from src.services.ledger import source_ledger

FAIL = []
def check(name, cond, detail=""):
    print(("PASS " if cond else "FAIL ") + name + ((" | " + detail) if detail else ""))
    if not cond: FAIL.append(name)

def components_of(ids, edges):
    unseen=set(ids);comp=[]
    while unseen:
        root=min(unseen);todo=[root];unseen.remove(root);part=[]
        while todo:
            k=todo.pop();part.append(k)
            for s,t in edges:
                j=t if s==k else s if t==k else None
                if j in unseen:unseen.remove(j);todo.append(j)
        comp.append(sorted(part))
    return comp

def make_result(nodes, edges, personalization=None, damping=.85, tol=1e-10, max_iter=1000):
    ids=[n["id"] for n in nodes]
    pr=pagerank(ids, edges, damping, personalization, tol, max_iter)
    return {"rows":[{"id":n["id"],"title":n["title"]} for n in nodes],"edges":[list(e) for e in edges],
            "pagerank":pr,"policy":{"damping":damping},"components":components_of(ids,edges)}

def demo_graph():
    rng=random.Random(2401);topics=["材料谱系","方法论","开放知识"]
    nodes=[{"id":f"YL{i:02d}","title":f"{topics[(i-1)//16]} · 文献{i:02d}的证据与讨论"} for i in range(1,49)]
    edges=set()
    for lo,hi,target in [(1,33,130),(33,47,30)]:
        local=set()
        while len(local)<target:
            source=rng.randrange(lo,min(hi,45));dest=rng.randrange(lo,hi)
            if source!=dest:local.add((f"YL{source:02d}",f"YL{dest:02d}"))
        edges.update(local)
    return nodes,[list(e) for e in sorted(edges)]

def common_checks(tag, L, pr, tol_gap):
    rec=L["reconciliation"];by={r["id"]:r for r in L["rows"]}
    check(tag+": 逐篇total等于运行PageRank", all(abs(by[i]["total"]-pr["scores"][i])==0 for i in by))
    check(tag+": 四桶+对账差=total(构造恒等)", all(abs(r["jump"]+r["direct"]+r["multihop"]+r["dangling"]+r["gap"]-r["total"])<1e-15 for r in L["rows"]))
    check(tag+": 桶非负", all(min(r["jump"],r["direct"],r["multihop"],r["dangling"])>=-1e-18 for r in L["rows"]))
    check(tag+": 对账差上限", rec["gap_max"]<tol_gap, f"gap_max={rec['gap_max']:.3e}")
    check(tag+": 概率和≈1", abs(rec["probability_sum"]-1)<1e-9, f"sum={rec['probability_sum']:.12f}")
    check(tag+": 桶合计+对账差=概率和", abs(rec["jump"]+rec["direct"]+rec["multihop"]+rec["dangling"]+sum(r["gap"] for r in L["rows"])-rec["probability_sum"])<1e-9)
    check(tag+": 引用流入=直接+多跳(收敛恒等)", all(abs(r["citation_inflow"]-(r["direct"]+r["multihop"]))<tol_gap+1e-12 for r in L["rows"]))
    src_ok=True
    for r in L["rows"]:
        listed=sum(s["flow"] for s in r["sources"])
        indeg=sum(1 for s,t in [(a,b) for a,b in EDGES_GLOBAL] if t==r["id"]) if EDGES_GLOBAL else 0
        if listed>r["citation_inflow"]+1e-9: src_ok=False
    check(tag+": 列出来源流量不超过引用流入", src_ok)
    check(tag+": 路径不含自返起点(循环不重复计入)", all(p["origin"]!=r["id"] for r in L["rows"] for p in r["paths"]))
    return by

EDGES_GLOBAL=None

# A. 演示图(48篇/160边,双分量+孤立YL47/YL48+悬空YL45/YL46),均匀回流,收敛
nodes,edges=demo_graph();EDGES_GLOBAL=edges
res=make_result(nodes,edges,None,.85,1e-10,1000);pr=res["pagerank"]
print(f"[A] demo converged={pr['converged']} iters={pr['iterations']} residual={pr['residual']:.3e}")
L=source_ledger(res);by=common_checks("[A]",L,pr,1e-9)
check("[A] 收敛标记", pr["converged"] and L["converged"])
for iso in ("YL47","YL48"):
    r=by[iso]
    check(f"[A] 孤立{iso}仅跳转+悬空回流", r["direct"]==0 and r["multihop"]==0 and not r["sources"] and abs(r["total"]-(r["jump"]+r["dangling"]+r["gap"]))<1e-15)
check("[A] 断连分量提示", any("弱连通分量" in n for n in L["notes"]))
check("[A] 悬空质量为正", L["dangling_mass"]>0)
check("[A] 悬空文献有回流注释", any("悬空" in n for n in by["YL45"]["notes"]))

# B. 零权重个性化:仅YL01:3,YL02:1,其余46篇为0
res=make_result(nodes,edges,{"YL01":3,"YL02":1},.85,1e-10,1000);pr=res["pagerank"]
print(f"[B] zero-weight converged={pr['converged']} iters={pr['iterations']}")
L=source_ledger(res);by=common_checks("[B]",L,pr,1e-9)
zeros=[i for i in by if res["pagerank"]["personalization"][i]==0]
check("[B] 46篇零权重", len(zeros)==46)
check("[B] 零权重篇跳转=悬空回流=0", all(by[i]["jump"]==0 and by[i]["dangling"]==0 for i in zeros))
check("[B] 零权重注释", all(any("权重为零" in n for n in by[i]["notes"]) for i in zeros[:5]) and any("46篇" in n for n in L["notes"]))

# C. 未收敛:max_iter=1
res=make_result(nodes,edges,None,.85,1e-10,1);pr=res["pagerank"]
print(f"[C] max_iter=1 converged={pr['converged']} residual={pr['residual']:.3e}")
L=source_ledger(res);rec=L["reconciliation"]
check("[C] 未收敛标记", not pr["converged"] and not L["converged"])
check("[C] 对账差非零且被交代", rec["gap_abs"]>1e-6 and rec["gap_max"]>0, f"gap_abs={rec['gap_abs']:.3e}")
check("[C] 未收敛提示", any("未收敛" in n for n in L["notes"]))
check("[C] 四桶+对账差仍逐篇闭合", all(abs(r["jump"]+r["direct"]+r["multihop"]+r["dangling"]+r["gap"]-r["total"])<1e-15 for r in L["rows"]))

# D. 手工图:2-循环A<->B、C->A、D孤立、E悬空
nodes4=[{"id":k,"title":k} for k in "ABCDE"]
edges4=[["A","B"],["B","A"],["C","A"]]
res=make_result(nodes4,edges4,None,.85,1e-12,1000);pr=res["pagerank"]
print(f"[D] cycle graph converged={pr['converged']} iters={pr['iterations']}")
EDGES_GLOBAL=edges4
L=source_ledger(res);by=common_checks("[D]",L,pr,1e-9)
check("[D] 循环双方自返质量被标注", by["A"]["cycle_return"]>0 and by["B"]["cycle_return"]>0, f"A={by['A']['cycle_return']:.3e} B={by['B']['cycle_return']:.3e}")
check("[D] 循环注释", any("回路" in n for n in by["A"]["notes"]))
check("[D] D孤立仅跳转+悬空回流", by["D"]["direct"]==0 and by["D"]["multihop"]==0 and abs(by["D"]["total"]-(by["D"]["jump"]+by["D"]["dangling"]+by["D"]["gap"]))<1e-15)
check("[D] 悬空质量=D+E(均无出边)", abs(L["dangling_mass"]-(pr["scores"]["D"]+pr["scores"]["E"]))<1e-15)
check("[D] 悬空回流按p均匀分配", all(abs(r["dangling"]-.85*L["dangling_mass"]*.2)<1e-12 for r in L["rows"]))
check("[D] A的主要来源含B与C", {s["id"] for s in by["A"]["sources"]}=={"B","C"})

# E. 全局对账恒等式(演示图)
res=make_result(*demo_graph(),None,.85,1e-10,1000)
L=source_ledger(res);rec=L["reconciliation"]
check("[E] Σ跳转=1-d", abs(rec["jump"]-.15)<1e-12, f"{rec['jump']:.12f}")
check("[E] Σ悬空回流=d·DM", abs(rec["dangling"]-.85*L["dangling_mass"])<1e-12)
check("[E] Σ直接+Σ多跳=d·(1-DM)(收敛)", abs(rec["direct"]+rec["multihop"]-.85*(1-L["dangling_mass"]))<1e-8, f"{rec['direct']+rec['multihop']:.12f} vs {.85*(1-L['dangling_mass']):.12f}")

print()
if FAIL: print("FAILED:", *FAIL); sys.exit(1)
print("ALL CHECKS PASSED")
