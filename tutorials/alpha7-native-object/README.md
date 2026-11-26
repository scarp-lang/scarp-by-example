# Experimental native object workshop

**Compiler:** [Scarp v0.0.7-alpha.2](https://github.com/scarp-lang/scarp/releases/tag/v0.0.7-alpha.2) (published pre-release, independently pinned). This workshop does not change the numbered interpreter course's compiler version.

Learn what a relocatable object is, how a pure integer function becomes an x86-64 ELF64 object, and how work limits, stack budgets and native diagnostics differ from interpreter execution. These are original teaching examples, not copies of compiler fixtures.

## Prerequisites

Install the pinned Scarp compiler and confirm `scarp version`. Start in this directory. Choose unused output paths in an existing writable directory on a filesystem supporting hard links. The command does not overwrite an existing output file. Object emission is cross-host; the optional C host exercise requires Linux x86-64 and a C compiler.

## 1. Checked arithmetic

```sh
scarp native-object --json x86_64-none checked checked.srp -o checked.o
```

The file exports `scarp_checked_integer_function` with two signed 64-bit integer arguments. The JSON describes the ABI and failure spans. Adding 12 and -5 returns 7. Adding 1 to the maximum signed 64-bit integer produces status 1 rather than wrapping. This is a native function result, not printed Scarp output.

## 2. Bounded loops

```sh
scarp native-object --json x86_64-none bounded 1000 bounded.srp -o bounded.o
```

The triangular function sums the first n positive integers. For n = 5 it returns 15; n = 0 returns 0. A negative repeat count returns status 5. A very large positive count exhausts the 1000-unit work allowance (status 4). Work units count native IR events, not seconds, CPU cycles or interpreter steps. The meter resets for each external invocation.

## 3. Bounded direct calls

```sh
scarp native-object --json x86_64-none bounded-entry compute 1000 4096 entry.srp -o entry.o
```

The source contains only pure function declarations. The selected entry takes two integer arguments, calls a private helper, and that helper calls an eight-argument function. Under the experimental SysV AMD64 ABI, the first six integer arguments use registers and the last two use caller-owned stack slots. The compiler verifies a static stack bound for the reachable call graph. The work allowance is shared across that graph.

For (21, 2), the expected result is (21 + 1 + 2 + 3 + 4 + 5 + 6) / 2 + 1 = 22. A zero divisor in the innermost helper returns status 2 and its source span to the external caller. The JSON's `peak_stack_bytes` must fit within `max_stack_bytes`; neither includes all stack space the surrounding host may need.

## 4. Optional native host (Linux x86-64)

```sh
cc -std=c11 -Wall -Wextra -Werror host.c checked.o bounded.o entry.o -o native-workshop
./native-workshop
```

Each output row contains label, signed value, status and source-span index. Consult the relevant object's JSON `failure_spans` only for a nonzero status; offsets are half-open UTF-8 byte ranges in the original source. The companion verifier checks emitted ELF headers, deterministic bytes, metadata, overwrite refusal, invalid targets, stack-budget rejection and (on Linux x86-64) these native results. The separate wide-argument host below adds three more result checks.

From the repository root, with a checkout of the compiler at the pinned commit:

```sh
python scripts/verify_alpha7_native_object.py --compiler /path/to/scarp --compiler-source /path/to/scarp-source --link-host
```

Omit `--link-host` when running on Windows, macOS or a non-x86-64 Linux host. This only validates object emission and command behavior on those hosts.

## 5. External eight-argument ABI

The first call-chain example passes extra arguments to an internal helper.
The separate [wide.srp](wide.srp) demonstrates an external caller passing
eight arguments directly. Its weighted sum makes argument swaps observable.
For 1 through 8 the expected result is 204; for 8 through 1 it is 120.

```sh
scarp native-object --json x86_64-none checked wide.srp -o wide.o
cc -std=c11 -Wall -Wextra -Werror wide_host.c wide.o -o wide-workshop
./wide-workshop
```

Use the C commands only on Linux x86-64. The JSON reports
`integer_arguments: 8` and `stack_argument_bytes: 16` for the external
caller. The caller's stack alignment padding is separate. The host
uses the exact eight-argument prototype; the two checked examples export
the same symbol and must be linked into separate executables.

## 6. Verify the precise stack boundary and diagnostic bytes

Take `peak_stack_bytes` from the entry object's JSON. Re-emit the same
source with that exact number instead of 4096 and a new output filename:
it must produce identical object bytes. Then use one byte less with
another unused path: compilation must fail without creating the output.
The Python verifier automates both checks without relying on a hard-coded
frame size. The stack allowance is not the work allowance.

The entry source starts with a Hindi/emoji comment. When division fails,
the host's span ID must map to the exact slash byte, not a Unicode character
index. A source offset is measured against the original UTF-8 file, not
rendered columns. The verifier also rejects unsupported recursion,
top-level print effects and invalid UTF-8 without publishing a partial object.
It compares six successful native result expectations against interpreter
execution of the same declarations plus print calls.

## Limits and next steps

The native command does not produce an executable, bootable kernel, or OS. It does not provide general heap-backed values, native recursion, memory-mapped I/O, interrupt handling, arbitrary external calls or project linking. Aggregate layout planning is a separate experimental Rust API, not native aggregate execution. Ordinary `scarp exec` continues to use the interpreter.

Practice: change the triangular count, inspect the metadata for the three modes, and compare the entry's reported stack bound against a smaller budget using a new output filename.

Upstream: [native object command](https://github.com/scarp-lang/scarp/blob/v0.0.7-alpha.2/docs/native-object-output.md) · [experimental ABI](https://github.com/scarp-lang/scarp/blob/v0.0.7-alpha.2/docs/native-elf64.md) · [layout planner](https://github.com/scarp-lang/scarp/blob/v0.0.7-alpha.2/docs/native-value-layout.md).

## हिंदी में संक्षिप्त परिचय

यह प्रयोगात्मक पाठ बताता है कि Scarp के शुद्ध integer functions को ELF64 object file में कैसे बदला जाता है। `checked` mode गणना की त्रुटियों की जाँच करता है, `bounded` mode लूप के काम की सीमा तय करता है और `bounded-entry` mode एक function तथा उसके सीधे helper calls को compile करता है। JSON report में stack की सीमा और त्रुटि के UTF-8 byte offsets मिलते हैं। Object file अपने आप executable या operating system नहीं है। सामान्य `scarp exec` अभी interpreter का उपयोग करता है।
