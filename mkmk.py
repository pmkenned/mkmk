#!/usr/bin/env python3

import sys

# TODO:
#  OS-specific
#  SDL, threads, sockets
#  parse args
#  run N times

# profile
# doc
# lint
# memcheck
# cachegrind
# install
# uninstall
# library
# asm
# disasm

# parameters:
#  SRC_DIR
#  BUILD_DIR


def main(argv):

    include_run     = True if 'run'     in argv[1:] else False
    include_test    = True if 'test'    in argv[1:] else False
    include_debug   = True if 'debug'   in argv[1:] else False
    include_disasm  = True if 'disasm'  in argv[1:] else False
    include_profile = True if 'profile' in argv[1:] else False
    include_doc     = True if 'doc'     in argv[1:] else False

    makefile_template = r"""CC = gcc
CPPFLAGS = -MMD
CFLAGS = -Wall -Wextra -pedantic -std=c99
LDFLAGS =
LDLIBS =

SRC_DIR = ./src
SRC = $(wildcard $(SRC_DIR)/*.c)

{variables}

.PHONY: all clean {phonies}

all: $(BUILD_DIR)/$(TARGET)

clean:
	rm -rf $(BUILD_DIR)

{phony_rules}

{pat_rules}
"""

    variables_template = r"""{pre}TARGET = {target}
{name}_DIR = {build_dir}
{pre}OBJ = $(SRC:$(SRC_DIR)/%.c=$({name}_DIR)/%.o)
{pre}DEP = $({pre}OBJ:%.o=%.d)
"""

    pattern_rules_template = r"""# ==== {name} ====

$({name}_DIR)/%.o: $(SRC_DIR)/%.c
	mkdir -p $({name}_DIR)
	$(CC) $(CPPFLAGS) $(CFLAGS) -c -o $@ $<

$({name}_DIR)/$({pre}TARGET): $({pre}OBJ)
	mkdir -p $({name}_DIR)
	$(CC) $(LDFLAGS) -o $@ $^ $(LDLIBS)

-include $({pre}DEP)
"""

    variables = list()
    phony_rules = list()
    pat_rules = list()
    phonies = list()

    # build
    variables.append(variables_template.format(name='BUILD', pre='', target='a.out', build_dir='./build'))
    pat_rules.append(pattern_rules_template.format(name='BUILD', pre=''))

    if include_run:
        phonies.append('run')
        phony_rules.append('RUN_N ?= 1\nARGS ?=\nrun: $(BUILD_DIR)/$(TARGET)\n\t@for n in `seq 1 $(RUN_N)`; do /usr/bin/time -f "%e" $(BUILD_DIR)/$(TARGET) $(ARGS) ; done\n')

    if include_test:
        variables.append(variables_template.format(name='TEST', pre='TEST_', target='test_$(TARGET)', build_dir='$(BUILD_DIR)/test'))
        phonies.append('test')
        phony_rules.append('test: CPPFLAGS += -DTEST\ntest: $(TEST_DIR)/$(TEST_TARGET)\n\t$(TEST_DIR)/$(TEST_TARGET)\n')
        pat_rules.append(pattern_rules_template.format(name='TEST', pre='TEST_'))

    if include_debug:
        phonies.append('debug' if include_debug else '')
        phony_rules.append('debug: all\n\tgdb $(BUILD_DIR)/$(TARGET)\n')

    if include_disasm:
        phonies.append('disasm')
        phony_rules.append('disasm: $(BUILD_DIR)/disasm.out\n')
        pat_rules.append('$(BUILD_DIR)/disasm.out: $(BUILD_DIR)/$(TARGET)\n\tobjdump -dS $< > $@')

    # TODO: replace multiple spaces with one space: s/ +/ /g, likewise for newlines
    print(makefile_template.format(
        variables       = "\n".join(variables),
        phonies         = " ".join(phonies),
        phony_rules     = "\n".join(phony_rules),
        pat_rules       = "\n".join(pat_rules),
    ))

if __name__ == "__main__":
    main(sys.argv)
