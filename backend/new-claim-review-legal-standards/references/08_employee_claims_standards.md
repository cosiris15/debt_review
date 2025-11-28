# Labor Claim Settlement Standards
# 劳动债权清偿顺序标准

## Purpose

Review standards for labor claims priority and settlement in civil debt contexts, including recognition, priority order, and statute of limitations under Labor Contract Law.

---

## Part 1: Labor Claim Definition and Scope

### 1.1 Legal Basis

**Labor Contract Law Articles 46-47**: Economic compensation for termination
**Labor Dispute Mediation and Arbitration Law Article 27**: 1-year arbitration limitation

### 1.2 Scope of Labor Claims

**(1) Unpaid Wages and Salaries (工资)**:
- Regular wages, bonuses, allowances
- Unpaid compensation for work performed

**(2) Economic Compensation (经济补偿金)**:
- Severance pay per Labor Contract Law
- Termination compensation for unlawful dismissal

**(3) Social Insurance Contributions (社会保险)**:
- Employee portion of pension, medical, unemployment insurance
- Unpaid contributions that should be credited to employee accounts

**(4) Overtime Pay and Benefits**:
- Unpaid overtime compensation
- Statutory holidays pay
- Annual leave compensation

---

## Part 2: Priority in Civil Execution

### 2.1 Execution Priority Order

**Supreme Court Civil Execution Interpretations**:

When multiple creditors seek execution of same debtor property:

1. **Labor claims** (wages, severance) → **First priority** among ordinary claims
2. Secured claims (within collateral value)
3. Tax claims
4. Other ordinary claims

**Rationale**: Labor claims have special protection for livelihood purposes

### 2.2 Application in Debt Review

**When reviewing mixed debt portfolio**:
- Identify labor claims separately
- Note priority status in risk identification
- In claimable range analysis: Labor claims have higher recovery probability

---

## Part 3: Statute of Limitations

### 3.1 Labor Arbitration Limitation Period

**Labor Dispute Mediation and Arbitration Law Article 27**:
- **1-year limitation** from date employee knew or should have known of rights infringement
- Exception: Ongoing employment relationship (limitation suspended until termination)

### 3.2 Civil Litigation After Arbitration

**Civil Procedure Law**:
- After arbitration: 15 days to file civil lawsuit if dissatisfied
- If arbitration missed: May directly file civil lawsuit (3-year general limitation)

### 3.3 Review Application

**When reviewing labor claims**:

```
□ Identify claim accrual date (last unpaid wage date, termination date, etc.)
□ Check if 1-year arbitration limitation expired
□ If expired: Mark as "statute risk - high" (★★★)
□ If within limitation: Evaluate based on evidence strength
```

---

## Part 4: Calculation of Severance Pay

### 4.1 Formula

```
Severance Pay = Monthly Wage × Years of Service
```

**Years of Service**:
- 6 months or more → Round up to 1 year
- Less than 6 months → 0.5 year

**Monthly Wage**: Average monthly wage in 12 months before termination

**Caps** (Labor Contract Law Article 47):
- If monthly wage > 3× local average wage: Capped at 3× local average
- Years counted: Maximum 12 years (for capped wages)

### 4.2 Review Application

**When reviewing severance pay claims**:
1. Verify termination date and reason (lawful termination required)
2. Calculate years of service
3. Verify average monthly wage (request payroll records)
4. Apply caps if applicable
5. Compare claimed amount vs. calculated amount

---

## Part 5: Evidence Evaluation

### 5.1 High-Strength Evidence

- Labor contracts with company seal
- Payroll bank transfer records
- Social insurance payment records
- Company-issued termination notices

### 5.2 Medium-Strength Evidence

- Signed attendance records
- Colleague witness testimony
- WeChat/email communications about work

### 5.3 Low-Strength Evidence

- Unilateral wage calculations (without company confirmation)
- Unsigned draft contracts
- Verbal agreements only

---

## Summary Checklist

**Labor Claim Review**:
```
□ Identified claim type (wages, severance, insurance, etc.)?
□ Verified employment relationship (contract, social insurance records)?
□ Checked arbitration/litigation limitation period?
□ Calculated severance pay if applicable (wage × years with caps)?
□ Evaluated evidence strength (High/Medium/Low)?
□ Noted priority status in execution context?
□ Assessed statute risk (within 1-year limitation or expired)?
```

---

## Cross-References

- Statute of limitations: `01_subject_and_evidence_standards.md`
- Evidence evaluation principles: `claim-review-foundations` Skill
- Calculation methodology: Use universal_debt_calculator_cli.py for interest on delayed wages
