# CliniqAI — Hands-On Lab Guide

**Course:** DSCI-275 Agentic AI with Cloudera Agent Studio  
**Domain:** Healthcare  
**Pattern:** Sequential Pipeline (5 agents, no Manager Agent)  
**Estimated time:** 60–75 minutes

---

## Overview

CliniqAI is an intelligent clinical documentation assistant built on Cloudera Agent Studio. It reads a patient CSV file, enriches each patient record with real FDA adverse-event data for their medications, generates a structured clinical assessment, and writes a professional PDF summary report — all without a single line of application code.

### What you will build

| # | Agent | Role | Tool |
|---|-------|------|------|
| 1 | **Patient Data Loader** | Reads the uploaded patient CSV | `csv reader tool` |
| 2 | **Medication Safety Analyst** | Queries FDA for adverse events per medication | `fda drug api tool` |
| 3 | **Clinical Assessment Agent** | Cross-references diagnoses, medications, and lab results | *(no external tool)* |
| 4 | **Report Structuring Agent** | Formats assessments into a clinical report document | *(no external tool)* |
| 5 | **PDF Report Generator** | Writes the final report to a shared PDF | Built-in: **Write to Shared PDF** |

### Architecture

```
[CSV Upload] → Patient Data Loader → Medication Safety Analyst
                                              ↓
                               Clinical Assessment Agent
                                              ↓
                               Report Structuring Agent
                                              ↓
                               PDF Report Generator → [clinical_summary_report.pdf]
```

---

## Prerequisites

- Access to a **Cloudera AI Workbench** environment with **Agent Studio** enabled
- No external API keys required (FDA OpenFDA API is free and public)
- The sample dataset `data/patients.csv` is included in this repository

---

## Part 1 — Create the Custom Tools

### Step 1 — Open Tools Catalog

1. Log in to Cloudera Agent Studio.
2. In the top navigation bar, click **Tools Catalog**.
3. You will see built-in tools (CSV Reader, Write to Shared PDF, etc.) and a **Create Tool Template** button.

---

### Step 2 — Create the `csv reader tool`

1. Click **Create Tool Template**.
2. In the **Tool Name** field, enter:
   ```
   csv reader tool
   ```
   > **Important:** Tool names in Agent Studio use **spaces, not underscores**. Enter the name exactly as shown.
3. Click **Generate** to create the template.
4. Click **Edit Tool File** → click **Edit** next to `tool.py`.
5. Replace the entire contents of `tool.py` with the code from:
   ```
   cliniqai/tools/csv reader tool.py
   ```
6. The `requirements.txt` for this tool only needs `pydantic` (already in the default template). No changes needed.
7. Click **Save**.

---

### Step 3 — Create the `fda drug api tool`

1. Click **Create Tool Template**.
2. Enter the tool name:
   ```
   fda drug api tool
   ```
3. Click **Generate**.
4. Click **Edit Tool File** → **Edit** next to `tool.py`.
5. Replace the entire contents with the code from:
   ```
   cliniqai/tools/fda drug api tool.py
   ```
6. In `requirements.txt`, ensure it contains:
   ```
   # https://pip.pypa.io/en/stable/reference/requirements-file-format/
   pydantic
   requests
   ```
7. Click **Save**.

---

### Step 4 — Confirm tools in the catalog

After saving both tools, go back to **Tools Catalog**. You should see:
- `csv reader tool`
- `fda drug api tool`

listed alongside the built-in tools.

---

## Part 2 — Create the Agentic Workflow

### Step 5 — Create a new workflow

1. Click **Agentic Workflows** in the top navigation.
2. Click **+ New Workflow** (or **Create Workflow**).
3. Name your workflow:
   ```
   CliniqAI XX
   ```
   *(Replace `XX` with your initials to keep it unique in a shared environment.)*
4. Click **Create**.

---

### Step 6 — Configure workflow settings

1. Open the workflow and click **Edit Workflow**.
2. Click the **Configure** tab.
3. Set the following:

   | Setting | Value |
   |---------|-------|
   | **Conversational** | **OFF** |
   | **Manager Agent** | **OFF** |

   > Both must be OFF. CliniqAI is a sequential pipeline — each agent passes its output to the next in a fixed order.

4. Click **Save** (or proceed to **Add Tasks**).

---

