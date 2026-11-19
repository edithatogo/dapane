# Run with Rscript --vanilla installed.R <isolated-library> <prepared-cases>.
# Uses only base/recommended R packages; tests an installed native package.
args <- commandArgs(trailingOnly = TRUE)
stopifnot(length(args) == 2L)
.libPaths(c(normalizePath(args[[1L]]), .Library))
library(dapaneR)
stopifnot(startsWith(find.package("dapaneR"), normalizePath(args[[1L]])))
cases_dir <- normalizePath(args[[2L]])
cases <- read.delim(file.path(cases_dir, "cases.tsv"), stringsAsFactors = FALSE)
read_exact <- function(path) {
  readChar(path, file.info(path)$size, useBytes = TRUE)
}
for (i in seq_len(nrow(cases))) {
  case <- cases[i, ]
  input <- read_exact(file.path(cases_dir, paste0(case$name, ".input.json")))
  expected <- read_exact(file.path(cases_dir, paste0(case$name, ".output.json")))
  evaluate <- if (case$operation == "point") evaluate_json else evaluate_intervals_json
  if (case$status == "ok") {
    stopifnot(identical(evaluate(input), expected))
  } else {
    error <- tryCatch(evaluate(input), dapane_error = identity)
    stopifnot(inherits(error, "dapane_error"), identical(error$code, case$status),
              identical(error$diagnostic_json, expected))
  }
}
for (input in list(NA_character_, NULL, character(), c("{}", "{}"), 1, NA_real_,
                   NaN, Inf, TRUE, list("{}"), charToRaw("{}"), factor("{}"))) {
  error <- tryCatch(evaluate_json(input), dapane_error = identity)
  stopifnot(inherits(error, "dapane_error"), error$code == "invalid_host_input")
}
bad_utf8 <- rawToChar(as.raw(c(0x22, 0xff, 0x22)))
Encoding(bad_utf8) <- "UTF-8"
stopifnot(inherits(tryCatch(evaluate_json(bad_utf8), dapane_error = identity),
                   "dapane_error"))
oversized <- strrep(" ", 4L * 1024L * 1024L + 1L)
stopifnot(tryCatch(evaluate_json(oversized), dapane_error = identity)$code == "input_limit")
rm(oversized)

# Keep returned values across repeated full GC, including collection on every
# allocation, then release the original request. No borrowed R memory may escape.
input <- read_exact(file.path(cases_dir, "workforce.input.json"))
expected <- evaluate_json(input)
gctorture(TRUE)
retained <- lapply(seq_len(8L), function(i) evaluate_json(paste0(input)))
gctorture(FALSE)
rm(input)
invisible(gc())
stopifnot(all(vapply(retained, identical, logical(1L), expected)))

# Concurrency uses independent interpreters: each .Call runs on its own R main
# thread. This intentionally does not call the R API from foreign worker threads.
cluster <- parallel::makePSOCKcluster(2L)
result <- tryCatch(parallel::clusterCall(cluster, function(lib, input) {
  .libPaths(c(lib, .Library))
  library(dapaneR)
  evaluate_json(input)
}, normalizePath(args[[1L]]), read_exact(file.path(cases_dir, "workforce.input.json"))),
finally = parallel::stopCluster(cluster))
stopifnot(all(vapply(result, identical, logical(1L), expected)))
cat(nrow(cases), "shared cases; host rejection, GC and two interpreter checks passed\n")
