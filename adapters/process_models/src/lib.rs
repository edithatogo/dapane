//! Bounded X2 PNML/Petri-net and named BPMN 2.0 subset adapters for Dapane.
//!
//! Zero third-party dependencies. Parses strict bounded subsets of ISO/IEC
//! 15909-2 PNML 2009 and OMG BPMN 2.0 XML, executes deterministic physical
//! process runs without floating-point arithmetic, separates consumption,
//! occupancy, and non-costable transfers, and projects traces into unchanged
//! Dapane `0.1` valuation requests under an independent quotation release.

pub mod bpmn;
pub mod json_io;
pub mod model;
pub mod pnml;
pub mod sha256;
pub mod xml;
