Summary:	C library optimized for size
Summary(pl):	Biblioteka C zoptymalizowana na rozmiar
Name:		uClibc
Version:	0.9.8
Release:	1
Epoch:		1
License:	LGPL
Group:		Libraries
Source0:	http://uclibc.org/downloads/%{name}-%{version}.tar.bz2
Patch0:		%{name}-setfsuid.patch
Patch1:		%{name}-Makefile.patch
URL:		http://uclibc.org/
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
Small libc for building embedded applications.

%description -l pl
MaЁa libc do budowania aplikacji wbudowanych.

%package devel
Summary:	Development files for uClibc
Summary(pl):	Pliki dla programistСw uClibc
Group:		Development/Libraries
Group(de):	Entwicklung/Libraries
Group(es):	Desarrollo/Bibliotecas
Group(fr):	Development/Librairies
Group(pl):	Programowanie/Biblioteki
Group(pt_BR):	Desenvolvimento/Bibliotecas
Group(ru):	Разработка/Библиотеки
Group(uk):	Розробка/Б╕бл╕отеки
Requires:	%{name} = %{version}
Requires:	binutils
Requires:	gcc

%description devel
Small libc for building embedded applications.

%description devel -l pl
MaЁa libc do budowania aplikacji wbudowanych.

%package static
Summary:	Static uClibc libratries
Summary(pl):	Biblioteki statyczne uClibc
Group:		Development/Libraries
Group(de):	Entwicklung/Libraries
Group(es):	Desarrollo/Bibliotecas
Group(fr):	Development/Librairies
Group(pl):	Programowanie/Biblioteki
Group(pt_BR):	Desenvolvimento/Bibliotecas
Group(ru):	Разработка/Библиотеки
Group(uk):	Розробка/Б╕бл╕отеки
Requires:	%{name}-devel = %{version}

%description static
Static uClibc libratries.

%description -l pl static
Biblioteki statyczne uClibc.

%prep
%setup -q -n %{name}
%patch0 -p1
%patch1 -p1

%ifarch %{ix86}
ln -sf extra/Configs/Config.i386 Config
%endif
%ifarch sparc sparc64
ln -sf extra/Configs/Config.sparc Config
%endif
%ifarch alpha
ln -sf extra/Configs/Config.alpha Config
%endif
%ifarch ppc ppc64
ln -sf extra/Configs/Config.powerpc Config
%endif

%build
cat Config > Config.tmp
sed -e 's/^INCLUDE_RPC *=.*$/INCLUDE_RPC = true/; s/^INCLUDE_IPV6 *=.*$/INCLUDE_IPV6 = true/' Config.tmp > Config
%{__make} \
	TARGET_ARCH="%{_arch}" \
	KERNEL_SOURCE=%{_kernelsrcdir} \
	CC=%{__cc} \
	OPTIMIZATION="%{rpmcflags}"

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT%{_bindir}

%{__make} install \
	PREFIX=$RPM_BUILD_ROOT

mv $RPM_BUILD_ROOT/usr/%{_arch}-linux-uclibc%{_bindir}/* \
	$RPM_BUILD_ROOT%{_bindir}
rm -rf $RPM_BUILD_ROOT/usr/%{_arch}-linux-uclibc/usr

find $RPM_BUILD_ROOT/usr/%{_arch}-linux-uclibc/include -name CVS | xargs rm -rf

gzip -9nf README TODO docs/threads.txt

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(644,root,root,755)
%dir %{_prefix}/%{_arch}-linux-uclibc
%dir %{_prefix}/%{_arch}-linux-uclibc/lib
%attr(755,root,root) %{_prefix}/%{_arch}-linux-uclibc/lib/ld-*
%attr(755,root,root) %{_prefix}/%{_arch}-linux-uclibc/lib/lib*%{version}.so
%attr(755,root,root) %{_prefix}/%{_arch}-linux-uclibc/lib/lib*.so.0

%files devel
%defattr(644,root,root,755)
%doc *.gz docs/*.gz docs/uclibc.org/*.html
%attr(755,root,root) %{_bindir}/*
%dir %{_prefix}/%{_arch}-linux-uclibc/bin
%attr(755,root,root) %{_prefix}/%{_arch}-linux-uclibc/bin/*
%{_prefix}/%{_arch}-linux-uclibc/lib/crt0.o
%attr(755,root,root) %{_prefix}/%{_arch}-linux-uclibc/lib/libc.so
%attr(755,root,root) %{_prefix}/%{_arch}-linux-uclibc/lib/libcrypt.so
%attr(755,root,root) %{_prefix}/%{_arch}-linux-uclibc/lib/libdl.so
%attr(755,root,root) %{_prefix}/%{_arch}-linux-uclibc/lib/libm.so
%attr(755,root,root) %{_prefix}/%{_arch}-linux-uclibc/lib/libresolv.so
%attr(755,root,root) %{_prefix}/%{_arch}-linux-uclibc/lib/libutil.so
%{_prefix}/%{_arch}-linux-uclibc/include

%files static
%{_prefix}/%{_arch}-linux-uclibc/lib/lib*.a
