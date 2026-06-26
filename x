cd /home/ajsbsd/ajsbsd-jwst-cli

git add .

git commit -m "feat: initial implementation of Cold War Erosion Simulation v0.1

- 8-meter global state engine (civilian_oversight, escalation_risk, etc.)
- 7 historical figures (LeMay, Truman, Eisenhower, McCarthy, McNamara, Johnson, Reagan)
- 31 historical events across 5 eras (1947-1991)
- 3 divergence branches (Korea nukes, Cuba airstrikes, Vietnam unrestricted)
- 7 possible endings including The Quiet Surrender (default)
- Year-by-year turn loop with rich terminal narrative output
- 49 unit tests, all passing"

git tag -a v0.1.0 -m "Release v0.1.0 — Cold War Erosion Simulation initial release"

git push origin main
git push origin v0.1.0
