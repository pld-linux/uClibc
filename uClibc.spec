# TODO:
# - test on something more that 'hello world'
# - check/update configuration
#
Summary:	C library optimized for size
Summary(pl):	Biblioteka C zoptymalizowana na rozmiar
Name:		uClibc
Version:	0.9.21
Release:	4
Epoch:		2
License:	LGPL
Group:		Libraries
Source0:	http://uclibc.org/downloads/%{name}-%{version}.tar.bz2
# Source0-md5:	d4ecdc8350b7c481e06cff830883b8ec
Patch0:		%{name}-lfs.patch
Patch1:		%{name}-no_bogus_gai.patch
Patch2:		%{name}-targetcpu.patch
Patch3:		%{name}-awk.patch
Patch4:		%{name}-asmflags.patch
Patch5:		%{name}-newsoname.patch
Patch6:		%{name}-use-kernel-headers.patch
Patch7:		%{name}-alpha.patch
Patch8:		%{name}-gmon.patch
URL:		http://uclibc.org/
BuildRequires:	which
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
Small libc for building embedded applications.

%description -l pl
Ma�a libc do budowania aplikacji wbudowanych.

%package devel
Summary:	Development files for uClibc
Summary(pl):	Pliki dla programist�w uClibc
Group:		Development/Libraries
Requires:	%{name} = %{epoch}:%{version}
Requires:	binutils
%requires_eq	gcc

%description devel
Small libc for building embedded applications.

%description devel -l pl
Ma�a libc do budowania aplikacji wbudowanych.

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
%patch2 -p1
%patch3 -p1
%patch4 -p1
%patch5 -p1
%patch6 -p1
%patch7 -p1
%patch8 -p1

%ifarch %{ix86}
ln -sf extra/Configs/Config.i386.default Config
%endif
%ifarch sparc sparc64
cp -f extra/Configs/Config.{powerpc,sparc}.default
ln -sf extra/Configs/Config.sparc.default Config
%endif
%ifarch alpha
# it doesn't matter I guess
cp -f extra/Configs/Config.{powerpc,alpha}.default
ln -sf extra/Configs/Config.alpha.default Config
%endif
%ifarch ppc ppc64
ln -sf extra/Configs/Config.powerpc.default Config
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
#for f in $RPM_BUILD_ROOT/usr/%{_target_cpu}-linux-uclibc%{_bindir}/* ; do
#	mv $f $RPM_BUILD_ROOT%{_bindir}
#	ln -sf ../../../bin/`basename $f` $f
#done

find $RPM_BUILD_ROOT/usr/%{_target_cpu}-linux-uclibc/include \
	-name CVS -o -name .cvsignore | xargs rm -rf

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(644,root,root,755)
%dir %{_prefix}/%{_target_cpu}-linux-uclibc
%dir %{_prefix}/%{_target_cpu}-linux-uclibc/lib
%ifarch %{ix86} ppc # sparc? should be
%attr(755,root,root) %{_prefix}/%{_target_cpu}-linux-uclibc/lib/ld-*
%endif
%ifarch %{ix86} ppc sparc sparc64
%attr(755,root,root) %{_prefix}/%{_target_cpu}-linux-uclibc/lib/lib*%{version}.so
%attr(755,root,root) %{_prefix}/%{_target_cpu}-linux-uclibc/lib/lib*.so.0
%endif
%ifarch ppc
%{_prefix}/powerpc-linux-uclibc
%endif

%files devel
%defattr(644,root,root,755)
%doc README TODO docs/threads.txt docs/uclibc.org/*.html
%attr(755,root,root) %{_bindir}/*
#%dir %{_prefix}/%{_target_cpu}-linux-uclibc/bin
#%attr(755,root,root) %{_prefix}/%{_target_cpu}-linux-uclibc/bin/*
%{_prefix}/%{_target_cpu}-linux-uclibc/usr
%{_prefix}/%{_target_cpu}-linux-uclibc/lib/crt*.o
%ifarch %{ix86} ppc sparc sparc64
%attr(755,root,root) %{_prefix}/%{_target_cpu}-linux-uclibc/lib/libc.so
%attr(755,root,root) %{_prefix}/%{_target_cpu}-linux-uclibc/lib/libcrypt.so
%attr(755,root,root) %{_prefix}/%{_target_cpu}-linux-uclibc/lib/libm.so
%attr(755,root,root) %{_prefix}/%{_target_cpu}-linux-uclibc/lib/libresolv.so
%attr(755,root,root) %{_prefix}/%{_target_cpu}-linux-uclibc/lib/libutil.so
%endif
%ifarch %{ix86} ppc
%attr(755,root,root) %{_prefix}/%{_target_cpu}-linux-uclibc/lib/libdl.so
%endif
%{_prefix}/%{_target_cpu}-linux-uclibc/include

%files static
%defattr(644,root,root,755)
%{_prefix}/%{_target_cpu}-linux-uclibc/lib/lib*.a
