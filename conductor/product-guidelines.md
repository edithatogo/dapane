# Product guidelines

## Inputs and scope

Ask for the decision, perspective, valuation basis, time basis and output
denominator before presenting a cost. Keep observed, derived, assumed and
simulated inputs distinguishable. Show source/effective dates and unresolved
inputs where they affect the interpretation.

Use domain packages to supply meaningful labels and defaults, with provenance.
A generic framework must not silently introduce a clinical pathway, employment
condition, inflation method or jurisdictional tariff. Preserve explicit choices
when an input bundle is reopened or revalued.

## Results and explanations

Lead with the result relevant to the requested decision and its completeness.
Make component detail, allocation reconciliation and source lineage inspectable.
Distinguish a total source ledger from allocated views of that same total. Display
units, currency, price year and denominator alongside monetary outputs.

Explain changes as changes in quantities, quotations, methods, scope or allocation
where the model supports that attribution. Show diagnostics when attribution is
ambiguous. Never display missing values or failed calculations as zero.

## Interfaces

Python, R, Julia, CLI and operational UIs consume the same contracts. Keep native
packaging and implementation details out of user workflows unless they affect a
decision. Use accessible tables and controls, explicit error messages and
exportable evidence bundles. Large payloads should not need to be rendered in a
form or copied into SharePoint List cells.

## Evidence and claims

Label every synthetic fixture prominently. Separate planned, implemented,
fixture-verified, installed-artifact-verified and externally validated
capabilities. Do not use one global badge to imply all those properties.

Reporting completeness, methodological appraisal, computational verification and
empirical validation are independent. A source licence, an accessible URL or a
SHACL pass does not establish factual truth or scientific validity.

## Product scope and optionality

Provide a useful local workflow before adding institutional surfaces. Preserve a
standard Power Apps option and keep premium services optional. Browser execution,
process mining, simulation, distributed compute and decision libraries are
separate capabilities with their own evidence. No optional integration should be
required to run the initial static costing example.
