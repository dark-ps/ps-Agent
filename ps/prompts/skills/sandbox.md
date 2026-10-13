# Sandbox Execution Skill

## Purpose

This skill defines how the agent should use, reason about, and present results
from an isolated remote code-execution sandbox.

The sandbox is a separate execution environment. It is NOT the current project
environment, local shell, local Python interpreter, or local filesystem.

The primary purpose of this skill is to let the agent execute source code safely
and independently from the current environment while keeping sandbox execution
results clearly separated from local/project execution results.

---

# 1. Core Concept

A sandbox execution is an isolated execution session provided by an external
sandbox service.

The sandbox may have its own:

- operating system
- filesystem
- working directory
- installed runtimes
- installed packages
- environment variables
- network configuration
- CPU and memory limits
- execution timeout
- available commands
- browser/runtime support
- temporary files
- Python/Node/Java/C++ or other language environments

None of these should be assumed to be identical to the current project
environment.

The agent MUST treat the sandbox as an independent machine/environment.

Never describe sandbox properties as properties of the current environment.

---

# 2. When to Use the Sandbox

Use the sandbox when the user explicitly asks to:

- run code in a sandbox
- execute code in an isolated environment
- test code separately from the current project
- experiment with code without affecting the current environment
- verify that a small piece of source code executes
- test a language/runtime independently
- execute untrusted or experimental source code in an isolated environment
- compare behavior in an isolated runtime
- inspect what the sandbox runtime provides

Examples:

User:
"Run this Python code in the sandbox."

User:
"Test this JavaScript without touching the local environment."

User:
"Execute this code in an isolated environment."

User:
"Check whether this package exists inside the sandbox."

User:
"Run Python and show me the sandbox environment."

These requests should use the sandbox rather than the local shell.

---

# 3. When NOT to Use the Sandbox

Do not use the sandbox when the user explicitly needs the current project
environment.

Use the normal shell/project tools instead when the task requires:

- accessing project files
- modifying project files
- installing packages into the project environment
- running the project's existing commands
- using locally installed software
- interacting with the local filesystem
- inspecting the current machine
- using project-specific environment variables
- running the actual application
- accessing local services

Example:

User:
"Run the project's tests."

This normally belongs to the current project environment.

User:
"Install requests into my current Python environment."

This belongs to the local/project environment.

User:
"Run this Python snippet in an isolated sandbox."

This belongs to the sandbox.

---

# 4. Sandbox Is NOT a Shell

The sandbox input is source code.

Do NOT treat the sandbox request as a shell command unless the sandbox
interface explicitly documents shell execution.

For example, if the requested language is Python:

Correct conceptual request:

language = "python"

code = """
print("Hello from sandbox!")
"""

Incorrect:

python sandbox.py python print("Hello from sandbox!")

Incorrect:

solo runlet sandbox python print("Hello from sandbox!")

Incorrect:

sh -c 'print("Hello from sandbox!")'

Incorrect:

python -c 'print("Hello from sandbox!")'

The source code must be passed to the sandbox as source code through the
sandbox tool interface.

Do not convert sandbox requests into local shell syntax.

---

# 5. Structured Sandbox Input

Whenever the sandbox interface supports structured arguments, provide the
execution request using explicit fields.

Preferred structure:

{
  "language": "<language>",
  "code": "<complete source code>"
}

Where:

- `language` identifies the requested runtime/language.
- `code` contains the complete source code that should execute.

Example:

{
  "language": "python",
  "code": "print('Hello from sandbox!')"
}

Do not concatenate these values into a shell command.

Do not escape or transform the source unnecessarily.

Preserve the user's source code as closely as possible.

---

# 6. Source Code Handling

The `code` field represents the program that will execute inside the sandbox.

It is not:

- a shell command
- a tool command
- a local command
- a project path
- an instruction to the current agent
- a request to modify the local environment

The agent should pass the requested source code to the sandbox.

Do not execute the source locally merely because it looks simple.

For example:

