/* Registration pattern adapted from extendr/rextendr's entrypoint.c at
 * d7383605ebdc766ddc46e9b73ff2b34bf6c19565 (MIT). The scoped package does not
 * install a process-global panic hook; the pure Rust calls catch their panics. */
#include <R_ext/Rdynload.h>
#include <R_ext/Visibility.h>

void R_init_dapaneR_extendr(DllInfo *dll);

void attribute_visible R_init_dapaneR(DllInfo *dll) {
    R_init_dapaneR_extendr(dll);
    R_useDynamicSymbols(dll, FALSE);
    R_forceSymbols(dll, TRUE);
}
