/* Native acceptance consumer: no numerical formulas, R or Python runtime. */
#include "dapane.h"
#include <assert.h>
#include <pthread.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static unsigned char *read_file(const char *path, size_t *length) {
    FILE *file = fopen(path, "rb");
    assert(file != NULL);
    assert(fseek(file, 0, SEEK_END) == 0);
    long size = ftell(file);
    assert(size >= 0);
    rewind(file);
    *length = (size_t)size;
    unsigned char *bytes = malloc(*length + 1);
    assert(bytes != NULL);
    assert(fread(bytes, 1, *length, file) == *length);
    assert(fclose(file) == 0);
    bytes[*length] = 0;
    return bytes;
}

static void check_result(uint64_t handle, const unsigned char *expected, size_t expected_len) {
    size_t len = 0, written = 99;
    assert(dapane_v1_result_length(handle, &len) == DAPANE_OK);
    assert(len == expected_len && len > 0);
    unsigned char *copy = malloc(len + 1);
    assert(copy != NULL);
    memset(copy, 0xa5, len + 1);
    assert(dapane_v1_result_copy(handle, copy, len - 1, &written) == DAPANE_BUFFER_TOO_SMALL);
    assert(written == len);
    for (size_t i = 0; i <= len; ++i) assert(copy[i] == 0xa5);
    assert(dapane_v1_result_copy(handle, NULL, 0, &written) == DAPANE_BUFFER_TOO_SMALL);
    assert(written == len);
    assert(dapane_v1_result_copy(handle, copy, len, &written) == DAPANE_OK);
    assert(written == len && copy[len] == 0xa5);
    assert(memcmp(copy, expected, len) == 0);
    assert(dapane_v1_result_free(handle) == DAPANE_OK);
    assert(dapane_v1_result_free(handle) == DAPANE_INVALID_HANDLE);
    assert(dapane_v1_result_length(handle, &len) == DAPANE_INVALID_HANDLE && len == 0);
    assert(dapane_v1_result_copy(handle, copy, expected_len, &written) == DAPANE_INVALID_HANDLE);
    assert(written == 0 && memcmp(copy, expected, expected_len) == 0);
    free(copy);
}

struct worker_input { const unsigned char *input; size_t length; const unsigned char *expected; size_t expected_len; };

static void *worker(void *context) {
    const struct worker_input *data = context;
    for (size_t i = 0; i < 100; ++i) {
        uint64_t handle = 0;
        assert(dapane_v1_evaluate(1, DAPANE_POINT, data->input, data->length, &handle) == DAPANE_OK);
        check_result(handle, data->expected, data->expected_len);
    }
    return NULL;
}

int main(int argc, char **argv) {
    assert(argc == 2 && dapane_abi_version() == 1);
    uint64_t handle = 0;
    size_t length = 99;
    const unsigned char invalid_utf8[] = {0xff};
    assert(dapane_v1_evaluate(99, DAPANE_POINT, NULL, 1, &handle) == DAPANE_ABI_MISMATCH && handle == 0);
    assert(dapane_v1_evaluate(1, 99, NULL, 1, &handle) == DAPANE_UNSUPPORTED_OPERATION && handle == 0);
    assert(dapane_v1_evaluate(1, DAPANE_POINT, NULL, 1, &handle) == DAPANE_INVALID_ARGUMENT);
    assert(dapane_v1_evaluate(1, DAPANE_POINT, invalid_utf8, 1, &handle) == DAPANE_INVALID_UTF8);
    assert(dapane_v1_evaluate(1, DAPANE_POINT, invalid_utf8, DAPANE_MAX_REQUEST_BYTES + 1, &handle) == DAPANE_INPUT_LIMIT);
    assert(dapane_v1_evaluate(1, DAPANE_POINT, NULL, 0, NULL) == DAPANE_INVALID_ARGUMENT);
    assert(dapane_v1_result_length(0, NULL) == DAPANE_INVALID_ARGUMENT);
    assert(dapane_v1_result_length(0, &length) == DAPANE_INVALID_HANDLE && length == 0);
    assert(dapane_v1_evaluate(1, DAPANE_POINT, NULL, 0, &handle) == DAPANE_CORE_ERROR && handle != 0);
    assert(dapane_v1_result_free(handle) == DAPANE_OK);
    handle = 0;

    char path[4096];
    assert(snprintf(path, sizeof(path), "%s/cases.tsv", argv[1]) < (int)sizeof(path));
    FILE *index = fopen(path, "r");
    assert(index != NULL);
    char row[1024], name[128], operation[32], status[128];
    assert(fgets(row, sizeof(row), index));
    size_t cases = 0;
    while (fgets(row, sizeof(row), index)) {
        assert(sscanf(row, "%127s %31s %127s", name, operation, status) == 3);
        assert(snprintf(path, sizeof(path), "%s/%s.input.json", argv[1], name) < (int)sizeof(path));
        size_t input_len, expected_len;
        unsigned char *input = read_file(path, &input_len);
        assert(snprintf(path, sizeof(path), "%s/%s.output.json", argv[1], name) < (int)sizeof(path));
        unsigned char *expected = read_file(path, &expected_len);
        uint32_t method = strcmp(operation, "point") == 0 ? DAPANE_POINT : DAPANE_INTERVAL;
        uint32_t wanted = strcmp(status, "ok") == 0 ? DAPANE_OK : DAPANE_CORE_ERROR;
        assert(dapane_v1_evaluate(1, method, input, input_len, &handle) == wanted);
        /* The returned handle cannot borrow the request's bytes. */
        memset(input, 0, input_len);
        free(input);
        assert(dapane_v1_evaluate(1, method, NULL, 0, &handle) == DAPANE_INVALID_ARGUMENT);
        check_result(handle, expected, expected_len);
        handle = 0;
        free(expected);
        ++cases;
    }
    assert(fclose(index) == 0);

    uint64_t handles[64] = {0};
    for (size_t i = 0; i < 64; ++i)
        assert(dapane_v1_evaluate(1, DAPANE_POINT, NULL, 0, &handles[i]) == DAPANE_CORE_ERROR);
    assert(dapane_v1_evaluate(1, DAPANE_POINT, NULL, 0, &handle) == DAPANE_RESOURCE_LIMIT && handle == 0);
    for (size_t i = 0; i < 64; ++i) assert(dapane_v1_result_free(handles[i]) == DAPANE_OK);

    struct worker_input data;
    assert(snprintf(path, sizeof(path), "%s/workforce.input.json", argv[1]) < (int)sizeof(path));
    data.input = read_file(path, &data.length);
    assert(snprintf(path, sizeof(path), "%s/workforce.output.json", argv[1]) < (int)sizeof(path));
    data.expected = read_file(path, &data.expected_len);
    pthread_t threads[4];
    for (size_t i = 0; i < 4; ++i) assert(pthread_create(&threads[i], NULL, worker, &data) == 0);
    for (size_t i = 0; i < 4; ++i) assert(pthread_join(threads[i], NULL) == 0);
    free((void *)data.input);
    free((void *)data.expected);
    printf("%zu shared cases; lifecycle, bounds and 400 concurrent native calls passed\n", cases);
    return 0;
}
