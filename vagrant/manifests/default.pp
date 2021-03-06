# puppet manifest

# Make sure the correct directories are in the path:
Exec {
    path => [
    '/usr/local/sbin',
    '/usr/local/bin',
    '/usr/sbin',
    '/usr/bin',
    '/sbin',
    '/bin',
    ],
    logoutput => true,
}

# Refresh the catalog of repositories from which packages can be installed:
exec {'apt-get-update':
    command => 'apt-get update'
}

# make sure we have some basic tools and libraries available

package {'redis-server':
    ensure => latest,
    require => Exec['apt-get-update'],
}

package {'libxslt1-dev':
    ensure => latest,
    require => Exec['apt-get-update'],
}

package {'libxml2':
    ensure => latest,
    require => Exec['apt-get-update'],
}

package {'libxml2-dev':
    ensure => latest,
    require => Exec['apt-get-update'],
}

package {'build-essential':
    ensure => latest,
    require => Exec['apt-get-update'],
}

package {'python-dev':
    ensure => installed,
    require => Exec['apt-get-update']
}

package {'python-pip':
    ensure => installed,
    require => Package['python-dev']
}

package {'python-setuptools':
    ensure => installed,
    require => Package['python-dev']
}

package {'git':
    ensure => latest,
    require => Exec['apt-get-update'],
}

package {'unzip':
    ensure => latest,
    require => Exec['apt-get-update'],
}

package {'curl':
    ensure => latest,
    require => Exec['apt-get-update'],
}

package {'wget':
    ensure => latest,
    require => Exec['apt-get-update'],
}

package {'libcurl4-openssl-dev':
    ensure => latest,
    require => Exec['apt-get-update'],
}

package {'openssl':
    ensure => latest,
    require => Exec['apt-get-update'],
}

package {'zlib1g-dev':
    ensure => latest,
    require => Exec['apt-get-update'],
}

package {'libsqlite3-dev':
    ensure => latest,
    require => Exec['apt-get-update'],
}

package {'sqlite3':
    ensure => latest,
    require => Exec['apt-get-update'],
}

# Install Postgresql
package {'postgresql':
    ensure => latest,
    require => Exec['apt-get-update'],
}

package {'postgresql-contrib':
    ensure => latest,
    require => Exec['apt-get-update'],
}

package {'libpq-dev':
    ensure => latest,
    require => Exec['apt-get-update'],
}

# Set up Postgres DB/user for project

exec {'drop-existing-project-user':
    require => Package['postgresql'],
    command => 'psql -d postgres -c "DROP USER IF EXISTS quis"',
    user => 'postgres',
    group => 'postgres',
    logoutput => true,
}

exec {'create-project-user':
    require => Exec['drop-existing-project-user'],
    command => 'psql -d postgres -c "CREATE USER quis WITH PASSWORD \'quis\'"',
    user => 'postgres',
    group => 'postgres',
    logoutput => true,
}

exec {'drop-project-db':
    require => Exec['create-project-user'],
    command => 'psql -d postgres -c "DROP DATABASE IF EXISTS quis"',
    user => 'postgres',
    group => 'postgres',
    logoutput => true,
}

exec {'create-project-db':
    require => Exec['drop-project-db'],
    command => 'psql -d postgres -c "CREATE DATABASE quis WITH OWNER quis"',
    user => 'postgres',
    group => 'postgres',
    logoutput => true,
}

# Ensure github.com ssh public key is in the .ssh/known_hosts file so
# pip won't try to prompt on the terminal to accept it
file {'/home/vagrant/.ssh':
    ensure => directory,
    mode => 0700,
}

exec {'known_hosts':
    provider => 'shell',
    user => 'vagrant',
    group => 'vagrant',
    command => 'ssh-keyscan github.com >> /home/vagrant/.ssh/known_hosts',
    unless => 'grep -sq github.com /home/vagrant/.ssh/known_hosts',
    require => [ File['/home/vagrant/.ssh'], ],
}

file {'/home/vagrant/.ssh/known_hosts':
    ensure => file,
    mode => 0744,
    require => [ Exec['known_hosts'], ],
}

# install virtualenv and virtualenvwrapper - depends on pip

package {'virtualenv':
    ensure => latest,
    provider => 'pip',
    require => [ Package['python-pip'], ],
}

package {'virtualenvwrapper':
    ensure => latest,
    provider => 'pip',
    require => [ Package['python-pip'], ],
}

file {'/etc/profile.d/venvwrapper.sh':
    ensure => file,
    content => 'source `which virtualenvwrapper.sh`',
    mode => '755',
    require => Package['virtualenvwrapper'],
}

# Create a symlink from ~/quis to /vagrant as a convenience for the developer
file {'/home/vagrant/quis':
    ensure => link,
    target => '/vagrant',
}

# Create a virtualenv for quis
exec {'create-virtualenv':
    provider => 'shell',
    user => 'vagrant',
    group => 'vagrant',
    require => [ Package['virtualenvwrapper'], File['/home/vagrant/quis'], Exec['known_hosts'], Exec['drop-project-db']],
    environment => ["HOME=/home/vagrant","WORKON_HOME=/home/vagrant/.virtualenvs"],
    command => '/vagrant/vagrant/venv_bootstrap.sh',
    creates => '/home/vagrant/.virtualenvs/quis',
}

# set the DJANGO_SETTINGS_MODULE environment variable
file_line {'add DJANGO_SETTINGS_MODULE env to postactivate':
    ensure => present,
    line => 'export DJANGO_SETTINGS_MODULE=quis.settings.local',
    path => '/home/vagrant/.virtualenvs/quis/bin/postactivate',
    require => Exec['create-virtualenv'],
}

file_line {'add DJANGO_SETTINGS_MODULE env to postdeactivate':
    ensure => present,
    line => 'unset DJANGO_SETTINGS_MODULE',
    path => '/home/vagrant/.virtualenvs/quis/bin/postdeactivate',
    require => Exec['create-virtualenv'],
}

# Active this virtualenv upon login
file {'/home/vagrant/.bash_profile':
    owner => 'vagrant',
    content => '
echo "Activating python virtual environment \"{ project_name }\""
workon project_name
        
# Show git repo branch at bash prompt
parse_git_branch() {
    git branch 2> /dev/null | sed -e \'/^[^*]/d\' -e \'s/* \(.*\)/(\1)/\'
}
PS1="${debian_chroot:+($debian_chroot)}\u@\h:\w\$(parse_git_branch) $ "
    ',
    require => Exec['create-virtualenv'],
}

