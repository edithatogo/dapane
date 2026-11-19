\name{evaluate_json}
\alias{evaluate_json}
\alias{evaluate_intervals_json}
\title{Evaluate exact JSON with the Dapane Rust kernel}
\usage{
evaluate_json(request_json)
evaluate_intervals_json(request_json)
}
\arguments{
\item{request_json}{One non-missing UTF-8 JSON character string. Exact numbers
are decimal strings or numerator/denominator string pairs. Numeric R values,
lists, factors, missing values and byte-encoded strings are rejected.}
}
\description{Calls the same Rust implementation directly, without Python,
Julia or the separate C ABI library. No valuation arithmetic is performed in R.}
\value{One complete JSON string. Failure raises a \code{dapane_error} condition
with \code{code}, \code{message}, \code{path}, and, for kernel failures,
\code{diagnostic_json}. No partial financial result is returned.}
\details{\code{evaluate_json} supports request profiles 0.1 and 0.2.
\code{evaluate_intervals_json} supports interval envelope 0.1, with declared
uniform calendar-day exposure and half-even rounding per generated segment.
JSON is not parsed in R; duplicate keys, numeric coercions and unsupported
methods remain errors in the kernel. Inputs are bounded to 4 MiB. Calls are
synchronous on the R main thread. Use separate R processes for concurrency;
foreign threads must never call the R API. Returned strings are owned by R.}
