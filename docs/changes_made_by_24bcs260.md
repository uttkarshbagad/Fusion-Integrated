# Changes Made by 24BCS260 — ELM Phase 2 Engineering Log

## 1. Student & Environment Configuration
- **Student Roll No**: 24BCS260
- **Repository**: `FusionIIIT/Fusion-Integrated`
- **Fork**: `https://github.com/uttkarshbagad/Fusion-Integrated`
- **Branch**: `elm-phase2`
- **Inherited Baseline**: Phase 1 implementation (`elm-pilot-qwen` / `ELM_MODEL_1`)
- **Machine**: Apple MacBook Air (M3, 16 GB Unified Memory)
- **Local AI Coding Model**: `qwen2.5-coder:7b` (via Ollama)
- **Coding Interface**: Continue VS Code Extension (Chat mode with `@file` context)

---

## 2. Inherited Phase-1 Baseline Audit
Reviewing the inherited Phase-1 code against the **ELM Specification Bundle v1.4** highlighted key areas requiring engineering attention:
1. **Incomplete Models**: `LeaveApplication` lacked a `reason` field, dropping user input. Status choices were limited to basic states (`PENDING`, `APPROVED`, etc.) without the workflow gates (`AWAITING_SUBSTITUTE`, `AWAITING_APPROVAL`) specified in `06_ELM_Workflow_Specifications_v1.6`. `SubstituteNomination` lacked a `status` field to record substitute consent (`BR-EL-015`).
2. **Missing Domain Validation**: No checks for leave balance sufficiency, date overlap (`BR-EL-012`), or self-nomination as substitute (`BR-EL-014`).
3. **Frontend Stubs**: `LeaveBalance.tsx` was empty; `LeaveApplication.tsx` only logged form inputs to `console.log` without calling the API.
4. **Test Coverage**: Zero unit or integration tests existed in `modules/elm/`.

---

## 3. Step-by-Step Prompts & Engineering Log

### Step 1 — Models & Workflow Schema Alignment
- **Target File**: `modules/elm/models.py`
- **Objective**: Align data models with workflow state lifecycles and persist leave reasons and substitute response statuses.
- **Prompt to Qwen2.5-Coder:7b**:
```text
@models.py
Review and update modules/elm/models.py to satisfy the ELM specifications:
1. In LeaveApplication:
   - Add a `reason` TextField (blank=True, default="").
   - Update `STATUS_CHOICES` to include:
     ('AWAITING_SUBSTITUTE', 'Awaiting Substitute Consent'),
     ('AWAITING_APPROVAL', 'Awaiting Approval'),
     ('APPROVED', 'Approved'),
     ('REJECTED', 'Rejected'),
     ('WITHDRAWN', 'Withdrawn'),
     ('CANCELLED', 'Cancelled')
   - Default status should be 'AWAITING_APPROVAL'.

2. In SubstituteNomination:
   - Add a `status` CharField with choices:
     ('PENDING', 'Pending Consent'),
     ('ACCEPTED', 'Accepted'),
     ('DECLINED', 'Declined')
     with default='PENDING'.
   - Add a `decline_reason` TextField (blank=True, default="").

Preserve all existing table names (Meta db_table) and integer ID conventions for Fusion compatibility.
```

- **Observations & Code Review**:
  - The model accurately updated `STATUS_CHOICES` and added `reason`, `SubstituteNomination.status`, and `decline_reason`.
  - **Defect Caught During Review**: The model retained `models.CharField(max_length=10)` on `LeaveApplication.status`. Because `"AWAITING_SUBSTITUTE"` is 19 characters, this would have triggered database truncation/`DataError` at runtime.
  - **Action**: Updated `max_length` to `30` on `LeaveApplication.status` and `20` on `SubstituteNomination.status`.

- **Commit**: `e4afea2` — `feat(elm): update models with workflow statuses and reasons`