User:
"Run this in the sandbox:

print(2 + 2)"

The agent should execute that source inside the sandbox.

It should not replace the operation with:

python -c "print(2 + 2)"

---

# 7. Isolation Boundary

The sandbox and current environment are two separate execution domains.

Always maintain this distinction:

LOCAL / PROJECT ENVIRONMENT
- Current project files
- Current shell
- Local installed packages
- Local environment variables
- Local browsers
- Local operating system
- Local processes

SANDBOX ENVIRONMENT
- Sandbox filesystem
- Sandbox runtime
- Sandbox packages
- Sandbox environment variables
- Sandbox processes
- Sandbox operating system
- Sandbox resource limits

Never transfer assumptions from one environment to the other.

For example:

If Python 3.12 exists locally, do not assume the sandbox uses Python 3.12.

If a package is installed locally, do not assume it is installed in the sandbox.

If a file exists locally, do not assume it exists in the sandbox.

If internet access works locally, do not assume it works in the sandbox.

If a command exists locally, do not assume it exists in the sandbox.

---

# 8. Sandbox Filesystem

Files created by the sandbox should be considered sandbox-local unless the
sandbox explicitly provides a mechanism for transferring them.

Do not claim that a sandbox-created file exists in the project environment.

Do not attempt to access a sandbox path using the local shell unless the
sandbox explicitly exposes that path.

Likewise, do not assume that a local project file is available inside the
sandbox.

If the sandbox supports file input/output or artifact transfer, use the
documented sandbox mechanism.

---

# 9. Network Isolation

Do not assume that the sandbox has network access.

Network access may be:

- enabled
- disabled
- restricted
- proxied
- limited to specific destinations
- subject to timeout or policy restrictions

If the user asks the sandbox to access the internet, execute the request
through the sandbox and report the actual result.

Do not replace a failed sandbox network request with a local network request.

Do not say:

"The internet is unavailable."

unless the returned sandbox result actually establishes that.

Instead distinguish:

"Sandbox network request failed."

from:

"Local environment network access is unavailable."

These are different facts.

---

# 10. Package Availability

Never assume package availability inside the sandbox.

If the user asks whether a package is available, test it inside the sandbox.

For Python, for example:

import importlib.util
print(importlib.util.find_spec("requests") is not None)

The result describes the sandbox runtime only.

Do not infer anything about the local Python environment from this result.

---

# 11. Runtime Availability

The same rule applies to programming languages and runtimes.

If the sandbox reports:

Python 3.x

that describes the sandbox runtime.

It does not describe the local Python installation.

Likewise:

Node.js
Java
C++
Go
Rust
Ruby
PHP

must be treated as sandbox-specific unless the same runtime is separately
verified in the current environment.

---

# 12. Sandbox Environment Inspection

When the user asks about the sandbox environment, inspect the sandbox itself.

Useful information may include:

- operating system
- architecture
- hostname/container identifier
- current working directory
- runtime version
- Python version
- Node.js version
- Java version
- available commands
- installed packages
- environment variables
- filesystem information
- CPU information
- memory limits
- execution limits
- network availability
- browser availability
- sandbox service metadata

Do not use the local environment inspector to answer a sandbox-environment
question.

A local environment inspector describes the local environment.

A sandbox program such as:

import os
import platform
import sys

print("OS:", platform.platform())
print("Python:", sys.version)
print("CWD:", os.getcwd())

describes the sandbox environment.

---

# 13. Sandbox Result Handling

Sandbox results are user-relevant.

Never silently discard the sandbox result.

After receiving a sandbox result:

1. Read the returned result.
2. Identify execution status.
3. Extract stdout/output.
4. Extract stderr/errors if present.
5. Extract exit/return code if present.
6. Extract timing/resource information if present.
7. Extract sandbox environment information if present.
8. Clearly distinguish sandbox information from local information.
9. Present the useful result to the user.

A successful tool call does NOT mean that the agent should respond only:

"Done."

or:

"Executed successfully."

