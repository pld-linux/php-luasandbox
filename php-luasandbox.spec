#
# Conditional build:
%bcond_without	tests		# build without tests

%define		php_name	php%{?php_suffix}
%define		modname	luasandbox
Summary:	LUA sandbox
Summary(pl.UTF-8):	%{modname} -
Name:		%{php_name}-%{modname}
# luasandbox_version.h defines 2.0-4
Version:	2.0
Release:	1
# see debian/copyright
License:	expat
Group:		Development/Languages/PHP
Source0:	https://github.com/wikimedia/mediawiki-php-luasandbox/archive/master/%{modname}-%{version}.tar.gz
# Source0-md5:	c5745b1c93afc56a16e00c5bc09ad414
URL:		https://gerrit.wikimedia.org/r/#/admin/projects/mediawiki/php/luasandbox
%{?with_tests:BuildRequires:    %{php_name}-cli}
BuildRequires:	%{php_name}-devel
BuildRequires:	rpmbuild(macros) >= 1.666
BuildRequires:	pkgconfig
BuildRequires:	luajit-devel
%{?requires_php_extension}
Provides:	php(luasandbox) = %{version}
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
PHP extension that provides a sandboxed environment to run Lua scripts
in.

%prep
%setup -qc
mv mediawiki-php-luasandbox-*/* .

%build
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

%install
rm -rf $RPM_BUILD_ROOT
%{__make} install \
	EXTENSION_DIR=%{php_extensiondir} \
	INSTALL_ROOT=$RPM_BUILD_ROOT

install -d $RPM_BUILD_ROOT%{php_sysconfdir}/conf.d
cat <<'EOF' > $RPM_BUILD_ROOT%{php_sysconfdir}/conf.d/%{modname}.ini
; Enable %{modname} extension module
extension=%{modname}.so
EOF

%clean
rm -rf $RPM_BUILD_ROOT

%post
%php_webserver_restart

%postun
if [ "$1" = 0 ]; then
	%php_webserver_restart
fi

%files
%defattr(644,root,root,755)
%doc README CREDITS
%config(noreplace) %verify(not md5 mtime size) %{php_sysconfdir}/conf.d/%{modname}.ini
%attr(755,root,root) %{php_extensiondir}/%{modname}.so
