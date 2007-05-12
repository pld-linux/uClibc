Summary:	C library optimized for size
Summary(pl.UTF-8):	Biblioteka C zoptymalizowana na rozmiar
Name:		uClibc
Version:	0.9.29
Release:	0.1
Epoch:		2
License:	LGPL
Group:		Libraries
Source0:	http://uclibc.org/downloads/%{name}-%{version}.tar.bz2
# Source0-md5:	61dc55f43b17a38a074f347e74095b20
Patch0:		%{name}-newsoname.patch
Patch1:		%{name}-toolchain-wrapper.patch
Patch2:		%{name}-targetcpu.patch
Patch3:		%{name}-debug.patch
Patch4:		%{name}-sparc.patch
Patch5:		%{name}-ppc-ioctl-errno.patch
Patch6:		%{name}-syscallerror.patch
URL:		http://uclibc.org/
BuildRequires:	binutils-gasp
BuildRequires:	gcc >= 5:3.0
BuildRequires:	linux-libc-headers >= 7:2.6.20
BuildRequires:	sed >= 4.0
BuildRequires:	which
ExclusiveArch:	alpha %{ix86} ppc sparc sparc64 sparcv9 %{x8664}
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define		uclibc_root	/usr/%{_target_cpu}-linux-uclibc
# note: the 2nd '\' is needed (some shell expansions?)
%define		TARGET_ARCH	%(echo %{_target_cpu} | sed -e 's/i.86\\|athlon\\|pentium./i386/;s/ppc/powerpc/;s/amd64\\|ia32e/x86_64/')

%description
Small libc for building embedded applications.

%description -l pl.UTF-8
Mała libc do budowania aplikacji wbudowanych.

%package devel
Summary:	Development files for uClibc
Summary(pl.UTF-8):	Pliki dla programistów uClibc
Group:		Development/Libraries
Requires:	%{name} = %{epoch}:%{version}-%{release}
Requires:	binutils
Requires:	linux-libc-headers >= 7:2.6.20
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
# check if it's needed now... ldso is broken on sparc anyway
#%patch4 -p1
# shouldn't be needed now
#%patch5 -p1
#%patch6 -p1

sed -i -e '
%ifarch sparc sparc64 sparcv9
	s/default TARGET_i386/default TARGET_sparc/
%endif
%ifarch alpha
	s/default TARGET_i386/default TARGET_alpha/
%endif
%ifarch ppc ppc64
	s/default TARGET_i386/default TARGET_powerpc/
%endif
%ifarch %{x8664}
	s/default TARGET_i386/default TARGET_x86_64/
%endif
	' extra/Configs/Config.in

%ifarch sparc64
ln -sf /usr/include/asm-sparc include/asm-sparc
ln -sf /usr/include/asm-sparc64 include/asm-sparc64
%{__perl} -pi -e 's/^(rm.*asm)\*/$1/' extra/scripts/fix_includes.sh
%endif

%build
%{__make} defconfig \
	TARGET_ARCH="%{TARGET_ARCH}" \
	TARGET_CPU="%{_target_cpu}" \
	KERNEL_SOURCE=%{_prefix} \
	HOSTCC="%{__cc}" \
	HOSTCFLAGS="%{rpmcflags} %{rpmldflags}" \
	OPTIMIZATION="%{rpmcflags} -Os" \
	CC="%{__cc}"

mv -f .config .config.tmp
sed -e 's/^.*UCLIBC_HAS_IPV6.*$/UCLIBC_HAS_IPV6=y/;
	s/^.*DO_C99_MATH.*$/DO_C99_MATH=y/;
	s/^.*UCLIBC_HAS_RPC.*/UCLIBC_HAS_RPC=y\n# UCLIBC_HAS_FULL_RPC is not set\n# UCLIBC_HAS_REENTRANT_RPC is not set/;
	s/^.*UCLIBC_HAS_SYS_SIGLIST.*$/UCLIBC_HAS_SYS_SIGLIST=y/;
	s,^SHARED_LIB_LOADER_PREFIX=.*,SHARED_LIB_LOADER_PREFIX="$(RUNTIME_PREFIX)/lib",
	s/^.*UCLIBC_HAS_PRINTF_M_SPEC.*$/UCLIBC_HAS_PRINTF_M_SPEC=y/;
