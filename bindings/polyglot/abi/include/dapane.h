#ifndef DAPANE_ABI_V1_H
#define DAPANE_ABI_V1_H

#include <stddef.h>
#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

#define DAPANE_ABI_VERSION 1u
#define DAPANE_MAX_REQUEST_BYTES 4194304u

enum {
    DAPANE_OK = 0,
    DAPANE_CORE_ERROR = 1,
    DAPANE_INVALID_ARGUMENT = 2,
    DAPANE_ABI_MISMATCH = 3,
    DAPANE_PANIC = 4,
    DAPANE_UNSUPPORTED_OPERATION = 5,
    DAPANE_INVALID_UTF8 = 6,
    DAPANE_INPUT_LIMIT = 7,
    DAPANE_INVALID_HANDLE = 8,
    DAPANE_BUFFER_TOO_SMALL = 9,
    DAPANE_RESOURCE_LIMIT = 10
};

enum { DAPANE_POINT = 1, DAPANE_INTERVAL = 2 };

/* ABI version is independent of request schema, engine and method versions. */
uint32_t dapane_abi_version(void);

/* out_handle must point to an aligned, initialized uint64_t containing zero.
 * It must not overlap request. Existing nonzero handles are never overwritten.
 * request may be NULL only when length is zero. Otherwise it must identify
 * length readable bytes (unless length exceeds the limit, checked before read).
 * Borrowed input must remain immutable and readable until return. No NUL is required.
 * Writable output slots and buffers are exclusive to the call until it returns.
 * OK and CORE_ERROR return a nonzero owned handle, including error JSON for the
 * latter. With a valid initially-zero slot, other statuses leave zero and no
 * partial report. Rejected nonzero slots retain their original handle.
 * The caller must release every returned handle, even when status is CORE_ERROR.
 */
uint32_t dapane_v1_evaluate(uint32_t requested_abi, uint32_t operation,
                           const uint8_t *request, size_t length,
                           uint64_t *out_handle);

/* out_length must be a valid aligned writable size_t, set to zero on failure. */
uint32_t dapane_v1_result_length(uint64_t handle, size_t *out_length);

/* Copy immutable UTF-8 JSON bytes, without a NUL terminator or partial writes.
 * out_written is required, aligned and disjoint from the output range. On OK it
 * is the copied length; on BUFFER_TOO_SMALL it is the required length, otherwise
 * zero. NULL output with capacity zero is a supported size query. When capacity
 * is sufficient, output must address that many writable bytes. Caller owns and
 * frees its output buffer. No pointer into Rust storage crosses this interface.
 */
uint32_t dapane_v1_result_copy(uint64_t handle, uint8_t *output,
                              size_t capacity, size_t *out_written);

/* Frees Rust-owned storage. Unknown, zero or already-freed handles return
 * INVALID_HANDLE. Identifiers are never reused during the library's lifetime.
 * Handles are local to this loaded library instance, not portable addresses.
 * At most 64 handles / 64 MiB of result bytes may be retained at once.
 * All calls are thread-safe; a copy racing free either completes under the lock
 * or reports INVALID_HANDLE. The caller must not unload the library while used.
 * Valid live caller pointers remain a C precondition: arbitrary pointer misuse,
 * process aborts, OOM and signals cannot be contained by Rust catch_unwind.
 */
uint32_t dapane_v1_result_free(uint64_t handle);

#ifdef __cplusplus
}
#endif
#endif
