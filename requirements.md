# Requirements — Phase 0

## Functional Requirements

| ID | Requirement |
|----|-------------|
| FR-1 | Users can authenticate (log in). |
| FR-2 | Authenticated users can ask natural-language questions. |
| FR-3 | The system returns an answer grounded in company documents. |
| FR-4 | Answers include citations to the source document(s). |
| FR-5 | Authorized users can upload documents. |
| FR-6 | Authorized users can list and delete documents. |
| FR-7 | Different users have different permissions (RBAC). |
| FR-8 | Users can only retrieve/see documents they are authorized to access. |
| FR-9 | Documents belong to an organization (tenant); one org can never see
        another org's documents. |

## Non-Functional Requirements

| ID | Requirement | Why it matters |
|----|-------------|-----------------|
| NFR-1 | Secure | Company data is sensitive; leaks are unacceptable. |
| NFR-2 | Reliable | Employees depend on it daily; silent failures erode trust. |
| NFR-3 | Observable | When it breaks, engineers must find out why quickly. |
| NFR-4 | Maintainable | The codebase must stay understandable as it grows. |
| NFR-5 | Testable | Every layer should be verifiable without manual clicking. |
| NFR-6 | Incrementally scalable | Built to grow, not built for scale we don't have yet. |
| NFR-7 | Answers are grounded | The LLM should minimize hallucination — no citation, no claim. |

## Explicitly Out of Scope (for now)

- Multi-language support
- Real-time collaborative editing of documents
- Mobile app
- SSO / external identity provider integration (we build our own simple
  auth first, to learn the concepts — swapping in SSO later is a natural
  extension, not covered in these phases)

## How this document will be used

Every phase should trace back to at least one FR or NFR here. If we're
about to build something that doesn't map to a requirement, that's a signal
we might be over-engineering — stop and ask why.
