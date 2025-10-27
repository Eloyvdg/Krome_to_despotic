UNAME_S := $(shell uname -s)
ifeq ($(UNAME_S),Linux)
include Make.mach.Linux
endif
ifeq ($(UNAME_S),Darwin)
include Make.mach.macOS
endif
