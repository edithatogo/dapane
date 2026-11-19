# Exact JSON is deliberately not decoded/re-encoded in this boundary.
.dapane_stop <- function(code, message, path = "/", diagnostic_json = NULL) {
  stop(structure(list(message = message, call = NULL, code = code, path = path,
                      diagnostic_json = diagnostic_json),
                 class = c("dapane_error", "error", "condition")))
}

.dapane_request <- function(request_json) {
  if (!is.character(request_json) || length(request_json) != 1L ||
      is.na(request_json) || is.object(request_json)) {
    .dapane_stop("invalid_host_input", "Supply one non-missing plain JSON character string.")
  }
  if (Encoding(request_json) == "bytes") {
    .dapane_stop("invalid_host_input", "A bytes-encoded string is not UTF-8 JSON.")
  }
  request_json <- enc2utf8(request_json)
  if (!validUTF8(request_json)) {
    .dapane_stop("invalid_host_input", "JSON input must be valid UTF-8.")
  }
  if (nchar(request_json, type = "bytes") > 4L * 1024L * 1024L) {
    .dapane_stop("input_limit", "JSON request exceeds 4 MiB.")
  }
  request_json
}

.dapane_result <- function(result) {
  if (!isTRUE(result$ok)) {
    .dapane_stop(result$code, result$message, result$path, result$json)
  }
  result$json
}

#' Evaluate exact point/capacity JSON with the Rust kernel.
#' @param request_json One non-missing UTF-8 JSON character string.
#' @return One JSON character string, preserving exact values and report digests.
#' @export
evaluate_json <- function(request_json) {
  .dapane_result(.Call(wrap__evaluate_json_native, .dapane_request(request_json)))
}

#' Evaluate an explicit calendar-day interval envelope with the Rust kernel.
#' @param request_json One non-missing UTF-8 JSON character string.
#' @return One JSON character string, preserving per-segment half-even rounding.
#' @export
evaluate_intervals_json <- function(request_json) {
  .dapane_result(.Call(wrap__evaluate_intervals_json_native, .dapane_request(request_json)))
}