### Step 7 — Add Task: Patient Data Loader

1. Click **Add Tasks** → **Create or Edit Agents**.
2. Click **+ Create New Agent**.
3. Fill in the agent details:

   | Field | Value |
   |-------|-------|
   | **Name** | `patient_data_loader` |
   | **Role** | Patient Data Loader |
   | **Backstory** | You are an expert at reading and parsing structured patient data from CSV files. You extract patient records accurately and pass them to the next agent for analysis. |
   | **Goal** | Read the uploaded patient CSV file and return all patient records in a structured format. |
   | **LLM Model** | gpt-4o (Default) |

4. Under **Add Tools**, click **Create or Edit Tools**.
5. Search for `csv reader tool` and click **Create Tool from Template** to add it to this agent.
6. Click **Save Agent**.

---

### Step 8 — Add Task: Medication Safety Analyst

1. Click **+ Create New Agent**.
2. Fill in:

   | Field | Value |
   |-------|-------|
   | **Name** | `medication_safety_analyst` |
   | **Role** | Medication Safety Analyst |
   | **Backstory** | You are a clinical pharmacist with expertise in drug safety databases. You look up FDA adverse event records for each medication a patient is taking and summarise the most frequently reported reactions. |
   | **Goal** | For each patient in the dataset, query the FDA adverse event database for each of their medications and return a structured summary of known adverse reactions. |
   | **LLM Model** | gpt-4o (Default) |

3. Under **Add Tools**, add `fda drug api tool`.
4. Click **Save Agent**.

---

### Step 9 — Add Task: Clinical Assessment Agent

1. Click **+ Create New Agent**.
2. Fill in:

   | Field | Value |
   |-------|-------|
   | **Name** | `clinical_assessment_agent` |
   | **Role** | Clinical Assessment Specialist |
   | **Backstory** | You are a senior clinician with deep expertise in internal medicine. You review patient records holistically — cross-referencing diagnoses, current medications, lab results, and known drug adverse events — to identify clinical risks, contraindications, and care gaps. |
   | **Goal** | For each patient, produce a structured clinical assessment that includes: (1) a brief case summary, (2) identified medication risks or interactions based on the FDA data, (3) concerning lab values, and (4) recommended clinical actions or monitoring priorities. |
   | **LLM Model** | gpt-4o (Default) |

3. No external tools needed for this agent.
4. Click **Save Agent**.

---

### Step 10 — Add Task: Report Structuring Agent

1. Click **+ Create New Agent**.
2. Fill in:

   | Field | Value |
   |-------|-------|
   | **Name** | `report_structuring_agent` |
   | **Role** | Clinical Report Writer |
   | **Backstory** | You are a medical documentation specialist who transforms clinical assessments into clear, professional reports formatted for clinical handover. |
   | **Goal** | Take the clinical assessments for all patients and format them into a single, well-structured clinical summary report. Use clear section headings for each patient. Include a brief executive summary at the top listing the highest-priority patients. Format the output as clean markdown suitable for PDF conversion. |
   | **LLM Model** | gpt-4o (Default) |

3. No external tools needed.
4. Click **Save Agent**.

---

### Step 11 — Add Task: PDF Report Generator

1. Click **+ Create New Agent**.
2. Fill in:

   | Field | Value |
   |-------|-------|
   | **Name** | `pdf_report_generator` |
   | **Role** | PDF Report Generator |
   | **Backstory** | You convert structured clinical reports into professional PDF documents that can be shared with clinical teams. |
   | **Goal** | Take the formatted clinical report markdown and write it to a PDF file named `clinical_summary_report.pdf` using the Write to Shared PDF tool. |
   | **LLM Model** | gpt-4o (Default) |

3. Under **Add Tools**, search for and add the built-in **Write to Shared PDF** tool.
4. Click **Save Agent**.

---

### Step 12 — Verify the agent pipeline

After creating all five agents, click on **Add Tasks** and confirm the pipeline shows the agents in this order:

```
patient_data_loader
      ↓
medication_safety_analyst
      ↓
clinical_assessment_agent
      ↓
report_structuring_agent
      ↓
pdf_report_generator
```

If the order is wrong, drag agents to reorder them.

---

## Part 3 — Test the Workflow

### Step 13 — Navigate to the Test screen

1. Click the **Test** tab in the workflow editor.

