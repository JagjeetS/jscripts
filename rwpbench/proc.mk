# This makefile builds the sample programs in $(ORACLE_HOME)/precomp/demo/proc
# and can serve as a template for linking customer applications.
#
# demo_proc64.mk is similar to demo_proc.mk, but is used to build 64-bit client
# executables.
MAKEFILE:= $(lastword $(MAKEFILE_LIST))

include $(ORACLE_HOME)/precomp/lib/env_precomp.mk

# SAMPLES is a list of the c proc sample programs.
# CPPSAMPLES is a list of the c++ proc sample programs.
# OBJECT_SAMPLES is a list of the proc sample programs using the new
# type features.  You must install ott in addition to proc to run some
# of those samples.
SAMPLES=oraunloader rwpbench oraunloader_na

# These targets build all of a class of samples in one call to make.
samples: clean $(SAMPLES)

# The target 'build' puts together an executable $(EXE) from the .o files
# in $(OBJS) and the libraries in $(PROLDLIBS).  It is used to build the
# c sample programs.
# The rules to make .o files from .c and .pc files are later in this file.
# $(PROLDLIBS) uses the client shared library; $(STATICPROLDLIBS) does not.
#
build: $(OBJS)
	$(DEMO_PROC_BUILD_SHARED)
build_static: $(OBJS)
	$(DEMO_PROC_BUILD_STATIC)

$(SAMPLES) $(OBJECT_SAMPLES):
	$(MAKE) -f $(MAKEFILE) OBJS=$@.o EXE=$@ build

#-------------------------------------------------------------------
# Clean up all executables, *.o and generated *.c files
clean:
	$(SILENT)$(RMF) $(SAMPLES) $(CPPSAMPLES) $(OBJECT_SAMPLES)
	$(SILENT)$(RMF) *.c *.lis *.$(OBJ_EXT)

# sample5.pc illustrates the precompiler part of building a precompiler-forms
# application.  Building the actual executable would require the FORMS bundle.
# Some of the samples require that .sql scripts be run before precompilation.
# If you set RUNSQL=run in your call to make, then make will use sqlplus or
# svrmgrl, as appropriate, to run the .sql scripts.
# If you leave RUNSQL unset, then make will print out a reminder to run the
# scripts.
# If you have already run the scripts, then RUNSQL=done will omit the reminder.

# Here are some rules for converting .pc -> .c -> .o and for .typ -> .h.
#
# If proc needs to find .h files, it should find the same .h files that the 
# c compiler finds.  We use a macro named INCLUDE to hadle that.  The general 
# format of the INCLUDE macro is 
#   INCLUDE= $(I_SYM)dir1 $(I_SYM)dir2 ...
#
# Normally, I_SYM=-I, for the c compiler.  However, we have a special target,
# pc1, which calls $(PROC_64) with various arguments, including $(INCLUDE).  It
# is used like this:
#	$(MAKE) -f $(MAKEFILE) <more args to make> I_SYM=include= pc1
# This is used for some of $(SAMPLES) and for $(OBJECT_SAMPLES).
.SUFFIXES: .pc .c .o .typ .h

pc1:
	$(PCC2C)

.pc.c:
	$(MAKE) -f $(MAKEFILE) PROCFLAGS="$(PROCFLAGS)" PCCSRC=$* I_SYM=include= pc1 common_parser=yes

.pc.o:
	$(MAKE) -f $(MAKEFILE) PROCFLAGS="$(PROCFLAGS)" PCCSRC=$* I_SYM=include= pc1 common_parser=yes
	$(C2O)

.c.o:
	$(C2O)

.typ.h:
	$(OTT) intype=$*.typ hfile=$*.h outtype=$*o.typ $(OTTFLAGS) code=c userid=$(USERID)

# These are specific targets to make the .o files for samples that require
# more careful handling.
# These macro definitions fill in some details or override some defaults
#LIBDIR=$(LIBDIR)
OTTFLAGS=$(PCCFLAGS)
PROCPPFLAGS=code=cpp $(CPLUS_SYS_INCLUDE)
PROCPLSFLAGS=SQLCHECK=SYNTAX DYNAMIC=ANSI 
PROCFLAGS=SQLCHECK=SYNTAX DYNAMIC=ANSI prefetch=100 common_parser=yes 
INCLUDE=$(I_SYM). $(I_SYM)$(PRECOMPHOME)public $(I_SYM)$(RDBMSHOME)public $(I_SYM)$(RDBMSHOME)demo $(I_SYM)$(PLSQLHOME)public $(I_SYM)$(NETWORKHOME)public
