Summary:	C library optimized for size
Name:		uClibc
Version:	20010521
Release:	5
License:	LGPL
Group:		Development/Libraries
Group(de):	Entwicklung/Libraries
Group(fr):	Development/Librairies
Group(pl):	Programowanie/Biblioteki
Source0:	%{name}-%{version}.tar.gz
#Patch0:	%{name}-install.patch
Patch0:		%{name}-setfsuid.patch
URL:		http://cvs.uclinux.org/uClibc.html
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
Small libc for building embedded applications.

%package devel-BOOT
Summary:	Development files for uClibc
Group:		Development/Libraries
Group(de):	Entwicklung/Libraries
Group(fr):	Development/Librairies
Group(pl):	Programowanie/Biblioteki
Requires:	%{name}-BOOT = %{version}

%description devel-BOOT
Small libc for building embedded applications.

%package BOOT
Summary:	uClibc for bootdisk
Group:		Development/Libraries
Group(de):	Entwicklung/Libraries
Group(fr):	Development/Librairies
Group(pl):	Programowanie/Biblioteki

%description BOOT
Small libc for building embedded applications.

%prep
%setup -q -n %{name}
%patch0 -p1


%build
perl -pi -e 's/^INCLUDE_RPC *=.*$/INCLUDE_RPC = true/g' Config
%{__make} KERNEL_SOURCE=/usr/src/linux CPUFLAGS="-m386"

%install
rm -rf $RPM_BUILD_ROOT

# BOOT
install -d $RPM_BUILD_ROOT%{_libdir}/bootdisk%{_libdir}
cp -a lib/* $RPM_BUILD_ROOT%{_libdir}/bootdisk%{_libdir}
# forgotten by maintainers
install ldso/libdl/libdl.a $RPM_BUILD_ROOT%{_libdir}/bootdisk%{_libdir}

find -name CVS | xargs rm -fr

cp -a include/ $RPM_BUILD_ROOT%{_libdir}/bootdisk%{_includedir}/
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
