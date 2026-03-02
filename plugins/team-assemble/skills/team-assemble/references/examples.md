# Team Assemble — Worked Examples

Three examples showing the full workflow for different task types.

---

## Example 1: Feature Development (Auth Refactor)

**User input**: "Assemble a team to refactor our authentication from session-based to JWT"

### Phase 1: Task Analysis

```
Relevant codebase areas:
- [x] src/auth/ — Current session-based auth implementation
- [x] src/middleware/ — Auth middleware
- [x] tests/auth/ — Auth test suite
- [ ] src/api/ — Uses auth but not directly modified
```

→ AskUserQuestion approval

### Phase 2: Codebase Scouts

auth-scout (opus) + middleware-scout (opus) launched in parallel:

```
Agent(name="auth-scout", model="opus", subagent_type="general-purpose", prompt="""
You are a codebase scout for the authentication area.
Task: Refactor from session-based to JWT authentication
Target path: src/auth/
...
""")
Agent(name="middleware-scout", model="opus", subagent_type="general-purpose", prompt="""
You are a codebase scout for the middleware area.
Task: Refactor from session-based to JWT authentication
Target path: src/middleware/
...
""")
```

### Phase 3: Integrate & Confirm

```
Proposed team: auth-refactor-team

| # | Agent | Role | Tasks | Dependencies |
|---|-------|------|-------|--------------|
| 1 | architect | System design | Design JWT flow, token strategy, migration path | - |
| 2 | implementer | Code changes | Implement JWT auth, update middleware | #1 |
| 3 | test-writer | Test coverage | Update auth tests for JWT flow | #2 |
| 4 | qa | Validation | PASS/FAIL against acceptance criteria | #2, #3 |

Acceptance criteria:
- [ ] AC-1: JWT token generation and validation implemented
- [ ] AC-2: All existing auth tests pass or are updated
- [ ] AC-3: Middleware correctly validates JWT tokens
- [ ] AC-4: No regression in existing API endpoints
```

→ AskUserQuestion final approval

### Phase 4: Execution

```
TeamCreate(team_name: "auth-refactor-team", description: "Refactor auth from session to JWT")

# Round 1: architect (independent)
Agent(name="architect", model="opus", ...)

# Round 2: implementer (#1 result included)
Agent(name="implementer", model="sonnet", prompt="Design:\n{architect_result}\n...")

# Round 3: test-writer (#2 result included)
Agent(name="test-writer", model="sonnet", prompt="Implementation:\n{implementer_result}\n...")
```

### Phase 5~6: Validate → Complete

qa PASS → result report → TeamDelete

---

## Example 2: Research & Decision Making

**User input**: "Use a team to evaluate caching strategies for our API — Redis vs Memcached vs in-memory"

### Phase 1: Task Analysis

```
Relevant codebase areas:
- [x] src/api/ — API endpoints that need caching
- [x] config/ — Infrastructure configuration
- [ ] tests/ — Not directly relevant yet

→ General research task — skip Phase 2 (no codebase scouting needed)
→ Design team directly using references/agents.md
```

### Phase 3: Team Design (Phase 2 skipped)

```
Proposed team: caching-eval-team

| # | Agent | Role | Tasks | Dependencies |
|---|-------|------|-------|--------------|
| 1 | redis-researcher | Redis analysis | Research Redis: features, performance, ops cost | - |
| 2 | memcached-researcher | Memcached analysis | Research Memcached: features, performance, ops cost | - |
| 3 | inmemory-researcher | In-memory analysis | Research in-memory caching: features, limits, trade-offs | - |
| 4 | analyst | Comparison | Synthesize findings into comparison matrix | #1, #2, #3 |
| 5 | qa | Validation | Verify completeness and accuracy | #4 |

Acceptance criteria:
- [ ] AC-1: All three options analyzed with feature/performance/cost dimensions
- [ ] AC-2: Comparison matrix with clear trade-offs
- [ ] AC-3: Recommendation with rationale based on our API's access patterns
```

### Phase 4: Execution

```
# Round 1: Three researchers in parallel (no dependencies)
Agent(name="redis-researcher", model="haiku", ...)
Agent(name="memcached-researcher", model="haiku", ...)
Agent(name="inmemory-researcher", model="haiku", ...)

# Round 2: analyst synthesizes (#1, #2, #3 results included)
Agent(name="analyst", model="sonnet", prompt="Research findings:\n{all_results}\n...")
```

### Phase 5~6: Validate → Complete

qa validates comparison matrix completeness → PASS → deliver report → TeamDelete

---

## Example 3: Multi-File Refactoring

**User input**: "Assemble a team to extract shared utilities from three microservices into a common library"

### Phase 1: Task Analysis

```
Relevant codebase areas:
- [x] services/user-service/src/utils/ — User service utilities
- [x] services/order-service/src/utils/ — Order service utilities
- [x] services/payment-service/src/utils/ — Payment service utilities
- [x] packages/ — Target for common library
```

→ AskUserQuestion approval

### Phase 2: Codebase Scouts

Three scouts launched in parallel (one per service):

```
Agent(name="user-svc-scout", model="opus", ...)
Agent(name="order-svc-scout", model="opus", ...)
Agent(name="payment-svc-scout", model="opus", ...)
```

Each scout identifies shared patterns and proposes extraction candidates.

### Phase 3: Integrate & Confirm

```
Proposed team: common-lib-team

| # | Agent | Role | Tasks | Dependencies |
|---|-------|------|-------|--------------|
| 1 | lib-architect | Library design | Define common lib API, module structure | - |
| 2 | lib-implementer | Create library | Build the common library package | #1 |
| 3 | user-svc-migrator | Service update | Update user-service to use common lib | #2 |
| 4 | order-svc-migrator | Service update | Update order-service to use common lib | #2 |
| 5 | payment-svc-migrator | Service update | Update payment-service to use common lib | #2 |
| 6 | qa | Validation | Verify all services work with common lib | #3, #4, #5 |

Acceptance criteria:
- [ ] AC-1: Common library created with shared utilities
- [ ] AC-2: All three services updated to import from common lib
- [ ] AC-3: No duplicate utility code remains in services
- [ ] AC-4: All existing tests pass
```

### Phase 4: Execution

```
# Round 1: lib-architect (independent)
Agent(name="lib-architect", model="opus", ...)

# Round 2: lib-implementer (#1 result)
Agent(name="lib-implementer", model="sonnet", ...)

# Round 3: Three migrators in parallel (#2 result, each owns different service)
Agent(name="user-svc-migrator", model="sonnet", ...)
Agent(name="order-svc-migrator", model="sonnet", ...)
Agent(name="payment-svc-migrator", model="sonnet", ...)
```

→ Round 3 agents run in parallel because they own non-overlapping files

### Phase 5~6: Validate → Complete

qa checks AC-1~4 → PASS → result report → TeamDelete
