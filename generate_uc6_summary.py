import csv, os
from datetime import datetime
from collections import defaultdict

with open('data/raw_outputs/uc6_raw_20260310_135253.csv') as f:
    rows = [r for r in csv.DictReader(f) if r.get('pred_label') != 'ERROR']

model_rows = defaultdict(list)
for r in rows:
    model_rows[r['model']].append(r)

summary = []
for model, mrs in sorted(model_rows.items()):
    lats = [int(r['latency_ms']) for r in mrs if int(r.get('latency_ms', 0)) > 0]
    correct = sum(1 for r in mrs if r.get('is_correct') == 'True')
    urg = [r for r in mrs if r.get('gold_label') == 'URGENT']
    urg_recall = round(sum(1 for r in urg if r.get('is_correct') == 'True') / len(urg) * 100, 1) if urg else 0
    summary.append({
        'model': model,
        'tier': mrs[0]['tier'],
        'params': mrs[0]['params'],
        'overall_acc': round(correct / len(mrs) * 100, 1),
        'urgent_recall': urg_recall,
        'p95_ms': sorted(lats)[int(len(lats) * 0.95)] if lats else 0,
        'n_inferences': len(mrs)
    })

os.makedirs('data/results', exist_ok=True)
ts = datetime.now().strftime('%Y%m%d_%H%M%S')
out = f'data/results/uc6_summary_{ts}.csv'
with open(out, 'w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=list(summary[0].keys()))
    w.writeheader()
    w.writerows(summary)

print(f'Saved: {out}')
for r in summary:
    print(f'  {r["model"]}: acc={r["overall_acc"]}% urg_recall={r["urgent_recall"]}% p95={r["p95_ms"]}ms')