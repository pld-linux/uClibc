Summary:	C library optimized for size
Summary(pl):	Biblioteka C zoptymalizowana na rozmiar
Name:		uClibc
Version:	20010826
Release:	8
License:	LGPL
Group:		Development/Libraries
Group(de):	Entwicklung/Libraries
Group(es):	Desarrollo/Bibliotecas
Group(fr):	Development/Librairies
Group(pl):	Programowanie/Biblioteki
Group(pt_BR):	Desenvolvimento/Bibliotecas
Group(ru):	Разработка/Библиотеки
Group(uk):	Розробка/Б╕бл╕отеки
Source0:	%{name}-%{version}.tar.gz
#Patch0:		%{name}-install.patch
Patch0:		%{name}-setfsuid.patch
URL:		http://cvs.uclinux.org/uClibc.html
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
Small libc for building embedded applications.

%description -l pl
MaЁa libc do budowania aplikacji wbudowanych.

%package devel-BOOT
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
Requires:	%{name}-BOOT = %{version}

%description devel-BOOT
Small libc for building embedded applications.

%description devel-BOOT -l pl
MaЁa libc do budowania aplikacji wbudowanych.

%package BOOT
Summary:	uClibc for bootdisk
Summary(pl):	uClibc dla bootkietki
Group:		Development/Libraries
Group(de):	Entwicklung/Libraries
Group(es):	Desarrollo/Bibliotecas
Group(fr):	Development/Librairies
Group(pl):	Programowanie/Biblioteki
Group(pt_BR):	Desenvolvimento/Bibliotecas
Group(ru):	Разработка/Библиотеки
Group(uk):	Розробка/Б╕бл╕отеки

%description BOOT
Small libc for building embedded applications.

%description BOOT -l pl
MaЁa libc do budowania aplikacji wbudowanych.

%prep
%setup -q -n %{name}
%patch0 -p1

cp -f extra/Configs/Config.i386 Config

%build
perl -pi -e 's/^INCLUDE_RPC *=.*$/INCLUDE_RPC = true/g' Config
%{__make} \
%ifarch %{ix86}
	TARGET_ARCH="i386" \
	CPUFLAGS="-m386" \
%else
	TARGET_ARCH="%{_target_cpu}" \
%endif
	KERNEL_SOURCE=%{_kernelsrcdir}

%install
rm -rf $RPM_BUILD_ROOT

# BOOT
install -d $RPM_BUILD_ROOT%{_libdir}/bootdisk%{_libdir}
cp -a lib/* $RPM_BUILD_ROOT%{_libdir}/bootdisk%{_libdir}
# forgotten by maintainers
install ldso/libdl/libdl.a $RPM_BUILD_ROOT%{_libdir}/bootdisk%{_libdir}

find -name CVS | xargs rm -fr

cp -a include $RPM_BUILD_ROOT%{_libdir}/bootdisk%{_includedir}
rm -f $RPM_BUILD_ROOT%{_libdir}/bootdisk%{_includedir}/{asm,linux,bits}
install -d $RPM_BUILD_ROOT%{_libdir}/bootdisk%{_includedir}/bits
install include/bits/* $RPM_BUILD_ROOT%{_libdir}/bootdisk%{_includedir}/bits

find $RPM_BUILD_ROOT%{_libdir}/bootdisk -name "CVS" |xargs rm -fr

# TODO normal package
#install -d $RPM_BUILD_ROOT%{_libdir}
#install crt0.o libc.a $RPM_BUILD_ROOT%{_libdir}

#rm include/asm include/linux

#gzip -9nf ./COPYING.LIB

%clean
rm -rf $RPM_BUILD_ROOT

# TODO
%files
%defattr(644,root,root,755)

%files devel-BOOT
%defattr(644,root,root,755)
%{_libdir}/bootdisk%{_includedir}/*
%{_libdir}/bootdisk%{_libdir}/*.a
%{_libdir}/bootdisk%{_libdir}/crt0.o

%files BOOT
%defattr(644,root,root,755)
%attr(755,root,root) %{_libdir}/bootdisk/%{_libdir}/*.so
