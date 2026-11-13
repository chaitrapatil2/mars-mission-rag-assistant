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



\## Baseline scores (vector search only, 12 questions)

\- Decline accuracy: 3/3

\- False declines: 1/9 (Q1)

\- Answers with citations: 8/8

\- Average latency: 4.26 s



\## Results: baseline vs hybrid retrieval + reranker (12 questions)

\- Decline accuracy: 3/3 -> 3/3

\- False declines: 1/9 -> 0/9 (Q1 fixed)

\- Citations present: 8/8 -> 9/9

\- Average latency: 4.26 s -> 22.83 s (reranker runs on CPU)



\## Citation spot check (Q1, v2)

Answer cited a life-support report for "about 180 days". The cited chunk states a one-way travel time of 180-300 days, so the citation is valid, but the answer simplified the range.



\## Final results on 25 questions (7 off-topic)

\- Decline accuracy: 7/7 -> 7/7

\- False declines: 1/18 (Q1) -> 0/18

\- Citations present: 17/17 -> 18/18

\- Average latency: 2.15 s -> 14.93 s (reranker runs on CPU)

Note: Q24 was removed before final scoring because "Schematic 1" is ambiguous without its source passage. The retrieved chunks were from the correct report, so it was a bad question, not a retrieval failure.

Test set: 12 hand-written questions plus 13 LLM-generated from report passages and manually filtered.