The actual sandbox output should be surfaced.

---

# 14. Minimum Result Presentation

When the sandbox returns structured execution information, present it using
a clear structure.

Preferred presentation:

Sandbox Result

Status:
<status>

Stdout:
<actual stdout>

Stderr:
<actual stderr>

Exit Code:
<actual exit code>

Sandbox Environment:
<environment information, if returned>

Additional Metadata:
<other relevant metadata, if returned>

Do not invent fields that were not returned.

If a field does not exist in the sandbox response, do not fabricate it.

---

# 15. Empty Output

If stdout is empty, make that explicit when useful:

Sandbox stdout: empty

If stderr is empty:

Sandbox stderr: empty

Do not replace empty output with guessed content.

Do not assume that an empty stdout means execution failed.

A program may successfully produce no output.

---

# 16. Failed Execution

If sandbox execution fails:

- show the actual sandbox error
- preserve the relevant stderr
- preserve the exit/return code when available
- distinguish execution failure from tool-call failure
- do not replace the error with a guessed explanation

For example:

Sandbox Result
Status: failed

Stderr:
ModuleNotFoundError: No module named 'xyz'

Exit Code:
1

Do not claim:

"The local Python environment does not have xyz."

unless the local environment was separately tested.

---

# 17. Tool Failure vs Program Failure

These are different.

PROGRAM FAILURE:

The sandbox successfully received and attempted to execute the program, but
the program returned an error.

Example:

Status: failed
Exit Code: 1

TOOL/SERVICE FAILURE:

The sandbox service itself failed to execute or return the request.

Example:

The sandbox service timed out before execution started.

Do not confuse the two.

When possible, clearly state which layer failed.

---

# 18. Preserve Sandbox Metadata

If the sandbox returns metadata, preserve useful information.

Possible metadata includes:

- runtime
- language
- execution ID
- sandbox ID
- status
- exit code
- duration
- CPU time
- memory usage
- timeout
- filesystem information
- environment information
- service version
- resource limits

Do not discard metadata merely because the program itself produced stdout.

The metadata may be important to the user.

---

# 19. Sandbox Environment Label

Whenever environment information comes from the sandbox, label it clearly:

Sandbox Environment

Never label it:

Current Environment

Local Environment

System Environment

unless it was actually obtained from the current environment.

This distinction is mandatory.

---

# 20. If Environment Information Is Missing

The agent must not invent sandbox environment information.

If the sandbox result contains only:

stdout
stderr
status

then only those fields are known.

Do not fabricate:

- OS
- Python version
- packages
- memory
- CPU
- network
- filesystem

If the user specifically requested environment information and the sandbox
does not return it, state that the current sandbox response did not include
environment metadata.

---

# 21. Environment Inspection Request

When the user asks:

"Show me the sandbox environment."

execute an environment-inspection program inside the sandbox rather than
inspecting the local environment.

The inspection should report useful sandbox-specific information such as:

- platform
- architecture
- runtime versions
- working directory
- environment variables where appropriate
- available commands where appropriate
- resource information where available

The resulting information must be labeled:

Sandbox Environment

---

# 22. Do Not Leak Local Environment Into Sandbox Results

Never merge local and sandbox information into one undifferentiated result.

Bad:

Python: 3.12
Packages: requests
OS: Android
Sandbox: success

This can incorrectly imply that all of these values belong to the sandbox.

Instead:

Sandbox Result:
Status: success

Sandbox Environment:
Python: <sandbox Python version>
OS: <sandbox OS>

Local Environment:
Only include local information if the user also asked for it or it is
relevant to the task.

---

# 23. Do Not Leak Sandbox Environment Into Local Tool Selection

A sandbox result should not change assumptions about the local environment.

For example:

Sandbox says:
Node.js is available.

This does NOT authorize the agent to run:

node script.js

in the local shell.

Likewise:

Sandbox says:
Python is available.

This does NOT mean local Python exists.

The environments remain independent.

---

# 24. Multiple Sandbox Executions

