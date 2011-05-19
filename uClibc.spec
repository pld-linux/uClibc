#
# Conditional build:
%bcond_without	shared		# don't build shared lib support
%bcond_with	verbose		# verbose mode
#
%ifarch alpha
%undefine	with_shared
%endif
#
Summary:	C library optimized for size
Summary(pl.UTF-8):	Biblioteka C zoptymalizowana na rozmiar
Name:		uClibc
Version:	0.9.30.3
Release:	7
Epoch:		4
License:	LGPL v2.1
Group:		Libraries
Source0:	http://uclibc.org/downloads/%{name}-%{version}.tar.bz2
# Source0-md5:	73a4bf4a0fa508b01a7a3143574e3d21
Patch0:		%{name}-newsoname.patch
Patch1:		%{name}-toolchain-wrapper.patch
Patch2:		%{name}-targetcpu.patch
Patch3:		%{name}-debug.patch
Patch4:		%{name}-stdio-unhide.patch
Patch5:		%{name}-inotify_init1.patch
Patch6:		%{name}-sockflags.patch
URL:		http://uclibc.org/
BuildRequires:	binutils-gasp
BuildRequires:	cpp
BuildRequires:	gcc >= 5:3.0
BuildRequires:	linux-libc-headers >= 7:2.6.24
BuildRequires:	ncurses-devel
BuildRequires:	rpmbuild(macros) >= 1.453
BuildRequires:	sed >= 4.0
BuildRequires:	which
ExclusiveArch:	alpha %{ix86} ppc sparc sparcv9 %{x8664}
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%if "%{cc_version}" >= "4.2"
%define		specflags	-fgnu89-inline
%endif

%define		uclibc_root	/usr/%{_target_cpu}-linux-uclibc

%description
Small libc for building embedded applications.

%description -l pl.UTF-8
Mała libc do budowania aplikacji wbudowanych.

%package devel
Summary:	Development files for uClibc
Summary(pl.UTF-8):	Pliki dla programistów uClibc
Group:		Development/Libraries
Requires:	%{name} = %{epoch}:%{version}-%{release}
Requires:	binutils-gasp
Requires:	linux-libc-headers >= 7:2.6.24
%requires_eq	gcc

%description devel
Small libc for building embedded applications.

%description devel -l pl.UTF-8
Mała libc do budowania aplikacji wbudowanych.

%package static
Summary:	Static uClibc libraries
Summary(pl.UTF-8):	Biblioteki statyczne uClibc
Group:		Development/Libraries
Requires:	%{name}-devel = %{epoch}:%{version}-%{release}
Provides:	libc-static

%description static
Static uClibc libraries.

%description static -l pl.UTF-8
Biblioteki statyczne uClibc.

%prep
%setup -q
%patch0 -p1
%patch1 -p1
%patch2 -p1
%patch3 -p1
%patch4 -p1
%patch5 -p1
%patch6 -p1

# ARCH is already determined by uname -m
%ifarch %{ix86}
defconfig=extra/Configs/defconfigs/i386
%ifarch i386
echo 'CONFIG_386=y' >> $defconfig
%endif
%ifarch i486
echo 'CONFIG_486=y' >> $defconfig
%endif
%ifarch i586
echo 'CONFIG_586=y' >> $defconfig
%endif
%ifarch i686
echo 'CONFIG_686=y' >> $defconfig
%endif
%ifarch pentium3
echo 'CONFIG_PENTIUMIII=y' >> $defconfig
%endif
%ifarch pentium4
echo 'CONFIG_PENTIUM4=y' >> $defconfig
%endif
%ifarch athlon
echo 'CONFIG_K7=y' >> $defconfig
%endif
%endif
%ifarch %{x8664}
defconfig=extra/Configs/defconfigs/x86_64
%endif
%ifarch alpha
defconfig=extra/Configs/defconfigs/alpha
%endif
%ifarch sparc sparcv9
defconfig=extra/Configs/defconfigs/sparc
%endif
%ifarch ppc
defconfig=extra/Configs/defconfigs/powerpc
%endif
%ifarch ia64
defconfig=extra/Configs/defconfigs/ia64
%endif

