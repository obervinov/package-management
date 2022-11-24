#!/bin/bash
set -e

# We allow python to connect to our database #
echo "host package-management python 0.0.0.0/0 $POSTGRES_HOST_AUTH_METHOD" >> ${PGDATA}/pg_hba.conf

# Creating a separate user and a database for our project #
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
	CREATE USER python;
	ALTER USER python WITH PASSWORD 'python';
	CREATE DATABASE "package-management";
	\c package-management;
	CREATE TABLE packages_prod (
		id serial PRIMARY KEY,
		package_name VARCHAR (50) UNIQUE NOT NULL,
		current_version VARCHAR (25) NOT NULL,
		repo_version VARCHAR (255) NOT NULL
	);
	CREATE TABLE packages_qa (
		id serial PRIMARY KEY,
		package_name VARCHAR (50) UNIQUE NOT NULL,
		current_version VARCHAR (25) NOT NULL,
		repo_version VARCHAR (255) NOT NULL
	);
	CREATE TABLE packages_dev (
		id serial PRIMARY KEY,
		package_name VARCHAR (50) UNIQUE NOT NULL,
		current_version VARCHAR (25) NOT NULL,
		repo_version VARCHAR (255) NOT NULL
	);
	CREATE TABLE yum_repos_d (
		id serial PRIMARY KEY,
		name VARCHAR (25) UNIQUE NOT NULL,
		content VARCHAR (2000) NOT NULL
	);
	CREATE TABLE rpm_list (
		id serial PRIMARY KEY,
		name VARCHAR (25) UNIQUE NOT NULL,
		url VARCHAR (250) NOT NULL
	);
	ALTER DATABASE "package-management" OWNER TO python;
	GRANT USAGE, SELECT ON SEQUENCE packages_dev_id_seq TO python;
	GRANT USAGE, SELECT ON SEQUENCE packages_qa_id_seq TO python;
	GRANT USAGE, SELECT ON SEQUENCE packages_prod_id_seq TO python;
	GRANT USAGE, SELECT ON SEQUENCE rpm_list_id_seq TO python;
	GRANT USAGE, SELECT ON SEQUENCE rpm_list_id_seq TO python;
	GRANT USAGE, SELECT ON SEQUENCE yum_repos_d_id_seq TO python;
	GRANT ALL PRIVILEGES ON DATABASE "package-management" TO python;
	GRANT ALL PRIVILEGES ON ALL TABLES in SCHEMA public TO python;
EOSQL

# Fill in the test data for an example #
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
	\c package-management;
	INSERT INTO packages_prod(package_name,current_version,repo_version)
	VALUES ('elasticsearch', '7.6.2', '7.6.2');
	INSERT INTO packages_prod(package_name,current_version,repo_version)
	VALUES ('logstash', '7.6.2', '7.6.2');
	INSERT INTO packages_prod(package_name,current_version,repo_version)
	VALUES ('kibana', '7.6.2', '7.6.2');
	INSERT INTO packages_prod(package_name,current_version,repo_version)
	VALUES ('nginx', '1.16', '1.16');
	INSERT INTO packages_prod(package_name,current_version,repo_version)
	VALUES ('python3', '3.6', '3.6');
	INSERT INTO packages_prod(package_name,current_version,repo_version)
	VALUES ('docker-ce', '19.0.0', 'not_found');
	INSERT INTO packages_prod(package_name,current_version,repo_version)
	VALUES ('bash', '4.4.19-1208', '4.4.19-1208');
	INSERT INTO packages_prod(package_name,current_version,repo_version)
	VALUES ('ca-certificates', '2021.2.50-80.0', '2021.2.50-80.0');
	INSERT INTO packages_prod(package_name,current_version,repo_version)
	VALUES ('chrony', '3.5-1', '3.5-1');
	INSERT INTO packages_qa(package_name,current_version,repo_version)
	VALUES ('elasticsearch', '7.6.2', '7.6.2');
	INSERT INTO packages_qa(package_name,current_version,repo_version)
	VALUES ('logstash', '7.6.2', '7.6.2');
	INSERT INTO packages_qa(package_name,current_version,repo_version)
	VALUES ('kibana', '7.6.2', '7.6.2');
	INSERT INTO packages_qa(package_name,current_version,repo_version)
	VALUES ('nginx', '1.16', '1.16');
	INSERT INTO packages_qa(package_name,current_version,repo_version)
	VALUES ('python3', '3.6', '3.6');
	INSERT INTO packages_qa(package_name,current_version,repo_version)
	VALUES ('docker-ce', '19.0.0', 'not_found');
	INSERT INTO packages_qa(package_name,current_version,repo_version)
	VALUES ('bash', '4.4.19-1208', '4.4.19-1208');
	INSERT INTO packages_dev(package_name,current_version,repo_version)
	VALUES ('elasticsearch', '7.6.2', '7.6.2');
	INSERT INTO packages_dev(package_name,current_version,repo_version)
	VALUES ('logstash', '7.6.2', '7.6.2');
	INSERT INTO packages_dev(package_name,current_version,repo_version)
	VALUES ('kibana', '7.6.2', '7.6.2');
	INSERT INTO packages_dev(package_name,current_version,repo_version)
	VALUES ('nginx', '1.16', '1.16');
	INSERT INTO packages_dev(package_name,current_version,repo_version)
	VALUES ('python3', '3.6', '3.6');
	INSERT INTO packages_dev(package_name,current_version,repo_version)
	VALUES ('docker-ce', '19.0.0', 'not_found');
EOSQL