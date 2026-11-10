\# Baseline examples (before hybrid retrieval and reranking)



\## Worked

Q: What are the main radiation risks for astronauts?

A: Cancer, cardiovascular, neurocognitive and immune risks, with citations

Sources: Probabilistic Assessment of Radiation Risk (p1), Moon 2 Mars Space Radiation Protection (p1, 2, 4, 7)

Latency: 4.38 s | Model: gemini-3.5-flash-lite

Note: most citations come from a single report.



\## Worked, but incomplete

Q: Why is sending humans to Mars so difficult?

Note: covered distance, logistics and landing, but missed radiation and life support.



\## Correct decline

Q: Who won the 2022 FIFA World Cup?

A: The reports do not contain enough information to answer this.



\## Failed (false decline)

Q: How long does a one-way trip to Mars take in the Design Reference Architecture 5.0?

A: The reports do not contain enough information to answer this.

Cause: retrieval returned intro pages of DRA 5.0 and SAC21, not the pages with the trip duration (pages 10 and 23).

Fix planned: hybrid retrieval and reranking (Step 9).