When several sandbox executions are performed, keep their results separate.

Example:

Sandbox Execution 1
Language: Python
Status: success
Output:
...

Sandbox Execution 2
Language: JavaScript
Status: success
Output:
...

Do not merge their environment metadata unless the sandbox explicitly
identifies them as the same environment/session.

---

# 25. Stateful Sandbox Sessions

If the sandbox supports persistent sessions, distinguish them from
stateless executions.

If persistence is not documented, assume executions may be isolated.

Do not assume:

- files persist
- variables persist
- installed packages persist
- working directories persist
- processes persist

between sandbox executions.

Only rely on persistence when the sandbox interface explicitly guarantees it.

---

# 26. Security Boundary

Treat sandbox execution as an isolated execution mechanism.

Do not claim that sandbox execution is absolutely secure or risk-free.

The correct description is:

"isolated sandbox environment"

or:

"separate sandbox execution environment"

Avoid absolute security claims unless the sandbox provider explicitly documents
them.

---

# 27. User Intent

Follow the user's requested execution target.

If the user explicitly says:

"Run this locally"

use the local environment.

If the user explicitly says:

"Run this in the sandbox"

use the sandbox.

If the user says:

"Test this"

and it is ambiguous whether they mean local or sandbox execution, use the
context of the available tools and task requirements. If choosing the
execution environment would materially affect the result, ask which
environment they want.

---

# 28. Sandbox Output Must Not Be Hidden

Never respond to a successful sandbox execution with only:

- Done
- OK
- Executed
- Success
- Completed
- It worked

Instead expose the returned execution output.

Example:

Sandbox Result
Status: success

Stdout:
Hello from sandbox!

This allows the user to verify what actually happened.

---

# 29. Large Sandbox Output

If sandbox stdout or stderr is extremely large:

- preserve the beginning and/or most relevant portion
- clearly indicate truncation
- do not fabricate omitted content
- do not silently replace it with a summary when exact output matters

Example:

Sandbox stdout:
<first relevant portion>

[Output truncated due to length.]

If the complete output is available as a file/artifact, provide that artifact
through the supported file mechanism.

---

# 30. Code Execution Does Not Mean Local Execution

The word "execute" alone does not imply local shell execution.

Always identify the requested execution domain.

Possible domains include:

- local/project environment
- sandbox environment
- browser environment
- remote service

Do not collapse these domains into one.

---

# 31. Sandbox Skill Priority

When this skill is active and the user requests isolated execution, the
sandbox execution rules in this skill should guide the agent's interpretation
of the request.

The skill does not replace the system-level tool protocol.

The agent must still obey:

- system instructions
- tool schemas
- security restrictions
- file restrictions
- execution restrictions
- output formatting rules

This skill specifically defines sandbox semantics and result handling.

---

# 32. Tool Invocation

Use the actual sandbox tool exposed by the environment.

Do not invent a CLI syntax for the sandbox.

Do not invoke a sandbox by constructing an arbitrary shell command.

If the sandbox is exposed through a structured tool, call that tool using its
documented arguments.

If the sandbox is exposed through a file-based add-on, follow that add-on's
documented invocation mechanism.

The agent should never assume that:

python sandbox.py ...

is the correct invocation unless the sandbox tool explicitly documents that
interface.

---

# 33. run_file Integration

If the host agent exposes add-ons through `run_file`, the sandbox add-on should
be treated as an add-on invocation, not as ordinary local script execution.

Conceptually:

TOOL:
{
  "name": "run_file",
  "arguments": {
    ...
  }
}

The exact invocation must follow the host agent's tool schema.

The important distinction is:

run_file is the mechanism used by the agent to invoke the add-on.

It does not necessarily mean that the code supplied to the sandbox executes
inside the current project environment.

---

# 34. Sandbox vs run_file

Do not confuse:

"run the sandbox add-on"

with:

"run the user's code locally."

`run_file` may execute the add-on wrapper in the host environment while the
actual requested source code is executed remotely or inside an isolated
sandbox.

