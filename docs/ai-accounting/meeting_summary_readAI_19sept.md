Summary:

The meeting defined how Bridgit should support staged bookkeeping, VAT, and wider accounting workflows.
• Start with job type, period, and available documents
• Use comparative files and completed jobs for training
• Separate transaction categorization from accounts-stage classification
• Add materiality reviews and client-specific thresholds
• Prioritize VAT, company accounts, and self-assessment
• Build reusable templates across common accounting services


Action Items:

* Mirza Raza will assess changes needed to separate Bridgit’s current one-pass processing into the firm’s staged bookkeeping workflow.
* Mirza Raza will incorporate job type, accounting period, and document context into Bridgit’s workflow design.
* Mirza Raza will continue developing the MA Associates integration so Bridgit can use job context and retrieve documents from OneDrive.
* Mirza Raza will ensure learned transaction treatments can be overridden when the circumstances of a later period differ.
* Mirza Raza will account for client-specific and proportional materiality checks in the reviewer-stage design.
* S FA will provide a completed job with its final working workbook and another job without the final working workbook for comparison.
* Mirza Raza will test the quarter-ending-May job and use the results to provide feedback on Bridget’s output.
* S FA will provide examples of recurring client correspondence that can be used as templates for future document generation.
* Mirza Raza will document the proposed template-bank requirements, including accounting templates and client-letter generation.
* S FA will provide representative accounting jobs from the highest-priority service types for Bridget’s training.
* Mirza Raza will investigate whether relevant open-source components or code associated with Nylon can be located in public repositories.


Key Discussion Points:

Walkthrough Scope and Bookkeeping Workflow
Mirza outlined the purpose of the walkthrough: to explain how a junior bookkeeper processes a real job and to capture the firm’s chart-of-accounts and VAT rules for Bridgit AI. Qasim described statement standardization, transfer into the working file, chart-of-accounts mapping, and the use of suspense for uncertain transactions.

Source Documents, Standard Outputs, and Comparative Files
S FA defined the common source documents and standard workbook outputs used across jobs. The team discussed how the initial bookkeeping analysis creates the basis for subsequent accounts work and how prior-period files support comparative coding and opening balances. First-year jobs without comparatives may use a similar job template and require additional refinement.

Exceptions, Matching, and Expense Classification
The group examined how to handle bank receipts without current-period invoices and distinguish prior-period receivables from unresolved items. They also agreed that Bridgit should initially categorize transactions and defer personal, business, and allowable-expense decisions to the appropriate accounts stage, using prior-period treatment where available.

Bridgit Capabilities and Current Limitations
Mirza demonstrated the back-end API workflow, including file reading, duplicate detection, prior-year coding, knowledge-base lookups, question generation, overrides, Excel output, and reconciliation controls. PDF extraction and the one-page summary were identified as works in progress, and the team recognized that Bridgit currently tries to perform multiple workflow stages at once.

Job Context, Period Validation, and Document Retrieval
S FA proposed that Bridgit establish the job type, accounting period, available documents, and missing information before processing. Qasim emphasized the need to validate the complete period, while Mirza described the planned MA Associates and OneDrive integration that would provide context and retrieve documents automatically.

Learning Rules, Exceptions, and Materiality Review
The group discussed how Bridgit should learn from user responses while allowing exceptions to prior decisions. They proposed a final reviewer stage that identifies unusually large or material transactions using client-specific thresholds or proportional tests before confirming the completed allocation.

Comparative Files and Training Jobs
Mirza and S FA clarified how prior-year or prior-quarter files could provide comparative information for Bridget. They identified the Kaliki and Sons VAT engagement as a new job without a comparative and agreed to use additional completed jobs, including versions with and without final workbooks, to strengthen training.

Test Job Delivery and Working-Paper Variations
S FA prepared a historically completed quarter-ending-May return and sent the relevant paperwork and comparative through OneDrive. The participants agreed that Bridget should use prior-quarter files as a guide while accommodating differences in client formats, documentation, and working-paper structures.

Template Bank and Document Generation
The team discussed creating a template bank for accounts, VAT, personal tax, property letting, self-employment, capital gains tax, and other services. They also proposed storing examples of engagement letters, regulatory correspondence, takeover letters, and other documents so Bridget could generate new versions from client-specific details.

Accounting and Tax Service Coverage
The participants reviewed the types of work Bridget may eventually support, including company accounts, self-assessment, property letting, CIS accounts, management accounts, partnership accounts, specialist tax advisory, and capital gains tax calculations. Mirza emphasized that Bridget initially needs baseline process knowledge, with detailed learning continuing through real client documents.

Representative Examples and Priority Workflows
Mirza asked for representative files from the most common service types rather than a complete example of every possible job. Company accounts, self-assessment, and VAT were identified as priority areas, with the broader goal of making Bridget sufficiently capable to handle common jobs before expanding coverage.

Subscription Costs and Specialist Integrations
The team discussed the cost of the relevant software plans and whether functionality from Nylon could be reproduced using open-source resources. Mirza explained how open-source components might be located, while Qasim suggested Nylon would be more valuable for specialist expense and tax-advisory cases than for routine chart-of-accounts tasks.


Notepad:

* No notes