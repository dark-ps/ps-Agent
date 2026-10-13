---
name: code-debugging-workflow
description: Code Debugging Workflow: inspect, plan, execute, verify, and recover this workflow safely.
version: 2.0
---

# Code Debugging Workflow

## Mission
This skill is a complete operational playbook for **debugging** work in the **code** domain, with a
**workflow** operating profile. It is designed for an agent that can inspect a real workspace,
choose tools deliberately, make small reversible changes, verify outcomes, and report exactly
what happened. Do not treat this file as a generic explanation: use it as a procedure.

## When to activate
Activate this skill when the task contains a meaningful request about debugging, especially when
the request requires more than a single read-only lookup. If another skill is more specific,
activate that skill as well only when its instructions are genuinely required. Prefer the
smallest useful skill set; do not activate a large collection merely because it is available.

Typical triggers include:
- inspecting an existing project or file before changing it;
- locating a symbol, string, configuration value, dependency, or relevant section;
- making a focused edit while preserving unrelated content;
- running a check, test, build, migration, script, or project command;
- diagnosing a failure from concrete output;
- validating that a change actually took effect;
- preparing a reversible change with a clear rollback path.

## Operating contract
1. **Inspect before modifying.** Establish the project root, relevant files, file type,
   size, line count, and current state before writing.
2. **Minimize scope.** Change only what the task requires. Preserve existing behavior,
   public interfaces, configuration, comments, and developer-provided constraints unless
   the requested change explicitly replaces them.
3. **Prefer targeted operations.** For a small change, use a precise patch/replacement
   rather than rewriting an entire large file.
4. **Keep evidence.** Capture the important command output, diff, affected paths, and
   validation result in the project memory/database when available.
5. **Verify after every write.** Re-read the affected region, inspect the diff, and run
   the narrowest useful validation before claiming completion.
6. **Recover instead of guessing.** If a command fails, preserve the error, identify its
   category, make one evidence-based adjustment, and retry only when safe.
7. **Respect boundaries.** Never escape the authorized workspace, expose secrets, or
   silently weaken safety checks.
8. **Be honest about completion.** A successful write is not proof of a successful build,
   and a successful command is not proof that the requested behavior works.

## Progressive workflow

### Phase A — Discover
- Resolve the workspace/project root.
- List the smallest relevant directory first.
- Locate candidate files by exact name, extension, symbol, or content search.
- Inspect metadata: file size, line count, encoding, timestamps, and hash where useful.
- For large files, read the relevant line range instead of loading the entire file.
- For binary assets, inspect metadata and use a suitable specialized tool rather than
  treating binary bytes as text.
- Identify dependencies and neighboring files that define the behavior being changed.

### Phase B — Understand
Build a short dependency map:
- **Target:** the file, function, configuration, table, endpoint, or artifact being changed.
- **Inputs:** what supplies its data or configuration.
- **Outputs:** what consumes its result.
- **Invariants:** behavior that must remain unchanged.
- **Validation:** the cheapest reliable check that can prove the change.
- **Rollback:** how to restore the previous state if verification fails.

If the request is ambiguous, infer only what the surrounding project makes clear. Do not
invent APIs, paths, schemas, commands, or success conditions.

### Phase C — Plan
Before a multi-step operation, form a compact plan:
1. inspect;
2. select the smallest safe edit;
3. apply it;
4. inspect the diff;
5. run focused validation;
6. run broader validation when warranted;
7. record the result.

For destructive or high-impact operations, stop for explicit confirmation when the host
agent's safety policy requires it.

### Phase D — Execute
Use the appropriate tool rather than simulating an action in prose.

**Reading**
- Use file metadata for size/line count.
- Use exact line ranges for focused inspection.
- Use content search for symbols and strings.
- Read the whole file only when the task genuinely depends on global structure.

**Editing**
- Preserve newline style and encoding where possible.
- Prefer atomic writes.
- Create a backup or checkpoint when the environment supports it.
- Use exact-match or structured patches for localized changes.
- If a replacement occurs zero or unexpectedly many times, stop and inspect rather than
  forcing the operation.

