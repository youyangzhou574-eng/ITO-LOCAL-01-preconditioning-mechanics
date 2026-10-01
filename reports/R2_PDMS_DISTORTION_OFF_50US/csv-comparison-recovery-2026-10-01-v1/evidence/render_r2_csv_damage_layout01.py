"""CSV-only figure layout correction; no comparison or scientific audit rerun."""
import csv,hashlib,json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parent
OUT=Path(json.loads((ROOT/'R2_CSV_COMPARISON_RECOVERY01_SOURCE_ADMISSION.json').read_text(encoding='utf-8'))['output'])
ident=json.loads((OUT/'INPUT_IDENTITIES.json').read_text(encoding='utf-8'))
target=OUT/'ITO_DAMAGE_CSV_LAYOUT01.png'
if target.exists():raise ValueError('Layout correction already exists')
variables=['cumulative_cracked_reference_fraction','deleted_reference_fraction','ITO_active_max_principal_MPa','ITO_active_CKLE_max_abs']
labels=['Cumulative cracked reference fraction','Deleted reference fraction','Active ITO max principal stress (MPa)','Active ITO |CKLE| max']
fig,axs=plt.subplots(2,2,figsize=(12,8))
for case,color in [('R1','#235789'),('R2','#c73e1d')]:
 name=case+'_SPATIAL_PATH.csv';path=Path(ident['paths'][name]);raw=path.read_bytes()
 if hashlib.sha256(raw).hexdigest()!=ident['hashes'][name]:raise ValueError('Closed CSV changed')
 with path.open(encoding='utf-8-sig',newline='') as f:rows=list(csv.DictReader(f))
 for ax,var,label in zip(axs.flat,variables,labels):
  ax.plot([100*float(r['macro_strain']) for r in rows],[float(r[var]) for r in rows],color=color,label=case,lw=1)
  ax.set(xlabel='Native measured macrostrain (%)',ylabel=label);ax.grid(alpha=.25);ax.legend()
fig.suptitle('Existing CSV diagnostic comparison; BOTH scientific gates FAIL',fontsize=12,y=.98)
fig.tight_layout(rect=(0,0,1,.94),pad=1.3)
fig.savefig(target,dpi=180);plt.close(fig)
print(json.dumps({'file':str(target),'bytes':target.stat().st_size,'sha256':hashlib.sha256(target.read_bytes()).hexdigest(),'comparison_reruns':0,'science_reruns':0,'ODB_calls':0,'NPZ_reads':0}))
