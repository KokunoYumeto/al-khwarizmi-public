# Dormant manual prompts

Run each job independently, or consecutively only after sealing the previous checkpoint. The ranges are exact and non-overlapping.

For each job, paste file 01, then say:

> Transcribe JOB NN from file 03, using the corresponding 400-ppi authority ZIP in files 05-08. Transcribe every assigned frame completely and source-faithfully into LaTeX. Preserve Arabic, formulas, diagrams, tables, editorial matter, punctuation, and printer errors. No translation in place of transcription, summary, silent normalization, or imported readings. Return `.tex`, physical-frame ledger, unresolved-reading ledger, seam checks, and last fully sealed frame. Stop at the declared end.

Jobs:

1. JOB01 physical frames 001-035, file 05.
2. JOB02 physical frames 036-070, file 06.
3. JOB03 physical frames 071-105, file 07.
4. JOB04 physical frames 106-130, file 08.

After all jobs, run a separate integration/audit pass: replay all 130 source frames, verify every formula and diagram, verify seams, build cleanly, preserve an unresolved ledger, and make no silent source changes.
