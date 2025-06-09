# Triage Logic Rules and Guideline References

| Rule/Test Case                        | Expected Triage | Source/Guideline                                      |
|---------------------------------------|-----------------|-------------------------------------------------------|
| Ambulance arrival                     | RED             | ESI v4, Table 2, p. 23                                |
| O₂ saturation < 90%                   | RED             | ESI v4, Table 2, p. 23                                |
| O₂ saturation 90-93%                  | YELLOW          | ESI v4, Table 2, p. 23                                |
| O₂ saturation ≥ 94%                   | GREEN           | ESI v4, Table 2, p. 23                                |
| GCS < 10                              | RED             | Manchester Triage, p. 45                              |
| GCS 10-13                             | YELLOW          | Manchester Triage, p. 45                              |
| GCS ≥ 14                              | GREEN           | Manchester Triage, p. 45                              |
| Temp < 35°C or > 40°C                 | RED             | WHO ETAT, p. 18                                       |
| Temp 35-36°C or 38-40°C               | YELLOW          | WHO ETAT, p. 18                                       |
| Temp 36-37.9°C                        | GREEN           | WHO ETAT, p. 18                                       |
| SBP < 80 or > 220                     | RED             | ESI v4, Table 2, p. 23                                |
| SBP 80-89 or 161-220                  | YELLOW          | ESI v4, Table 2, p. 23                                |
| SBP 90-160                            | GREEN           | ESI v4, Table 2, p. 23                                |
| DBP > 120                             | RED             | ESI v4, Table 2, p. 23                                |
| DBP 101-120                           | YELLOW          | ESI v4, Table 2, p. 23                                |
| DBP ≤ 100                             | GREEN           | ESI v4, Table 2, p. 23                                |
| HR < 40 or > 150                      | RED             | ESI v4, Table 2, p. 23                                |
| HR 40-49 or 101-150                   | YELLOW          | ESI v4, Table 2, p. 23                                |
| HR 50-100                             | GREEN           | ESI v4, Table 2, p. 23                                |
| RED symptoms (e.g., chest pain, etc.) | RED             | ESI v4, Manchester Triage, clinical consensus         |
| YELLOW symptoms                       | YELLOW          | ESI v4, Manchester Triage, clinical consensus         |
| GREEN symptoms                        | GREEN           | Local protocol, clinical consensus                    |
| No symptoms, all vitals normal        | GREEN           | ESI v4, Manchester Triage, WHO ETAT                   |

*See test_triage_logic.py for detailed mapping of symptoms and vitals to triage tags.* 