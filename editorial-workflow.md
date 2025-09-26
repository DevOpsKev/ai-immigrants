# editorial-workflow.md

## 📘 Purpose
This document defines the repeatable **chapter improvement workflow** for *AI Immigrants: The Bloody Algos Are Here!*  

It ensures every chapter passes through a consistent cycle of drafting, sourcing, critique, editing, and finalization — while staying aligned with the **Writer’s Guide**, **Editorial Guide**, and **Agentic Template**.

---

## 🔄 Chapter Editorial Workflow

### **0. Prep**
- Create a new scaffolded draft in `/drafts/` (e.g., `chXX-working.md`).  
- Commit with:  
  ```
  feat(chXX): add scaffold for [chapter title]
  ```

---

### **1. First Draft (Narrator + Researcher)**
- Run **Narrator + Researcher** agents using the chapter prompt.  
- Requirements:  
  - Use immigrant metaphor consistently.  
  - Narrative nonfiction voice, accessible but serious.  
  - Insert `[REF: …]` markers for citations (no fabrications).  
- Save to `drafts/chXX-working.md`.  
- Commit:  
  ```
  feat(chXX): add first draft of [chapter title]
  ```

---

### **2. Researcher Pass (Fill References)**
- Run **Researcher** agent on the draft.  
- For every `[REF: …]` marker:  
  - Propose 2–3 credible sources (APA 7th format).  
  - Provide a 1-sentence relevance note.  
  - Include a key quote or data point.  
- Manually verify at least some references before accepting.  
- Add `## References` section to the draft.  
- Commit:  
  ```
  chore(chXX): add APA references and notes
  ```

---

### **3. Critic Pass (Toughen Argument)**
- Run **Critic** agent on the updated draft.  
- Output should flag:  
  - Over-claims or weak reasoning.  
  - Missing nuance/counterexamples.  
  - Duplication of earlier chapters.  
  - Clichés or weak use of metaphor.  
- Address each point with edits in `chXX-working.md`.  
- Commit:  
  ```
  refactor(chXX): applied critic feedback
  ```

---

### **4. Editor Pass (Polish & Align)**
- Run **Editor** agent.  
- Checks:  
  - APA 7th in-text + end references.  
  - Grammar, flow, parallel structure.  
  - Readability > 60 (Flesch).  
  - Terminology consistency (AI system/model/agent).  
- Save final version as `/final/chXX.md`.  
- Commit:  
  ```
  feat(chXX): finalize chapter [title]
  ```

---

### **5. QA Checklist (Definition of Done)**
- [ ] Hook is compelling (≤ 2 paragraphs).  
- [ ] All promised themes covered.  
- [ ] Balanced view: AI as tool vs human misuse.  
- [ ] Citations present, credible, and formatted APA 7th.  
- [ ] No duplication of earlier chapters.  
- [ ] Ends with reflection tied back to the hook.  
- [ ] Readable, polished, and audiobook-ready.  

---

### **6. Merge into Manuscript**
- Append `/final/chXX.md` into master manuscript (e.g., `/publish/manuscript.md`).  
- Commit:  
  ```
  feat(book): merge chapter [XX] into manuscript
  ```

---

### **7. Optional Post-Processing**
- **Audio check**: run through ElevenLabs to catch awkward phrasing.  
- **Peer review**: share selected sections for outside feedback.  
- **Sensitivity check**: flag content warnings where needed (e.g., violence, self-harm).  

---

## 🚀 Benefits
- Scales across chapters.  
- Encourages continuous improvement.  
- Locks in consistency with book’s voice, tone, and metaphor.  
- Builds a verifiable reference trail (APA citations, GitHub commits).  
