/* Separate host because both checked objects export the same ABI symbol. */
#include <inttypes.h>
#include <stdint.h>
#include <stdio.h>

struct result {
    int64_t value;
    uint32_t status;
    uint32_t span_id;
};

extern struct result scarp_checked_integer_function(
    int64_t, int64_t, int64_t, int64_t, int64_t, int64_t, int64_t, int64_t);

static void report(const char *label, struct result r) {
    printf("%s %" PRId64 " %" PRIu32 " %" PRIu32 "\n",
           label, r.value, r.status, r.span_id);
}

int main(void) {
    report("wide-forward", scarp_checked_integer_function(1, 2, 3, 4, 5, 6, 7, 8));
    report("wide-reverse", scarp_checked_integer_function(8, 7, 6, 5, 4, 3, 2, 1));
    report("wide-overflow", scarp_checked_integer_function(0, 0, 0, 0, 0, 0, 0, INT64_MAX));
    return 0;
}
