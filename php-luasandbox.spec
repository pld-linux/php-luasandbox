#
# Conditional build:
%bcond_without	tests	# build without tests
%bcond_without	php		# build PHP extension
%bcond_without	hhvm	# build HHVM extension

%define		php_name	php%{?php_suffix}
%define		modname	luasandbox
Summary:	Lua extension for PHP
Name:		%{php_name}-%{modname}
# luasandbox_version.h defines 2.0-4
Version:	2.0
Release:	1
# see debian/copyright
License:	expat
Group:		Development/Languages/PHP
Source0:	https://github.com/wikimedia/mediawiki-php-luasandbox/archive/master/%{modname}-%{version}.tar.gz
# Source0-md5:	c5745b1c93afc56a16e00c5bc09ad414
URL:		https://www.mediawiki.org/wiki/Extension:Scribunto
%{?with_tests:BuildRequires:    %{php_name}-cli}
BuildRequires:	%{php_name}-devel
BuildRequires:	lua51-devel >= 5.1.5-1.2
BuildRequires:	luajit-devel
BuildRequires:	pcre-devel >= 8.10
BuildRequires:	pkgconfig
BuildRequires:	rpmbuild(macros) >= 1.666
%{?requires_php_extension}
Provides:	php(luasandbox) = %{version}
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define		hhvm_extensiondir	%{_libdir}/hhvm

%description
PHP extension that provides a sandboxed environment to run Lua scripts
in.

%package -n hhvm-%{modname}
Summary:	Lua extension for HHVM
License:	expat
Group:		Development/Languages/PHP
Provides:	hhvm(luasandbox) = %{version}

%description -n hhvm-%{modname}
HHVM extension that provides a sandboxed environment to run Lua
scripts in.

%prep
%setup -qc
mv mediawiki-php-luasandbox-* php-src
mv php-src/{README,CREDITS} .
cp -a php-src hhvm-src

%build
%if %{with php}
cd php-src
phpize
%configure
%{__make}

%if %{with tests}
# simple module load test
%{__php} -n -q \
	-d extension_dir=modules \
	-d extension=%{modname}.so \
	-m > modules.log
grep %{modname} modules.log

export NO_INTERACTION=1 REPORT_EXIT_STATUS=1 MALLOC_CHECK_=2
%{__make} test \
	PHP_EXECUTABLE=%{__php}
%endif
cd ..
%endif

%if %{with hhvm}
cd hhvm-src
hphpize
%cmake . \
	%{?cmake_ccache} \
	-DHHVM_EXTENSION_DIR=%{hhvm_extensiondir} \
	-DLUA_USE_CPP=1
%{__make}
%endif

%install
rm -rf $RPM_BUILD_ROOT
%if %{with php}
%{__make} install -C php-src \
	EXTENSION_DIR=%{php_extensiondir} \
	INSTALL_ROOT=$RPM_BUILD_ROOT

install -d $RPM_BUILD_ROOT%{php_sysconfdir}/conf.d
cat <<'EOF' > $RPM_BUILD_ROOT%{php_sysconfdir}/conf.d/%{modname}.ini
; Enable %{modname} extension module
extension=%{modname}.so
EOF
%endif

%if %{with hhvm}
%{__make} install -C hhvm-src \
	DESTDIR=$RPM_BUILD_ROOT
%endif

%clean
rm -rf $RPM_BUILD_ROOT

%post
%php_webserver_restart

%postun
if [ "$1" = 0 ]; then
	%php_webserver_restart
fi

%if %{with php}
%files
%defattr(644,root,root,755)
%doc README CREDITS
%config(noreplace) %verify(not md5 mtime size) %{php_sysconfdir}/conf.d/%{modname}.ini
%attr(755,root,root) %{php_extensiondir}/%{modname}.so
%endif

%if %{with hhvm}
%files -n hhvm-%{modname}
%defattr(644,root,root,755)
%doc README CREDITS
%attr(755,root,root) %{hhvm_extensiondir}/%{modname}.so
%endif
