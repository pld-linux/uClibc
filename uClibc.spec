# TODO:
# - test on something more that 'hello world'
# - check/update configuration
#
Summary:	C library optimized for size
Summary(pl):	Biblioteka C zoptymalizowana na rozmiar
Name:		uClibc
Version:	0.9.26
Release:	2
Epoch:		2
License:	LGPL
Group:		Libraries
Source0:	http://uclibc.org/downloads/%{name}-%{version}.tar.bz2
# Source0-md5:	7212713c432dd0de6ec2140c2a6212e4
Patch0:		%{name}-asmflags.patch
Patch1:		%{name}-newsoname.patch
Patch2:		%{name}-use-kernel-headers.patch
Patch3:		%{name}-alpha.patch
Patch4:		%{name}-sparc.patch
Patch5:		%{name}-toolchain-wrapper.patch
Patch6:		%{name}-targetcpu.patch
Patch7:		%{name}-linux2.6.patch
URL:		http://uclibc.org/
BuildRequires:	sed >= 4.0
BuildRequires:	which
ExclusiveArch:	alpha %{ix86} ppc sparc sparc64
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

# note: the 2nd '\' is needed (some shell expansions?)
%define		TARGET_ARCH	%(echo %{_target_cpu} | sed -e 's/i.86\\|athlon\\|pentium3/i386/;s/ppc/powerpc/')

%description
Small libc for building embedded applications.

%description -l pl
Ma³a libc do budowania aplikacji wbudowanych.

%package devel
Summary:	Development files for uClibc
Summary(pl):	Pliki dla programistów uClibc
Group:		Development/Libraries
Requires:	%{name} = %{epoch}:%{version}-%{release}
Requires:	binutils
Requires:	linux-libc-headers
%requires_eq	gcc

%description devel
Small libc for building embedded applications.

%description devel -l pl
Ma³a libc do budowania aplikacji wbudowanych.

%package static
Summary:	Static uClibc libratries
Summary(pl):	Biblioteki statyczne uClibc
Group:		Development/Libraries
Requires:	%{name}-devel = %{epoch}:%{version}-%{release}
Provides:	libc-static

%description static
Static uClibc libratries.

%description static -l pl
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
%patch7 -p1

sed -e '
%ifarch sparc sparc64
	s/default TARGET_i386/default TARGET_sparc/
%endif
%ifarch alpha
	s/default TARGET_i386/default TARGET_alpha/
%endif
%ifarch ppc ppc64
	s/default TARGET_i386/default TARGET_powerpc/
%endif
	' extra/Configs/Config.in > Conf.in.tmp
mv -f Conf.in.tmp extra/Configs/Config.in

grep -v 'HAVE_NO_SHARED\|ARCH_HAS_NO_LDSO' extra/Configs/Config.sparc > C.tmp
mv -f C.tmp extra/Configs/Config.sparc

%build
%{__make} defconfig \
	TARGET_ARCH="%{TARGET_ARCH}" \
	TARGET_CPU="%{_target_cpu}" \
	KERNEL_SOURCE=%{_prefix} \
	HOSTCC=%{__cc} \
	HOSTCFLAGS="%{rpmcflags} %{rpmldflags}" \
	OPTIMIZATION="%{rpmcflags} -Os" \
	CC="%{__cc}"

mv -f .config .config.tmp
sed -e 's/^.*UCLIBC_HAS_IPV6.*$/UCLIBC_HAS_IPV6=y/;
	s/^.*DO_C99_MATH.*$/DO_C99_MATH=y/;
	s/^.*UCLIBC_HAS_RPC.*/UCLIBC_HAS_RPC=y\n# UCLIBC_HAS_FULL_RPC is not set/
	' .config.tmp > .config
# force regeneration after .config changes
rm -f include/bits/uClibc_config.h

# note: defconfig and all must be run in separate make process because of macros
%{__make} \
	TARGET_ARCH="%{TARGET_ARCH}" \
	TARGET_CPU="%{_target_cpu}" \
	KERNEL_SOURCE=%{_prefix} \
	HOSTCC=%{__cc} \
	HOSTCFLAGS="%{rpmcflags} %{rpmldflags}" \
	OPTIMIZATION="%{rpmcflags} -Os" \
	CC="%{__cc}"

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT%{_bindir}

%{__make} install \
	NATIVE_CC=%{__cc} \
	NATIVE_CFLAGS="%{rpmcflags} %{rpmldflags}" \
	TARGET_ARCH="%{TARGET_ARCH}" \
	TARGET_CPU="%{_target_cpu}" \
	CC="%{__cc}" \
	PREFIX=$RPM_BUILD_ROOT

# these links are *needed* (by stuff in bin/)
for f in $RPM_BUILD_ROOT/usr/%{_target_cpu}-linux-uclibc/bin/* ; do
	mv -f $f $RPM_BUILD_ROOT%{_bindir}
	ln -sf ../../bin/`basename $f` $f
done

rm -rf $RPM_BUILD_ROOT/usr/%{_target_cpu}-linux-uclibc/usr/include/{linux,asm}
ln -sf /usr/include/asm $RPM_BUILD_ROOT/usr/%{_target_cpu}-linux-uclibc/usr/include/asm
ln -sf /usr/include/linux $RPM_BUILD_ROOT/usr/%{_target_cpu}-linux-uclibc/usr/include/linux

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(644,root,root,755)
%dir %{_prefix}/*-linux-uclibc
%ifarch %{ix86} ppc sparc sparc64
%dir %{_prefix}/*-linux-uclibc/lib
%attr(755,root,root) %{_prefix}/*-linux-uclibc/lib/*.so*
%endif

%files devel
%defattr(644,root,root,755)
%doc README TODO docs/threads.txt docs/uclibc.org/*.html
%attr(755,root,root) %{_bindir}/*
%{_prefix}/*-linux-uclibc/usr/lib/*.o
%dir %{_prefix}/*-linux-uclibc/usr
%attr(755,root,root) %{_prefix}/*-linux-uclibc/%{_bindir}/*
%dir %{_prefix}/*-linux-uclibc/usr/lib
%ifarch %{ix86} ppc sparc sparc64
%attr(755,root,root) %{_prefix}/*-linux-uclibc/usr/lib/*.so
%endif
%{_prefix}/*-linux-uclibc/usr/include

%files static
%defattr(644,root,root,755)
%{_prefix}/*-linux-uclibc/usr/lib/lib*.a
