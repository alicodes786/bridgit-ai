# 30. Hit Hunters Excel spike (process-log Phase 1)

> 26 Sep 2026. Statutory pack, 21 tabs. Bridgit may **rewrite Banking and Bank Pay
> only**. Do not overwrite ETB / Pg 9 col G (depreciation trap) until Phase 2.

**Comparative file:** 21 sheets including `Banking`, `Bank Pay`, `Bank Rec`, `ETB`.

**Banking:** header row 6. Cols A Date, B Details, C Amount, D–K category echo,
L `=SUM(D:K)-C`. Month-marker rows (1st of month, no details). TOTAL = SUM.

**Bank Pay:** headers rows 4–5 joined. Col A = day-of-month (not full date).
Echo `=C{row}` in the category column. AD `=SUM(D:AC)-C`. TOTAL row was 287
on the 2025 file.

**CSV (Countingup):** newest-first. Opening = earliest running balance ± that
row's movement. Proven on disk 26 Sep: open **£24,704.55**, in **£20,001.01**,
out **£11,760.55**, close **£32,945.01**, rec difference **£0.00**.

**Code by payee** from 2025 echo columns (49 payees extracted). CSV `Category`
is ignored.