cat <<'EOF' >> $defconfig
UCLIBC_HAS_IPV6=y
DO_C99_MATH=y
UCLIBC_HAS_RPC=y
# UCLIBC_HAS_FULL_RPC is not set
# UCLIBC_HAS_REENTRANT_RPC is not set
UCLIBC_HAS_SYS_SIGLIST=y
SHARED_LIB_LOADER_PREFIX="$(RUNTIME_PREFIX)/lib"
LDSO_GNU_HASH_SUPPORT=y
%if %{without shared}
HAVE_NO_SHARED=y
# HAVE_SHARED is not set
%endif
UCLIBC_HAS_PRINTF_M_SPEC=y
UCLIBC_SUSV3_LEGACY=y
UCLIBC_SUSV3_LEGACY_MACROS=y
# DOSTRIP is not set
%{?debug:DODEBUG=y}
%{?debug:SUPPORT_LD_DEBUG=y}
%{?debug:SUPPORT_LD_DEBUG_EARLY=y}
EOF

%build

# NOTE: 'defconfig' and 'all' must be run in separate make process because of macros
%{__make} -j1 defconfig \
	%{?with_verbose:VERBOSE=1} \
	TARGET_CPU="%{_target_cpu}" \
	GCC_BIN=%{_host_cpu}-%{_vendor}-%{_os}-gcc \
	HOSTCC="%{__cc}" \
	CC="%{__cc}" \
	HOSTCFLAGS="%{rpmcflags} %{rpmldflags}" \
	OPTIMIZATION="%{rpmcflags} -Os"

# The Makefile includes .config and later tries to assign same variable,
# eventually it gets lost and sets wrong value for TARGET_ARCH and bad value
# for UCLIBC_LDSO in extra/gcc-uClibc.
# So we pass it as make arg to be sure it's proper!
target_arch=$(grep -s '^TARGET_ARCH' .config | sed -e 's/^TARGET_ARCH=//' -e 's/"//g')

%{__make} -j1 \
	%{?with_verbose:VERBOSE=1} \
	TARGET_CPU="%{_target_cpu}" \
	TARGET_ARCH=$target_arch \
	GCC_BIN=%{_host_cpu}-%{_vendor}-%{_os}-gcc \
	HOSTCC="%{__cc}" \
	CC="%{__cc}" \
	HOSTCFLAGS="%{rpmcflags} %{rpmldflags}" \
	OPTIMIZATION="%{rpmcflags} -Os"

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT%{_bindir}

%{__make} -j1 install \
	%{?with_verbose:VERBOSE=1} \
	TARGET_CPU="%{_target_cpu}" \
	HOSTCC="%{__cc}" \
	HOSTCFLAGS="%{rpmcflags} %{rpmldflags}" \
	CC="%{__cc}" \
	OPTIMIZATION="%{rpmcflags} -Os" \
	DESTDIR=$RPM_BUILD_ROOT

%if %{with shared}
mv -f $RPM_BUILD_ROOT%{uclibc_root}/usr/lib/{libpthread-uclibc,libpthread}.so
ln -sf libpthread-%{version}.so $RPM_BUILD_ROOT%{uclibc_root}/lib/libpthread.so.0
chmod a+rx $RPM_BUILD_ROOT%{uclibc_root}/lib/*.so
%endif

# these links are *needed* (by stuff in bin/)
for f in $RPM_BUILD_ROOT%{uclibc_root}/bin/*; do
	if [ -L $f ]; then
		l=$(readlink $f)
		a=${l##*/}
		d=${l%/*}
		case "$d" in
		%{_bindir})
			ln -sf ${l#%{_bindir}/} $RPM_BUILD_ROOT%{_bindir}/${f##*/}
			rm -f $f
			;;
		$a)
			mv -f $f $RPM_BUILD_ROOT%{_bindir}
			;;
		*)
			exit 1
			;;
		esac
	else
		a=${f#*/%{_target_cpu}-uclibc-}
		ln -sf %{_bindir}/$(basename $f) $RPM_BUILD_ROOT%{uclibc_root}/usr/bin/$a
		mv -f $f $RPM_BUILD_ROOT%{_bindir}
	fi
done

for f in $RPM_BUILD_ROOT%{uclibc_root}/usr/bin/*; do
	if [ -L $f ]; then
		l=$(readlink $f)
		case "${l%/*}" in
		%{uclibc_root}/bin)
			a=${l#*/%{_target_cpu}-uclibc-}
			ln -sf %{_bindir}/$a $f
			;;
		%{_bindir})
			:
			;;
		*)
			exit 2
			;;
		esac
	fi
done

