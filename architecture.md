# Architecture — Phase 0

This document describes the system at a high level, before any code exists.
It will evolve as we add phases. Nothing here is final — it's the map we use
to know why each phase exists.

## 1. What we're building

An internal tool that lets employees ask natural-language questions and get
answers grounded in their company's own documents (policies, wikis, PDFs,
etc.), with citations back to the source — and only from documents they're
actually allowed to see.

## 2. Who uses it

- **Employees** — ask questions, read answers, see citations.
- **Document owners / admins** — upload documents, manage who can access them.
- **Platform engineers (us)** — operate, monitor, and evolve the system.

## 3. System boundaries

What the system IS responsible for:
- Storing and indexing company documents
- Answering questions grounded in those documents
- Enforcing who can see what
- Being reliable and observable enough to run in production

What it is NOT responsible for (out of scope, at least for now):
- Being a general-purpose chatbot with no document grounding
- Editing or authoring documents
- Replacing existing identity systems (we build our own auth for learning
  purposes, but a real company would likely plug into SSO/OKTA/Azure AD)

## 4. Functional requirements

See `requirements.md` for the full list — summarized here:
1. Users authenticate.
2. Users ask questions and get grounded answers with citations.
3. Users can only retrieve information from documents they're authorized
   to access.
4. Authorized users can upload/manage documents.
5. Different users/roles have different permissions.

## 5. Non-functional requirements

- **Secure** — no data leaks across users or tenants.
- **Reliable** — failures are handled, not silent.
- **Observable** — when something breaks, we can find out why.
- **Maintainable** — a new engineer (future-you) can understand the code.
- **Incrementally scalable** — we don't over-build for scale we don't have
  yet, but we don't paint ourselves into a corner either.

## 6. High-level component map (where we're heading)

This is the *eventual* picture. We are nowhere near all of this yet — most
boxes below don't exist until their phase is reached.

```text
                    ┌─────────────┐
                    │   Client    │
                    └──────┬──────┘
                           │ HTTPS
                           ▼
                    ┌─────────────┐
                    │   FastAPI   │  ← Phase 1 (we are here)
                    └──────┬──────┘
                           │
            ┌──────────────┼───────────────┐
            ▼              ▼               ▼
      ┌───────────┐  ┌───────────┐   ┌───────────┐
      │   Auth    │  │  Documents │   │   Ask     │
      │ (Phase 4) │  │ (Phase 7)  │   │(Phase 13) │
      └───────────┘  └─────┬──────┘   └─────┬─────┘
                            │                │
                            ▼                ▼
                     ┌────────────┐   ┌─────────────┐
                     │ Ingestion  │   │  Retrieval   │
                     │ (Phase 8)  │   │ (Phase 10-12)│
                     └─────┬──────┘   └─────┬────────┘
                           ▼                ▼
                    ┌────────────┐   ┌─────────────┐
                    │  Vector DB │◄──┤     LLM      │
                    │ (Phase 9)  │   │ (Phase 13)   │
                    └────────────┘   └─────────────┘

      ┌────────────┐   ┌────────────┐
      │ PostgreSQL │   │   Redis     │
      │ (Phase 3)  │   │ (Phase 16)  │
      └────────────┘   └────────────┘
```

## 7. Data flow (target state, far future)

```text
User Question
     ↓
Authentication      → who are you?
     ↓
Authorization       → what are you allowed to see?
     ↓
Retrieval           → find relevant chunks (only from allowed docs)
     ↓
Reranking           → pick the best few
     ↓
Context assembly    → build the prompt
     ↓
LLM                 → generate an answer
     ↓
Answer + citations  → returned to user
```

## 8. API boundaries (what we're building first)

Phase 1 gives us three endpoints, no auth yet, no real logic:

```text
GET  /health
GET  /
POST /api/v1/ask
```

Everything else in the diagram above gets bolted on phase by phase.

## 9. What changes phase to phase

Each phase either:
- adds a new capability (e.g. Phase 4 adds login), or
- replaces a placeholder with a real implementation (e.g. Phase 13 replaces
  the fake "answer will be implemented later" with a real LLM call)

We will never jump ahead — e.g. we will not add JWT logic until Phase 4,
even though it's tempting to "just add it now."
