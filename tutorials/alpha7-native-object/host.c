/* Independent Linux x86-64 SysV test host; not part of Scarp's runtime. */
#include <inttypes.h>
#include <stdint.h>
#include <stdio.h>

struct result {
    int64_t value;
    uint32_t status;
    uint32_t span_id;
};

extern struct result scarp_checked_integer_function(int64_t, int64_t);
extern struct result scarp_bounded_integer_function(int64_t);
extern struct result scarp_bounded_integer_entry(int64_t, int64_t);

static void report(const char *label, struct result r) {
    printf("%s %" PRId64 " %" PRIu32 " %" PRIu32 "\n",
           label, r.value, r.status, r.span_id);
}

int main(void) {
    report("checked", scarp_checked_integer_function(12, -5));
    report("overflow", scarp_checked_integer_function(INT64_MAX, 1));
    report("empty", scarp_bounded_integer_function(0));
    report("triangle", scarp_bounded_integer_function(5));
    report("negative", scarp_bounded_integer_function(-1));
    report("exhausted", scarp_bounded_integer_function(INT64_MAX));
    report("entry", scarp_bounded_integer_entry(21, 2));
    report("divide", scarp_bounded_integer_entry(21, 0));
    report("again", scarp_bounded_integer_entry(21, 2));
    return 0;
}
