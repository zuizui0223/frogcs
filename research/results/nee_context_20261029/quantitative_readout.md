# G1 quantitative readout — fixed 2026-10-29 design

| background | mode | term | beta | low | high | q_bh |
| --- | --- | --- | --- | --- | --- | --- |
| uniform | pooled | Odonata:Caudata | -0.1344 | -0.1932 | -0.0732 | 0.0091 |
| uniform | pooled | Odonata:vegetation | -0.0771 | -0.1107 | -0.0440 | 0.0091 |
| uniform | pooled | Caudata:vegetation | 0.0486 | 0.0046 | 0.0887 | 0.0935 |
| uniform | pooled | Odonata:Caudata:vegetation | 0.0130 | -0.0201 | 0.0439 | 0.5696 |
| uniform | within | Odonata:Caudata | -0.0707 | -0.1423 | 0.0008 | 0.1558 |
| uniform | within | Odonata:vegetation | -0.0434 | -0.0735 | -0.0108 | 0.0413 |
| uniform | within | Caudata:vegetation | -0.0089 | -0.0489 | 0.0310 | 0.7491 |
| uniform | within | Odonata:Caudata:vegetation | 0.0006 | -0.0311 | 0.0323 | 0.9906 |
| uniform | between | Odonata:Caudata | -0.1632 | -0.2567 | -0.0746 | 0.0091 |
| uniform | between | Odonata:vegetation | -0.1166 | -0.2099 | -0.0325 | 0.0724 |
| uniform | between | Caudata:vegetation | 0.1152 | 0.0117 | 0.2152 | 0.0949 |
| uniform | between | Odonata:Caudata:vegetation | 0.0208 | -0.0635 | 0.1041 | 0.7526 |
| target_group | pooled | Odonata:Caudata | -0.0827 | -0.1675 | 0.0038 | 0.1708 |
| target_group | pooled | Odonata:vegetation | -0.0507 | -0.0937 | -0.0047 | 0.1033 |
| target_group | pooled | Caudata:vegetation | 0.0440 | -0.0268 | 0.0950 | 0.3319 |
| target_group | pooled | Odonata:Caudata:vegetation | 0.0204 | -0.0366 | 0.0622 | 0.5500 |
| target_group | within | Odonata:Caudata | -0.1065 | -0.3019 | 0.0434 | 0.3572 |
| target_group | within | Odonata:vegetation | -0.0355 | -0.0798 | 0.0027 | 0.2484 |
| target_group | within | Caudata:vegetation | 0.0239 | -0.0398 | 0.0763 | 0.5648 |
| target_group | within | Odonata:Caudata:vegetation | 0.0284 | -0.0380 | 0.0740 | 0.4823 |
| target_group | between | Odonata:Caudata | -0.0962 | -0.1963 | 0.0165 | 0.1981 |
| target_group | between | Odonata:vegetation | -0.0575 | -0.1382 | 0.0337 | 0.3390 |
| target_group | between | Caudata:vegetation | 0.0612 | -0.0690 | 0.1752 | 0.4823 |
| target_group | between | Odonata:Caudata:vegetation | 0.0221 | -0.0615 | 0.1145 | 0.7233 |


## Geographic coverage

| region | sites | routes | vegetated_sites | vegetated_routes |
| --- | --- | --- | --- | --- |
| NE | 2111 | 214 | 198 | 50 |
| NW | 668 | 67 | 11 | 6 |
| SE | 791 | 82 | 129 | 24 |
| SW | 678 | 69 | 168 | 30 |


## Residual spatial diagnostic

| background | adjustment | moran_I | permutation_p |
| --- | --- | --- | --- |
| uniform | none | 0.2513 | 0.0010 |
| uniform | survey | 0.2265 | 0.0010 |
| uniform | environment | 0.1602 | 0.0010 |
| uniform | space | 0.0760 | 0.0010 |
| target_group | none | 0.2487 | 0.0010 |
| target_group | survey | 0.2123 | 0.0010 |
| target_group | environment | 0.1598 | 0.0010 |
| target_group | space | 0.1037 | 0.0010 |


84 models; 588 coefficients. Four NW models have only 545/999 valid resamples; their p/q values are withheld. Intervals in these rows describe only the estimable resamples and are not adequate inferential intervals. BH uses 320 finite focal interaction p values; it does not correct prior research-wide selection. Fixed 2-degree bootstrap uses 56 geographic blocks.