---

### Step 14 — Upload the patient CSV

1. In the Test screen, you will see an **Attachments** field (or a file upload area).
2. Upload the file:
   ```
   cliniqai/data/patients.csv
   ```
3. In the **Input** text box, enter:
   ```
   Analyse the uploaded patient file and generate a clinical summary report.
   ```

> **How `{Attachments}` works:** The `csv reader tool` accepts a `file_path` parameter. When the patient CSV is uploaded in the Test screen, Agent Studio sets `{Attachments}` to the file's path in the shared workspace. The agent passes this path to the tool automatically.

---

### Step 15 — Run and observe

1. Click **Run**.
2. Watch each agent's progress in the task panel:
   - **Patient Data Loader** — reads and returns 8 patient records
   - **Medication Safety Analyst** — queries FDA for each drug; expect 5–15 reactions per medication
   - **Clinical Assessment Agent** — generates assessments with risks and recommendations
   - **Report Structuring Agent** — formats the executive summary + per-patient sections
   - **PDF Report Generator** — writes `clinical_summary_report.pdf`

> **Typical runtime:** 3–6 minutes depending on the number of FDA API calls.

---

### Step 16 — Review the output PDF

1. After the run completes, navigate to **Files** in the Agent Studio workspace.
2. Locate `clinical_summary_report.pdf`.
3. Open it to verify:
   - Executive summary listing the highest-risk patients
   - Per-patient sections with diagnosis summary, medication risks, and clinical recommendations
   - Clean formatting with section headings

---

## Part 4 — Deploy the Workflow

### Step 17 — Deploy

1. Click the **Deploy** tab.
2. Click **Deploy Workflow**.
3. Once deployed, the workflow is available via the Agent Studio API endpoint and can be integrated with other Cloudera services.

---

## Expected Output Sample

Below is an excerpt from a typical `clinical_summary_report.pdf`:

```
CLINICAL SUMMARY REPORT
Generated by CliniqAI — Cloudera Agent Studio
Date: [run date]

EXECUTIVE SUMMARY — HIGH PRIORITY PATIENTS
==========================================
1. Carlos Rivera (P002) — INR 2.8 with K+ 3.4: warfarin over-anticoagulation risk 
   combined with electrolyte imbalance requires urgent review.
2. Rajiv Sharma (P006) — CKD Stage 3b with K+ 5.2: hyperkalaemia risk; atorvastatin 
   dose may need renal adjustment.
3. Samuel Okonkwo (P004) — Active prednisolone course driving glucose to 178 mg/dL; 
   metformin dose review recommended.

---

PATIENT: Aisha Patel (P001)
Age: 58 | Gender: Female
Diagnosis: Type 2 Diabetes; Hypertension
...
```

---

## Troubleshooting

| Issue | Likely cause | Fix |
|-------|-------------|-----|
| `File not found` error from csv reader tool | `file_path` not set to `{Attachments}` | In the agent's tool call, set the `file_path` parameter to `{Attachments}` |
| FDA tool returns no results | Drug name capitalisation or spacing | Try generic name in lowercase (e.g. `metformin` not `Metformin 500mg`) |
| PDF not appearing in Files | Write to Shared PDF not saved | Confirm the built-in tool was added and the agent is the last in the pipeline |
| Pipeline stops after first agent | Manager Agent accidentally ON | Go to Configure → set Manager Agent to OFF |

---

## Files in This Lab

```
cliniqai/
├── tools/
│   ├── csv reader tool.py        ← Tool 1: reads patient CSV
│   └── fda drug api tool.py      ← Tool 2: queries FDA adverse events
├── data/
│   └── patients.csv              ← Sample dataset (8 patients)
├── requirements.txt
└── README.md                     ← This guide
```

---

## Key Learning Points

- **Sequential Pipeline pattern:** Each agent's output becomes the next agent's input — no manager agent needed.
- **`{Attachments}` variable:** Allows students to upload files from the Test screen without hardcoding paths.
- **Free public APIs:** The FDA OpenFDA API requires no key and is accessible from Cloudera AI Workbench.
- **Built-in tools:** "Write to Shared PDF" is a Cloudera-provided tool — no custom PDF code required.
- **Separation of concerns:** Each agent has one clearly defined responsibility, making the pipeline easy to debug and extend.