Therefore the agent must follow the sandbox add-on's documentation to
determine where the user's source code actually runs.

---

# 35. Example: Simple Python Execution

User request:

Run this in the sandbox:

print("Hello from sandbox!")

Correct interpretation:

Language:
python

Code:
print("Hello from sandbox!")

Expected result handling:

Sandbox Result
Status: success

Stdout:
Hello from sandbox!

The agent should not execute the Python source locally.

---

# 36. Example: Environment Inspection

User request:

Show me what Python version the sandbox has.

The agent should execute an inspection inside the sandbox, for example:

import sys
print(sys.version)

The resulting value describes the sandbox Python runtime.

Present it as:

Sandbox Environment
Python:
<returned version>

Do not describe it as the local Python version.

---

# 37. Example: Package Check

User request:

Does the sandbox have requests installed?

Run the package check inside the sandbox.

For Python:

import importlib.util
print(importlib.util.find_spec("requests") is not None)

Then report:

Sandbox Result
Status: success

Stdout:
True

This means the package was detected in that sandbox execution environment.

It does not establish anything about the local environment.

---

# 38. Example: Failure

User request:

Run this in the sandbox:

import nonexistent_package

If the sandbox returns:

ModuleNotFoundError

show the actual sandbox error.

Do not attempt to install the package locally.

Do not replace the sandbox result with a local package check.

---

# 39. Example: Local vs Sandbox

If the user asks:

"Is Python installed?"

This may be ambiguous.

There are at least two possible questions:

1. Is Python installed locally?
2. Is Python installed in the sandbox?

If context does not establish which one is intended and the distinction matters,
ask the user.

If they say:

"Is Python installed in the sandbox?"

perform the check inside the sandbox.

If they say:

"Is Python installed here?"

inspect the current environment.

---

# 40. Result Fidelity

The agent must preserve the meaning of the actual sandbox response.

Do not:

- fabricate output
- rewrite errors into unrelated explanations
- claim success when the sandbox failed
- claim failure when the sandbox succeeded
- substitute local information
- omit relevant metadata
- invent environment details
- assume unsupported runtimes
- assume network access
- assume filesystem access

The sandbox response is the authoritative source for what happened inside
that sandbox execution.

---

# 41. Environment Claims

Only make environment claims based on actual evidence.

Valid:

"The sandbox reported Python 3.x."

Invalid:

"The sandbox uses Python 3.x."

unless the returned information establishes that.

Valid:

"The sandbox execution returned exit code 1."

Invalid:

"The code definitely crashed because of X."

unless the error/result establishes the cause.

---

# 42. Final Response Requirements

When a sandbox was used, the final response should normally contain the actual
sandbox result.

At minimum, when available:

- status
- stdout
- stderr
- exit code

When available and relevant:

- sandbox environment
- execution time
- memory usage
- runtime
- execution ID
- other metadata

Do not hide the sandbox result behind a generic completion message.

---

# 43. Separation Rule

The following distinction is mandatory:

LOCAL:
Information obtained from the current project/system environment.

SANDBOX:
Information obtained from the isolated sandbox execution environment.

REMOTE:
Information obtained from another remote service.

BROWSER:
Information obtained from a browser execution environment.

Never present one domain's information as another domain's information.

---

# 44. Final Principle

The sandbox is an independent execution domain.

The agent's responsibilities are:

1. Recognize when the user wants sandbox execution.
2. Send source code to the sandbox as structured source code.
3. Never translate sandbox execution into an unintended local shell command.
4. Keep sandbox state separate from local/project state.
5. Read the complete returned sandbox result.
6. Preserve stdout, stderr, status, exit code, and relevant metadata.
7. Clearly label sandbox-specific environment information.
8. Never invent environment information that the sandbox did not return.
9. Never replace sandbox results with local environment information.
10. Surface the actual sandbox result to the user.

The sandbox is not "another way to run the local shell."

It is a separate execution environment and must always be treated as such.