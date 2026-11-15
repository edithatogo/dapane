//! Optional, synthetic-only paired-draw and fiscal reference contracts.
//!
//! D1 resource costing delegates to the existing Dapane Rust core. Provider methods,
//! clinical models, random sampling and empirical source admission are outside
//! this crate. See CONTRACT.md for the bounded input and accounting semantics.

#![forbid(unsafe_code)]

mod common;
pub mod fiscal;
pub mod paired;

pub use dapane_core::DapaneError;