rm -rf $RPM_BUILD_ROOT%{uclibc_root}/usr/include/{linux,asm*}
# rpm -ql linux-libc-headers | awk -F/ ' /^\/usr\/include\// { print "/usr/include/" $4 } ' | sort -u
for dir in asm asm-generic linux mtd rdma sound video xen; do
	ln -sf /usr/include/${dir} $RPM_BUILD_ROOT%{uclibc_root}/usr/include/${dir}
done
# for future use
%ifarch sparc64
ln -sf /usr/include/asm-sparc $RPM_BUILD_ROOT%{uclibc_root}/usr/include/asm-sparc
ln -sf /usr/include/asm-sparc64 $RPM_BUILD_ROOT%{uclibc_root}/usr/include/asm-sparc64
%endif

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(644,root,root,755)
%doc Changelog* DEDICATION.mjn3 MAINTAINERS README TODO
%dir %{uclibc_root}
%ifarch %{ix86} %{x8664} ppc sparc sparcv9
%if %{with shared}
%dir %{uclibc_root}/lib
%attr(755,root,root) %{uclibc_root}/lib/*.so*
%endif
%endif

%files devel
%defattr(644,root,root,755)
%doc docs/*.txt
%attr(755,root,root) %{_bindir}/%{_target_cpu}-uclibc-addr2line
%attr(755,root,root) %{_bindir}/%{_target_cpu}-uclibc-ar
%attr(755,root,root) %{_bindir}/%{_target_cpu}-uclibc-as
%attr(755,root,root) %{_bindir}/%{_target_cpu}-uclibc-c++
%attr(755,root,root) %{_bindir}/%{_target_cpu}-uclibc-cc
%attr(755,root,root) %{_bindir}/%{_target_cpu}-uclibc-cpp
%attr(755,root,root) %{_bindir}/%{_target_cpu}-uclibc-g++
%attr(755,root,root) %{_bindir}/%{_target_cpu}-uclibc-gasp
%attr(755,root,root) %{_bindir}/%{_target_cpu}-uclibc-gcc
%attr(755,root,root) %{_bindir}/%{_target_cpu}-uclibc-ld
%attr(755,root,root) %{_bindir}/%{_target_cpu}-uclibc-nm
%attr(755,root,root) %{_bindir}/%{_target_cpu}-uclibc-objcopy
%attr(755,root,root) %{_bindir}/%{_target_cpu}-uclibc-objdump
%attr(755,root,root) %{_bindir}/%{_target_cpu}-uclibc-ranlib
%attr(755,root,root) %{_bindir}/%{_target_cpu}-uclibc-size
%attr(755,root,root) %{_bindir}/%{_target_cpu}-uclibc-strings
%attr(755,root,root) %{_bindir}/%{_target_cpu}-uclibc-strip
%{uclibc_root}/usr/lib/*.o
%dir %{uclibc_root}/usr
%dir %{uclibc_root}/usr/bin
%attr(755,root,root) %{uclibc_root}/usr/bin/addr2line
%attr(755,root,root) %{uclibc_root}/usr/bin/ar
%attr(755,root,root) %{uclibc_root}/usr/bin/as
%attr(755,root,root) %{uclibc_root}/usr/bin/c++
%attr(755,root,root) %{uclibc_root}/usr/bin/cc
%attr(755,root,root) %{uclibc_root}/usr/bin/cpp
%attr(755,root,root) %{uclibc_root}/usr/bin/g++
%attr(755,root,root) %{uclibc_root}/usr/bin/gasp
%attr(755,root,root) %{uclibc_root}/usr/bin/gcc
%attr(755,root,root) %{uclibc_root}/usr/bin/ld
%attr(755,root,root) %{uclibc_root}/usr/bin/nm
%attr(755,root,root) %{uclibc_root}/usr/bin/objcopy
%attr(755,root,root) %{uclibc_root}/usr/bin/objdump
%attr(755,root,root) %{uclibc_root}/usr/bin/ranlib
%attr(755,root,root) %{uclibc_root}/usr/bin/size
%attr(755,root,root) %{uclibc_root}/usr/bin/strings
%attr(755,root,root) %{uclibc_root}/usr/bin/strip
%dir %{uclibc_root}/usr/lib
%if %{with shared}
%{uclibc_root}/usr/lib/uclibc_nonshared.a
%ifarch %{ix86} %{x8664} ppc sparc sparcv9
%attr(755,root,root) %{uclibc_root}/usr/lib/*.so
%endif
%endif
%{uclibc_root}/usr/include

%files static
%defattr(644,root,root,755)
%{uclibc_root}/usr/lib/lib*.a