%{?debug:s/^.*\<DODEBUG\>.*$/DODEBUG=y/;s/^.*SUPPORT_LD_DEBUG\>.*$/SUPPORT_LD_DEBUG=y/;s/^.*SUPPORT_LD_DEBUG_EARLY.*$/SUPPORT_LD_DEBUG_EARLY=y/;s/^.*\<DOSTRIP\>.*$/# DOSTRIP is not set/;}
	' .config.tmp > .config

# force regeneration after .config changes
rm -f include/bits/uClibc_config.h

# note: defconfig and all must be run in separate make process because of macros
%{__make} \
	TARGET_ARCH="%{TARGET_ARCH}" \
	TARGET_CPU="%{_target_cpu}" \
	KERNEL_SOURCE=%{_prefix} \
	HOSTCC="%{__cc}" \
	HOSTCFLAGS="%{rpmcflags} %{rpmldflags}" \
	OPTIMIZATION="%{rpmcflags} -Os" \
	CC="%{__cc}"

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT%{_bindir}

%{__make} install \
	NATIVE_CC="%{__cc}" \
	NATIVE_CFLAGS="%{rpmcflags} %{rpmldflags}" \
	TARGET_ARCH="%{TARGET_ARCH}" \
	TARGET_CPU="%{_target_cpu}" \
	CC="%{__cc}" \
	PREFIX=$RPM_BUILD_ROOT

mv -f $RPM_BUILD_ROOT%{uclibc_root}/usr/lib/{libpthread-uclibc,libpthread}.so
ln -sf libpthread-0.9.29.so $RPM_BUILD_ROOT%{uclibc_root}/lib/libpthread.so.0

# these links are *needed* (by stuff in bin/)
for f in $RPM_BUILD_ROOT%{uclibc_root}/bin/*; do
	mv -f $f $RPM_BUILD_ROOT%{_bindir}
	ln -sf ../../bin/`basename $f` $f
done

for f in c++ cc g++ gcc ld; do
	ln -sf /usr/bin/%{_target_cpu}-uclibc-$f \
		$RPM_BUILD_ROOT%{uclibc_root}/usr/bin/$f
done

rm -rf $RPM_BUILD_ROOT%{uclibc_root}/usr/include/{linux,asm*}
ln -sf /usr/include/asm $RPM_BUILD_ROOT%{uclibc_root}/usr/include/asm
ln -sf /usr/include/asm-generic $RPM_BUILD_ROOT%{uclibc_root}/usr/include/asm-generic
%ifarch %{x8664}
	ln -sf /usr/include/asm-i386 $RPM_BUILD_ROOT%{uclibc_root}/usr/include/asm-i386
	ln -sf /usr/include/asm-x86_64 $RPM_BUILD_ROOT%{uclibc_root}/usr/include/asm-x86_64
%endif
%ifarch sparc64
ln -sf /usr/include/asm-sparc $RPM_BUILD_ROOT%{uclibc_root}/usr/include/asm-sparc
ln -sf /usr/include/asm-sparc64 $RPM_BUILD_ROOT%{uclibc_root}/usr/include/asm-sparc64
%endif
ln -sf /usr/include/linux $RPM_BUILD_ROOT%{uclibc_root}/usr/include/linux

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(644,root,root,755)
%doc Changelog* DEDICATION.mjn3 MAINTAINERS README TODO
%dir %{uclibc_root}
%ifarch %{ix86} %{x8664} ppc sparc sparc64 sparcv9
%dir %{uclibc_root}/lib
%attr(755,root,root) %{uclibc_root}/lib/*.so*
%endif

%files devel
%defattr(644,root,root,755)
%doc docs/*.txt
%attr(755,root,root) %{_bindir}/*
%{uclibc_root}/usr/lib/*.o
%dir %{uclibc_root}/usr
%dir %{uclibc_root}/usr/bin
%attr(755,root,root) %{uclibc_root}/usr/bin/*
%dir %{uclibc_root}/usr/lib
%{uclibc_root}/usr/lib/uclibc_nonshared.a
%ifarch %{ix86} %{x8664} ppc sparc sparc64 sparcv9
%attr(755,root,root) %{uclibc_root}/usr/lib/*.so
%endif
%{uclibc_root}/usr/include

%files static
%defattr(644,root,root,755)
%{uclibc_root}/usr/lib/lib*.a
