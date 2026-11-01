"""Read-only archive checks. Does not recalculate Excel or fetch market data."""
from pathlib import Path
import hashlib
import json
import math
import openpyxl

ROOT = Path(__file__).resolve().parents[1]

def main():
    manifest = json.loads((ROOT / 'docs/file_manifest.json').read_text())
    for item in manifest:
        p = ROOT / item['path']
        assert hashlib.sha256(p.read_bytes()).hexdigest() == item['sha256'], item['path']
    w = openpyxl.load_workbook(ROOT / 'models/insurance_model.xlsx', data_only=True)
    s = w['3. 분석 및 모델링']
    params = w['모델 가정']
    alpha, beta, gamma, delta = [params[f'B{r}'].value for r in range(4, 8)]
    diffs = []
    for r in range(2,49):
        rho, effort = s[f'G{r}'].value, s[f'H{r}'].value
        df = max(params['B8'].value, min(params['B9'].value, 1+alpha*(rho-1)-beta*effort))
        bpf = max(-params['B12'].value, min(params['B10'].value, gamma*(rho-1)-delta*effort))
        old_ep = s[f'C{r}'].value*s[f'D{r}'].value
        new_ep = old_ep*df
        rc_new = new_ep*params['B11'].value*(1+bpf)
        for cell, expected in [(f'I{r}',df),(f'T{r}',bpf),(f'J{r}',old_ep),(f'K{r}',new_ep),(f'U{r}',rc_new)]:
            assert math.isclose(s[cell].value,expected,rel_tol=1e-9,abs_tol=1e-7), cell
        old_uw = old_ep-s[f'L{r}'].value-s[f'N{r}'].value
        new_uw = new_ep-s[f'M{r}'].value-s[f'O{r}'].value
        assert math.isclose(old_uw,s[f'P{r}'].value,abs_tol=1e-7)
        assert math.isclose(new_uw,s[f'Q{r}'].value,abs_tol=1e-7)
        diffs.append(new_uw-old_uw)
    assert math.isclose(sum(diffs),s['R49'].value,abs_tol=1e-7)
    errors = [(sh.title,c.coordinate,c.value) for sh in w for row in sh for c in row if c.data_type=='e']
    assert not errors, errors
    sim=w['5. 통합']
    years=[(sim[f'A{r}'].value,sim[f'AJ{r}'].value) for r in range(3,39)]
    result = {
        'files_sha256_verified':len(manifest),
        'firms_with_independent_t0_formula_checks':47,
        'cached_excel_error_cells':len(errors),
        'cached_values_only_not_full_recalculation':True,
        'old_uw_t0':s['P49'].value,
        'new_uw_t0':s['Q49'].value,
        'delta_uw_t0':s['R49'].value,
        'minimum_cumulative_npv':min(years,key=lambda x:x[1]),
        'first_positive_cumulative_npv_year':next(t for t,v in years if v>0),
        'npv_t35':sim['AJ38'].value,
        'known_issues':['Presentation and workbook values differ','Formula regime changes at t=31','Full event-study re-execution requires external market data']
    }
    print(json.dumps(result,ensure_ascii=False,indent=2))

if __name__ == '__main__':
    main()
