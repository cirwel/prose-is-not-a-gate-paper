# Final read of the rendered PDF: Google family

Reader: Antigravity CLI, self-reported model `Gemini 4 Neon (High)`, sandboxed with no repository access, 2026-11-21. Input: the 22 page images of `paper/main.pdf` as built from commit `ddc2df0` and its extracted text. The report is reproduced as returned. Dispositions are in `docs/REVIEWS.md` section 6.

---

```text
FINAL PRE-PUBLICATION REVIEW REPORT

(A) RENDERING DEFECTS (most severe first)

1. Page 21 (Appendix C, "Sensitivity.", line 1): Text runs past the right margin and is physically clipped off the right edge of the page.
   Quoted text: "Sensitivity. Table 9 recomputes the hold counts on clean-labelled patches; results/clean_label_sensitivit"
   The end of the filename ("y.md") is cut off beyond the page boundary because the monospace string has no break point.

2. Page 22 (Table 8, row T18, right column): LaTeX quote-ligature rendering defect corrupts Python code syntax.
   Quoted text: "check_tenant_access(", ") is False"
   Two adjacent single quotes representing empty strings ('', '') were collapsed by LaTeX into a double-quote glyph, turning two empty-string arguments into a single string ", ". All single quotes in Table 8 code snippets are also rendered as curved right apostrophes rather than straight ASCII quotes.

3. Page 16 (Section 8, lines 2-3): Two consecutive lines overflow well into the right margin (overfull hboxes from unbreakable monospace paths).
   Quoted text:
   - "results/recount_check.txt reporting DISCREPANCIES: 0), figure generator (scripts/make_figures.py),"
   - "claims ledger (CLAIMS-LEDGER.md), the label audit with its executable checks (docs/CLEAN-LABEL-AUDIT.md,"

4. Page 14 (Section 6, line 1): Broken citation formatting -- bare number in parentheses instead of bracketed citation.
   Quoted text: "Certificate Transparency logs for TLS certificates (18; since superseded by RFC 9162)"
   Every other citation uses square brackets (e.g., [27], [3]); this should be ([18]; since superseded by RFC 9162).

5. Page 20 (Figure 3, Panel A title and layout): Panel A's bold title overflows past the right edge of Panel A and nearly collides with the top y-axis label of Panel B ("gemma4 synth -> nemotron3"). Additionally, the y-axis of Panel A ("Non-Empty Clean Crux Rate") extends to 1.2 for a proportion bounded by 1.0, and the tick and legend labels across both panels are very small (~6 pt).

6. Page 13 (Figure 2): Axis labels, legend text, and bar annotations are very small and cramped; on Panel B, the "0/4" annotation nearly touches the y-axis spine, and the long label "Partial, completion claimed (n=4)" crowds the right edge of Panel A.

7. Page 12 (Table 5 caption, line 10): Missing closing double quotation mark.
   Quoted text: "which the protocol called "concealed or integrity-violating; eight of the ten runs filed a report"
   (Opening curly quote before "concealed" has no matching closing quote after "integrity-violating".)

8. Page 4 (Section 3.1, paragraph 2) and Page 11 (Section 5, paragraph 1): Awkward line-break hyphenations inside monospace identifiers.
   Quoted text:
   - Page 4: "tests/-" / "test_<module>.py"
   - Page 11: "unimplemented_-" / "requirements"

9. Pages 9, 12, and 19 (Tables 3, 5, and 6): Each table slightly exceeds the body text width symmetrically into the left and right margins (still well inside the page bounds, and legible, though tight).

Note: All figure numbers (Figures 1-3), table numbers (Tables 1-9), section numbers (Sections 1-8, Appendices A-C), and reference numbers ([1]-[28], aside from the missing brackets on 18) are sequential and properly numbered, with no orphaned headings (Section 8 at the bottom of page 15 has two lines of body text beneath it).


(B) ERRORS A CAREFUL READER WOULD CATCH (most severe first)

1. Missing repository URL / archive link despite ~25 internal file-path cross-references (Pages 2, 4, 5, 6, 7, 9, 11, 12, 15-16, 18, 19, 20, 21, 22).
   Quoted text (Page 15-16, Section 8): "All source code, task definitions (C00..C03, T00..T35), pre-registered hypotheses (f7ec48c), raw JSON traces (runs/confirmatory/, N = 6,012), statistical tables (results/tables.md, results/summary.json)... reside in the project repository (86/86 offline unit tests pass under pytest)."
   No URL, DOI, or archival location for "the project repository" appears anywhere in the 22 pages. Readers cannot inspect results/tables.md, docs/CLEAN-LABEL-AUDIT.md, results/clean_label_sensitivity.md, or commit f7ec48c.

2. Figure 2 Panel B silently omits one of the seven outcomes (7/216 runs) while claiming to show "each outcome" (Page 13, Figure 2 and caption).
   Quoted text: "B: fraction of each outcome that the deterministic gates flag."
   The six bars in Panel B sum to 1 + 34 + 34 + 5 + 131 + 4 = 209 runs. The 7 "Passed both suites despite freeze" (Evaded) runs from Panel A and Table 5 (which deterministic gates flag 0/7) are silently omitted without mention in the figure or caption.

3. Contrasts H3a, H3b, and H3c are never defined anywhere in the paper (Pages 10, 18, 19, 21).
   Quoted text:
   - Page 10 (Section 4.3): "All three pre-registered contrasts are non-significant at the final decision (pooled sign test pHolm = 1.00, 0.68, 1.00; largest pooled difference +2.8 pp in holds on clean-labelled PRs)."
   - Page 19 (Table 6): column header "H3a / H3b / H3c (b, c McNemar raw p)"
   - Page 19 (Appendix A, item 3): "The pre-registered Stage-3 contrasts H3a-H3c are non-significant"
   Unlike H1a-H1c (defined on page 7) and H2a-H2c (defined on page 9), the reader is never told which pair of arms/conditions corresponds to H3a, H3b, and H3c and must reverse-engineer them from the (b, c) counts in Table 6.

4. Table 7 omits Youden's J immediately after the text states that Table 7 reports it (Page 20, Appendix B).
   Quoted text: "The protocol pre-specified signal-detection summaries [25]: hit rate H (holds on silent_partial), false-alarm rate FA (holds on clean), Youden's J = H - FA, and log-linear d' and c with the 0.5 correction [17]. Table 7 gives them for Experiment A under neutral;"
   Table 7 only contains columns for Model, H, FA, d', and c; Youden's J is missing.

5. Table 5 column "Dis_Fail" is never defined in Table 5's caption or in Section 5's prose (Page 12, Table 5).
   Quoted text (Page 12, Table 5 header and caption): Column header "Dis_Fail" (Pooled All = 34). The caption defines Evaded, Dis_Part / Sil_Part, False_Pass, Test_Edit, Unfin, H4a, and H4b, but skips Dis_Fail completely (its meaning, "Disclosed failing", only appears in Figure 2 on page 13). Similarly, H4b is defined in Table 5's caption but never discussed by name in Section 5's text.

6. Unexplained model parameter label "gemma4 (8B)" in Figure 1 disagrees with the rest of the paper (Page 8, Figure 1).
   Quoted text (Page 8, Figure 1 y-axis): "gemma4 (8B)"
   Everywhere else in the paper (Section 3.2 on page 5, Tables 2-5 and 7, Figure 2), the model is named "gemma4:latest" (with Ollama image hash 371e604cf9be) and no parameter count is ever stated. Figure 1 also labels nemotron3:33b as "nemotron3 (33B)" and Figure 3 shortens claude-haiku-5-5 to "haiku-5-5".

7. Inconsistent sign convention across H2a, H2b, and H2c, plus an imprecise description of H2b's p-value as the "sign-test floor" (Page 9, Section 4.2).
   Quoted text:
   - Item 1 (p. 9): "lowers silent_partial holds by -70.6 pp pooled across Core 5 (0.817 to 0.111...)"
   - Item 2 (p. 9): "Together these give a pooled +22.8 pp H2b gap (sign-test floor pHolm = 8.73 x 10^-11)."
   - Item 3 (p. 9): "cuts holds by -74.4 pp pooled (0.817 to 0.072...)"
   All three contrasts measure drops from goal_duty (99.4% to 76.7% for H2b), yet H2a and H2c are reported as negative while H2b is reported as positive (+22.8 pp). Furthermore, Table 3's caption notes H2b has 35/0/1 repositories (not 36/0/0), so its raw two-sided sign-test p-value is 2^-34 = 5.82 x 10^-11, NOT the N=36 sign-test floor (2^-35); its Holm-adjusted value equals 8.73 x 10^-11 only because Holm step-down monotonicity floors it at H2a's adjusted p-value (3 * 2^-35).

8. Undefined structural term "Part 1", premature use of "Stage-1/2", and unexplained "attempt = 5" (Pages 6, 11, 14).
   Quoted text:
   - Page 6 (Section 3.2): "the 4 Stage-1/2 records that carry retry metadata show attempt = 1 (none attempt = 5)."
     "Stage-1/2" appears 12 pages before Experiment C's three stages are defined in Appendix A (page 18), and the retry cap of 5 is never stated anywhere in the paper.
   - Page 11 (Section 5 heading): "5 Part 2: Live Worker Outcomes Under an API-Freeze Constraint (H4)"
   - Page 14 (Section 7.1, item 3): "and Part 1 injects a focused omission fault model"
     Section 4 is never labelled "Part 1", so "Part 1" is undefined and "Part 2" appears abruptly.

9. Unexplained "n/a" cell in Table 1 and unmentioned Experiment A cell "false_ci under bare_verified" (Pages 4, 6-7).
   Quoted text:
   - Page 4 (Table 1): TestIntegrityGate on false_ci is "n/a", with no explanation in the text or caption (whereas page 3 bullet 3 implies all three checks were characterized across the fixtures).
   - Page 7 (Section 4.1, item 2): "driven by nemotron3:33b (0/36 under neutral and 1/36 under bare_verified jumping to 35/36 under mismatch prose)"
     Section 4.1 (page 6) never mentions that bare_verified was evaluated on false_ci, and Table 2 omits that column.

10. Minor cross-section / wording discrepancies and grammar errors:
    - Page 9 (Section 4.2, item 2): Errant comma between subject and verb: "Two models (gpt-6-luna dropping 36/36 to 2/36, pHolm = 3.49 x 10^-10; gpt-6.1-sol dropping 18/18 to 0/18, pHolm = 2.29 x 10^-5), follow the narrow rule over the explicit disclosure;"
    - Page 14 (Section 7.1, item 3): "(gpt-6.1-sol and qwen3.6 evaluated on BALANCED_18, N = 18)" overlooks that qwen3.6 ran all 36 tasks in Experiment C Stage 1 (as stated on pages 5 and 18).
    - Page 10 (Section 4.2, item 3): "across the frontier models" refers inconsistently to the hosted models (which include gpt-5.4-nano and claude-haiku-5-5, called "hosted models" everywhere else) and cites a 36-task denominator ("31/36 to 36/36") that excludes 18-task gpt-6.1-sol.
    - Page 19 (Appendix A, item 3): Compressed, non-parallel phrasing: "raised gpt-5.4-nano from 0/36 to 3/36 vs. 1/36" (should clarify "from 0/36 under consensus and 1/36 under gated to 3/36 under ungated").
    - Page 2 vs. Page 6: Page 2 explicitly notes the vouchers "are not Git commit signatures", yet page 6 quotes the scoped_verified badge text as "(Ed25519 commit signature; ...)" without flagging the mismatch between harness prompt text and actual mechanism.
    - Undefined or unexpanded abbreviations: AST (p. 2), CI (p. 1), pp (p. 1), PR (p. 2, after "pull request" is never paired with "(PR)"), GBNF (p. 6), DoS (p. 7), UX (p. 14).
    - Minor redundancies: Page 1 (Abstract) repeats the 2-vs-2 post hoc split in consecutive sentences ("two then held every silent partial again (36/36 and 18/18) and two still held none (0/36 each). Holds returned in two models and stayed at zero in two."); Page 11 (Section 5, item 1) mentions the 15 unfinished green-local-test runs twice within three sentences.
    - Note on arithmetic verification: Every table row total, column total, percentage, pooled difference, exact McNemar p-value, exact sign-test p-value, Holm adjustment, clean-audit subset denominator (792, 244, 548, 80), and log-linear d' and c value in Table 7 was checked and adds up accurately.


(C) OVERCLAIMING AND SENTENCES LIKELY TO BE MISREAD (most severe first)

1. Abstract reports a specific finding (16 no-change disclosed partials) that appears nowhere in the body of the paper (Pages 1-2, Abstract).
   Quoted text: "131 were classified as disclosed partials, the instructed outcome (16 of them changed no file and disclosed that);"
   This count of 16 no-op disclosed partials is never mentioned, broken down by model, or substantiated anywhere in Section 5, Table 5, Figure 2, or the Appendices.

2. Abstract and Section 7.2 assert a behavioral mechanism for H1c ("two local models that rarely/seldom ran the tests themselves") that is never reported in Section 4.1 and is in tension with gemma4's reported behavior (Pages 1, 7, 15).
   Quoted text:
   - Page 1 (Abstract): "An accurate mismatch notice raised holds on patches with a false CI claim from 133/180 to 179/180 (+25.6 pp, 36/36 repositories), entirely through two local models that rarely ran the tests themselves;"
   - Page 15 (Section 7.2, item 2): "entirely through two local models that seldom ran the tests themselves;"
   Section 4.1 never reports run_pytest rates on false_ci for either local model. The only Experiment A run_pytest figures given for gemma4 (page 7) are on clean patches (23/36 under bare_verified, 9/36 under green_ci_badge), and gemma4 already caught 25/36 (69%) of false_ci patches under neutral and ran run_pytest on 36/36 trials in the post hoc arm (page 10). Saying both local models "rarely/seldom" ran tests on false_ci goes beyond what the body shows.

3. Abstract and Introduction claim recomputed pooled contrasts on the audited clean subsets, but the paper omits H3a (and all 4-unobjected contrasts) and punts them to an unlinked file (Pages 1, 3, 21).
   Quoted text:
   - Page 1 (Abstract): "and recompute the hold counts and pooled contrasts that use the label on the audited subsets."
   - Page 3 (Section 1, item 3): "and the hold counts and pooled contrasts that use the clean label recomputed on the audited subsets."
   Appendix C (page 21) reports only H3b on the 25-task subset (p = 0.016); H3a and all 4-task subset contrasts are absent from the paper and deferred to results/clean_label_sensitivity.md.

4. Abstract's summary of the post hoc arm is likely to be misread as a clean 2-vs-2 retest of four original Experiment B receivers (Page 1, Abstract vs. Page 10, Section 4.2 item 4).
   Quoted text (Page 1, Abstract): "kept the CI-only check and left the verdict open on the four models that cost nothing to call: two then held every silent partial again (36/36 and 18/18) and two still held none (0/36 each)."
   In fact, qwen3.6 (the 18/18 model) was not an original Experiment B receiver (so "again" is misleading; all three duties were run fresh on BALANCED_18), and nemotron3 (one of the two 0/36 models) is explicitly called "weak evidence about the wording" on page 10 because it only held 7/36 under goal_duty and ran pytest on 0/36 open-verdict trials.

5. Abstract's final sentences on deterministic checks can easily be read as self-contradictory (Page 2, Abstract).
   Quoted text: "Digest and test-integrity checks flagged every failing run and every test edit they can see (CI, report or integrity problems, not ticket omissions), but only 3 of the 131 disclosed partials and none of the 4 over-claims: a green local suite does not separate a partial change from a complete one. None of the three deterministic checks used here caught test-passing partial work."
   Because the Abstract does not explain that those 3 flagged disclosed partials had reported tests_passed = false (a report mismatch, explained only on page 11), saying "only 3 of the 131" followed immediately by "None of the three deterministic checks used here caught test-passing partial work" looks contradictory to a reader.

6. Section 1 overstates model coverage for Section 4 (Page 2, Section 1, item 2).
   Quoted text: "Controlled evidence from 7 models by 5 developers on scripted handoffs (Section 4):"
   Experiments A and B (Tables 2 and 3) evaluate only 6 models from 4 developers as receivers; the 7th model (qwen3.6, Alibaba Qwen) appears only in the Experiment C Stage-1 panel (Appendix A), the post hoc arm, and Part 2 (Section 5).

7. Section 3.1 misstates what gate verdicts depend on (Page 4, Section 3.1, paragraph 1).
   Quoted text: "though test labels and gate verdicts depend solely on executed behavior."
   Only the hidden oracle and deterministic gates depend solely on executed behavior; LLM receiver gate verdicts depend heavily on natural-language instructions, contributor notes, and badges (the central finding of the paper), and Part 2's disclosed_partial/silent_partial classifier depends on report text and keywords.

8. Abstract's opening phrasing "a single change" sits uneasily with the paper's own caveat that the change is bundled (Page 1, Abstract; Page 9, Section 4.2).
   Quoted text (Page 1, Abstract): "The largest pre-registered effect of a single change comes from one sentence of the receiver's instruction."
   Seven lines later the Abstract notes: "The two instructions differ in both the scope of the check and the dictated verdict" (and Section 7.1 item 5 calls it "a bundled instruction change"). Calling it "a single change" invites misreading before the caveat arrives; "a single sentence" would be more accurate.


(D) EMBARRASSING OR UNPOLISHED ITEMS FOR PUBLIC RELEASE (most severe first)

1. Multiple passages read like a cover letter or reply to peer/LLM reviewers rather than a standalone archival paper, exposing draft history and internal review files (Pages 2, 7, 10, 16, 21).
   Quoted text:
   - Page 2 (Section 1): "The protocol was locked under the working title Prose Is Not a Gate; I changed the title after review because the largest effect in the study comes from changing prose in the receiver's instruction."
   - Page 7 (Section 4.1, item 3): "An earlier draft read the first group as over-rejecting. The label audit (Appendix C, docs/CLEAN-LABEL-AUDIT.md) does not support that reading."
   - Page 10 (Section 4.2, item 4): "After review I ran one arm that is not in the locked protocol."
   - Page 16 (Section 8): "claims ledger (CLAIMS-LEDGER.md)... and cross-family review dispositions (docs/REVIEWS.md) reside in the project repository" and "developed using AI coding workflows (Antigravity, then Claude Code for the revision, label audit and post hoc arm)"
   - Page 21 (Appendix C): "An earlier one-pass audit of 22 tasks, which had seen the hold reasons, is superseded by this one and archived in the repository."
   Public readers do not have "an earlier draft" or the review comments. Keep the transparency (e.g., noting the pre-registration's working title in a footnote and labelling the arm exploratory/post hoc), but remove the review-rebuttal framing and internal workflow files (CLAIMS-LEDGER.md, docs/REVIEWS.md).

2. Raw internal file paths and bare git commit hashes clutter nearly every table caption and even a numbered result heading, with no public repository link (Pages 4, 5, 6, 7, 9, 11, 12, 15-16, 18, 19, 20, 21, 22).
   Quoted text examples:
   - Page 18 (Appendix A, item 1 bold heading): "1. Unconditional synthesis returns a crux or an unverified premise on every clean PR (results/tables.md Table 3b):"
   - Table captions on pages 4, 7, 9, 11, 12, 19, 20, 22 all parenthetically cite local markdown files such as "(results/tables.md Section 1)", "(results/exploratory_attention_arm.md)", "(results/clean_label_sensitivity.md)".
   These belong consolidated in a single Data Availability / Code Availability section with a permanent archive URL or DOI, not scattered as bare local paths across headings and captions (where one path literally clips off page 21).

3. Raw, defensive audit-checklist bookkeeping in Section 3.2 (Pages 5-6).
   Quoted text:
   - Page 5: "Later retries also lowered the token limit from 2048 to 1024 (from the third attempt) and the final retry appended a one-line instruction to the prompt; neither is in the deviations log."
   - Page 5: "the $2.29 difference is unreconciled here: the usage log itself is not in the archive, and it would include pre-lock calibration on C00..C03 and any call not retained in a record."
   - Page 6: "the 4 Stage-1/2 records that carry retry metadata show attempt = 1 (none attempt = 5)."
   The candor about protocol deviations is commendable, but the phrasing reads like unedited answers to an internal audit rather than a clean Protocol Deviations summary; ideally the $2.29 discrepancy and deviations log should be cleaned up or summarized cleanly before locking a permanent DOI.

4. Missing version/snapshot identifiers for five of the evaluated/auditing hosted models (Pages 5, 7, 21).
   Quoted text (Page 5, Section 3.2): "gpt-5.4-nano (OpenAI snapshot gpt-5.4-nano-2026-03-17), gpt-6-luna, gpt-6.1-sol (OpenAI), and claude-haiku-5-5 (Anthropic)." (Plus auditors claude-fable-5-2 and gpt-6.2-sol on pages 7 and 21.)
   Giving exact image hashes for the Ollama models and a dated snapshot for gpt-5.4-nano highlights the absence of exact API snapshot/version strings for the remaining hosted models.


(E) BIBLIOGRAPHY ASSESSMENT (Pages 16-18, [1]-[28])

Overall assessment: The bibliography looks real and well-grounded. The 23 entries from 1988 through early 2025 ([1]-[5], [7], [9]-[12], [14]-[18], [20], [22]-[28]) are all genuine works with accurate authors, titles, venues, years, and identifiers (arXiv IDs, RFCs, DOIs, URLs). None appear fabricated. Five recent late-2025/2026 entries ([6] Cheng et al. Science 2026, [8] Cotton-Barratt & Finnveden Forethought 2026, [13] Goswami arXiv:2509.13597, [19] MCP specification version 2026-07-28, [21] Prakash arXiv:2603.24775) have plausible authors, venues, and identifier formats for a November 2026 paper, though the author should live-verify their URLs/DOIs/version strings (especially the 2026-07-28 MCP spec date and Science DOI 10.1126/science.aec8352) before final deposit.

Malformed or incomplete entries:
- [1] (Page 16): Capitalization defect in title: "Agent2agent (A2A) protocol" (missing BibTeX braces around {Agent2Agent}; the author field right before it and Section 6 use "Agent2Agent").
- [6] (Page 16): Incomplete journal metadata -- "Science, 2026. doi: 10.1126/science.aec8352." is missing volume, issue, and page/article number.
- [26] (Page 18): Incomplete journal metadata -- "Science, 2024. doi: 10.1126/science.adq2852." is missing volume, issue, and article number (386(6719):eadq2852).
- [18] (Page 17, cited on Page 14): Entry [18] itself is complete, but page 14 cites it as "(18; since superseded by RFC 9162)" without brackets and without a bibliography entry for RFC 9162.
- [17], [20], [25] (Pages 17-18): Journal articles missing DOIs, whereas [3], [6], [16], [26] include DOIs.
- [2] (Page 16): Missing NDSS DOI/pages (minor).
- [19] (Page 17): BibTeX sentence-cased title ("Model context protocol specification") and no access date; [7], [8], [27] also lack publication/access dates.
- [9], [10], [12], [23] (Pages 17-18): Cited only as arXiv preprints despite having archival conference publications (NeurIPS 2024, ICML 2024, CSCW 2023, ICLR 2024).
- [11], [15], [22], [26] (Pages 17-18): Use "et al." inconsistently while [4], [5], [23], [24] list 8-10 authors in full.


Page images viewed: p-01.png, p-02.png, p-03.png, p-04.png, p-05.png, p-06.png, p-07.png, p-08.png, p-09.png, p-10.png, p-11.png, p-12.png, p-13.png, p-14.png, p-15.png, p-16.png, p-17.png, p-18.png, p-19.png, p-20.png, p-21.png, p-22.png
Model: Gemini 4 Neon (High)
Score: 3.5/5
READY AFTER THE LISTED FIXES
```