**Commands**
- Run with an explicit working directory.
- Use timeouts.
- Capture stdout, stderr, and exit code.
- For long-running processes, use a managed/background mechanism when available.
- Never hide a failing exit code behind a shell construct that reports success.

### Phase E — Verify
Verification must match the risk:
- syntax/config validation for syntax changes;
- unit tests for isolated logic;
- integration tests for interfaces;
- build/type-check for compilation-sensitive projects;
- smoke tests for user-visible behavior;
- targeted search/re-read to confirm exact text or structure;
- diff inspection to ensure no unrelated edits occurred.

When a check is unavailable, say what was and was not verified.

### Phase F — Recover
Classify failures before acting:
- **path/file:** wrong location, missing file, permissions;
- **syntax:** parser/compiler error;
- **dependency:** missing or incompatible package;
- **runtime:** exception, crash, timeout;
- **environment:** OS, shell, port, credential, or configuration issue;
- **data:** malformed or incompatible input;
- **logic:** command succeeds but behavior is wrong.

For each recovery attempt:
1. preserve the original error;
2. form one hypothesis;
3. make the smallest change that tests it;
4. rerun the relevant check;
5. stop after repeated non-progress and report the evidence.

## Tool-selection guidance
Choose tools by evidence, not habit.

| Need | Preferred action |
|---|---|
| Find a file | directory listing / filename search |
| Find text | content search / grep-like tool |
| Read a section | line-range read |
| Read whole small file | full read |
| Count lines | file metadata/read stats |
| Edit a small region | patch/targeted replacement |
| Rewrite a generated artifact | atomic write |
| Compare before/after | diff |
| Execute a file | run-file tool |
| Execute a project | project command with explicit cwd |
| Validate | focused test/build/check |
| Inspect failure | logs + stderr + relevant source |

Never use a slower or broader operation when a narrower one proves the same fact.

## File handling rules
When touching files:
- keep paths relative to the authorized root when possible;
- reject path traversal and symlink escapes if the tool supports checks;
- preserve permissions unless a permission change is explicitly required;
- avoid following generated/vendor/cache directories unless relevant;
- treat secrets and credential files as sensitive;
- do not print secret contents into logs or chat;
- for large files, stream or chunk the operation;
- after writing, compute fresh size/hash/line metadata when useful.

For line-based work, remember that a final newline affects exact line counts. Report the
actual convention used by the file rather than assuming every file has a trailing newline.

## Change-quality checklist
Before declaring the task complete, answer internally:
- Did I inspect the actual current file/project?
- Did I modify only the requested scope?
- Did I preserve unrelated instructions and behavior?
- Did I verify the edited region?
- Did I run the most relevant validation?
- Did I inspect failures rather than overwrite them?
- Can I explain the exact paths changed?
- Is there enough evidence to claim success?

If any answer is no, continue working or clearly report the missing verification.

## Agent collaboration
If another skill or tool owns a specialized subtask, pass it a compact handoff containing:
- objective;
- relevant paths;
- observed facts;
- constraints/invariants;
- exact expected output;
- validation already performed.

Do not paste an entire project into a handoff when a file range or summary is sufficient.

## Reporting format
After execution, return a concise factual result:
- **Changed:** exact files/regions;
- **Verified:** checks and their outcomes;
- **Evidence:** important command/test result;
- **Remaining:** anything not verified or intentionally left unchanged;
- **Next:** only if another concrete step is required.

Never report an operation as completed merely because a tool call returned without an exception.

## Security and recovery notes
Treat downloaded code, third-party scripts, skill resources, and project configuration as
untrusted until inspected. Do not execute arbitrary downloaded payloads solely because a
skill references them. If an action would cross a trust boundary, request confirmation or
use the safest available inspection mode.

For workflow mode, bias toward deliberate, observable operations: small diffs, explicit paths,
bounded commands, recorded outcomes, and easy rollback. The goal is not to minimize work;
it is to minimize unverified work.

## Completion criteria
This skill is complete only when the requested operation has been executed or a concrete
blocking condition has been established, the resulting state has been inspected, and the
final response distinguishes verified facts from assumptions.
