Summary:	C library optimized for size
Name:		uClibc
Version:	20010413
Release:	1
License:	LGPL
Group:		Development/Libraries
Group(de):	Entwicklung/Libraries
Group(fr):	Development/Librairies
Group(pl):	Programowanie/Biblioteki
Source0:	%{name}-%{version}.tar.gz
#Patch0:	%{name}-install.patch
URL:		http://cvs.uclinux.org/uClibc.html
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)
BuildRequires:	linux-devel-BOOT

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
#%patch -p1


%build
%{__make} KERNEL_SOURCE=%{_libdir}/bootdisk%{_prefix}

%install
rm -rf $RPM_BUILD_ROOT

# BOOT
install -d $RPM_BUILD_ROOT%{_libdir}/bootdisk%{_libdir}
install crt0.o libc.a $RPM_BUILD_ROOT%{_libdir}/bootdisk%{_libdir}
install libuClibc.so.1 $RPM_BUILD_ROOT%{_libdir}/bootdisk%{_libdir}

cp -a  include/ $RPM_BUILD_ROOT%{_libdir}/bootdisk%{_includedir}
rm $RPM_BUILD_ROOT%{_libdir}/bootdisk%{_includedir}/{asm,linux,bits}
cp -pr include/bits $RPM_BUILD_ROOT%{_libdir}/bootdisk%{_includedir}

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

%files BOOT
%defattr(644,root,root,755)
%attr(755,root,root) %{_libdir}/bootdisk/%{_libdir}/*.so*
%{_libdir}/bootdisk%{_libdir}/libc.a
%{_libdir}/bootdisk%{_libdir}/crt0.o
