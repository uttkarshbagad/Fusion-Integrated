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

---

### Step 2 — Pure-Python Domain Business Rules & Transitions
- **Target File**: `modules/elm/domain/policy.py`
- **Objective**: Implement pure-Python domain business rules (`BR-EL-012`, `BR-EL-014`, balance validation, and workflow state transitions) with no Django or ORM dependencies.
- **Prompt to Qwen2.5-Coder:7b**:
```text
@policy.py
Update modules/elm/domain/policy.py with pure-Python business rules from the ELM Specification Bundle (no Django or ORM imports):

1. Add `validate_substitute_eligibility(applicant_id: int, substitute_id: int) -> None`:
   - Raise ValueError if applicant_id == substitute_id (BR-EL-014).

2. Add `check_date_overlap(start_a: date, end_a: date, start_b: date, end_b: date) -> bool`:
   - Return True if the two date intervals [start_a, end_a] and [start_b, end_b] overlap (BR-EL-012).

3. Add `validate_balance_sufficiency(current_balance: float | int, requested_days: float | int) -> None`:
   - Raise ValueError("Insufficient leave balance") if requested_days > current_balance.

4. Add `is_valid_transition(current_status: str, target_status: str) -> bool`:
   - Implement the allowed state transitions:
     - AWAITING_SUBSTITUTE -> AWAITING_APPROVAL, WITHDRAWN
     - AWAITING_APPROVAL -> APPROVED, REJECTED, WITHDRAWN
     - APPROVED -> CANCELLED
   - Return False for all other transitions.

Keep all existing LeaveCode, LeaveEntitlement, LEAVE_ENTITLEMENTS, and requested_days functions intact.
```

- **Observations & Code Review**:
  - The model correctly added `validate_substitute_eligibility`, `check_date_overlap`, `validate_balance_sufficiency`, and `is_valid_transition`.
  - Zero Django or ORM dependencies were introduced, fully respecting Fusion ERP's strict architecture rule (`domain/` may not import Django, DRF or Celery).

