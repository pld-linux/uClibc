# TODO:
# - test on something more that 'hello world'
# - check/update configuration
#
Summary:	C library optimized for size
Summary(pl):	Biblioteka C zoptymalizowana na rozmiar
Name:		uClibc
Version:	0.9.26
Release:	0.1
Epoch:		2
License:	LGPL
Group:		Libraries
Source0:	http://uclibc.org/downloads/%{name}-%{version}.tar.bz2
# Source0-md5:	7212713c432dd0de6ec2140c2a6212e4
Patch0:		%{name}-lfs.patch
Patch1:		%{name}-no_bogus_gai.patch
Patch2:		%{name}-targetcpu.patch
Patch3:		%{name}-awk.patch
Patch4:		%{name}-asmflags.patch
Patch5:		%{name}-newsoname.patch
Patch6:		%{name}-use-kernel-headers.patch
Patch7:		%{name}-alpha.patch
Patch8:		%{name}-gmon.patch
Patch9:		%{name}-sparc.patch
Patch10:	%{name}-toolchain-wrapper.patch
URL:		http://uclibc.org/
BuildRequires:	which
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
Small libc for building embedded applications.

%description -l pl
Ma³a libc do budowania aplikacji wbudowanych.

%package devel
Summary:	Development files for uClibc
Summary(pl):	Pliki dla programistów uClibc
Group:		Development/Libraries
Requires:	%{name} = %{epoch}:%{version}
Requires:	glibc-kernel-headers
Requires:	binutils
%requires_eq	gcc

%description devel
Small libc for building embedded applications.

%description devel -l pl
Ma³a libc do budowania aplikacji wbudowanych.

%package static
Summary:	Static uClibc libratries
Summary(pl):	Biblioteki statyczne uClibc
Group:		Development/Libraries
Requires:	%{name}-devel = %{epoch}:%{version}
Provides:	libc-static

%description static
Static uClibc libratries.

%description static -l pl
Biblioteki statyczne uClibc.

%prep
%setup -q
#%patch0 -p1  -- needs update
#%patch1 -p1  -- causes compilation errors
#%patch2 -p1
# OBSOLETE
#%patch3 -p1
#%patch4 -p1
%patch5 -p1
%patch6 -p1
#%patch7 -p1
#%patch8 -p1
#%patch9 -p1
%patch10 -p1

%ifarch %{ix86}
ln -sf extra/Configs/Config.i386 Config
%endif
%ifarch sparc sparc64
cp -f extra/Configs/Config.{powerpc,sparc}
ln -sf extra/Configs/Config.sparc Config
%endif
%ifarch alpha
# it doesn't matter I guess
cp -f extra/Configs/Config.{powerpc,alpha}
ln -sf extra/Configs/Config.alpha Config
%endif
%ifarch ppc ppc64
ln -sf extra/Configs/Config.powerpc Config
%endif

%build
cat Config > Config.tmp

#	s/^SYSTEM_DEVEL_PREFIX *=.*$/SYSTEM_DEVEL_PREFIX=\$\(DEVEL_PREFIX\)\/usr/;
sed -e '
%ifarch alpha
	s/^HAVE_SHARED *=.*$/HAVE_SHARED=n/;
%else
	s/^HAVE_SHARED *=.*$/HAVE_SHARED=y/;
%endif
	s/^SYSTEM_DEVEL_PREFIX *=.*$/SYSTEM_DEVEL_PREFIX="\/usr"/;
	s/^DOLFS *=.*$/DOLFS=y/;
	s/^HAS_SHADOW *=.*$/HAS_SHADOW=y/;
	s/^INCLUDE_IPV6 *=.*$/INCLUDE_IPV6=y/;
	s/^DO_C99_MATH *=.*$/DO_C99_MATH=y/;
	s/.*UCLIBC_HAS_RPC.*/UCLIBC_HAS_RPC=y/' Config.tmp > Config

# note: defconfig and all must be run in separate make process because of macros
for targ in defconfig all ; do
%{__make} ${targ} \
%ifarch ppc
	TARGET_ARCH="powerpc" \
	TARGET_CPU="powerpc" \
%else
	TARGET_ARCH="%(echo %{_target_cpu} | sed -e 's/i.86\|athlon/i386/')" \
	TARGET_CPU="%{_target_cpu}" \
%endif
	KERNEL_SOURCE=%{_prefix} \
	HOSTCC=%{__cc} \
	HOSTCFLAGS="%{rpmcflags} %{rpmldflags}" \
	OPTIMIZATION="%{rpmcflags} -Os" \
	CC="%{__cc}"
done

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT%{_bindir}
TARGET_ARCH="%(echo %{_target_cpu} | sed -e 's/i.86\|athlon/i386/')"

%{__make} install \
	NATIVE_CC=%{__cc} \
	NATIVE_CFLAGS="%{rpmcflags} %{rpmldflags}" \
	TARGET_ARCH="%(echo %{_target_cpu} | sed -e 's/i.86\|athlon/i386/')" \
	TARGET_CPU="%{_target_cpu}" \
	CC="%{__cc}" \
	PREFIX=$RPM_BUILD_ROOT

%ifarch ppc
ln -sf ppc-linux-uclibc $RPM_BUILD_ROOT/usr/powerpc-linux-uclibc
%endif

# these links are *needed* (by stuff in bin/)
for f in $RPM_BUILD_ROOT/usr/${TARGET_ARCH}-linux-uclibc/bin/* ; do
	mv -f $f $RPM_BUILD_ROOT%{_bindir}
	ln -sf ../../bin/`basename $f` $f
done

# links for proper arch (like athlon->i386 on athlon)
if [ "${TARGET_ARCH}" != "%{_target_cpu}" ]; then
	for f in $RPM_BUILD_ROOT%{_bindir}/*; do
		sf=$(basename "$f")
		newsf=$(echo "$sf" | sed -e "s#${TARGET_ARCH}#%{_target_cpu}#g")
		ln -s "$sf" $RPM_BUILD_ROOT%{_bindir}/${newsf}
	done
fi

rm -rf $RPM_BUILD_ROOT/usr/${TARGET_ARCH}-linux-uclibc/usr/include/{linux,asm}
ln -sf /usr/include/asm $RPM_BUILD_ROOT/usr/${TARGET_ARCH}-linux-uclibc/usr/include/asm
ln -sf /usr/include/linux $RPM_BUILD_ROOT/usr/${TARGET_ARCH}-linux-uclibc/usr/include/linux

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(644,root,root,755)
%dir %{_prefix}/*-linux-uclibc
%dir %{_prefix}/*-linux-uclibc/lib
%ifarch %{ix86} ppc sparc sparc64
%attr(755,root,root) %{_prefix}/*-linux-uclibc/lib/*.so*
%endif
%ifarch ppc
%{_prefix}/powerpc-linux-uclibc
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
