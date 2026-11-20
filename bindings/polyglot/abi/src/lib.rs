//! C ABI v1: opaque immutable results and caller-owned copy buffers.
//!
//! Only transport is implemented here. The linked core owns all validation,
//! exact arithmetic and report/error JSON. See include/dapane.h for the contract.

use std::collections::BTreeMap;
use std::sync::{Mutex, OnceLock};

#[cfg(not(panic = "unwind"))]
compile_error!("dapane-abi requires panic=unwind for the FFI panic boundary");

pub const ABI_VERSION: u32 = 1;
pub const OK: u32 = 0;
pub const CORE_ERROR: u32 = 1;
pub const INVALID_ARGUMENT: u32 = 2;
pub const ABI_MISMATCH: u32 = 3;
pub const PANIC: u32 = 4;
pub const UNSUPPORTED_OPERATION: u32 = 5;
pub const INVALID_UTF8: u32 = 6;
pub const INPUT_LIMIT: u32 = 7;
pub const INVALID_HANDLE: u32 = 8;
pub const BUFFER_TOO_SMALL: u32 = 9;
pub const RESOURCE_LIMIT: u32 = 10;
const MAX_HANDLES: usize = 64;
const MAX_RETAINED_BYTES: usize = 64 * 1024 * 1024;

#[derive(Default)]
struct Results {
    next: u64,
    bytes: usize,
    values: BTreeMap<u64, Box<[u8]>>,
}

impl Results {
    fn insert(&mut self, value: String) -> Result<u64, u32> {
        let bytes = self.bytes.checked_add(value.len()).ok_or(RESOURCE_LIMIT)?;
        let next = self.next.checked_add(1).ok_or(RESOURCE_LIMIT)?;
        if self.values.len() >= MAX_HANDLES || bytes > MAX_RETAINED_BYTES {
            return Err(RESOURCE_LIMIT);
        }
        self.values
            .insert(next, value.into_bytes().into_boxed_slice());
        self.bytes = bytes;
        self.next = next;
        Ok(next)
    }

    fn free(&mut self, handle: u64) -> u32 {
        if let Some(value) = self.values.remove(&handle) {
            self.bytes -= value.len();
            OK
        } else {
            INVALID_HANDLE
        }
    }
}

fn results() -> &'static Mutex<Results> {
    static RESULTS: OnceLock<Mutex<Results>> = OnceLock::new();
    RESULTS.get_or_init(|| Mutex::new(Results::default()))
}

fn guard(operation: impl FnOnce() -> u32 + std::panic::UnwindSafe) -> u32 {
    std::panic::catch_unwind(operation).unwrap_or(PANIC)
}

fn aligned<T>(pointer: *mut T) -> bool {
    !pointer.is_null() && (pointer as usize).is_multiple_of(std::mem::align_of::<T>())
}

/// Return the major C ABI version without allocating or touching host memory.
#[unsafe(no_mangle)]
pub extern "C" fn dapane_abi_version() -> u32 {
    ABI_VERSION
}

/// Evaluate point/capacity (1) or interval (2) JSON through the existing core.
///
/// # Safety
/// out_handle must be aligned, initialized, writable, and disjoint from input.
/// Input must be readable for length bytes when within the core limit, or null
/// when empty. Input must remain immutable and the output slot exclusively held until return.
#[unsafe(no_mangle)]
pub unsafe extern "C" fn dapane_v1_evaluate(
    requested_abi: u32,
    operation: u32,
    request: *const u8,
    length: usize,
    out_handle: *mut u64,
) -> u32 {
    guard(|| {
        if !aligned(out_handle) {
            return INVALID_ARGUMENT;
        }
        // SAFETY: the caller supplies an initialized aligned writable scalar.
        if unsafe { *out_handle } != 0 {
            return INVALID_ARGUMENT;
        }
        if requested_abi != ABI_VERSION {
            return ABI_MISMATCH;
        }
        let evaluate = match operation {
            1 => dapane_core::evaluate_json,
            2 => dapane_core::evaluate_intervals_json,
            _ => return UNSUPPORTED_OPERATION,
        };
        if length > dapane_core::MAX_JSON_BYTES {
            return INPUT_LIMIT;
        }
        let input = if length == 0 {
            &[]
        } else if request.is_null() {
            return INVALID_ARGUMENT;
        } else {
            // SAFETY: caller guarantees readable, immutable bytes; the limit is
            // below isize::MAX, and this borrow does not survive the call.
            unsafe { std::slice::from_raw_parts(request, length) }
        };
        let Ok(input) = std::str::from_utf8(input) else {
            return INVALID_UTF8;
        };
        let (status, json) = match evaluate(input) {
            Ok(report) => (OK, report),
            Err(error) => (CORE_ERROR, error.to_string()),
        };
        let Ok(mut results) = results().lock() else {
            return PANIC;
        };
        match results.insert(json) {
            Ok(handle) => {
                // SAFETY: validated non-null/aligned pointer and caller contract.
                unsafe { *out_handle = handle };
                status
            }
            Err(status) => status,
        }
    })
}

/// Read a retained result's byte length without lending Rust memory to the host.
///
/// # Safety
/// out_length must point to an aligned writable usize exclusively held during the call.
#[unsafe(no_mangle)]
pub unsafe extern "C" fn dapane_v1_result_length(handle: u64, out_length: *mut usize) -> u32 {
    guard(|| {
        if !aligned(out_length) {
            return INVALID_ARGUMENT;
        }
        // SAFETY: aligned writable scalar supplied by the caller.
        unsafe { *out_length = 0 };
        let Ok(results) = results().lock() else {
            return PANIC;
        };
        if let Some(value) = results.values.get(&handle) {
            // SAFETY: same scalar; no Rust layout crosses the boundary.
            unsafe { *out_length = value.len() };
            OK
        } else {
            INVALID_HANDLE
        }
    })
}

/// Copy a complete immutable result. Short buffers are never partly written.
///
/// # Safety
/// out_written must be an aligned writable usize, disjoint from output. If
/// capacity is sufficient, output must point to capacity writable bytes. Neither
/// pointer may be accessed concurrently by another thread during this call.
#[unsafe(no_mangle)]
pub unsafe extern "C" fn dapane_v1_result_copy(
    handle: u64,
    output: *mut u8,
    capacity: usize,
    out_written: *mut usize,
) -> u32 {
    guard(|| {
        if !aligned(out_written) {
            return INVALID_ARGUMENT;
        }
        // SAFETY: caller-supplied aligned writable scalar.
        unsafe { *out_written = 0 };
        let Ok(results) = results().lock() else {
            return PANIC;
        };
        let Some(value) = results.values.get(&handle) else {
            return INVALID_HANDLE;
        };
        if capacity < value.len() {
            // SAFETY: same valid scalar; output is not touched on this path.
            unsafe { *out_written = value.len() };
            return BUFFER_TOO_SMALL;
        }
        if output.is_null() || capacity > isize::MAX as usize {
            return INVALID_ARGUMENT;
        }
        // SAFETY: caller guarantees output capacity and disjoint pointers; Rust
        // bytes are private, immutable, and remain locked against free throughout.
        unsafe {
            std::ptr::copy_nonoverlapping(value.as_ptr(), output, value.len());
            *out_written = value.len();
        }
        OK
    })
}

/// Release an opaque handle; repeated/unknown/stale identifiers fail closed.
#[unsafe(no_mangle)]
pub extern "C" fn dapane_v1_result_free(handle: u64) -> u32 {
    guard(|| match results().lock() {
        Ok(mut results) => results.free(handle),
        Err(_) => PANIC,
    })
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn panics_cannot_unwind_out_of_the_common_boundary() {
        assert_eq!(guard(|| panic!("synthetic transport failure")), PANIC);
        assert_eq!(guard(|| OK), OK);
    }

    #[test]
    fn handles_are_not_reused_and_storage_is_reclaimed() {
        let mut results = Results::default();
        let first = results.insert("first".into()).unwrap();
        assert_eq!(results.free(first), OK);
        assert_eq!(results.bytes, 0);
        let next = results.insert("next".into()).unwrap();
        assert!(next > first);
        assert_eq!(results.free(first), INVALID_HANDLE);
        assert_eq!(results.free(next), OK);
        assert!(results.values.is_empty());
    }

    #[test]
    fn saturation_rejects_and_free_restores_capacity() {
        let mut results = Results::default();
        let handles: Vec<_> = (0..MAX_HANDLES)
            .map(|_| results.insert("x".into()).unwrap())
            .collect();
        assert_eq!(results.insert("x".into()), Err(RESOURCE_LIMIT));
        assert_eq!(results.free(handles[0]), OK);
        assert!(results.insert("x".into()).is_ok());
    }

    #[test]
    fn result_byte_limit_rejects_without_retaining_a_partial_value() {
        let mut results = Results::default();
        assert_eq!(
            results.insert("x".repeat(MAX_RETAINED_BYTES + 1)),
            Err(RESOURCE_LIMIT)
        );
        assert_eq!(results.bytes, 0);
        assert!(results.values.is_empty());
    }

    #[test]
    fn exhausted_identifier_space_fails_closed() {
        let mut results = Results {
            next: u64::MAX,
            ..Results::default()
        };
        assert_eq!(results.insert("x".into()), Err(RESOURCE_LIMIT));
        assert!(results.values.is_empty());
    }
}
