CREATE USER rrr;
CREATE SCHEMA administration AUTHORIZATION rrr;
GRANT USAGE ON SCHEMA administration TO PUBLIC;

SET search_path TO administration;

CREATE TABLE administration.users (
	id SERIAL PRIMARY KEY,
	user_name text UNIQUE,
	full_name text,
	password text,
	group_account boolean DEFAULT FALSE,
	db_quota bigint DEFAULT 53687091200,
	db_use bigint DEFAULT 0,
	db_quota_exceeded boolean DEFAULT FALSE
);

ALTER TABLE administration.users OWNER TO rrr;
GRANT SELECT ON TABLE administration.users TO PUBLIC;
INSERT INTO administration.users (user_name, full_name, password, group_account) VALUES ('PUBLIC', 'public user', '', TRUE);

CREATE TABLE administration.group_members (
	id SERIAL PRIMARY KEY,
	user_id integer,
	group_id integer,
	UNIQUE (user_id, group_id)
);

ALTER TABLE administration.group_members OWNER TO rrr;
REVOKE UPDATE ON TABLE administration.group_members FROM rrr;
GRANT SELECT ON TABLE administration.group_members TO PUBLIC;

CREATE OR REPLACE FUNCTION group_members() RETURNS trigger AS $group_members_trigger$
DECLARE
	group_name text;
	user_name text;
BEGIN
	IF (TG_OP = 'INSERT') THEN
		EXECUTE 'SELECT user_name FROM administration.users WHERE id = ' || NEW.group_id INTO group_name;
		EXECUTE 'SELECT user_name FROM administration.users WHERE id = ' || NEW.user_id INTO user_name;
		EXECUTE 'ALTER GROUP ' || quote_ident(group_name) || ' ADD USER ' || quote_ident(user_name);
		RETURN NEW;
	ELSIF (TG_OP = 'DELETE') THEN
		EXECUTE 'SELECT user_name FROM administration.users WHERE id = ' || OLD.group_id INTO group_name;
		EXECUTE 'SELECT user_name FROM administration.users WHERE id = ' || OLD.user_id INTO user_name;
		EXECUTE 'ALTER GROUP ' || quote_ident(group_name) || ' DROP USER ' || quote_ident(user_name);
		RETURN OLD;
	END IF;
END;
$group_members_trigger$ LANGUAGE plpgsql;

CREATE TRIGGER group_members_trigger
BEFORE INSERT OR DELETE ON administration.group_members
FOR EACH ROW EXECUTE PROCEDURE group_members();

CREATE TABLE administration.campaigns (
	id integer PRIMARY KEY,
	user_id integer REFERENCES administration.users (id),

	title text,
	description text,
	db_size bigint DEFAULT 0
);

ALTER TABLE administration.campaigns OWNER TO rrr;
GRANT SELECT ON TABLE administration.campaigns TO PUBLIC;

CREATE SEQUENCE administration.campaigns_id_seq;
ALTER TABLE administration.campaigns_id_seq OWNER TO rrr;
GRANT SELECT ON TABLE administration.campaigns_id_seq TO PUBLIC;

CREATE TABLE administration.authorizations (
	id integer PRIMARY KEY,
	user_id integer REFERENCES administration.users,
	campaign_id integer,
	authorized_id integer
);

ALTER TABLE administration.authorizations OWNER TO rrr;
GRANT SELECT ON TABLE administration.authorizations TO PUBLIC;

CREATE SEQUENCE administration.authorizations_id_seq;
ALTER TABLE administration.authorizations_id_seq OWNER TO rrr;

CREATE OR REPLACE FUNCTION public.set_user_schema() RETURNS VOID AS $set_user_schema_function$
BEGIN
	SET constraint_exclusion = on;
	EXECUTE 'SET search_path TO ' || quote_ident(user);
END;
$set_user_schema_function$ LANGUAGE plpgsql;

ALTER FUNCTION public.set_user_schema() OWNER TO rrr;
GRANT EXECUTE ON FUNCTION public.set_user_schema() TO PUBLIC;

CREATE FUNCTION public.administrate_db() RETURNS VOID AS $administrate_db_function$
BEGIN
	SET constraint_exclusion = on;
	SET search_path TO administration;
END;
$administrate_db_function$ LANGUAGE plpgsql;

ALTER FUNCTION public.administrate_db() OWNER TO rrr;
GRANT EXECUTE ON FUNCTION public.administrate_db() TO PUBLIC;

CREATE FUNCTION administration.change_password(password text) RETURNS VOID AS $change_password_function$
BEGIN
	EXECUTE 'ALTER ROLE ' || user || ' PASSWORD ' || quote_literal(password);
END;
$change_password_function$ LANGUAGE plpgsql;

ALTER FUNCTION administration.change_password(password text) OWNER TO rrr;

CREATE OR REPLACE FUNCTION administration.calculate_campaign_size(campaign_id integer) RETURNS bigint AS $$
DECLARE
	campaign_size bigint;
	campaign_size_help bigint;
	user_name text;
BEGIN
	campaign_size := 0;

	EXECUTE 'SELECT user_name FROM administration.users JOIN administration.campaigns ON users.id = campaigns.user_id WHERE campaigns.id = ' || campaign_id INTO user_name;

	EXECUTE 'SELECT pg_total_relation_size(''' || user_name || '.scenarios_' || campaign_id || ''')' INTO campaign_size_help;
	campaign_size := campaign_size_help;

	EXECUTE 'SELECT pg_total_relation_size(''' || user_name || '.files_' || campaign_id || ''')' INTO campaign_size_help;
	campaign_size := campaign_size + campaign_size_help;

	EXECUTE 'SELECT pg_total_relation_size(''' || user_name || '.parameters_' || campaign_id || ''')' INTO campaign_size_help;
	campaign_size := campaign_size + campaign_size_help;

	EXECUTE 'SELECT pg_total_relation_size(''' || user_name || '.jobs_' || campaign_id || ''')' INTO campaign_size_help;
	campaign_size := campaign_size + campaign_size_help;

	EXECUTE 'SELECT pg_total_relation_size(''' || user_name || '.pd_fs_' || campaign_id || ''')' INTO campaign_size_help;
	campaign_size := campaign_size + campaign_size_help;

	EXECUTE 'SELECT pg_total_relation_size(''' || user_name || '.pdf_histograms_' || campaign_id || ''')' INTO campaign_size_help;
	campaign_size := campaign_size + campaign_size_help;

	EXECUTE 'SELECT pg_total_relation_size(''' || user_name || '.log_evals_' || campaign_id || ''')' INTO campaign_size_help;
	campaign_size := campaign_size + campaign_size_help;

	EXECUTE 'SELECT pg_total_relation_size(''' || user_name || '.log_eval_entries_' || campaign_id || ''')' INTO campaign_size_help;
	campaign_size := campaign_size + campaign_size_help;

	EXECUTE 'SELECT pg_total_relation_size(''' || user_name || '.moments_' || campaign_id || ''')' INTO campaign_size_help;
	campaign_size := campaign_size + campaign_size_help;

	EXECUTE 'SELECT pg_total_relation_size(''' || user_name || '.batch_means_' || campaign_id || ''')' INTO campaign_size_help;
	campaign_size := campaign_size + campaign_size_help;

	EXECUTE 'SELECT pg_total_relation_size(''' || user_name || '.batch_means_histograms_' || campaign_id || ''')' INTO campaign_size_help;
	campaign_size := campaign_size + campaign_size_help;

	EXECUTE 'SELECT pg_total_relation_size(''' || user_name || '.lres_' || campaign_id || ''')' INTO campaign_size_help;
	campaign_size := campaign_size + campaign_size_help;

	EXECUTE 'SELECT pg_total_relation_size(''' || user_name || '.lre_histograms_' || campaign_id || ''')' INTO campaign_size_help;
	campaign_size := campaign_size + campaign_size_help;

	EXECUTE 'SELECT pg_total_relation_size(''' || user_name || '.dlres_' || campaign_id || ''')' INTO campaign_size_help;
	campaign_size := campaign_size + campaign_size_help;

	EXECUTE 'SELECT pg_total_relation_size(''' || user_name || '.dlre_histograms_' || campaign_id || ''')' INTO campaign_size_help;
	campaign_size := campaign_size + campaign_size_help;

	EXECUTE 'SELECT pg_total_relation_size(''' || user_name || '.tables_' || campaign_id || ''')' INTO campaign_size_help;
	campaign_size := campaign_size + campaign_size_help;

	EXECUTE 'SELECT pg_total_relation_size(''' || user_name || '.table_rows_' || campaign_id || ''')' INTO campaign_size_help;
	campaign_size := campaign_size + campaign_size_help;

	RETURN campaign_size;
END
$$ LANGUAGE plpgsql;

ALTER FUNCTION administration.calculate_campaign_size(campaign_id integer) OWNER TO rrr;


CREATE OR REPLACE FUNCTION administration.revoke_campaign_access(user_id integer) RETURNS void AS $$
DECLARE
	user_name text;
BEGIN
	EXECUTE 'SELECT user_name FROM administration.users WHERE id = ' || user_id INTO user_name;

	EXECUTE 'REVOKE INSERT ON TABLE ' || quote_ident(user_name) || '.campaigns FROM ' || quote_ident(user_name);
	EXECUTE 'REVOKE INSERT ON TABLE ' || quote_ident(user_name) || '.scenarios FROM ' || quote_ident(user_name);
	EXECUTE 'REVOKE INSERT ON TABLE ' || quote_ident(user_name) || '.files FROM ' || quote_ident(user_name);
	EXECUTE 'REVOKE INSERT ON TABLE ' || quote_ident(user_name) || '.parameters FROM ' || quote_ident(user_name);
	EXECUTE 'REVOKE INSERT ON TABLE ' || quote_ident(user_name) || '.jobs FROM ' || quote_ident(user_name);
	EXECUTE 'REVOKE INSERT ON TABLE ' || quote_ident(user_name) || '.pd_fs FROM ' || quote_ident(user_name);
	EXECUTE 'REVOKE INSERT ON TABLE ' || quote_ident(user_name) || '.pdf_histograms FROM ' || quote_ident(user_name);
	EXECUTE 'REVOKE INSERT ON TABLE ' || quote_ident(user_name) || '.log_evals FROM ' || quote_ident(user_name);
	EXECUTE 'REVOKE INSERT ON TABLE ' || quote_ident(user_name) || '.log_eval_entries FROM ' || quote_ident(user_name);
	EXECUTE 'REVOKE INSERT ON TABLE ' || quote_ident(user_name) || '.moments FROM ' || quote_ident(user_name);
	EXECUTE 'REVOKE INSERT ON TABLE ' || quote_ident(user_name) || '.batch_means FROM ' || quote_ident(user_name);
	EXECUTE 'REVOKE INSERT ON TABLE ' || quote_ident(user_name) || '.batch_means_histograms FROM ' || quote_ident(user_name);
	EXECUTE 'REVOKE INSERT ON TABLE ' || quote_ident(user_name) || '.lres FROM ' || quote_ident(user_name);
	EXECUTE 'REVOKE INSERT ON TABLE ' || quote_ident(user_name) || '.lre_histograms FROM ' || quote_ident(user_name);
	EXECUTE 'REVOKE INSERT ON TABLE ' || quote_ident(user_name) || '.dlres FROM ' || quote_ident(user_name);
	EXECUTE 'REVOKE INSERT ON TABLE ' || quote_ident(user_name) || '.dlre_histograms FROM ' || quote_ident(user_name);
	EXECUTE 'REVOKE INSERT ON TABLE ' || quote_ident(user_name) || '.tables FROM ' || quote_ident(user_name);
	EXECUTE 'REVOKE INSERT ON TABLE ' || quote_ident(user_name) || '.table_rows FROM ' || quote_ident(user_name);
END
$$ LANGUAGE plpgsql;

ALTER FUNCTION administration.revoke_campaign_access(user_id integer) OWNER TO rrr;


CREATE OR REPLACE FUNCTION administration.grant_campaign_access(user_id integer) RETURNS void AS $$
DECLARE
	user_name text;
BEGIN
	EXECUTE 'SELECT user_name FROM administration.users WHERE id = ' || user_id INTO user_name;

	EXECUTE 'GRANT INSERT ON TABLE ' || quote_ident(user_name) || '.campaigns TO ' || quote_ident(user_name);
	EXECUTE 'GRANT INSERT ON TABLE ' || quote_ident(user_name) || '.scenarios TO ' || quote_ident(user_name);
	EXECUTE 'GRANT INSERT ON TABLE ' || quote_ident(user_name) || '.files TO ' || quote_ident(user_name);
	EXECUTE 'GRANT INSERT ON TABLE ' || quote_ident(user_name) || '.parameters TO ' || quote_ident(user_name);
	EXECUTE 'GRANT INSERT ON TABLE ' || quote_ident(user_name) || '.jobs TO ' || quote_ident(user_name);
	EXECUTE 'GRANT INSERT ON TABLE ' || quote_ident(user_name) || '.pd_fs TO ' || quote_ident(user_name);
	EXECUTE 'GRANT INSERT ON TABLE ' || quote_ident(user_name) || '.pdf_histograms TO ' || quote_ident(user_name);
	EXECUTE 'GRANT INSERT ON TABLE ' || quote_ident(user_name) || '.log_evals TO ' || quote_ident(user_name);
	EXECUTE 'GRANT INSERT ON TABLE ' || quote_ident(user_name) || '.log_eval_entries TO ' || quote_ident(user_name);
	EXECUTE 'GRANT INSERT ON TABLE ' || quote_ident(user_name) || '.moments TO ' || quote_ident(user_name);
	EXECUTE 'GRANT INSERT ON TABLE ' || quote_ident(user_name) || '.batch_means TO ' || quote_ident(user_name);
	EXECUTE 'GRANT INSERT ON TABLE ' || quote_ident(user_name) || '.batch_means_histograms TO ' || quote_ident(user_name);
	EXECUTE 'GRANT INSERT ON TABLE ' || quote_ident(user_name) || '.lres TO ' || quote_ident(user_name);
	EXECUTE 'GRANT INSERT ON TABLE ' || quote_ident(user_name) || '.lre_histograms TO ' || quote_ident(user_name);
	EXECUTE 'GRANT INSERT ON TABLE ' || quote_ident(user_name) || '.dlres TO ' || quote_ident(user_name);
	EXECUTE 'GRANT INSERT ON TABLE ' || quote_ident(user_name) || '.dlre_histograms TO ' || quote_ident(user_name);
	EXECUTE 'GRANT INSERT ON TABLE ' || quote_ident(user_name) || '.tables TO ' || quote_ident(user_name);
	EXECUTE 'GRANT INSERT ON TABLE ' || quote_ident(user_name) || '.table_rows TO ' || quote_ident(user_name);
END
$$ LANGUAGE plpgsql;

ALTER FUNCTION administration.grant_campaign_access(user_id integer) OWNER TO rrr;


CREATE OR REPLACE FUNCTION administration.calculate_db_use() RETURNS void AS $$
BEGIN
	UPDATE administration.campaigns SET db_size = 0;
END
$$ LANGUAGE plpgsql SECURITY DEFINER;

ALTER FUNCTION administration.calculate_db_use() OWNER TO rrr;
GRANT EXECUTE ON FUNCTION administration.calculate_db_use() TO PUBLIC;

CREATE OR REPLACE FUNCTION administration.create_parameter_sets_view(campaign_id int) RETURNS void AS $$
DECLARE
	parameter_name text;
	statement_select text;
	statement_from text;
	statement_where1 text;
	statement_where2 text;
	parameters_record RECORD;
BEGIN
	EXECUTE 'SELECT parameter_name FROM parameters_' || campaign_id || ' LIMIT 1' INTO parameter_name;

	statement_select := 'SELECT ' || quote_ident(parameter_name) || '.campaign_id AS campaign_id, ' || quote_ident(parameter_name) || '.scenario_id AS scenario_id, ';
	statement_from := ' FROM';
	statement_where1 := ' WHERE';
	statement_where2 := '';

	FOR parameters_record IN EXECUTE 'SELECT DISTINCT parameter_name, parameter_type FROM parameters_' || campaign_id LOOP
		statement_select := statement_select || ' ' || quote_ident(parameters_record.parameter_name) || '.' || quote_ident(parameters_record.parameter_type) || ' AS ' || quote_ident(lower(parameters_record.parameter_name)) || ',';
		statement_from := statement_from || ' parameters_' || campaign_id || ' ' || quote_ident(parameters_record.parameter_name) || ',';
		statement_where2 := statement_where2 || ' ' || quote_ident(parameters_record.parameter_name) || '.parameter_name = ' || quote_literal(parameters_record.parameter_name) || ' AND';
		CONTINUE WHEN parameters_record.parameter_name = parameter_name;
		statement_where1 := statement_where1 || ' ' || quote_ident(parameter_name) || '.scenario_id = ' || quote_ident(parameters_record.parameter_name) || '.scenario_id AND';
	END LOOP;

	EXECUTE 'CREATE TEMPORARY VIEW parameter_sets AS ' || rtrim(statement_select, ',') || rtrim(statement_from, ',') || statement_where1 || rtrim(statement_where2, 'AND');

END;
$$ LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION administration.drop_parameter_sets_view() RETURNS void AS $$
BEGIN
	DROP VIEW parameter_sets;
END;
$$ LANGUAGE plpgsql;

SET SESSION ROLE rrr;

CREATE OR REPLACE FUNCTION administration.create_user(user_id integer, user_name text, full_name text, password text) RETURNS void AS $$
DECLARE
	user_db text;
BEGIN
	-- create user and schema
	EXECUTE 'SELECT * FROM pg_user WHERE usename = ' || quote_literal(user_name) INTO user_db;
	IF user_db IS NULL THEN
		EXECUTE 'CREATE USER ' || quote_ident(user_name) || ' PASSWORD ' || quote_literal(password);
	ELSE
		EXECUTE 'ALTER USER ' || quote_ident(user_name) || ' PASSWORD ' || quote_literal(password);
	END IF;

	EXECUTE 'CREATE SCHEMA ' || quote_ident(user_name) || ' AUTHORIZATION rrr';
	EXECUTE 'GRANT USAGE ON SCHEMA ' || quote_ident(user_name) || ' TO ' || quote_ident(user_name);


	-- create private users view
	EXECUTE 'CREATE OR REPLACE VIEW ' || quote_ident(user_name) || '.users AS
			SELECT * FROM administration.users';

	EXECUTE 'ALTER TABLE ' || quote_ident(user_name) || '.users OWNER TO rrr';
	EXECUTE 'GRANT SELECT ON TABLE ' || quote_ident(user_name) || '.users TO ' || quote_ident(user_name);


	-- create private campaigns table
	EXECUTE 'CREATE TABLE ' || quote_ident(user_name) || '.campaigns (
		) INHERITS(administration.campaigns)';

	EXECUTE	'ALTER TABLE ' || quote_ident(user_name) || '.campaigns ALTER COLUMN user_id SET DEFAULT ' || quote_literal(user_id);
	EXECUTE	'ALTER TABLE ' || quote_ident(user_name) || '.campaigns ADD PRIMARY KEY (id)';
	--EXECUTE 'ALTER TABLE ' || quote_ident(user_name) || '.campaigns ADD CONSTRAINT usersfk FOREIGN KEY (user_id) REFERENCES administration.users (id) ON DELETE CASCADE';
	EXECUTE 'ALTER TABLE ' || quote_ident(user_name) || '.campaigns OWNER TO rrr';
	EXECUTE 'GRANT SELECT ON TABLE ' || quote_ident(user_name) || '.campaigns TO PUBLIC';
	EXECUTE 'GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE ' || quote_ident(user_name) || '.campaigns TO ' || quote_ident(user_name);


	-- create private authorizations table
	EXECUTE 'CREATE TABLE ' || quote_ident(user_name) || '.authorizations (
		) INHERITS(administration.authorizations)';

	EXECUTE	'ALTER TABLE ' || quote_ident(user_name) || '.authorizations ALTER COLUMN user_id SET DEFAULT ' || quote_literal(user_id);
	EXECUTE	'ALTER TABLE ' || quote_ident(user_name) || '.authorizations ADD PRIMARY KEY (id)';
	--EXECUTE 'ALTER TABLE ' || quote_ident(user_name) || '.authorizations ADD CONSTRAINT usersfk FOREIGN KEY (user_id) REFERENCES administration.users (id) ON DELETE CASCADE';
	EXECUTE 'ALTER TABLE ' || quote_ident(user_name) || '.authorizations OWNER TO rrr';
	EXECUTE 'GRANT SELECT ON TABLE ' || quote_ident(user_name) || '.authorizations TO PUBLIC';
	EXECUTE 'GRANT SELECT, INSERT, DELETE ON TABLE ' || quote_ident(user_name) || '.authorizations TO ' || quote_ident(user_name);


	-- create private "root" tables
	EXECUTE 'CREATE SEQUENCE ' || quote_ident(user_name) || '.scenarios_id_seq';
	EXECUTE 'ALTER TABLE ' || quote_ident(user_name) || '.scenarios_id_seq OWNER TO rrr';
	EXECUTE 'GRANT UPDATE, SELECT ON TABLE ' || quote_ident(user_name) || '.scenarios_id_seq TO ' || quote_ident(user_name);
	EXECUTE 'CREATE TABLE ' || quote_ident(user_name) || '.scenarios (
			id bigint PRIMARY KEY DEFAULT 0,
			campaign_id bigint,
			current_job_id integer,

			state character varying(9),
			max_sim_time double precision,
			current_sim_time double precision,
			sim_time_last_write double precision
		)';

	EXECUTE 'ALTER TABLE ' || quote_ident(user_name) || '.scenarios OWNER TO rrr';
	EXECUTE 'GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE ' || quote_ident(user_name) || '.scenarios TO ' || quote_ident(user_name);

	EXECUTE 'CREATE SEQUENCE ' || quote_ident(user_name) || '.files_id_seq';
	EXECUTE 'ALTER TABLE ' || quote_ident(user_name) || '.files_id_seq OWNER TO rrr';
	EXECUTE 'GRANT UPDATE, SELECT ON TABLE ' || quote_ident(user_name) || '.files_id_seq TO ' || quote_ident(user_name);
	EXECUTE 'CREATE TABLE ' || quote_ident(user_name) || '.files (
			id bigint PRIMARY KEY DEFAULT 0,
			campaign_id bigint,

			name text,
			date timestamp without time zone,
			file text
		)';

	EXECUTE 'ALTER TABLE ' || quote_ident(user_name) || '.files OWNER TO rrr';
	EXECUTE 'GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE ' || quote_ident(user_name) || '.files TO ' || quote_ident(user_name);

	EXECUTE 'CREATE SEQUENCE ' || quote_ident(user_name) || '.parameters_id_seq';
	EXECUTE 'ALTER TABLE ' || quote_ident(user_name) || '.parameters_id_seq OWNER TO rrr';
	EXECUTE 'GRANT UPDATE, SELECT ON TABLE ' || quote_ident(user_name) || '.parameters_id_seq TO ' || quote_ident(user_name);
	EXECUTE 'CREATE TABLE ' || quote_ident(user_name) || '.parameters (
			id bigint PRIMARY KEY DEFAULT 0,
			campaign_id bigint,
			scenario_id bigint,

			parameter_type character(12),
			parameter_name text,
			type_bool bool DEFAULT FALSE,
			type_integer integer DEFAULT 0,
			type_float double precision DEFAULT 0.0,
			type_string text DEFAULT ''''
		)';

	EXECUTE 'ALTER TABLE ' || quote_ident(user_name) || '.parameters OWNER TO rrr';
	EXECUTE 'GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE ' || quote_ident(user_name) || '.parameters TO ' || quote_ident(user_name);

	EXECUTE 'CREATE SEQUENCE ' || quote_ident(user_name) || '.jobs_id_seq';
	EXECUTE 'ALTER TABLE ' || quote_ident(user_name) || '.jobs_id_seq OWNER TO rrr';
	EXECUTE 'GRANT UPDATE, SELECT ON TABLE ' || quote_ident(user_name) || '.jobs_id_seq TO ' || quote_ident(user_name);
	EXECUTE 'CREATE TABLE ' || quote_ident(user_name) || '.jobs (
			id bigint PRIMARY KEY DEFAULT 0,
			campaign_id bigint,
			scenario_id bigint,

			sge_job_id integer,
			queue_date timestamp without time zone,
			start_date timestamp without time zone,
			stop_date timestamp without time zone,
			hostname text,
			stdout text,
			stderr text
		)';

	EXECUTE 'ALTER TABLE ' || quote_ident(user_name) || '.jobs OWNER TO rrr';
	EXECUTE 'GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE ' || quote_ident(user_name) || '.jobs TO ' || quote_ident(user_name);

	EXECUTE 'CREATE SEQUENCE ' || quote_ident(user_name) || '.probes_id_seq';
	EXECUTE 'ALTER TABLE ' || quote_ident(user_name) || '.probes_id_seq OWNER TO rrr';
	EXECUTE 'GRANT UPDATE, SELECT ON TABLE ' || quote_ident(user_name) || '.probes_id_seq TO ' || quote_ident(user_name);
	EXECUTE 'CREATE TABLE ' || quote_ident(user_name) || '.probes (
			id bigint PRIMARY KEY DEFAULT 0,
			campaign_id bigint,
			scenario_id bigint,

			filename text,
			name text,
			alt_name text,
			description text,
			minimum double precision,
			maximum double precision,
			trials bigint,
			mean double precision,
			variance double precision,
			relative_variance double precision,
			standard_deviation double precision,
			relative_standard_deviation double precision,
			skewness double precision,
			moment2 double precision,
			moment3 double precision,
			sum_of_all_values double precision,
			sum_of_all_values_square double precision,
			sum_of_all_values_cubic double precision
		)';

	EXECUTE 'ALTER TABLE ' || quote_ident(user_name) || '.probes OWNER TO rrr';
	EXECUTE 'GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE ' || quote_ident(user_name) || '.probes TO ' || quote_ident(user_name);

	EXECUTE 'CREATE SEQUENCE ' || quote_ident(user_name) || '.pd_fs_id_seq';
	EXECUTE 'ALTER TABLE ' || quote_ident(user_name) || '.pd_fs_id_seq OWNER TO rrr';
	EXECUTE 'GRANT UPDATE, SELECT ON TABLE ' || quote_ident(user_name) || '.pd_fs_id_seq TO ' || quote_ident(user_name);
	EXECUTE 'CREATE TABLE ' || quote_ident(user_name) || '.pd_fs (
			id bigint PRIMARY KEY DEFAULT 0,

			p01 double precision,
			p05 double precision,
			p50 double precision,
			p95 double precision,
			p99 double precision,
			min_x double precision,
			max_x double precision,
			number_of_bins integer,
			underflows bigint,
			overflows bigint
		) INHERITS (' || quote_ident(user_name) || '.probes)';

	EXECUTE 'ALTER TABLE ' || quote_ident(user_name) || '.pd_fs OWNER TO rrr';
	EXECUTE 'GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE ' || quote_ident(user_name) || '.pd_fs TO ' || quote_ident(user_name);

	EXECUTE 'CREATE SEQUENCE ' || quote_ident(user_name) || '.pdf_histograms_id_seq';
	EXECUTE 'ALTER TABLE ' || quote_ident(user_name) || '.pdf_histograms_id_seq OWNER TO rrr';
	EXECUTE 'GRANT UPDATE, SELECT ON TABLE ' || quote_ident(user_name) || '.pdf_histograms_id_seq TO ' || quote_ident(user_name);
	EXECUTE 'CREATE TABLE ' || quote_ident(user_name) || '.pdf_histograms (
			id bigint PRIMARY KEY DEFAULT 0,
			campaign_id bigint,
			probe_id bigint,

			x double precision,
			cdf double precision,
			ccdf double precision,
			pdf double precision
		)';

	EXECUTE 'ALTER TABLE ' || quote_ident(user_name) || '.pdf_histograms OWNER TO rrr';
	EXECUTE 'GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE ' || quote_ident(user_name) || '.pdf_histograms TO ' || quote_ident(user_name);

	EXECUTE 'CREATE SEQUENCE ' || quote_ident(user_name) || '.log_evals_id_seq';
	EXECUTE 'ALTER TABLE ' || quote_ident(user_name) || '.log_evals_id_seq OWNER TO rrr';
	EXECUTE 'GRANT UPDATE, SELECT ON TABLE ' || quote_ident(user_name) || '.log_evals_id_seq TO ' || quote_ident(user_name);
	EXECUTE 'CREATE TABLE ' || quote_ident(user_name) || '.log_evals (
			id bigint PRIMARY KEY DEFAULT 0
		) INHERITS (' || quote_ident(user_name) || '.probes)';

	EXECUTE 'ALTER TABLE ' || quote_ident(user_name) || '.log_evals OWNER TO rrr';
	EXECUTE 'GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE ' || quote_ident(user_name) || '.log_evals TO ' || quote_ident(user_name);

	EXECUTE 'CREATE SEQUENCE ' || quote_ident(user_name) || '.log_eval_entries_id_seq';
	EXECUTE 'ALTER TABLE ' || quote_ident(user_name) || '.log_eval_entries_id_seq OWNER TO rrr';
	EXECUTE 'GRANT UPDATE, SELECT ON TABLE ' || quote_ident(user_name) || '.log_eval_entries_id_seq TO ' || quote_ident(user_name);
	EXECUTE 'CREATE TABLE ' || quote_ident(user_name) || '.log_eval_entries (
			id bigint PRIMARY KEY DEFAULT 0,
			campaign_id bigint,
			probe_id bigint,

			x double precision,
			y double precision
		)';

	EXECUTE 'ALTER TABLE ' || quote_ident(user_name) || '.log_eval_entries OWNER TO rrr';
	EXECUTE 'GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE ' || quote_ident(user_name) || '.log_eval_entries TO ' || quote_ident(user_name);

	EXECUTE 'CREATE SEQUENCE ' || quote_ident(user_name) || '.moments_id_seq';
	EXECUTE 'ALTER TABLE ' || quote_ident(user_name) || '.moments_id_seq OWNER TO rrr';
	EXECUTE 'GRANT UPDATE, SELECT ON TABLE ' || quote_ident(user_name) || '.moments_id_seq TO ' || quote_ident(user_name);
	EXECUTE 'CREATE TABLE ' || quote_ident(user_name) || '.moments (
			id bigint PRIMARY KEY DEFAULT 0
		) INHERITS (' || quote_ident(user_name) || '.probes)';

	EXECUTE 'ALTER TABLE ' || quote_ident(user_name) || '.moments OWNER TO rrr';
	EXECUTE 'GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE ' || quote_ident(user_name) || '.moments TO ' || quote_ident(user_name);

	EXECUTE 'CREATE SEQUENCE ' || quote_ident(user_name) || '.batch_means_id_seq';
	EXECUTE 'ALTER TABLE ' || quote_ident(user_name) || '.batch_means_id_seq OWNER TO rrr';
	EXECUTE 'GRANT UPDATE, SELECT ON TABLE ' || quote_ident(user_name) || '.batch_means_id_seq TO ' || quote_ident(user_name);
	EXECUTE 'CREATE TABLE ' || quote_ident(user_name) || '.batch_means (
			id bigint PRIMARY KEY DEFAULT 0,

			lower_border double precision,
			upper_border double precision,
			number_of_intervals integer,
			interval_size double precision,
			size_of_groups integer,
			maximum_relative_error double precision,
			evaluated_groups integer,
			underflows bigint,
			overflows bigint,
			mean_bm double precision,
			confidence_of_mean_absolute double precision,
			confidence_of_mean_percent double precision,
			relative_error_mean double precision,
			variance_bm double precision,
			confidence_of_variance_absolute double precision,
			confidence_of_variance_percent double precision,
			relative_error_variance double precision,
			sigma double precision,
			first_order_correlation_coefficient double precision
		) INHERITS (' || quote_ident(user_name) || '.probes)';

	EXECUTE 'ALTER TABLE ' || quote_ident(user_name) || '.batch_means OWNER TO rrr';
	EXECUTE 'GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE ' || quote_ident(user_name) || '.batch_means TO ' || quote_ident(user_name);

	EXECUTE 'CREATE SEQUENCE ' || quote_ident(user_name) || '.batch_means_histograms_id_seq';
	EXECUTE 'ALTER TABLE ' || quote_ident(user_name) || '.batch_means_histograms_id_seq OWNER TO rrr';
	EXECUTE 'GRANT UPDATE, SELECT ON TABLE ' || quote_ident(user_name) || '.batch_means_histograms_id_seq TO ' || quote_ident(user_name);
	EXECUTE 'CREATE TABLE ' || quote_ident(user_name) || '.batch_means_histograms (
			id bigint PRIMARY KEY DEFAULT 0,
			campaign_id bigint,
			probe_id bigint,

			x double precision,
			cdf double precision,
			pdf double precision,
			relative_error double precision,
			confidence double precision,
			number_of_trials_per_interval integer
		)';

	EXECUTE 'ALTER TABLE ' || quote_ident(user_name) || '.batch_means_histograms OWNER TO rrr';
	EXECUTE 'GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE ' || quote_ident(user_name) || '.batch_means_histograms TO ' || quote_ident(user_name);

	EXECUTE 'CREATE SEQUENCE ' || quote_ident(user_name) || '.lres_id_seq';
	EXECUTE 'ALTER TABLE ' || quote_ident(user_name) || '.lres_id_seq OWNER TO rrr';
	EXECUTE 'GRANT UPDATE, SELECT ON TABLE ' || quote_ident(user_name) || '.lres_id_seq TO ' || quote_ident(user_name);
	EXECUTE 'CREATE TABLE ' || quote_ident(user_name) || '.lres (
			id bigint PRIMARY KEY DEFAULT 0,

			lre_type text,
			maximum_relative_error double precision,
			f_max double precision,
			f_min double precision,
			scaling text,
			maximum_number_of_trials_per_level integer,
			rho_n60 integer,
			rho_n50 integer,
			rho_n40 integer,
			rho_n30 integer,
			rho_n20 integer,
			rho_n10 integer,
			rho_00 integer,
			rho_p25 integer,
			rho_p50 integer,
			rho_p75 integer,
			rho_p90 integer,
			rho_p95 integer,
			rho_p99 integer,
			peak_number_of_sorting_elements integer,
			level_index integer,
			number_of_levels integer,
			relative_error_mean double precision,
			relative_error_variance double precision,
			relative_error_standard_deviation double precision,
			mean_local_correlation_coefficient_mean double precision,
			mean_local_correlation_coefficient_variance double precision,
			mean_local_correlation_coefficient_standard_deviation double precision,
			deviation_from_mean_local_cc_mean double precision,
			deviation_from_mean_local_cc_variance double precision,
			deviation_from_mean_local_cc_standard_deviation double precision,
			number_of_trials_per_interval_mean double precision,
			number_of_trials_per_interval_variance double precision,
			number_of_trials_per_interval_standard_deviation double precision,
			number_of_transitions_per_interval_mean double precision,
			number_of_transitions_per_interval_variance double precision,
			number_of_transitions_per_interval_standard_deviation double precision
		) INHERITS (' || quote_ident(user_name) || '.probes)';

	EXECUTE 'ALTER TABLE ' || quote_ident(user_name) || '.lres OWNER TO rrr';
	EXECUTE 'GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE ' || quote_ident(user_name) || '.lres TO ' || quote_ident(user_name);

	EXECUTE 'CREATE SEQUENCE ' || quote_ident(user_name) || '.lre_histograms_id_seq';
	EXECUTE 'ALTER TABLE ' || quote_ident(user_name) || '.lre_histograms_id_seq OWNER TO rrr';
	EXECUTE 'GRANT UPDATE, SELECT ON TABLE ' || quote_ident(user_name) || '.lre_histograms_id_seq TO ' || quote_ident(user_name);
	EXECUTE 'CREATE TABLE ' || quote_ident(user_name) || '.lre_histograms (
			id bigint PRIMARY KEY DEFAULT 0,
			campaign_id bigint,
			probe_id bigint,

			abscissa double precision,
			ordinate double precision,
			relative_error double precision,
			mean_local_correlation_coefficient double precision,
			deviation_from_mean_local_cc double precision,
			number_of_trials_per_interval double precision,
			number_of_transitions_per_interval double precision,
			relative_error_within_limit character(1)
		)';

	EXECUTE 'ALTER TABLE ' || quote_ident(user_name) || '.lre_histograms OWNER TO rrr';
	EXECUTE 'GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE ' || quote_ident(user_name) || '.lre_histograms TO ' || quote_ident(user_name);

	EXECUTE 'CREATE SEQUENCE ' || quote_ident(user_name) || '.dlres_id_seq';
	EXECUTE 'ALTER TABLE ' || quote_ident(user_name) || '.dlres_id_seq OWNER TO rrr';
	EXECUTE 'GRANT UPDATE, SELECT ON TABLE ' || quote_ident(user_name) || '.dlres_id_seq TO ' || quote_ident(user_name);
	EXECUTE 'CREATE TABLE ' || quote_ident(user_name) || '.dlres (
			id bigint PRIMARY KEY DEFAULT 0,

			dlre_type text,
			lower_border double precision,
			upper_border double precision,
			number_of_intervals integer,
			interval_size double precision,
			maximum_number_of_samples double precision,
			maximum_relative_error_percent double precision,
			evaluated_levels integer,
			underflows bigint,
			overflows bigint
		) INHERITS (' || quote_ident(user_name) || '.probes)';

	EXECUTE 'ALTER TABLE ' || quote_ident(user_name) || '.dlres OWNER TO rrr';
	EXECUTE 'GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE ' || quote_ident(user_name) || '.dlres TO ' || quote_ident(user_name);

	EXECUTE 'CREATE SEQUENCE ' || quote_ident(user_name) || '.dlre_histograms_id_seq';
	EXECUTE 'ALTER TABLE ' || quote_ident(user_name) || '.dlre_histograms_id_seq OWNER TO rrr';
	EXECUTE 'GRANT UPDATE, SELECT ON TABLE ' || quote_ident(user_name) || '.dlre_histograms_id_seq TO ' || quote_ident(user_name);
	EXECUTE 'CREATE TABLE ' || quote_ident(user_name) || '.dlre_histograms (
			id bigint PRIMARY KEY DEFAULT 0,
			campaign_id bigint,
			probe_id bigint,

			abscissa double precision,
			ordinate double precision,
			relative_error double precision,
			mean_local_correlation_coefficient double precision,
			deviation_from_mean_local_cc double precision,
			number_of_trials_per_interval double precision,
			number_of_transitions_per_interval double precision,
			relative_error_within_limit character(1)
		)';

	EXECUTE 'ALTER TABLE ' || quote_ident(user_name) || '.dlre_histograms OWNER TO rrr';
	EXECUTE 'GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE ' || quote_ident(user_name) || '.dlre_histograms TO ' || quote_ident(user_name);

	EXECUTE 'CREATE SEQUENCE ' || quote_ident(user_name) || '.tables_id_seq';
	EXECUTE 'ALTER TABLE ' || quote_ident(user_name) || '.tables_id_seq OWNER TO rrr';
	EXECUTE 'GRANT UPDATE, SELECT ON TABLE ' || quote_ident(user_name) || '.tables_id_seq TO ' || quote_ident(user_name);
	EXECUTE 'CREATE TABLE ' || quote_ident(user_name) || '.tables (
			id bigint PRIMARY KEY DEFAULT 0,
			campaign_id bigint,
			scenario_id bigint,

			filename text,
			name text,
			type text,
			first_col_type character(1),
			first_col_description text,
			second_col_type character(1),
			second_col_description text,
			description text,
			minimum double precision,
			maximum double precision
		)';

	EXECUTE 'ALTER TABLE ' || quote_ident(user_name) || '.tables OWNER TO rrr';
	EXECUTE 'GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE ' || quote_ident(user_name) || '.tables TO ' || quote_ident(user_name);

	EXECUTE 'CREATE SEQUENCE ' || quote_ident(user_name) || '.table_rows_id_seq';
	EXECUTE 'ALTER TABLE ' || quote_ident(user_name) || '.table_rows_id_seq OWNER TO rrr';
	EXECUTE 'GRANT UPDATE, SELECT ON TABLE ' || quote_ident(user_name) || '.table_rows_id_seq TO ' || quote_ident(user_name);
	EXECUTE 'CREATE TABLE ' || quote_ident(user_name) || '.table_rows (
			id bigint PRIMARY KEY DEFAULT 0,
			campaign_id bigint,
			probe_id bigint,

			first_col double precision,
			second_col double precision,
			value double precision
		)';

	EXECUTE 'ALTER TABLE ' || quote_ident(user_name) || '.table_rows OWNER TO rrr';
	EXECUTE 'GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE ' || quote_ident(user_name) || '.table_rows TO ' || quote_ident(user_name);


	-- create private functions
	EXECUTE 'CREATE FUNCTION ' || quote_ident(user_name) || '.campaign_before() RETURNS trigger AS $campaign_before_trigger$
		DECLARE
			db_size bigint;
		BEGIN
			IF (TG_OP = ''INSERT'') THEN
				NEW.id := nextval(''administration.campaigns_id_seq''::regclass);
				NEW.db_size := 0;
				RETURN NEW;
			ELSIF (TG_OP = ''UPDATE'') THEN
				NEW.id := OLD.id;
				EXECUTE ''SELECT administration.calculate_campaign_size('' || OLD.id || '')'' INTO db_size;
				NEW.db_size := db_size;
				RETURN NEW;
			END IF;
		END;
		$campaign_before_trigger$ LANGUAGE plpgsql SECURITY DEFINER;;

		CREATE TRIGGER campaign_before_trigger
		BEFORE INSERT OR UPDATE ON ' || quote_ident(user_name) || '.campaigns
		FOR EACH ROW EXECUTE PROCEDURE ' || quote_ident(user_name) || '.campaign_before()';

	EXECUTE 'ALTER FUNCTION ' || quote_ident(user_name) || '.campaign_before() OWNER TO rrr';
	EXECUTE 'REVOKE ALL ON FUNCTION ' || quote_ident(user_name) || '.campaign_before() FROM PUBLIC';
	EXECUTE 'GRANT EXECUTE ON FUNCTION ' || quote_ident(user_name) || '.campaign_before() TO ' || quote_ident(user_name);

	EXECUTE 'CREATE FUNCTION ' || quote_ident(user_name) || '.campaign() RETURNS trigger AS $campaign_trigger$
		BEGIN
			IF (TG_OP = ''INSERT'') THEN
				EXECUTE ''CREATE TABLE ' || quote_ident(user_name) || '.authorizations_'' || NEW.id || '' () INHERITS(' || quote_ident(user_name) || '.authorizations)'';
				EXECUTE ''ALTER TABLE ' || quote_ident(user_name) || '.authorizations_'' || NEW.id || '' ADD CONSTRAINT campaignsfk FOREIGN KEY (campaign_id) REFERENCES ' || quote_ident(user_name) || '.campaigns (id) ON DELETE CASCADE'';
				EXECUTE ''ALTER TABLE ' || quote_ident(user_name) || '.authorizations_'' || NEW.id || '' ALTER campaign_id SET DEFAULT '' || NEW.id;
				EXECUTE ''ALTER TABLE ' || quote_ident(user_name) || '.authorizations_'' || NEW.id || '' ADD CONSTRAINT campaignid CHECK (campaign_id = '' || NEW.id || '')'';
				EXECUTE	''ALTER TABLE ' || quote_ident(user_name) || '.authorizations_'' || NEW.id || '' ADD PRIMARY KEY (id)'';
				EXECUTE ''ALTER TABLE ' || quote_ident(user_name) || '.authorizations_'' || NEW.id || '' ADD UNIQUE (user_id, authorized_id)'';
				EXECUTE ''GRANT SELECT, DELETE ON TABLE ' || quote_ident(user_name) || '.authorizations_'' || NEW.id || '' TO PUBLIC'';
				EXECUTE ''CREATE TRIGGER delete_authorizations_trigger_'' || NEW.id || '' BEFORE DELETE ON ' || quote_ident(user_name) || '.authorizations_'' || NEW.id || '' FOR EACH ROW EXECUTE PROCEDURE ' || quote_ident(user_name) || '.delete_authorizations()'';

				EXECUTE ''CREATE TABLE ' || quote_ident(user_name) || '.scenarios_'' || NEW.id || '' () INHERITS(' || quote_ident(user_name) || '.scenarios)'';
				EXECUTE ''ALTER TABLE ' || quote_ident(user_name) || '.scenarios_'' || NEW.id || '' ADD CONSTRAINT campaignsfk FOREIGN KEY (campaign_id) REFERENCES ' || quote_ident(user_name) || '.campaigns (id) ON DELETE CASCADE'';
				EXECUTE ''ALTER TABLE ' || quote_ident(user_name) || '.scenarios_'' || NEW.id || '' ALTER campaign_id SET DEFAULT '' || NEW.id;
				EXECUTE ''ALTER TABLE ' || quote_ident(user_name) || '.scenarios_'' || NEW.id || '' ADD CONSTRAINT campaignid CHECK (campaign_id = '' || NEW.id || '')'';
				EXECUTE	''ALTER TABLE ' || quote_ident(user_name) || '.scenarios_'' || NEW.id || '' ADD PRIMARY KEY (id)'';
				EXECUTE ''CREATE TRIGGER scenarios_update_trigger_'' || NEW.id || '' AFTER UPDATE ON ' || quote_ident(user_name) || '.scenarios_'' || NEW.id || '' FOR EACH ROW EXECUTE PROCEDURE ' || quote_ident(user_name) || '.scenarios_update()'';
				EXECUTE ''GRANT SELECT, UPDATE, DELETE ON TABLE ' || quote_ident(user_name) || '.scenarios_'' || NEW.id || '' TO ' || quote_ident(user_name) || ''';

				EXECUTE ''CREATE TABLE ' || quote_ident(user_name) || '.files_'' || NEW.id || '' () INHERITS(' || quote_ident(user_name) || '.files)'';
				EXECUTE ''ALTER TABLE ' || quote_ident(user_name) || '.files_'' || NEW.id || '' ADD CONSTRAINT campaignsfk FOREIGN KEY (campaign_id) REFERENCES ' || quote_ident(user_name) || '.campaigns (id) ON DELETE CASCADE'';
				EXECUTE ''ALTER TABLE ' || quote_ident(user_name) || '.files_'' || NEW.id || '' ALTER campaign_id SET DEFAULT '' || NEW.id;
				EXECUTE ''ALTER TABLE ' || quote_ident(user_name) || '.files_'' || NEW.id || '' ADD CONSTRAINT campaignid CHECK (campaign_id = '' || NEW.id || '')'';
				EXECUTE	''ALTER TABLE ' || quote_ident(user_name) || '.files_'' || NEW.id || '' ADD PRIMARY KEY (id)'';
				EXECUTE ''GRANT SELECT, UPDATE, DELETE ON TABLE ' || quote_ident(user_name) || '.files_'' || NEW.id || '' TO ' || quote_ident(user_name) || ''';

				EXECUTE ''CREATE TABLE ' || quote_ident(user_name) || '.parameters_'' || NEW.id || '' () INHERITS(' || quote_ident(user_name) || '.parameters)'';
				EXECUTE ''ALTER TABLE ' || quote_ident(user_name) || '.parameters_'' || NEW.id || '' ADD CONSTRAINT scenariosfk FOREIGN KEY (scenario_id) REFERENCES ' || quote_ident(user_name) || '.scenarios_'' || NEW.id || '' (id) ON DELETE CASCADE'';
				EXECUTE ''ALTER TABLE ' || quote_ident(user_name) || '.parameters_'' || NEW.id || '' ALTER campaign_id SET DEFAULT '' || NEW.id;
				EXECUTE ''ALTER TABLE ' || quote_ident(user_name) || '.parameters_'' || NEW.id || '' ADD CONSTRAINT campaignid CHECK (campaign_id = '' || NEW.id || '')'';
				EXECUTE	''ALTER TABLE ' || quote_ident(user_name) || '.parameters_'' || NEW.id || '' ADD PRIMARY KEY (id)'';
				EXECUTE ''ALTER TABLE ' || quote_ident(user_name) || '.parameters_'' || NEW.id || '' ADD UNIQUE (campaign_id, scenario_id, parameter_name)'';
				EXECUTE ''CREATE INDEX parameters_scenario_id_index_'' || NEW.id || '' ON ' || quote_ident(user_name) || '.parameters_'' || NEW.id || '' (scenario_id)'';
				EXECUTE ''GRANT SELECT, UPDATE, DELETE ON TABLE ' || quote_ident(user_name) || '.parameters_'' || NEW.id || '' TO ' || quote_ident(user_name) || ''';

				EXECUTE ''CREATE TABLE ' || quote_ident(user_name) || '.jobs_'' || NEW.id || '' () INHERITS(' || quote_ident(user_name) || '.jobs)'';
				EXECUTE ''ALTER TABLE ' || quote_ident(user_name) || '.jobs_'' || NEW.id || '' ADD CONSTRAINT scenariosfk FOREIGN KEY (scenario_id) REFERENCES ' || quote_ident(user_name) || '.scenarios_'' || NEW.id || '' (id) ON DELETE CASCADE'';
				EXECUTE ''ALTER TABLE ' || quote_ident(user_name) || '.jobs_'' || NEW.id || '' ALTER campaign_id SET DEFAULT '' || NEW.id;
				EXECUTE ''ALTER TABLE ' || quote_ident(user_name) || '.jobs_'' || NEW.id || '' ADD CONSTRAINT campaignid CHECK (campaign_id = '' || NEW.id || '')'';
				EXECUTE	''ALTER TABLE ' || quote_ident(user_name) || '.jobs_'' || NEW.id || '' ADD PRIMARY KEY (id)'';
				EXECUTE ''CREATE INDEX jobs_scenario_id_index_'' || NEW.id || '' ON ' || quote_ident(user_name) || '.jobs_'' || NEW.id || '' (scenario_id)'';
				EXECUTE ''GRANT SELECT, UPDATE, DELETE ON TABLE ' || quote_ident(user_name) || '.jobs_'' || NEW.id || '' TO ' || quote_ident(user_name) || ''';

				EXECUTE ''CREATE TABLE ' || quote_ident(user_name) || '.pd_fs_'' || NEW.id || '' () INHERITS(' || quote_ident(user_name) || '.pd_fs)'';
				EXECUTE ''ALTER TABLE ' || quote_ident(user_name) || '.pd_fs_'' || NEW.id || '' ADD CONSTRAINT scenariosfk FOREIGN KEY (scenario_id) REFERENCES ' || quote_ident(user_name) || '.scenarios_'' || NEW.id || '' (id) ON DELETE CASCADE'';
				EXECUTE ''ALTER TABLE ' || quote_ident(user_name) || '.pd_fs_'' || NEW.id || '' ALTER campaign_id SET DEFAULT '' || NEW.id;
				EXECUTE ''ALTER TABLE ' || quote_ident(user_name) || '.pd_fs_'' || NEW.id || '' ADD CONSTRAINT campaignid CHECK (campaign_id = '' || NEW.id || '')'';
				EXECUTE	''ALTER TABLE ' || quote_ident(user_name) || '.pd_fs_'' || NEW.id || '' ADD PRIMARY KEY (id)'';
				EXECUTE ''CREATE INDEX pd_fs_scenario_id_index_'' || NEW.id || '' ON ' || quote_ident(user_name) || '.pd_fs_'' || NEW.id || '' (scenario_id)'';
				EXECUTE ''GRANT SELECT, UPDATE, DELETE ON TABLE ' || quote_ident(user_name) || '.pd_fs_'' || NEW.id || '' TO ' || quote_ident(user_name) || ''';

				EXECUTE ''CREATE TABLE ' || quote_ident(user_name) || '.pdf_histograms_'' || NEW.id || '' () INHERITS(' || quote_ident(user_name) || '.pdf_histograms)'';
				EXECUTE ''ALTER TABLE ' || quote_ident(user_name) || '.pdf_histograms_'' || NEW.id || '' ADD CONSTRAINT pd_fsfk FOREIGN KEY (probe_id) REFERENCES ' || quote_ident(user_name) || '.pd_fs_'' || NEW.id || '' (id) ON DELETE CASCADE'';
				EXECUTE ''ALTER TABLE ' || quote_ident(user_name) || '.pdf_histograms_'' || NEW.id || '' ALTER campaign_id SET DEFAULT '' || NEW.id;
				EXECUTE ''ALTER TABLE ' || quote_ident(user_name) || '.pdf_histograms_'' || NEW.id || '' ADD CONSTRAINT campaignid CHECK (campaign_id = '' || NEW.id || '')'';
				EXECUTE	''ALTER TABLE ' || quote_ident(user_name) || '.pdf_histograms_'' || NEW.id || '' ADD PRIMARY KEY (id)'';
				EXECUTE ''CREATE INDEX pdf_histograms_probe_id_index_'' || NEW.id || '' ON ' || quote_ident(user_name) || '.pdf_histograms_'' || NEW.id || '' (probe_id)'';
				EXECUTE ''GRANT SELECT, UPDATE, DELETE ON TABLE ' || quote_ident(user_name) || '.pdf_histograms_'' || NEW.id || '' TO ' || quote_ident(user_name) || ''';

				EXECUTE ''CREATE TABLE ' || quote_ident(user_name) || '.log_evals_'' || NEW.id || '' () INHERITS(' || quote_ident(user_name) || '.log_evals)'';
				EXECUTE ''ALTER TABLE ' || quote_ident(user_name) || '.log_evals_'' || NEW.id || '' ADD CONSTRAINT scenariosfk FOREIGN KEY (scenario_id) REFERENCES ' || quote_ident(user_name) || '.scenarios_'' || NEW.id || '' (id) ON DELETE CASCADE'';
				EXECUTE ''ALTER TABLE ' || quote_ident(user_name) || '.log_evals_'' || NEW.id || '' ALTER campaign_id SET DEFAULT '' || NEW.id;
				EXECUTE ''ALTER TABLE ' || quote_ident(user_name) || '.log_evals_'' || NEW.id || '' ADD CONSTRAINT campaignid CHECK (campaign_id = '' || NEW.id || '')'';
				EXECUTE	''ALTER TABLE ' || quote_ident(user_name) || '.log_evals_'' || NEW.id || '' ADD PRIMARY KEY (id)'';
				EXECUTE ''CREATE INDEX log_evals_scenario_id_index_'' || NEW.id || '' ON ' || quote_ident(user_name) || '.log_evals_'' || NEW.id || '' (scenario_id)'';
				EXECUTE ''GRANT SELECT, UPDATE, DELETE ON TABLE ' || quote_ident(user_name) || '.log_evals_'' || NEW.id || '' TO ' || quote_ident(user_name) || ''';

				EXECUTE ''CREATE TABLE ' || quote_ident(user_name) || '.log_eval_entries_'' || NEW.id || '' () INHERITS(' || quote_ident(user_name) || '.log_eval_entries)'';
				EXECUTE ''ALTER TABLE ' || quote_ident(user_name) || '.log_eval_entries_'' || NEW.id || '' ADD CONSTRAINT log_evalsfk FOREIGN KEY (probe_id) REFERENCES ' || quote_ident(user_name) || '.log_evals_'' || NEW.id || '' (id) ON DELETE CASCADE'';
				EXECUTE ''ALTER TABLE ' || quote_ident(user_name) || '.log_eval_entries_'' || NEW.id || '' ALTER campaign_id SET DEFAULT '' || NEW.id;
				EXECUTE ''ALTER TABLE ' || quote_ident(user_name) || '.log_eval_entries_'' || NEW.id || '' ADD CONSTRAINT campaignid CHECK (campaign_id = '' || NEW.id || '')'';
				EXECUTE	''ALTER TABLE ' || quote_ident(user_name) || '.log_eval_entries_'' || NEW.id || '' ADD PRIMARY KEY (id)'';
				EXECUTE ''CREATE INDEX log_eval_entries_probe_id_index_'' || NEW.id || '' ON ' || quote_ident(user_name) || '.log_eval_entries_'' || NEW.id || '' (probe_id)'';
				EXECUTE ''GRANT SELECT, UPDATE, DELETE ON TABLE ' || quote_ident(user_name) || '.log_eval_entries_'' || NEW.id || '' TO ' || quote_ident(user_name) || ''';

				EXECUTE ''CREATE TABLE ' || quote_ident(user_name) || '.moments_'' || NEW.id || '' () INHERITS(' || quote_ident(user_name) || '.moments)'';
				EXECUTE ''ALTER TABLE ' || quote_ident(user_name) || '.moments_'' || NEW.id || '' ADD CONSTRAINT scenariosfk FOREIGN KEY (scenario_id) REFERENCES ' || quote_ident(user_name) || '.scenarios_'' || NEW.id || '' (id) ON DELETE CASCADE'';
				EXECUTE ''ALTER TABLE ' || quote_ident(user_name) || '.moments_'' || NEW.id || '' ALTER campaign_id SET DEFAULT '' || NEW.id;
				EXECUTE ''ALTER TABLE ' || quote_ident(user_name) || '.moments_'' || NEW.id || '' ADD CONSTRAINT campaignid CHECK (campaign_id = '' || NEW.id || '')'';
				EXECUTE	''ALTER TABLE ' || quote_ident(user_name) || '.moments_'' || NEW.id || '' ADD PRIMARY KEY (id)'';
				EXECUTE ''CREATE INDEX moments_scenario_id_index_'' || NEW.id || '' ON ' || quote_ident(user_name) || '.moments_'' || NEW.id || '' (scenario_id)'';
				EXECUTE ''GRANT SELECT, UPDATE, DELETE ON TABLE ' || quote_ident(user_name) || '.moments_'' || NEW.id || '' TO ' || quote_ident(user_name) || ''';

				EXECUTE ''CREATE TABLE ' || quote_ident(user_name) || '.batch_means_'' || NEW.id || '' () INHERITS(' || quote_ident(user_name) || '.batch_means)'';
				EXECUTE ''ALTER TABLE ' || quote_ident(user_name) || '.batch_means_'' || NEW.id || '' ADD CONSTRAINT scenariosfk FOREIGN KEY (scenario_id) REFERENCES ' || quote_ident(user_name) || '.scenarios_'' || NEW.id || '' (id) ON DELETE CASCADE'';
				EXECUTE ''ALTER TABLE ' || quote_ident(user_name) || '.batch_means_'' || NEW.id || '' ALTER campaign_id SET DEFAULT '' || NEW.id;
				EXECUTE ''ALTER TABLE ' || quote_ident(user_name) || '.batch_means_'' || NEW.id || '' ADD CONSTRAINT campaignid CHECK (campaign_id = '' || NEW.id || '')'';
				EXECUTE	''ALTER TABLE ' || quote_ident(user_name) || '.batch_means_'' || NEW.id || '' ADD PRIMARY KEY (id)'';
				EXECUTE ''CREATE INDEX batch_means_scenario_id_index_'' || NEW.id || '' ON ' || quote_ident(user_name) || '.batch_means_'' || NEW.id || '' (scenario_id)'';
				EXECUTE ''GRANT SELECT, UPDATE, DELETE ON TABLE ' || quote_ident(user_name) || '.batch_means_'' || NEW.id || '' TO ' || quote_ident(user_name) || ''';

				EXECUTE ''CREATE TABLE ' || quote_ident(user_name) || '.batch_means_histograms_'' || NEW.id || '' () INHERITS(' || quote_ident(user_name) || '.batch_means_histograms)'';
				EXECUTE ''ALTER TABLE ' || quote_ident(user_name) || '.batch_means_histograms_'' || NEW.id || '' ADD CONSTRAINT batch_meansfk FOREIGN KEY (probe_id) REFERENCES ' || quote_ident(user_name) || '.batch_means_'' || NEW.id || '' (id) ON DELETE CASCADE'';
				EXECUTE ''ALTER TABLE ' || quote_ident(user_name) || '.batch_means_histograms_'' || NEW.id || '' ALTER campaign_id SET DEFAULT '' || NEW.id;
				EXECUTE ''ALTER TABLE ' || quote_ident(user_name) || '.batch_means_histograms_'' || NEW.id || '' ADD CONSTRAINT campaignid CHECK (campaign_id = '' || NEW.id || '')'';
				EXECUTE	''ALTER TABLE ' || quote_ident(user_name) || '.batch_means_histograms_'' || NEW.id || '' ADD PRIMARY KEY (id)'';
				EXECUTE ''CREATE INDEX batch_means_histograms_probe_id_index_'' || NEW.id || '' ON ' || quote_ident(user_name) || '.batch_means_histograms_'' || NEW.id || '' (probe_id)'';
				EXECUTE ''GRANT SELECT, UPDATE, DELETE ON TABLE ' || quote_ident(user_name) || '.batch_means_histograms_'' || NEW.id || '' TO ' || quote_ident(user_name) || ''';

				EXECUTE ''CREATE TABLE ' || quote_ident(user_name) || '.lres_'' || NEW.id || '' () INHERITS(' || quote_ident(user_name) || '.lres)'';
				EXECUTE ''ALTER TABLE ' || quote_ident(user_name) || '.lres_'' || NEW.id || '' ADD CONSTRAINT scenariosfk FOREIGN KEY (scenario_id) REFERENCES ' || quote_ident(user_name) || '.scenarios_'' || NEW.id || '' (id) ON DELETE CASCADE'';
				EXECUTE ''ALTER TABLE ' || quote_ident(user_name) || '.lres_'' || NEW.id || '' ALTER campaign_id SET DEFAULT '' || NEW.id;
				EXECUTE ''ALTER TABLE ' || quote_ident(user_name) || '.lres_'' || NEW.id || '' ADD CONSTRAINT campaignid CHECK (campaign_id = '' || NEW.id || '')'';
				EXECUTE	''ALTER TABLE ' || quote_ident(user_name) || '.lres_'' || NEW.id || '' ADD PRIMARY KEY (id)'';
				EXECUTE ''CREATE INDEX lres_scenario_id_index_'' || NEW.id || '' ON ' || quote_ident(user_name) || '.lres_'' || NEW.id || '' (scenario_id)'';
				EXECUTE ''GRANT SELECT, UPDATE, DELETE ON TABLE ' || quote_ident(user_name) || '.lres_'' || NEW.id || '' TO ' || quote_ident(user_name) || ''';

				EXECUTE ''CREATE TABLE ' || quote_ident(user_name) || '.lre_histograms_'' || NEW.id || '' () INHERITS(' || quote_ident(user_name) || '.lre_histograms)'';
				EXECUTE ''ALTER TABLE ' || quote_ident(user_name) || '.lre_histograms_'' || NEW.id || '' ADD CONSTRAINT lresfk FOREIGN KEY (probe_id) REFERENCES ' || quote_ident(user_name) || '.lres_'' || NEW.id || '' (id) ON DELETE CASCADE'';
				EXECUTE ''ALTER TABLE ' || quote_ident(user_name) || '.lre_histograms_'' || NEW.id || '' ALTER campaign_id SET DEFAULT '' || NEW.id;
				EXECUTE ''ALTER TABLE ' || quote_ident(user_name) || '.lre_histograms_'' || NEW.id || '' ADD CONSTRAINT campaignid CHECK (campaign_id = '' || NEW.id || '')'';
				EXECUTE	''ALTER TABLE ' || quote_ident(user_name) || '.lre_histograms_'' || NEW.id || '' ADD PRIMARY KEY (id)'';
				EXECUTE ''CREATE INDEX lre_histograms_probe_id_index_'' || NEW.id || '' ON ' || quote_ident(user_name) || '.lre_histograms_'' || NEW.id || '' (probe_id)'';
				EXECUTE ''GRANT SELECT, UPDATE, DELETE ON TABLE ' || quote_ident(user_name) || '.lre_histograms_'' || NEW.id || '' TO ' || quote_ident(user_name) || ''';

				EXECUTE ''CREATE TABLE ' || quote_ident(user_name) || '.dlres_'' || NEW.id || '' () INHERITS(' || quote_ident(user_name) || '.dlres)'';
				EXECUTE ''ALTER TABLE ' || quote_ident(user_name) || '.dlres_'' || NEW.id || '' ADD CONSTRAINT scenariosfk FOREIGN KEY (scenario_id) REFERENCES ' || quote_ident(user_name) || '.scenarios_'' || NEW.id || '' (id) ON DELETE CASCADE'';
				EXECUTE ''ALTER TABLE ' || quote_ident(user_name) || '.dlres_'' || NEW.id || '' ALTER campaign_id SET DEFAULT '' || NEW.id;
				EXECUTE ''ALTER TABLE ' || quote_ident(user_name) || '.dlres_'' || NEW.id || '' ADD CONSTRAINT campaignid CHECK (campaign_id = '' || NEW.id || '')'';
				EXECUTE	''ALTER TABLE ' || quote_ident(user_name) || '.dlres_'' || NEW.id || '' ADD PRIMARY KEY (id)'';
				EXECUTE ''CREATE INDEX dlres_scenario_id_index_'' || NEW.id || '' ON ' || quote_ident(user_name) || '.dlres_'' || NEW.id || '' (scenario_id)'';
				EXECUTE ''GRANT SELECT, UPDATE, DELETE ON TABLE ' || quote_ident(user_name) || '.dlres_'' || NEW.id || '' TO ' || quote_ident(user_name) || ''';

				EXECUTE ''CREATE TABLE ' || quote_ident(user_name) || '.dlre_histograms_'' || NEW.id || '' () INHERITS(' || quote_ident(user_name) || '.dlre_histograms)'';
				EXEXUTE ''ALTER TABLE ' || quote_ident(user_name) || '.dlre_histograms_'' || NEW.id || '' ADD CONSTRAINT dlresfk FOREIGN KEY (probe_id) REFERENCES ' || quote_ident(user_name) || '.dlres_'' || NEW.id || '' (id) ON DELETE CASCADE'';
				EXEXUTE ''ALTER TABLE ' || quote_ident(user_name) || '.dlre_histograms_'' || NEW.id || '' ALTER campaign_id SET DEFAULT '' || NEW.id;
				EXEXUTE ''ALTER TABLE ' || quote_ident(user_name) || '.dlre_histograms_'' || NEW.id || '' ADD CONSTRAINT campaignid CHECK (campaign_id = '' || NEW.id || '')'';
				EXECUTE	''ALTER TABLE ' || quote_ident(user_name) || '.dlre_histograms_'' || NEW.id || '' ADD PRIMARY KEY (id)'';
				EXEXUTE ''CREATE INDEX dlre_histograms_probe_id_index_'' || NEW.id || '' ON ' || quote_ident(user_name) || '.dlre_histograms_'' || NEW.id || '' (probe_id)'';
				EXEXUTE ''GRANT SELECT, UPDATE, DELETE ON TABLE ' || quote_ident(user_name) || '.dlre_histograms_'' || NEW.id || '' TO ' || quote_ident(user_name) || ''';

				EXEXUTE ''CREATE TABLE ' || quote_ident(user_name) || '.tables_'' || NEW.id || '' () INHERITS(' || quote_ident(user_name) || '.tables)'';
				EXEXUTE ''ALTER TABLE ' || quote_ident(user_name) || '.tables_'' || NEW.id || '' ADD CONSTRAINT scenariosfk FOREIGN KEY (scenario_id) REFERENCES ' || quote_ident(user_name) || '.scenarios_'' || NEW.id || '' (id) ON DELETE CASCADE'';
				EXEXUTE ''ALTER TABLE ' || quote_ident(user_name) || '.tables_'' || NEW.id || '' ALTER campaign_id SET DEFAULT '' || NEW.id;
				EXEXUTE ''ALTER TABLE ' || quote_ident(user_name) || '.tables_'' || NEW.id || '' ADD CONSTRAINT campaignid CHECK (campaign_id = '' || NEW.id || '')'';
				EXECUTE	''ALTER TABLE ' || quote_ident(user_name) || '.tables_'' || NEW.id || '' ADD PRIMARY KEY (id)'';
				EXEXUTE ''CREATE INDEX tables_scenario_id_index_'' || NEW.id || '' ON ' || quote_ident(user_name) || '.tables_'' || NEW.id || '' (scenario_id)'';
				EXEXUTE ''GRANT SELECT, UPDATE, DELETE ON TABLE ' || quote_ident(user_name) || '.tables_'' || NEW.id || '' TO ' || quote_ident(user_name) || ''';

				EXEXUTE ''CREATE TABLE ' || quote_ident(user_name) || '.table_rows_'' || NEW.id || '' () INHERITS(' || quote_ident(user_name) || '.table_rows)'';
				EXEXUTE ''ALTER TABLE ' || quote_ident(user_name) || '.table_rows_'' || NEW.id || '' ADD CONSTRAINT tablesfk FOREIGN KEY (probe_id) REFERENCES ' || quote_ident(user_name) || '.tables_'' || NEW.id || '' (id) ON DELETE CASCADE'';
				EXEXUTE ''ALTER TABLE ' || quote_ident(user_name) || '.table_rows_'' || NEW.id || '' ALTER campaign_id SET DEFAULT '' || NEW.id;
				EXEXUTE ''ALTER TABLE ' || quote_ident(user_name) || '.table_rows_'' || NEW.id || '' ADD CONSTRAINT campaignid CHECK (campaign_id = '' || NEW.id || '')'';
				EXECUTE	''ALTER TABLE ' || quote_ident(user_name) || '.table_rows_'' || NEW.id || '' ADD PRIMARY KEY (id)'';
				EXEXUTE ''CREATE INDEX table_rows_probe_id_index_'' || NEW.id || '' ON ' || quote_ident(user_name) || '.table_rows_'' || NEW.id || '' (probe_id)'';
				EXEXUTE ''GRANT SELECT, UPDATE, DELETE ON TABLE ' || quote_ident(user_name) || '.table_rows_'' || NEW.id || '' TO ' || quote_ident(user_name) || ''';

				EXEXUTE ''INSERT INTO ' || quote_ident(user_name) || '.authorizations_'' || NEW.id || '' (id, authorized_id) VALUES (nextval('' || administration.authorizations_id_seq || ''::regclass), ' || user_id || ')'';
				EXEXUTE ''UPDATE ' || quote_ident(user_name) || '.campaigns SET db_size = 0 WHERE id = '' || NEW.id;

				RETURN NEW;
			ELSIF (TG_OP = ''UPDATE'') THEN
				UPDATE administration.users SET db_use = 0 WHERE id = ' || user_id || ';
				RETURN NEW;
			ELSIF (TG_OP = ''DELETE'') THEN
				EXEXUTE ''DROP TABLE ' || quote_ident(user_name) || '.authorizations_'' || OLD.id || '',
						     ' || quote_ident(user_name) || '.scenarios_'' || OLD.id || '',
						     ' || quote_ident(user_name) || '.files_'' || OLD.id || '',
						     ' || quote_ident(user_name) || '.parameters_'' || OLD.id || '',
						     ' || quote_ident(user_name) || '.jobs_'' || OLD.id || '',
						     ' || quote_ident(user_name) || '.pd_fs_'' || OLD.id || '',
						     ' || quote_ident(user_name) || '.pdf_histograms_'' || OLD.id || '',
						     ' || quote_ident(user_name) || '.log_evals_'' || OLD.id || '',
						     ' || quote_ident(user_name) || '.log_eval_entries_'' || OLD.id || '',
						     ' || quote_ident(user_name) || '.moments_'' || OLD.id || '',
						     ' || quote_ident(user_name) || '.batch_means_'' || OLD.id || '',
						     ' || quote_ident(user_name) || '.batch_means_histograms_'' || OLD.id || '',
						     ' || quote_ident(user_name) || '.lres_'' || OLD.id || '',
						     ' || quote_ident(user_name) || '.lre_histograms_'' || OLD.id || '',
						     ' || quote_ident(user_name) || '.dlres_'' || OLD.id || '',
						     ' || quote_ident(user_name) || '.dlre_histograms_'' || OLD.id || '',
						     ' || quote_ident(user_name) || '.tables_'' || OLD.id || '',
						     ' || quote_ident(user_name) || '.table_rows_'' || OLD.id || '' CASCADE'';

				UPDATE administration.users SET db_use = 0 WHERE id = ' || user_id || ';

				RETURN OLD;
			END IF;
		END;
		$campaign_trigger$ LANGUAGE plpgsql SECURITY DEFINER;

		CREATE TRIGGER campaign_trigger
		AFTER INSERT OR UPDATE OR DELETE ON ' || quote_ident(user_name) || '.campaigns
		FOR EACH ROW EXECUTE PROCEDURE ' || quote_ident(user_name) || '.campaign()';

	EXECUTE 'ALTER FUNCTION ' || quote_ident(user_name) || '.campaign() OWNER TO rrr';
	EXECUTE 'REVOKE ALL ON FUNCTION ' || quote_ident(user_name) || '.campaign() FROM PUBLIC';
	EXECUTE 'GRANT EXECUTE ON FUNCTION ' || quote_ident(user_name) || '.campaign() TO ' || quote_ident(user_name);

	EXECUTE 'CREATE FUNCTION ' || quote_ident(user_name) || '.insert_authorizations() RETURNS trigger AS $insert_authorizations_trigger$
		DECLARE
			authorized_user text;
			authorization_id integer;
		BEGIN
			IF (NEW.user_id = NEW.authorized_id) THEN
				RETURN NEW;
			ELSE
				EXEXUTE ''SELECT user_name FROM administration.users WHERE id = '' || NEW.authorized_id INTO authorized_user;

				EXEXUTE ''GRANT USAGE ON SCHEMA ' || quote_ident(user_name) || ' TO '' || quote_ident(authorized_user);
				EXEXUTE ''GRANT SELECT ON TABLE ' || quote_ident(user_name) || '.scenarios_'' || NEW.campaign_id || '' TO '' || quote_ident(authorized_user);
				EXEXUTE ''GRANT SELECT ON TABLE ' || quote_ident(user_name) || '.files_'' || NEW.campaign_id || '' TO '' || quote_ident(authorized_user);
				EXEXUTE ''GRANT SELECT ON TABLE ' || quote_ident(user_name) || '.parameters_'' || NEW.campaign_id || '' TO '' || quote_ident(authorized_user);
				EXEXUTE ''GRANT SELECT ON TABLE ' || quote_ident(user_name) || '.jobs_'' || NEW.campaign_id || '' TO '' || quote_ident(authorized_user);
				EXEXUTE ''GRANT SELECT ON TABLE ' || quote_ident(user_name) || '.pd_fs_'' || NEW.campaign_id || '' TO '' || quote_ident(authorized_user);
				EXEXUTE ''GRANT SELECT ON TABLE ' || quote_ident(user_name) || '.pdf_histograms_'' || NEW.campaign_id || '' TO '' || quote_ident(authorized_user);
				EXEXUTE ''GRANT SELECT ON TABLE ' || quote_ident(user_name) || '.log_evals_'' || NEW.campaign_id || '' TO '' || quote_ident(authorized_user);
				EXEXUTE ''GRANT SELECT ON TABLE ' || quote_ident(user_name) || '.log_eval_entries_'' || NEW.campaign_id || '' TO '' || quote_ident(authorized_user);
				EXEXUTE ''GRANT SELECT ON TABLE ' || quote_ident(user_name) || '.moments_'' || NEW.campaign_id || '' TO '' || quote_ident(authorized_user);
				EXEXUTE ''GRANT SELECT ON TABLE ' || quote_ident(user_name) || '.batch_means_'' || NEW.campaign_id || '' TO '' || quote_ident(authorized_user);
				EXEXUTE ''GRANT SELECT ON TABLE ' || quote_ident(user_name) || '.batch_means_histograms_'' || NEW.campaign_id || '' TO '' || quote_ident(authorized_user);
				EXEXUTE ''GRANT SELECT ON TABLE ' || quote_ident(user_name) || '.lres_'' || NEW.campaign_id || '' TO '' || quote_ident(authorized_user);
				EXEXUTE ''GRANT SELECT ON TABLE ' || quote_ident(user_name) || '.lre_histograms_'' || NEW.campaign_id || '' TO '' || quote_ident(authorized_user);
				EXEXUTE ''GRANT SELECT ON TABLE ' || quote_ident(user_name) || '.dlres_'' || NEW.campaign_id || '' TO '' || quote_ident(authorized_user);
				EXEXUTE ''GRANT SELECT ON TABLE ' || quote_ident(user_name) || '.dlre_histograms_'' || NEW.campaign_id || '' TO '' || quote_ident(authorized_user);
				EXEXUTE ''GRANT SELECT ON TABLE ' || quote_ident(user_name) || '.tables_'' || NEW.campaign_id || '' TO '' || quote_ident(authorized_user);
				EXEXUTE ''GRANT SELECT ON TABLE ' || quote_ident(user_name) || '.table_rows_'' || NEW.campaign_id || '' TO '' || quote_ident(authorized_user);

				EXEXUTE ''SELECT nextval('' || administration.authorizations_id_seq || ''::regclass)'' INTO authorization_id;
				EXEXUTE ''INSERT INTO ' || quote_ident(user_name) || '.authorizations_'' || NEW.campaign_id || '' (id, campaign_id, authorized_id)
					VALUES ('' || quote_literal(authorization_id) || '', '' || quote_literal(NEW.campaign_id) || '', '' || quote_literal(NEW.authorized_id) || '')'';
				RETURN NULL;
			END IF;
		END;
		$insert_authorizations_trigger$ LANGUAGE plpgsql SECURITY DEFINER;

		CREATE TRIGGER insert_authorizations_trigger
		BEFORE INSERT ON ' || quote_ident(user_name) || '.authorizations
		FOR EACH ROW EXECUTE PROCEDURE ' || quote_ident(user_name) || '.insert_authorizations()';

	EXECUTE 'ALTER FUNCTION ' || quote_ident(user_name) || '.insert_authorizations() OWNER TO rrr';
	EXECUTE 'REVOKE ALL ON FUNCTION ' || quote_ident(user_name) || '.insert_authorizations() FROM PUBLIC';
	EXECUTE 'GRANT EXECUTE ON FUNCTION ' || quote_ident(user_name) || '.insert_authorizations() TO ' || quote_ident(user_name);

	EXECUTE 'CREATE FUNCTION ' || quote_ident(user_name) || '.delete_authorizations() RETURNS trigger AS $delete_authorizations_trigger$
		DECLARE
			authorized_user text;
			authorization_id integer;
		BEGIN
			IF (OLD.user_id = OLD.authorized_id) THEN
				RETURN OLD;
			ELSE
				EXEXUTE ''SELECT user_name FROM administration.users WHERE id = '' || OLD.authorized_id INTO authorized_user;

				EXEXUTE ''REVOKE ALL ON TABLE ' || quote_ident(user_name) || '.scenarios_'' || OLD.campaign_id || '' FROM '' || quote_ident(authorized_user);
				EXEXUTE ''REVOKE ALL ON TABLE ' || quote_ident(user_name) || '.files_'' || OLD.campaign_id || '' FROM '' || quote_ident(authorized_user);
				EXEXUTE ''REVOKE ALL ON TABLE ' || quote_ident(user_name) || '.parameters_'' || OLD.campaign_id || '' FROM '' || quote_ident(authorized_user);
				EXEXUTE ''REVOKE ALL ON TABLE ' || quote_ident(user_name) || '.jobs_'' || OLD.campaign_id || '' FROM '' || quote_ident(authorized_user);
				EXEXUTE ''REVOKE ALL ON TABLE ' || quote_ident(user_name) || '.pd_fs_'' || OLD.campaign_id || '' FROM '' || quote_ident(authorized_user);
				EXEXUTE ''REVOKE ALL ON TABLE ' || quote_ident(user_name) || '.pdf_histograms_'' || OLD.campaign_id || '' FROM '' || quote_ident(authorized_user);
				EXEXUTE ''REVOKE ALL ON TABLE ' || quote_ident(user_name) || '.log_evals_'' || OLD.campaign_id || '' FROM '' || quote_ident(authorized_user);
				EXEXUTE ''REVOKE ALL ON TABLE ' || quote_ident(user_name) || '.log_eval_entries_'' || OLD.campaign_id || '' FROM '' || quote_ident(authorized_user);
				EXEXUTE ''REVOKE ALL ON TABLE ' || quote_ident(user_name) || '.moments_'' || OLD.campaign_id || '' FROM '' || quote_ident(authorized_user);
				EXEXUTE ''REVOKE ALL ON TABLE ' || quote_ident(user_name) || '.batch_means_'' || OLD.campaign_id || '' FROM '' || quote_ident(authorized_user);
				EXEXUTE ''REVOKE ALL ON TABLE ' || quote_ident(user_name) || '.batch_means_histograms_'' || OLD.campaign_id || '' FROM '' || quote_ident(authorized_user);
				EXEXUTE ''REVOKE ALL ON TABLE ' || quote_ident(user_name) || '.lres_'' || OLD.campaign_id || '' FROM '' || quote_ident(authorized_user);
				EXEXUTE ''REVOKE ALL ON TABLE ' || quote_ident(user_name) || '.lre_histograms_'' || OLD.campaign_id || '' FROM '' || quote_ident(authorized_user);
				EXEXUTE ''REVOKE ALL ON TABLE ' || quote_ident(user_name) || '.dlres_'' || OLD.campaign_id || '' FROM '' || quote_ident(authorized_user);
				EXEXUTE ''REVOKE ALL ON TABLE ' || quote_ident(user_name) || '.dlre_histograms_'' || OLD.campaign_id || '' FROM '' || quote_ident(authorized_user);
				EXEXUTE ''REVOKE ALL ON TABLE ' || quote_ident(user_name) || '.tables_'' || OLD.campaign_id || '' FROM '' || quote_ident(authorized_user);
				EXEXUTE ''REVOKE ALL ON TABLE ' || quote_ident(user_name) || '.table_rows_'' || OLD.campaign_id || '' FROM '' || quote_ident(authorized_user);

				RETURN OLD;
			END IF;
		END;
		$delete_authorizations_trigger$ LANGUAGE plpgsql SECURITY DEFINER';

	EXECUTE 'ALTER FUNCTION ' || quote_ident(user_name) || '.delete_authorizations() OWNER TO rrr';
	EXECUTE 'REVOKE ALL ON FUNCTION ' || quote_ident(user_name) || '.delete_authorizations() FROM PUBLIC';
	EXECUTE 'GRANT EXECUTE ON FUNCTION ' || quote_ident(user_name) || '.delete_authorizations() TO ' || quote_ident(user_name);

	EXECUTE 'CREATE FUNCTION ' || quote_ident(user_name) || '.scenarios() RETURNS trigger AS $scenarios_trigger$
		BEGIN
			EXEXUTE ''INSERT INTO ' || quote_ident(user_name) || '.scenarios_'' || NEW.campaign_id || '' (id, campaign_id, current_job_id, state, max_sim_time,
					current_sim_time, sim_time_last_write)
				VALUES ('' || quote_literal(nextval(''' || quote_ident(user_name) || '.scenarios_id_seq''::regclass)) || '', '' || quote_literal(NEW.campaign_id) || '',
					'' || quote_literal(NEW.current_job_id) || '', '' || quote_literal(NEW.state) || '', '' || quote_literal(NEW.max_sim_time) || '',
					'' || quote_literal(NEW.current_sim_time) || '', '' || quote_literal(NEW.sim_time_last_write) || '')'';
			RETURN NULL;
		END;
		$scenarios_trigger$ LANGUAGE plpgsql SECURITY DEFINER;

		CREATE TRIGGER scenarios_trigger
		BEFORE INSERT ON ' || quote_ident(user_name) || '.scenarios
		FOR EACH ROW EXECUTE PROCEDURE ' || quote_ident(user_name) || '.scenarios()';

	EXECUTE 'ALTER FUNCTION ' || quote_ident(user_name) || '.scenarios() OWNER TO rrr';
	EXECUTE 'REVOKE ALL ON FUNCTION ' || quote_ident(user_name) || '.scenarios() FROM PUBLIC';
	EXECUTE 'GRANT EXECUTE ON FUNCTION ' || quote_ident(user_name) || '.scenarios() TO ' || quote_ident(user_name);

	EXECUTE 'CREATE FUNCTION ' || quote_ident(user_name) || '.scenarios_update() RETURNS trigger AS $scenarios_update_trigger$
		BEGIN
			EXEXUTE ''UPDATE ' || quote_ident(user_name) || '.campaigns SET db_size = 0 WHERE id = '' || OLD.campaign_id;
			RETURN NEW;
		END;
		$scenarios_update_trigger$ LANGUAGE plpgsql SECURITY DEFINER';

	EXECUTE 'ALTER FUNCTION ' || quote_ident(user_name) || '.scenarios_update() OWNER TO rrr';
	EXECUTE 'REVOKE ALL ON FUNCTION ' || quote_ident(user_name) || '.scenarios_update() FROM PUBLIC';
	EXECUTE 'GRANT EXECUTE ON FUNCTION ' || quote_ident(user_name) || '.scenarios_update() TO ' || quote_ident(user_name);

	EXECUTE 'CREATE FUNCTION ' || quote_ident(user_name) || '.files() RETURNS trigger AS $files_trigger$
		BEGIN
			EXEXUTE ''INSERT INTO ' || quote_ident(user_name) || '.files_'' || NEW.campaign_id || '' (id, campaign_id, name, date, file)
				VALUES ('' || quote_literal(nextval(''' || quote_ident(user_name) || '.files_id_seq''::regclass)) || '', '' || quote_literal(NEW.campaign_id) || '',
					'' || quote_literal(NEW.name) || '', '' || quote_literal(NEW.date) || '', '' || quote_literal(NEW.file) || '')'';
			RETURN NULL;
		END;
		$files_trigger$ LANGUAGE plpgsql SECURITY DEFINER;

		CREATE TRIGGER files_trigger
		BEFORE INSERT ON ' || quote_ident(user_name) || '.files
		FOR EACH ROW EXECUTE PROCEDURE ' || quote_ident(user_name) || '.files()';

	EXECUTE 'ALTER FUNCTION ' || quote_ident(user_name) || '.files() OWNER TO rrr';
	EXECUTE 'REVOKE ALL ON FUNCTION ' || quote_ident(user_name) || '.files() FROM PUBLIC';
	EXECUTE 'GRANT EXECUTE ON FUNCTION ' || quote_ident(user_name) || '.files() TO ' || quote_ident(user_name);

	EXECUTE 'CREATE FUNCTION ' || quote_ident(user_name) || '.parameters() RETURNS trigger AS $parameters_trigger$
		BEGIN
			IF NEW.type_bool THEN
				EXEXUTE ''INSERT INTO ' || quote_ident(user_name) || '.parameters_'' || NEW.campaign_id || '' (id, campaign_id, scenario_id, parameter_type, parameter_name, type_bool, type_integer, type_float, type_string)
					VALUES ('' || quote_literal(nextval(''' || quote_ident(user_name) || '.parameters_id_seq''::regclass)) || '', '' || quote_literal(NEW.campaign_id) || '',
						'' || quote_literal(NEW.scenario_id) || '', '' || quote_literal(NEW.parameter_type) || '', '' || quote_literal(NEW.parameter_name) || '',
						TRUE, '' || NEW.type_integer || '', '' || NEW.type_float || '', '' || quote_literal(NEW.type_string) || '')'';
			ELSE
				EXEXUTE ''INSERT INTO ' || quote_ident(user_name) || '.parameters_'' || NEW.campaign_id || '' (id, campaign_id, scenario_id, parameter_type, parameter_name, type_bool, type_integer, type_float, type_string)
					VALUES ('' || quote_literal(nextval(''' || quote_ident(user_name) || '.parameters_id_seq''::regclass)) || '', '' || quote_literal(NEW.campaign_id) || '',
						'' || quote_literal(NEW.scenario_id) || '', '' || quote_literal(NEW.parameter_type) || '', '' || quote_literal(NEW.parameter_name) || '',
						FALSE, '' || NEW.type_integer || '', '' || NEW.type_float || '', '' || quote_literal(NEW.type_string) || '')'';
			END IF;
			RETURN NULL;
		END;
		$parameters_trigger$ LANGUAGE plpgsql SECURITY DEFINER;

		CREATE TRIGGER parameters_trigger
		BEFORE INSERT ON ' || quote_ident(user_name) || '.parameters
		FOR EACH ROW EXECUTE PROCEDURE ' || quote_ident(user_name) || '.parameters()';

	EXECUTE 'ALTER FUNCTION ' || quote_ident(user_name) || '.parameters() OWNER TO rrr';
	EXECUTE 'REVOKE ALL ON FUNCTION ' || quote_ident(user_name) || '.parameters() FROM PUBLIC';
	EXECUTE 'GRANT EXECUTE ON FUNCTION ' || quote_ident(user_name) || '.parameters() TO ' || quote_ident(user_name);

	EXECUTE 'CREATE FUNCTION ' || quote_ident(user_name) || '.jobs() RETURNS trigger AS $jobs_trigger$
		BEGIN
			EXEXUTE ''INSERT INTO ' || quote_ident(user_name) || '.jobs_'' || NEW.campaign_id || '' (id, campaign_id, scenario_id, sge_job_id, queue_date, start_date, stop_date, hostname, stdout, stderr)
				VALUES ('' || quote_literal(nextval(''' || quote_ident(user_name) || '.jobs_id_seq''::regclass)) || '', '' || quote_literal(NEW.campaign_id) || '',
					'' || quote_literal(NEW.scenario_id) || '', '' || quote_literal(NEW.sge_job_id) || '', '' || quote_literal(NEW.queue_date) || '',
					'' || quote_literal(NEW.start_date) || '', '' || quote_literal(NEW.stop_date) || '', '' || quote_literal(NEW.hostname) || '',
					'' || quote_literal(NEW.stdout) || '', '' || quote_literal(NEW.stderr) || '')'';
			EXEXUTE ''UPDATE ' || quote_ident(user_name) || '.scenarios SET current_job_id = '' || NEW.sge_job_id || '' WHERE id = '' || NEW.scenario_id || '' AND campaign_id = '' || NEW.campaign_id;
			RETURN NULL;
		END;
		$jobs_trigger$ LANGUAGE plpgsql SECURITY DEFINER;

		CREATE TRIGGER jobs_trigger
		BEFORE INSERT ON ' || quote_ident(user_name) || '.jobs
		FOR EACH ROW EXECUTE PROCEDURE ' || quote_ident(user_name) || '.jobs()';

	EXECUTE 'ALTER FUNCTION ' || quote_ident(user_name) || '.jobs() OWNER TO rrr';
	EXECUTE 'REVOKE ALL ON FUNCTION ' || quote_ident(user_name) || '.jobs() FROM PUBLIC';
	EXECUTE 'GRANT EXECUTE ON FUNCTION ' || quote_ident(user_name) || '.jobs() TO ' || quote_ident(user_name);

	EXECUTE 'CREATE FUNCTION ' || quote_ident(user_name) || '.pd_fs() RETURNS trigger AS $pd_fs_trigger$
		BEGIN
			EXEXUTE ''INSERT INTO ' || quote_ident(user_name) || '.pd_fs_'' || NEW.campaign_id || '' (id, campaign_id, scenario_id, skewness, description, moment3,
					moment2, standard_deviation, relative_standard_deviation, minimum, alt_name, relative_variance, name, trials, maximum, filename, variance,
					sum_of_all_values, sum_of_all_values_square, sum_of_all_values_cubic, mean, p01, p05, p50, p95, p99, min_x, max_x, number_of_bins, underflows, overflows)
				VALUES ('' || quote_literal(nextval(''' || quote_ident(user_name) || '.pd_fs_id_seq''::regclass)) || '', '' || quote_literal(NEW.campaign_id) || '',
					'' || quote_literal(NEW.scenario_id) || '', '' || quote_literal(NEW.skewness) || '', '' || quote_literal(NEW.description) || '', '' || quote_literal(NEW.moment3) || '',
					'' || quote_literal(NEW.moment2) || '', '' || quote_literal(NEW.standard_deviation) || '', '' || quote_literal(NEW.relative_standard_deviation) || '',
					'' || quote_literal(NEW.minimum) || '', '' || quote_literal(NEW.alt_name) || '', '' || quote_literal(NEW.relative_variance) || '', '' || quote_literal(NEW.name) || '',
					'' || quote_literal(NEW.trials) || '', '' || quote_literal(NEW.maximum) || '', '' || quote_literal(NEW.filename) || '', '' || quote_literal(NEW.variance) || '',
					'' || quote_literal(NEW.sum_of_all_values) || '', '' || quote_literal(NEW.sum_of_all_values_square) || '', '' || quote_literal(NEW.sum_of_all_values_cubic) || '',
					'' || quote_literal(NEW.mean) || '', '' || quote_literal(NEW.p01) || '', '' || quote_literal(NEW.p05) || '', '' || quote_literal(NEW.p50) || '',
					'' || quote_literal(NEW.p95) || '', '' || quote_literal(NEW.p99) || '', '' || quote_literal(NEW.min_x) || '', '' || quote_literal(NEW.max_x) || '',
					'' || quote_literal(NEW.number_of_bins) || '', '' || quote_literal(NEW.underflows) || '', '' || quote_literal(NEW.overflows) || '')'';
			RETURN NULL;
		END;
		$pd_fs_trigger$ LANGUAGE plpgsql SECURITY DEFINER;

		CREATE TRIGGER pd_fs_trigger
		BEFORE INSERT ON ' || quote_ident(user_name) || '.pd_fs
		FOR EACH ROW EXECUTE PROCEDURE ' || quote_ident(user_name) || '.pd_fs()';

	EXECUTE 'ALTER FUNCTION ' || quote_ident(user_name) || '.pd_fs() OWNER TO rrr';
	EXECUTE 'REVOKE ALL ON FUNCTION ' || quote_ident(user_name) || '.pd_fs() FROM PUBLIC';
	EXECUTE 'GRANT EXECUTE ON FUNCTION ' || quote_ident(user_name) || '.pd_fs() TO ' || quote_ident(user_name);

	EXECUTE 'CREATE FUNCTION ' || quote_ident(user_name) || '.pdf_histograms() RETURNS trigger AS $pdf_histograms_trigger$
		BEGIN
			EXEXUTE ''INSERT INTO ' || quote_ident(user_name) || '.pdf_histograms_'' || NEW.campaign_id || '' (id, probe_id, x, cdf, ccdf, pdf)
				VALUES ('' || quote_literal(nextval(''' || quote_ident(user_name) || '.pdf_histograms_id_seq''::regclass)) || '', '' || quote_literal(NEW.probe_id) || '',
					'' || quote_literal(NEW.x) || '', '' || quote_literal(NEW.cdf) || '', '' || quote_literal(NEW.ccdf) || '', '' || quote_literal(NEW.pdf) || '')'';
			RETURN NULL;
		END;
		$pdf_histograms_trigger$ LANGUAGE plpgsql SECURITY DEFINER;

		CREATE TRIGGER pdf_histograms_trigger
		BEFORE INSERT ON ' || quote_ident(user_name) || '.pdf_histograms
		FOR EACH ROW EXECUTE PROCEDURE ' || quote_ident(user_name) || '.pdf_histograms()';

	EXECUTE 'ALTER FUNCTION ' || quote_ident(user_name) || '.pdf_histograms() OWNER TO rrr';
	EXECUTE 'REVOKE ALL ON FUNCTION ' || quote_ident(user_name) || '.pdf_histograms() FROM PUBLIC';
	EXECUTE 'GRANT EXECUTE ON FUNCTION ' || quote_ident(user_name) || '.pdf_histograms() TO ' || quote_ident(user_name);

	EXECUTE 'CREATE FUNCTION ' || quote_ident(user_name) || '.log_evals() RETURNS trigger AS $log_evals_trigger$
		BEGIN
			EXEXUTE ''INSERT INTO ' || quote_ident(user_name) || '.log_evals_'' || NEW.campaign_id || '' (id, campaign_id, scenario_id, skewness, description, moment3,
					moment2, standard_deviation, relative_standard_deviation, minimum, alt_name, relative_variance, name, trials, maximum, filename, variance,
					sum_of_all_values, sum_of_all_values_square, sum_of_all_values_cubic, mean)
				VALUES ('' || quote_literal(nextval(''' || quote_ident(user_name) || '.log_evals_id_seq''::regclass)) || '', '' || quote_literal(NEW.campaign_id) || '',
					'' || quote_literal(NEW.scenario_id) || '', '' || quote_literal(NEW.skewness) || '', '' || quote_literal(NEW.description) || '', '' || quote_literal(NEW.moment3) || '',
					'' || quote_literal(NEW.moment2) || '', '' || quote_literal(NEW.standard_deviation) || '', '' || quote_literal(NEW.relative_standard_deviation) || '',
					'' || quote_literal(NEW.minimum) || '', '' || quote_literal(NEW.alt_name) || '', '' || quote_literal(NEW.relative_variance) || '', '' || quote_literal(NEW.name) || '',
					'' || quote_literal(NEW.trials) || '', '' || quote_literal(NEW.maximum) || '', '' || quote_literal(NEW.filename) || '', '' || quote_literal(NEW.variance) || '',
					'' || quote_literal(NEW.sum_of_all_values) || '', '' || quote_literal(NEW.sum_of_all_values_square) || '', '' || quote_literal(NEW.sum_of_all_values_cubic) || '',
					'' || quote_literal(NEW.mean) || '')'';
			RETURN NULL;
		END;
		$log_evals_trigger$ LANGUAGE plpgsql SECURITY DEFINER;

		CREATE TRIGGER log_evals_trigger
		BEFORE INSERT ON ' || quote_ident(user_name) || '.log_evals
		FOR EACH ROW EXECUTE PROCEDURE ' || quote_ident(user_name) || '.log_evals()';

	EXECUTE 'ALTER FUNCTION ' || quote_ident(user_name) || '.log_evals() OWNER TO rrr';
	EXECUTE 'REVOKE ALL ON FUNCTION ' || quote_ident(user_name) || '.log_evals() FROM PUBLIC';
	EXECUTE 'GRANT EXECUTE ON FUNCTION ' || quote_ident(user_name) || '.log_evals() TO ' || quote_ident(user_name);

	EXECUTE 'CREATE FUNCTION ' || quote_ident(user_name) || '.log_eval_entries() RETURNS trigger AS $log_eval_entries_trigger$
		BEGIN
			EXEXUTE ''INSERT INTO ' || quote_ident(user_name) || '.log_eval_entries_'' || NEW.campaign_id || '' (id, probe_id, x, y)
				VALUES ('' || quote_literal(nextval(''' || quote_ident(user_name) || '.log_eval_entries_id_seq''::regclass)) || '', '' || quote_literal(NEW.probe_id) || '',
					'' || quote_literal(NEW.x) || '', '' || quote_literal(NEW.y) || '')'';
			RETURN NULL;
		END;
		$log_eval_entries_trigger$ LANGUAGE plpgsql SECURITY DEFINER;

		CREATE TRIGGER log_eval_entries_trigger
		BEFORE INSERT ON ' || quote_ident(user_name) || '.log_eval_entries
		FOR EACH ROW EXECUTE PROCEDURE ' || quote_ident(user_name) || '.log_eval_entries()';

	EXECUTE 'ALTER FUNCTION ' || quote_ident(user_name) || '.log_eval_entries() OWNER TO rrr';
	EXECUTE 'REVOKE ALL ON FUNCTION ' || quote_ident(user_name) || '.log_eval_entries() FROM PUBLIC';
	EXECUTE 'GRANT EXECUTE ON FUNCTION ' || quote_ident(user_name) || '.log_eval_entries() TO ' || quote_ident(user_name);

	EXECUTE 'CREATE FUNCTION ' || quote_ident(user_name) || '.moments() RETURNS trigger AS $moments_trigger$
		BEGIN
			EXEXUTE ''INSERT INTO ' || quote_ident(user_name) || '.moments_'' || NEW.campaign_id || '' (id, campaign_id, scenario_id, skewness, description, moment3,
					moment2, standard_deviation, relative_standard_deviation, minimum, alt_name, relative_variance, name, trials, maximum, filename, variance,
					sum_of_all_values, sum_of_all_values_square, sum_of_all_values_cubic, mean)
				VALUES ('' || quote_literal(nextval(''' || quote_ident(user_name) || '.moments_id_seq''::regclass)) || '', '' || quote_literal(NEW.campaign_id) || '',
					'' || quote_literal(NEW.scenario_id) || '', '' || quote_literal(NEW.skewness) || '', '' || quote_literal(NEW.description) || '', '' || quote_literal(NEW.moment3) || '',
					'' || quote_literal(NEW.moment2) || '', '' || quote_literal(NEW.standard_deviation) || '', '' || quote_literal(NEW.relative_standard_deviation) || '',
					'' || quote_literal(NEW.minimum) || '', '' || quote_literal(NEW.alt_name) || '', '' || quote_literal(NEW.relative_variance) || '', '' || quote_literal(NEW.name) || '',
					'' || quote_literal(NEW.trials) || '', '' || quote_literal(NEW.maximum) || '', '' || quote_literal(NEW.filename) || '', '' || quote_literal(NEW.variance) || '',
					'' || quote_literal(NEW.sum_of_all_values) || '', '' || quote_literal(NEW.sum_of_all_values_square) || '', '' || quote_literal(NEW.sum_of_all_values_cubic) || '',
					'' || quote_literal(NEW.mean) || '')'';
			RETURN NULL;
		END;
		$moments_trigger$ LANGUAGE plpgsql SECURITY DEFINER;

		CREATE TRIGGER moments_trigger
		BEFORE INSERT ON ' || quote_ident(user_name) || '.moments
		FOR EACH ROW EXECUTE PROCEDURE ' || quote_ident(user_name) || '.moments()';

	EXECUTE 'ALTER FUNCTION ' || quote_ident(user_name) || '.moments() OWNER TO rrr';
	EXECUTE 'REVOKE ALL ON FUNCTION ' || quote_ident(user_name) || '.moments() FROM PUBLIC';
	EXECUTE 'GRANT EXECUTE ON FUNCTION ' || quote_ident(user_name) || '.moments() TO ' || quote_ident(user_name);

	EXECUTE 'CREATE FUNCTION ' || quote_ident(user_name) || '.batch_means() RETURNS trigger AS $batch_means_trigger$
		BEGIN
			EXEXUTE ''INSERT INTO ' || quote_ident(user_name) || '.batch_means_'' || NEW.campaign_id || '' (id, campaign_id, scenario_id, skewness, description, moment3,
					moment2, standard_deviation, relative_standard_deviation, minimum, alt_name, relative_variance, name, trials, maximum, filename, variance,
					sum_of_all_values, sum_of_all_values_square, sum_of_all_values_cubic, mean,
					lower_border, upper_border, number_of_intervals, interval_size, size_of_groups, maximum_relative_error, evaluated_groups, underflows, overflows,
					mean_bm, confidence_of_mean_absolute, confidence_of_mean_percent, relative_error_mean, variance_bm, confidence_of_variance_absolute, confidence_of_variance_percent,
					relative_error_variance, sigma, first_order_correlation_coefficient)
				VALUES ('' || quote_literal(nextval(''' || quote_ident(user_name) || '.batch_means_id_seq''::regclass)) || '', '' || quote_literal(NEW.campaign_id) || '',
					'' || quote_literal(NEW.scenario_id) || '', '' || quote_literal(NEW.skewness) || '', '' || quote_literal(NEW.description) || '', '' || quote_literal(NEW.moment3) || '',
					'' || quote_literal(NEW.moment2) || '', '' || quote_literal(NEW.standard_deviation) || '', '' || quote_literal(NEW.relative_standard_deviation) || '',
					'' || quote_literal(NEW.minimum) || '', '' || quote_literal(NEW.alt_name) || '', '' || quote_literal(NEW.relative_variance) || '', '' || quote_literal(NEW.name) || '',
					'' || quote_literal(NEW.trials) || '', '' || quote_literal(NEW.maximum) || '', '' || quote_literal(NEW.filename) || '', '' || quote_literal(NEW.variance) || '',
					'' || quote_literal(NEW.sum_of_all_values) || '', '' || quote_literal(NEW.sum_of_all_values_square) || '',
					'' || quote_literal(NEW.sum_of_all_values_cubic) || '',	'' || quote_literal(NEW.mean) || '', '' || quote_literal(NEW.lower_border) || '',
					'' || quote_literal(NEW.upper_border) || '', '' || quote_literal(NEW.number_of_intervals) || '', '' || quote_literal(NEW.interval_size) || '',
					'' || quote_literal(NEW.size_of_groups) || '', '' || quote_literal(NEW.maximum_relative_error) || '', '' || quote_literal(NEW.evaluated_groups) || '',
					'' || quote_literal(NEW.underflows) || '', '' || quote_literal(NEW.overflows) || '', '' || quote_literal(NEW.mean_bm) || '', '' || quote_literal(NEW.confidence_of_mean_absolute) || '',
					'' || quote_literal(NEW.confidence_of_mean_percent) || '', '' || quote_literal(NEW.relative_error_mean) || '', '' || quote_literal(NEW.variance_bm) || '',
					'' || quote_literal(NEW.confidence_of_variance_absolute) || '', '' || quote_literal(NEW.confidence_of_variance_percent) || '', '' || quote_literal(NEW.relative_error_variance) || '',
					'' || quote_literal(NEW.sigma) || '', '' || quote_literal(NEW.first_order_correlation_coefficient) || '')'';
			RETURN NULL;
		END;
		$batch_means_trigger$ LANGUAGE plpgsql SECURITY DEFINER;

		CREATE TRIGGER batch_means_trigger
		BEFORE INSERT ON ' || quote_ident(user_name) || '.batch_means
		FOR EACH ROW EXECUTE PROCEDURE ' || quote_ident(user_name) || '.batch_means()';

	EXECUTE 'ALTER FUNCTION ' || quote_ident(user_name) || '.batch_means() OWNER TO rrr';
	EXECUTE 'REVOKE ALL ON FUNCTION ' || quote_ident(user_name) || '.batch_means() FROM PUBLIC';
	EXECUTE 'GRANT EXECUTE ON FUNCTION ' || quote_ident(user_name) || '.batch_means() TO ' || quote_ident(user_name);

	EXECUTE 'CREATE FUNCTION ' || quote_ident(user_name) || '.batch_means_histograms() RETURNS trigger AS $batch_means_histograms_trigger$
		BEGIN
			EXEXUTE ''INSERT INTO ' || quote_ident(user_name) || '.batch_means_histograms_'' || NEW.campaign_id || '' (id, probe_id, x, cdf, pdf, relative_error, confidence, number_of_trials_per_interval)
				VALUES ('' || quote_literal(nextval(''' || quote_ident(user_name) || '.batch_means_histograms_id_seq''::regclass)) || '', '' || quote_literal(NEW.probe_id) || '',
					'' || quote_literal(NEW.x) || '', '' || quote_literal(NEW.cdf) || '', '' || quote_literal(NEW.pdf) || '', '' || quote_literal(NEW.relative_error) || '',
					'' || quote_literal(NEW.confidence) || '', '' || quote_literal(NEW.number_of_trials_per_interval) || '')'';
			RETURN NULL;
		END;
		$batch_means_histograms_trigger$ LANGUAGE plpgsql SECURITY DEFINER;

		CREATE TRIGGER batch_means_histograms_trigger
		BEFORE INSERT ON ' || quote_ident(user_name) || '.batch_means_histograms
		FOR EACH ROW EXECUTE PROCEDURE ' || quote_ident(user_name) || '.batch_means_histograms()';

	EXECUTE 'ALTER FUNCTION ' || quote_ident(user_name) || '.batch_means_histograms() OWNER TO rrr';
	EXECUTE 'REVOKE ALL ON FUNCTION ' || quote_ident(user_name) || '.batch_means_histograms() FROM PUBLIC';
	EXECUTE 'GRANT EXECUTE ON FUNCTION ' || quote_ident(user_name) || '.batch_means_histograms() TO ' || quote_ident(user_name);

	EXECUTE 'CREATE FUNCTION ' || quote_ident(user_name) || '.lres() RETURNS trigger AS $lres_trigger$
		BEGIN
			EXEXUTE ''INSERT INTO ' || quote_ident(user_name) || '.lres_'' || NEW.campaign_id || '' (id, campaign_id, scenario_id, skewness, description, moment3,
					moment2, standard_deviation, relative_standard_deviation, minimum, alt_name, relative_variance, name, trials, maximum, filename, variance,
					sum_of_all_values, sum_of_all_values_square, sum_of_all_values_cubic, mean,
					lre_type, maximum_relative_error, f_max, f_min, scaling, maximum_number_of_trials_per_level, rho_n60, rho_n50, rho_n40, rho_n30, rho_n20, rho_n10, rho_00,
					rho_p25, rho_p50, rho_p75, rho_p90, rho_p95, rho_p99, peak_number_of_sorting_elements, level_index, number_of_levels, relative_error_mean,
					relative_error_variance, relative_error_standard_deviation, mean_local_correlation_coefficient_mean, mean_local_correlation_coefficient_variance,
					mean_local_correlation_coefficient_standard_deviation, deviation_from_mean_local_cc_mean, deviation_from_mean_local_cc_variance,
					deviation_from_mean_local_cc_standard_deviation, number_of_trials_per_interval_mean, number_of_trials_per_interval_variance,
					number_of_trials_per_interval_standard_deviation, number_of_transitions_per_interval_mean, number_of_transitions_per_interval_variance,
					number_of_transitions_per_interval_standard_deviation)
				VALUES ('' || quote_literal(nextval(''' || quote_ident(user_name) || '.lres_id_seq''::regclass)) || '', '' || quote_literal(NEW.campaign_id) || '',
					'' || quote_literal(NEW.scenario_id) || '', '' || quote_literal(NEW.skewness) || '', '' || quote_literal(NEW.description) || '', '' || quote_literal(NEW.moment3) || '',
					'' || quote_literal(NEW.moment2) || '', '' || quote_literal(NEW.standard_deviation) || '', '' || quote_literal(NEW.relative_standard_deviation) || '',
					'' || quote_literal(NEW.minimum) || '', '' || quote_literal(NEW.alt_name) || '', '' || quote_literal(NEW.relative_variance) || '', '' || quote_literal(NEW.name) || '',
					'' || quote_literal(NEW.trials) || '', '' || quote_literal(NEW.maximum) || '', '' || quote_literal(NEW.filename) || '', '' || quote_literal(NEW.variance) || '',
					'' || quote_literal(NEW.sum_of_all_values) || '', '' || quote_literal(NEW.sum_of_all_values_square) || '', '' || quote_literal(NEW.sum_of_all_values_cubic) || '',
					'' || quote_literal(NEW.mean) || '', '' || quote_literal(NEW.lre_type) || '', '' || quote_literal(NEW.maximum_relative_error) || '', '' || quote_literal(NEW.f_max) || '',
					'' || quote_literal(NEW.f_min) || '', '' || quote_literal(NEW.scaling) || '', '' || quote_literal(NEW.maximum_number_of_trials_per_level) || '', '' || quote_literal(NEW.rho_n60) || '',
					'' || quote_literal(NEW.rho_n50) || '', '' || quote_literal(NEW.rho_n40) || '', '' || quote_literal(NEW.rho_n30) || '', '' || quote_literal(NEW.rho_n20) || '',
					'' || quote_literal(NEW.rho_n10) || '', '' || quote_literal(NEW.rho_00) || '', '' || quote_literal(NEW.rho_p25) || '', '' || quote_literal(NEW.rho_p50) || '',
					'' || quote_literal(NEW.rho_p75) || '', '' || quote_literal(NEW.rho_p90) || '', '' || quote_literal(NEW.rho_p95) || '', '' || quote_literal(NEW.rho_p99) || '',
					'' || quote_literal(NEW.peak_number_of_sorting_elements) || '', '' || quote_literal(NEW.level_index) || '', '' || quote_literal(NEW.number_of_levels) || '',
					'' || quote_literal(NEW.relative_error_mean) || '', '' || quote_literal(NEW.relative_error_variance) || '',
					'' || quote_literal(NEW.relative_error_standard_deviation) || '', '' || quote_literal(NEW.mean_local_correlation_coefficient_mean) || '', '' || quote_literal(NEW.mean_local_correlation_coefficient_variance) || '',
					'' || quote_literal(NEW.mean_local_correlation_coefficient_standard_deviation) || '', '' || quote_literal(NEW.deviation_from_mean_local_cc_mean) || '',
					'' || quote_literal(NEW.deviation_from_mean_local_cc_variance) || '', '' || quote_literal(NEW.deviation_from_mean_local_cc_standard_deviation) || '',
					'' || quote_literal(NEW.number_of_trials_per_interval_mean) || '', '' || quote_literal(NEW.number_of_trials_per_interval_variance) || '',
					'' || quote_literal(NEW.number_of_trials_per_interval_standard_deviation) || '', '' || quote_literal(NEW.number_of_transitions_per_interval_mean) || '',
					'' || quote_literal(NEW.number_of_transitions_per_interval_variance) || '', '' || quote_literal(NEW.number_of_transitions_per_interval_standard_deviation) || '')'';
			RETURN NULL;
		END;
		$lres_trigger$ LANGUAGE plpgsql SECURITY DEFINER;

		CREATE TRIGGER lres_trigger
		BEFORE INSERT ON ' || quote_ident(user_name) || '.lres
		FOR EACH ROW EXECUTE PROCEDURE ' || quote_ident(user_name) || '.lres()';

	EXECUTE 'ALTER FUNCTION ' || quote_ident(user_name) || '.lres() OWNER TO rrr';
	EXECUTE 'REVOKE ALL ON FUNCTION ' || quote_ident(user_name) || '.lres() FROM PUBLIC';
	EXECUTE 'GRANT EXECUTE ON FUNCTION ' || quote_ident(user_name) || '.lres() TO ' || quote_ident(user_name);

	EXECUTE 'CREATE FUNCTION ' || quote_ident(user_name) || '.lre_histograms() RETURNS trigger AS $lre_histograms_trigger$
		BEGIN
			EXEXUTE ''INSERT INTO ' || quote_ident(user_name) || '.lre_histograms_'' || NEW.campaign_id || '' (id, probe_id, abscissa, ordinate, relative_error, mean_local_correlation_coefficient,
					deviation_from_mean_local_cc, number_of_trials_per_interval, number_of_transitions_per_interval, relative_error_within_limit)
				VALUES ('' || quote_literal(nextval(''' || quote_ident(user_name) || '.lre_histograms_id_seq''::regclass)) || '', '' || quote_literal(NEW.probe_id) || '',
					'' || quote_literal(NEW.abscissa) || '', '' || quote_literal(NEW.ordinate) || '', '' || quote_literal(NEW.relative_error) || '',
					'' || quote_literal(NEW.mean_local_correlation_coefficient) || '', '' || quote_literal(NEW.deviation_from_mean_local_cc) || '',
					'' || quote_literal(NEW.number_of_trials_per_interval) || '', '' || quote_literal(NEW.number_of_transitions_per_interval) || '',
					'' || quote_literal(NEW.relative_error_within_limit) || '')'';
			RETURN NULL;
		END;
		$lre_histograms_trigger$ LANGUAGE plpgsql SECURITY DEFINER;

		CREATE TRIGGER lre_histograms_trigger
		BEFORE INSERT ON ' || quote_ident(user_name) || '.lre_histograms
		FOR EACH ROW EXECUTE PROCEDURE ' || quote_ident(user_name) || '.lre_histograms()';

	EXECUTE 'ALTER FUNCTION ' || quote_ident(user_name) || '.lre_histograms() OWNER TO rrr';
	EXECUTE 'REVOKE ALL ON FUNCTION ' || quote_ident(user_name) || '.lre_histograms() FROM PUBLIC';
	EXECUTE 'GRANT EXECUTE ON FUNCTION ' || quote_ident(user_name) || '.lre_histograms() TO ' || quote_ident(user_name);

	EXECUTE 'CREATE FUNCTION ' || quote_ident(user_name) || '.dlres() RETURNS trigger AS $dlres_trigger$
		BEGIN
			EXEXUTE ''INSERT INTO ' || quote_ident(user_name) || '.dlres_'' || NEW.campaign_id || '' (id, campaign_id, scenario_id, skewness, description, moment3,
					moment2, standard_deviation, relative_standard_deviation, minimum, alt_name, relative_variance, name, trials, maximum, filename, variance,
					sum_of_all_values, sum_of_all_values_square, sum_of_all_values_cubic, mean,
					dlre_type, lower_border, upper_border, number_of_intervals, interval_size, maximum_number_of_samples, maximum_relative_error_percent, evaluated_levels,
					underflows, overflows)
				VALUES ('' || quote_literal(nextval(''' || quote_ident(user_name) || '.dlres_id_seq''::regclass)) || '', '' || quote_literal(NEW.campaign_id) || '',
					'' || quote_literal(NEW.scenario_id) || '', '' || quote_literal(NEW.skewness) || '', '' || quote_literal(NEW.description) || '', '' || quote_literal(NEW.moment3) || '',
					'' || quote_literal(NEW.moment2) || '', '' || quote_literal(NEW.standard_deviation) || '', '' || quote_literal(NEW.relative_standard_deviation) || '',
					'' || quote_literal(NEW.minimum) || '', '' || quote_literal(NEW.alt_name) || '', '' || quote_literal(NEW.relative_variance) || '', '' || quote_literal(NEW.name) || '',
					'' || quote_literal(NEW.trials) || '', '' || quote_literal(NEW.maximum) || '', '' || quote_literal(NEW.filename) || '', '' || quote_literal(NEW.variance) || '',
					'' || quote_literal(NEW.sum_of_all_values) || '', '' || quote_literal(NEW.sum_of_all_values_square) || '', '' || quote_literal(NEW.sum_of_all_values_cubic) || '',
					'' || quote_literal(NEW.mean) || '', '' || quote_literal(NEW.dlre_type) || '', '' || quote_literal(NEW.lower_border) || '', '' || quote_literal(NEW.upper_border) || '',
					'' || quote_literal(NEW.number_of_intervals) || '', '' || quote_literal(NEW.interval_size) || '', '' || quote_literal(NEW.maximum_number_of_samples) || '',
					'' || quote_literal(NEW.maximum_relative_error_percent) || '', '' || quote_literal(NEW.evaluated_levels) || '', '' || quote_literal(NEW.underflows) || '',
					'' || quote_literal(NEW.overflows) || '')'';
			RETURN NULL;
		END;
		$dlres_trigger$ LANGUAGE plpgsql SECURITY DEFINER;

		CREATE TRIGGER dlres_trigger
		BEFORE INSERT ON ' || quote_ident(user_name) || '.dlres
		FOR EACH ROW EXECUTE PROCEDURE ' || quote_ident(user_name) || '.dlres()';

	EXECUTE 'ALTER FUNCTION ' || quote_ident(user_name) || '.dlres() OWNER TO rrr';
	EXECUTE 'REVOKE ALL ON FUNCTION ' || quote_ident(user_name) || '.dlres() FROM PUBLIC';
	EXECUTE 'GRANT EXECUTE ON FUNCTION ' || quote_ident(user_name) || '.dlres() TO ' || quote_ident(user_name);

	EXECUTE 'CREATE FUNCTION ' || quote_ident(user_name) || '.dlre_histograms() RETURNS trigger AS $dlre_histograms_trigger$
		BEGIN
			EXEXUTE ''INSERT INTO ' || quote_ident(user_name) || '.dlre_histograms_'' || NEW.campaign_id || '' (id, probe_id, abscissa, ordinate, relative_error, mean_local_correlation_coefficient,
					deviation_from_mean_local_cc, number_of_trials_per_interval, number_of_transitions_per_interval, relative_error_within_limit)
				VALUES ('' || quote_literal(nextval(''' || quote_ident(user_name) || '.lre_histograms_id_seq''::regclass)) || '', '' || quote_literal(NEW.probe_id) || '',
					'' || quote_literal(NEW.abscissa) || '', '' || quote_literal(NEW.ordinate) || '', '' || quote_literal(NEW.relative_error) || '',
					'' || quote_literal(NEW.mean_local_correlation_coefficient) || '', '' || quote_literal(NEW.deviation_from_mean_local_cc) || '',
					'' || quote_literal(NEW.number_of_trials_per_interval) || '', '' || quote_literal(NEW.number_of_transitions_per_interval) || '',
					'' || quote_literal(NEW.relative_error_within_limit) || '')'';
			RETURN NULL;
		END;
		$dlre_histograms_trigger$ LANGUAGE plpgsql SECURITY DEFINER;

		CREATE TRIGGER dlre_histograms_trigger
		BEFORE INSERT ON ' || quote_ident(user_name) || '.dlre_histograms
		FOR EACH ROW EXECUTE PROCEDURE ' || quote_ident(user_name) || '.dlre_histograms()';

	EXECUTE 'ALTER FUNCTION ' || quote_ident(user_name) || '.dlre_histograms() OWNER TO rrr';
	EXECUTE 'REVOKE ALL ON FUNCTION ' || quote_ident(user_name) || '.dlre_histograms() FROM PUBLIC';
	EXECUTE 'GRANT EXECUTE ON FUNCTION ' || quote_ident(user_name) || '.dlre_histograms() TO ' || quote_ident(user_name);

	EXECUTE 'CREATE FUNCTION ' || quote_ident(user_name) || '.tables() RETURNS trigger AS $tables_trigger$
		BEGIN
			EXEXUTE ''INSERT INTO ' || quote_ident(user_name) || '.tables_'' || NEW.campaign_id || '' (id, campaign_id, scenario_id, filename, name, type,
					first_col_type, first_col_description, second_col_type, second_col_description, description, minimum, maximum)
				VALUES ('' || quote_literal(nextval(''' || quote_ident(user_name) || '.tables_id_seq''::regclass)) || '', '' || quote_literal(NEW.campaign_id) || '',
					'' || quote_literal(NEW.scenario_id) || '', '' || quote_literal(NEW.filename) || '', '' || quote_literal(NEW.name) || '', '' || quote_literal(NEW.type) || '',
					'' || quote_literal(NEW.first_col_type) || '', '' || quote_literal(NEW.first_col_description) || '',
					'' || quote_literal(NEW.second_col_type) || '', '' || quote_literal(NEW.second_col_description) || '', '' || quote_literal(NEW.description) || '',
					'' || quote_literal(NEW.minimum) || '', '' || quote_literal(NEW.maximum) || '')'';
			RETURN NULL;
		END;
		$tables_trigger$ LANGUAGE plpgsql SECURITY DEFINER;

		CREATE TRIGGER tables_trigger
		BEFORE INSERT ON ' || quote_ident(user_name) || '.tables
		FOR EACH ROW EXECUTE PROCEDURE ' || quote_ident(user_name) || '.tables()';

	EXECUTE 'ALTER FUNCTION ' || quote_ident(user_name) || '.tables() OWNER TO rrr';
	EXECUTE 'REVOKE ALL ON FUNCTION ' || quote_ident(user_name) || '.tables() FROM PUBLIC';
	EXECUTE 'GRANT EXECUTE ON FUNCTION ' || quote_ident(user_name) || '.tables() TO ' || quote_ident(user_name);

	EXECUTE 'CREATE FUNCTION ' || quote_ident(user_name) || '.table_rows() RETURNS trigger AS $table_rows_trigger$
		BEGIN
			EXEXUTE ''INSERT INTO ' || quote_ident(user_name) || '.table_rows_'' || NEW.campaign_id || '' (id, probe_id, first_col, second_col, value)
				VALUES ('' || quote_literal(nextval(''' || quote_ident(user_name) || '.table_rows_id_seq''::regclass)) || '', '' || quote_literal(NEW.probe_id) || '',
					'' || quote_literal(NEW.first_col) || '', '' || quote_literal(NEW.second_col) || '', '' || quote_literal(NEW.value) || '')'';
			RETURN NULL;
		END;
		$table_rows_trigger$ LANGUAGE plpgsql SECURITY DEFINER;

		CREATE TRIGGER table_rows_trigger
		BEFORE INSERT ON ' || quote_ident(user_name) || '.table_rows
		FOR EACH ROW EXECUTE PROCEDURE ' || quote_ident(user_name) || '.table_rows()';

	EXECUTE 'ALTER FUNCTION ' || quote_ident(user_name) || '.table_rows() OWNER TO rrr';
	EXECUTE 'REVOKE ALL ON FUNCTION ' || quote_ident(user_name) || '.table_rows() FROM PUBLIC';
	EXECUTE 'GRANT EXECUTE ON FUNCTION ' || quote_ident(user_name) || '.table_rows() TO ' || quote_ident(user_name);

	EXECUTE 'CREATE FUNCTION ' || quote_ident(user_name) || '.show_all_campaigns() RETURNS VOID AS $show_all_campaigns_function$
		BEGIN
			CREATE TEMPORARY VIEW campaigns AS SELECT * FROM administration.campaigns;
			CREATE TEMPORARY VIEW authorizations AS SELECT * FROM administration.authorizations;
		END;
		$show_all_campaigns_function$ LANGUAGE plpgsql';

	EXECUTE 'ALTER FUNCTION ' || quote_ident(user_name) || '.show_all_campaigns() OWNER TO rrr';
	EXECUTE 'REVOKE ALL ON FUNCTION ' || quote_ident(user_name) || '.show_all_campaigns() FROM PUBLIC';
	EXECUTE 'GRANT EXECUTE ON FUNCTION ' || quote_ident(user_name) || '.show_all_campaigns() TO ' || quote_ident(user_name);

	EXECUTE 'CREATE FUNCTION ' || quote_ident(user_name) || '.show_own_campaigns() RETURNS VOID AS $show_own_campaigns_function$
		BEGIN
			DROP VIEW campaigns;
			DROP VIEW authorizations;
		END;
		$show_own_campaigns_function$ LANGUAGE plpgsql';

	EXECUTE 'ALTER FUNCTION ' || quote_ident(user_name) || '.show_own_campaigns() OWNER TO rrr';
	EXECUTE 'REVOKE ALL ON FUNCTION ' || quote_ident(user_name) || '.show_own_campaigns() FROM PUBLIC';
	EXECUTE 'GRANT EXECUTE ON FUNCTION ' || quote_ident(user_name) || '.show_own_campaigns() TO ' || quote_ident(user_name);

	EXECUTE 'CREATE FUNCTION ' || quote_ident(user_name) || '.view_campaigns(arr_campaigns integer[]) RETURNS void AS $view_campaigns_function$
		DECLARE
			statement text;
			other_user text;

			parameter_name text;
			statement_select text;
			statement_from text;
			statement_where1 text;
			statement_where2 text;
			parameters_record RECORD;
		BEGIN
			EXEXUTE ''SELECT user_name FROM administration.users INNER JOIN administration.campaigns ON users.id = campaigns.user_id
					 WHERE campaigns.id = '' || arr_campaigns[1] INTO other_user;
			statement := ''SELECT * FROM '' || other_user || ''.scenarios_'' || arr_campaigns[1];
			FOR campaign IN array_lower(arr_campaigns, 1)+1..array_upper(arr_campaigns, 1) LOOP
				EXEXUTE ''SELECT user_name FROM administration.users INNER JOIN administration.campaigns ON users.id = campaigns.user_id
						 WHERE campaigns.id = '' || arr_campaigns[campaign] INTO other_user;
				statement := statement || '' UNION ALL SELECT * FROM '' || other_user || ''.scenarios_'' || arr_campaigns[campaign];
			END LOOP;
			EXEXUTE ''CREATE OR REPLACE TEMPORARY VIEW scenarios AS '' || statement;


			EXEXUTE ''SELECT user_name FROM administration.users INNER JOIN administration.campaigns ON users.id = campaigns.user_id
					 WHERE campaigns.id = '' || arr_campaigns[1] INTO other_user;
			statement := ''SELECT * FROM '' || other_user || ''.files_'' || arr_campaigns[1];
			FOR campaign IN array_lower(arr_campaigns, 1)+1..array_upper(arr_campaigns, 1) LOOP
				EXEXUTE ''SELECT user_name FROM administration.users INNER JOIN administration.campaigns ON users.id = campaigns.user_id
						 WHERE campaigns.id = '' || arr_campaigns[campaign] INTO other_user;
				statement := statement || '' UNION ALL SELECT * FROM '' || other_user || ''.files_'' || arr_campaigns[campaign];
			END LOOP;
			EXEXUTE ''CREATE OR REPLACE TEMPORARY VIEW files AS '' || statement;


			EXEXUTE ''SELECT user_name FROM administration.users INNER JOIN administration.campaigns ON users.id = campaigns.user_id
					 WHERE campaigns.id = '' || arr_campaigns[1] INTO other_user;
			statement := ''SELECT * FROM '' || other_user || ''.parameters_'' || arr_campaigns[1];
			FOR campaign IN array_lower(arr_campaigns, 1)+1..array_upper(arr_campaigns, 1) LOOP
				EXEXUTE ''SELECT user_name FROM administration.users INNER JOIN administration.campaigns ON users.id = campaigns.user_id
						 WHERE campaigns.id = '' || arr_campaigns[campaign] INTO other_user;
				statement := statement || '' UNION ALL SELECT * FROM '' || other_user || ''.parameters_'' || arr_campaigns[campaign];
			END LOOP;
			EXEXUTE ''CREATE OR REPLACE TEMPORARY VIEW parameters AS '' || statement;


			EXEXUTE ''SELECT user_name FROM administration.users INNER JOIN administration.campaigns ON users.id = campaigns.user_id
					 WHERE campaigns.id = '' || arr_campaigns[1] INTO other_user;
			statement := ''SELECT * FROM '' || other_user || ''.jobs_'' || arr_campaigns[1];
			FOR campaign IN array_lower(arr_campaigns, 1)+1..array_upper(arr_campaigns, 1) LOOP
				EXEXUTE ''SELECT user_name FROM administration.users INNER JOIN administration.campaigns ON users.id = campaigns.user_id
						 WHERE campaigns.id = '' || arr_campaigns[campaign] INTO other_user;
				statement := statement || '' UNION ALL SELECT * FROM '' || other_user || ''.jobs_'' || arr_campaigns[campaign];
			END LOOP;
			EXEXUTE ''CREATE OR REPLACE TEMPORARY VIEW jobs AS '' || statement;


			EXEXUTE ''SELECT user_name FROM administration.users INNER JOIN administration.campaigns ON users.id = campaigns.user_id
					 WHERE campaigns.id = '' || arr_campaigns[1] INTO other_user;
			statement := ''SELECT * FROM '' || other_user || ''.pd_fs_'' || arr_campaigns[1];
			FOR campaign IN array_lower(arr_campaigns, 1)+1..array_upper(arr_campaigns, 1) LOOP
				EXEXUTE ''SELECT user_name FROM administration.users INNER JOIN administration.campaigns ON users.id = campaigns.user_id
						 WHERE campaigns.id = '' || arr_campaigns[campaign] INTO other_user;
				statement := statement || '' UNION ALL SELECT * FROM '' || other_user || ''.pd_fs_'' || arr_campaigns[campaign];
			END LOOP;
			EXEXUTE ''CREATE OR REPLACE TEMPORARY VIEW pd_fs AS '' || statement;


			EXEXUTE ''SELECT user_name FROM administration.users INNER JOIN administration.campaigns ON users.id = campaigns.user_id
					 WHERE campaigns.id = '' || arr_campaigns[1] INTO other_user;
			statement := ''SELECT * FROM '' || other_user || ''.pdf_histograms_'' || arr_campaigns[1];
			FOR campaign IN array_lower(arr_campaigns, 1)+1..array_upper(arr_campaigns, 1) LOOP
				EXEXUTE ''SELECT user_name FROM administration.users INNER JOIN administration.campaigns ON users.id = campaigns.user_id
						 WHERE campaigns.id = '' || arr_campaigns[campaign] INTO other_user;
				statement := statement || '' UNION ALL SELECT * FROM '' || other_user || ''.pdf_histograms_'' || arr_campaigns[campaign];
			END LOOP;
			EXEXUTE ''CREATE OR REPLACE TEMPORARY VIEW pdf_histograms AS '' || statement;


			EXEXUTE ''SELECT user_name FROM administration.users INNER JOIN administration.campaigns ON users.id = campaigns.user_id
					 WHERE campaigns.id = '' || arr_campaigns[1] INTO other_user;
			statement := ''SELECT * FROM '' || other_user || ''.log_evals_'' || arr_campaigns[1];
			FOR campaign IN array_lower(arr_campaigns, 1)+1..array_upper(arr_campaigns, 1) LOOP
				EXEXUTE ''SELECT user_name FROM administration.users INNER JOIN administration.campaigns ON users.id = campaigns.user_id
						 WHERE campaigns.id = '' || arr_campaigns[campaign] INTO other_user;
				statement := statement || '' UNION ALL SELECT * FROM '' || other_user || ''.log_evals_'' || arr_campaigns[campaign];
			END LOOP;
			EXEXUTE ''CREATE OR REPLACE TEMPORARY VIEW log_evals AS '' || statement;


			EXEXUTE ''SELECT user_name FROM administration.users INNER JOIN administration.campaigns ON users.id = campaigns.user_id
					 WHERE campaigns.id = '' || arr_campaigns[1] INTO other_user;
			statement := ''SELECT * FROM '' || other_user || ''.log_eval_entries_'' || arr_campaigns[1];
			FOR campaign IN array_lower(arr_campaigns, 1)+1..array_upper(arr_campaigns, 1) LOOP
				EXEXUTE ''SELECT user_name FROM administration.users INNER JOIN administration.campaigns ON users.id = campaigns.user_id
						 WHERE campaigns.id = '' || arr_campaigns[campaign] INTO other_user;
				statement := statement || '' UNION ALL SELECT * FROM '' || other_user || ''.log_eval_entries_'' || arr_campaigns[campaign];
			END LOOP;
			EXEXUTE ''CREATE OR REPLACE TEMPORARY VIEW log_eval_entries AS '' || statement;


			EXEXUTE ''SELECT user_name FROM administration.users INNER JOIN administration.campaigns ON users.id = campaigns.user_id
					 WHERE campaigns.id = '' || arr_campaigns[1] INTO other_user;
			statement := ''SELECT * FROM '' || other_user || ''.moments_'' || arr_campaigns[1];
			FOR campaign IN array_lower(arr_campaigns, 1)+1..array_upper(arr_campaigns, 1) LOOP
				EXEXUTE ''SELECT user_name FROM administration.users INNER JOIN administration.campaigns ON users.id = campaigns.user_id
						 WHERE campaigns.id = '' || arr_campaigns[campaign] INTO other_user;
				statement := statement || '' UNION ALL SELECT * FROM '' || other_user || ''.moments_'' || arr_campaigns[campaign];
			END LOOP;
			EXEXUTE ''CREATE OR REPLACE TEMPORARY VIEW moments AS '' || statement;


			EXEXUTE ''SELECT user_name FROM administration.users INNER JOIN administration.campaigns ON users.id = campaigns.user_id
					 WHERE campaigns.id = '' || arr_campaigns[1] INTO other_user;
			statement := ''SELECT * FROM '' || other_user || ''.batch_means_'' || arr_campaigns[1];
			FOR campaign IN array_lower(arr_campaigns, 1)+1..array_upper(arr_campaigns, 1) LOOP
				EXEXUTE ''SELECT user_name FROM administration.users INNER JOIN administration.campaigns ON users.id = campaigns.user_id
						 WHERE campaigns.id = '' || arr_campaigns[campaign] INTO other_user;
				statement := statement || '' UNION ALL SELECT * FROM '' || other_user || ''.batch_means_'' || arr_campaigns[campaign];
			END LOOP;
			EXEXUTE ''CREATE OR REPLACE TEMPORARY VIEW batch_means AS '' || statement;


			EXEXUTE ''SELECT user_name FROM administration.users INNER JOIN administration.campaigns ON users.id = campaigns.user_id
					 WHERE campaigns.id = '' || arr_campaigns[1] INTO other_user;
			statement := ''SELECT * FROM '' || other_user || ''.batch_means_histograms_'' || arr_campaigns[1];
			FOR campaign IN array_lower(arr_campaigns, 1)+1..array_upper(arr_campaigns, 1) LOOP
				EXEXUTE ''SELECT user_name FROM administration.users INNER JOIN administration.campaigns ON users.id = campaigns.user_id
						 WHERE campaigns.id = '' || arr_campaigns[campaign] INTO other_user;
				statement := statement || '' UNION ALL SELECT * FROM '' || other_user || ''.batch_means_histograms_'' || arr_campaigns[campaign];
			END LOOP;
			EXEXUTE ''CREATE OR REPLACE TEMPORARY VIEW batch_means_histograms AS '' || statement;


			EXEXUTE ''SELECT user_name FROM administration.users INNER JOIN administration.campaigns ON users.id = campaigns.user_id
					 WHERE campaigns.id = '' || arr_campaigns[1] INTO other_user;
			statement := ''SELECT * FROM '' || other_user || ''.lres_'' || arr_campaigns[1];
			FOR campaign IN array_lower(arr_campaigns, 1)+1..array_upper(arr_campaigns, 1) LOOP
				EXEXUTE ''SELECT user_name FROM administration.users INNER JOIN administration.campaigns ON users.id = campaigns.user_id
						 WHERE campaigns.id = '' || arr_campaigns[campaign] INTO other_user;
				statement := statement || '' UNION ALL SELECT * FROM '' || other_user || ''.lres_'' || arr_campaigns[campaign];
			END LOOP;
			EXEXUTE ''CREATE OR REPLACE TEMPORARY VIEW lres AS '' || statement;


			EXEXUTE ''SELECT user_name FROM administration.users INNER JOIN administration.campaigns ON users.id = campaigns.user_id
					 WHERE campaigns.id = '' || arr_campaigns[1] INTO other_user;
			statement := ''SELECT * FROM '' || other_user || ''.lre_histograms_'' || arr_campaigns[1];
			FOR campaign IN array_lower(arr_campaigns, 1)+1..array_upper(arr_campaigns, 1) LOOP
				EXEXUTE ''SELECT user_name FROM administration.users INNER JOIN administration.campaigns ON users.id = campaigns.user_id
						 WHERE campaigns.id = '' || arr_campaigns[campaign] INTO other_user;
				statement := statement || '' UNION ALL SELECT * FROM '' || other_user || ''.lre_histograms_'' || arr_campaigns[campaign];
			END LOOP;
			EXEXUTE ''CREATE OR REPLACE TEMPORARY VIEW lre_histograms AS '' || statement;


			EXEXUTE ''SELECT user_name FROM administration.users INNER JOIN administration.campaigns ON users.id = campaigns.user_id
					 WHERE campaigns.id = '' || arr_campaigns[1] INTO other_user;
			statement := ''SELECT * FROM '' || other_user || ''.dlres_'' || arr_campaigns[1];
			FOR campaign IN array_lower(arr_campaigns, 1)+1..array_upper(arr_campaigns, 1) LOOP
				EXEXUTE ''SELECT user_name FROM administration.users INNER JOIN administration.campaigns ON users.id = campaigns.user_id
						 WHERE campaigns.id = '' || arr_campaigns[campaign] INTO other_user;
				statement := statement || '' UNION ALL SELECT * FROM '' || other_user || ''.dlres_'' || arr_campaigns[campaign];
			END LOOP;
			EXEXUTE ''CREATE OR REPLACE TEMPORARY VIEW dlres AS '' || statement;


			EXEXUTE ''SELECT user_name FROM administration.users INNER JOIN administration.campaigns ON users.id = campaigns.user_id
					 WHERE campaigns.id = '' || arr_campaigns[1] INTO other_user;
			statement := ''SELECT * FROM '' || other_user || ''.dlre_histograms_'' || arr_campaigns[1];
			FOR campaign IN array_lower(arr_campaigns, 1)+1..array_upper(arr_campaigns, 1) LOOP
				EXEXUTE ''SELECT user_name FROM administration.users INNER JOIN administration.campaigns ON users.id = campaigns.user_id
						 WHERE campaigns.id = '' || arr_campaigns[campaign] INTO other_user;
				statement := statement || '' UNION ALL SELECT * FROM '' || other_user || ''.dlre_histograms_'' || arr_campaigns[campaign];
			END LOOP;
			EXEXUTE ''CREATE OR REPLACE TEMPORARY VIEW dlre_histograms AS '' || statement;


			EXEXUTE ''SELECT user_name FROM administration.users INNER JOIN administration.campaigns ON users.id = campaigns.user_id
					 WHERE campaigns.id = '' || arr_campaigns[1] INTO other_user;
			statement := ''SELECT * FROM '' || other_user || ''.tables_'' || arr_campaigns[1];
			FOR campaign IN array_lower(arr_campaigns, 1)+1..array_upper(arr_campaigns, 1) LOOP
				EXEXUTE ''SELECT user_name FROM administration.users INNER JOIN administration.campaigns ON users.id = campaigns.user_id
						 WHERE campaigns.id = '' || arr_campaigns[campaign] INTO other_user;
				statement := statement || '' UNION ALL SELECT * FROM '' || other_user || ''.tables_'' || arr_campaigns[campaign];
			END LOOP;
			EXEXUTE ''CREATE OR REPLACE TEMPORARY VIEW tables AS '' || statement;


			EXEXUTE ''SELECT user_name FROM administration.users INNER JOIN administration.campaigns ON users.id = campaigns.user_id
					 WHERE campaigns.id = '' || arr_campaigns[1] INTO other_user;
			statement := ''SELECT * FROM '' || other_user || ''.table_rows_'' || arr_campaigns[1];
			FOR campaign IN array_lower(arr_campaigns, 1)+1..array_upper(arr_campaigns, 1) LOOP
				EXEXUTE ''SELECT user_name FROM administration.users INNER JOIN administration.campaigns ON users.id = campaigns.user_id
						 WHERE campaigns.id = '' || arr_campaigns[campaign] INTO other_user;
				statement := statement || '' UNION ALL SELECT * FROM '' || other_user || ''.table_rows_'' || arr_campaigns[campaign];
			END LOOP;
			EXEXUTE ''CREATE OR REPLACE TEMPORARY VIEW table_rows AS '' || statement;


			EXEXUTE ''SELECT parameter_name FROM parameters LIMIT 1'' INTO parameter_name;

			statement_select := ''SELECT '' || quote_ident(parameter_name) || ''.campaign_id AS campaign_id, '' || quote_ident(parameter_name) || ''.scenario_id AS scenario_id, '';
			statement_from := '' FROM'';
			statement_where1 := '' WHERE'';
			statement_where2 := '''';
			FOR parameters_record IN EXEXUTE ''SELECT DISTINCT parameter_name, parameter_type FROM parameters'' LOOP
				statement_select := statement_select || '' '' || quote_ident(parameters_record.parameter_name) || ''.'' || quote_ident(parameters_record.parameter_type) || '' AS '' || quote_ident(lower(parameters_record.parameter_name)) || '','';
				statement_from := statement_from || '' parameters '' || quote_ident(parameters_record.parameter_name) || '','';
				statement_where2 := statement_where2 || '' '' || quote_ident(parameters_record.parameter_name) || ''.parameter_name = '' || quote_literal(parameters_record.parameter_name) || '' AND'';
				CONTINUE WHEN parameters_record.parameter_name = parameter_name;
				statement_where1 := statement_where1 || '' '' || quote_ident(parameter_name) || ''.scenario_id = '' || quote_ident(parameters_record.parameter_name) || ''.scenario_id AND'';
			END LOOP;

			EXEXUTE ''CREATE TEMPORARY VIEW parameter_sets AS '' || rtrim(statement_select, '','') || rtrim(statement_from, '','') || statement_where1 || rtrim(statement_where2, ''AND'');
		END;
		$view_campaigns_function$ LANGUAGE plpgsql';

	EXECUTE 'ALTER FUNCTION ' || quote_ident(user_name) || '.view_campaigns(arr_campaigns integer[]) OWNER TO rrr';
	EXECUTE 'REVOKE ALL ON FUNCTION ' || quote_ident(user_name) || '.view_campaigns(arr_campaigns integer[]) FROM PUBLIC';
	EXECUTE 'GRANT EXECUTE ON FUNCTION ' || quote_ident(user_name) || '.view_campaigns(arr_campaigns integer[]) TO ' || quote_ident(user_name);

	EXECUTE 'CREATE FUNCTION ' || quote_ident(user_name) || '.modify_campaigns() RETURNS VOID AS $modify_campaigns_function$
		BEGIN
			SET search_path TO ' || quote_ident(user_name) || ';

			DROP VIEW scenarios;
			DROP VIEW files;
			DROP VIEW parameter_sets;
			DROP VIEW parameters;
			DROP VIEW jobs;
			DROP VIEW pd_fs;
			DROP VIEW pdf_histograms;
			DROP VIEW log_evals;
			DROP VIEW log_eval_entries;
			DROP VIEW moments;
			DROP VIEW batch_means;
			DROP VIEW batch_means_histograms;
			DROP VIEW lres;
			DROP VIEW lre_histograms;
			DROP VIEW dlres;
			DROP VIEW dlre_histograms;
			DROP VIEW tables;
			DROP VIEW table_rows;
		END;
		$modify_campaigns_function$ LANGUAGE plpgsql';

	EXECUTE 'ALTER FUNCTION ' || quote_ident(user_name) || '.modify_campaigns() OWNER TO rrr';
	EXECUTE 'REVOKE ALL ON FUNCTION ' || quote_ident(user_name) || '.modify_campaigns() FROM PUBLIC';
	EXECUTE 'GRANT EXECUTE ON FUNCTION ' || quote_ident(user_name) || '.modify_campaigns() TO ' || quote_ident(user_name);

	EXECUTE 'CREATE OR REPLACE FUNCTION ' || quote_ident(user_name) || '.truncate_pdf_histograms(campaign_id integer) RETURNS void AS $truncate_pdf_histograms$
		BEGIN
			EXEXUTE ''TRUNCATE ' || quote_ident(user_name) || '.pdf_histograms_'' || campaign_id;
			EXEXUTE ''UPDATE ' || quote_ident(user_name) || '.campaigns SET db_size = 0 WHERE id = '' || campaign_id;
		END;
		$truncate_pdf_histograms$ LANGUAGE plpgsql SECURITY DEFINER';

	EXECUTE 'ALTER FUNCTION ' || quote_ident(user_name) || '.truncate_pdf_histograms(campaign_id integer) OWNER TO rrr';
	EXECUTE 'REVOKE ALL ON FUNCTION ' || quote_ident(user_name) || '.truncate_pdf_histograms(campaign_id integer) FROM PUBLIC';
	EXECUTE 'GRANT EXECUTE ON FUNCTION ' || quote_ident(user_name) || '.truncate_pdf_histograms(campaign_id integer) TO ' || quote_ident(user_name);

	EXECUTE 'CREATE OR REPLACE FUNCTION ' || quote_ident(user_name) || '.truncate_pd_fs(campaign_id integer) RETURNS void AS $truncate_pd_fs$
		BEGIN
			EXEXUTE ''TRUNCATE ' || quote_ident(user_name) || '.pdf_histograms_'' || campaign_id || '', '
					     || quote_ident(user_name) || '.pd_fs_'' || campaign_id;
			EXEXUTE ''UPDATE ' || quote_ident(user_name) || '.campaigns SET db_size = 0 WHERE id = '' || campaign_id;
		END;
		$truncate_pd_fs$ LANGUAGE plpgsql SECURITY DEFINER';

	EXECUTE 'ALTER FUNCTION ' || quote_ident(user_name) || '.truncate_pd_fs(campaign_id integer) OWNER TO rrr';
	EXECUTE 'REVOKE ALL ON FUNCTION ' || quote_ident(user_name) || '.truncate_pd_fs(campaign_id integer) FROM PUBLIC';
	EXECUTE 'GRANT EXECUTE ON FUNCTION ' || quote_ident(user_name) || '.truncate_pd_fs(campaign_id integer) TO ' || quote_ident(user_name);

	EXECUTE 'CREATE OR REPLACE FUNCTION ' || quote_ident(user_name) || '.truncate_log_eval_entries(campaign_id integer) RETURNS void AS $truncate_log_eval_entries$
		BEGIN
			EXEXUTE ''TRUNCATE ' || quote_ident(user_name) || '.log_eval_entries_'' || campaign_id;
			EXEXUTE ''UPDATE ' || quote_ident(user_name) || '.campaigns SET db_size = 0 WHERE id = '' || campaign_id;
		END;
		$truncate_log_eval_entries$ LANGUAGE plpgsql SECURITY DEFINER';

	EXECUTE 'ALTER FUNCTION ' || quote_ident(user_name) || '.truncate_log_eval_entries(campaign_id integer) OWNER TO rrr';
	EXECUTE 'REVOKE ALL ON FUNCTION ' || quote_ident(user_name) || '.truncate_log_eval_entries(campaign_id integer) FROM PUBLIC';
	EXECUTE 'GRANT EXECUTE ON FUNCTION ' || quote_ident(user_name) || '.truncate_log_eval_entries(campaign_id integer) TO ' || quote_ident(user_name);

	EXECUTE 'CREATE OR REPLACE FUNCTION ' || quote_ident(user_name) || '.truncate_log_evals(campaign_id integer) RETURNS void AS $truncate_log_evals$
		BEGIN
			EXEXUTE ''TRUNCATE ' || quote_ident(user_name) || '.log_eval_entries_'' || campaign_id || '', '
					     || quote_ident(user_name) || '.log_evals_'' || campaign_id;
			EXEXUTE ''UPDATE ' || quote_ident(user_name) || '.campaigns SET db_size = 0 WHERE id = '' || campaign_id;
		END;
		$truncate_log_evals$ LANGUAGE plpgsql SECURITY DEFINER';

	EXECUTE 'ALTER FUNCTION ' || quote_ident(user_name) || '.truncate_log_evals(campaign_id integer) OWNER TO rrr';
	EXECUTE 'REVOKE ALL ON FUNCTION ' || quote_ident(user_name) || '.truncate_log_evals(campaign_id integer) FROM PUBLIC';
	EXECUTE 'GRANT EXECUTE ON FUNCTION ' || quote_ident(user_name) || '.truncate_log_evals(campaign_id integer) TO ' || quote_ident(user_name);

	EXECUTE 'CREATE OR REPLACE FUNCTION ' || quote_ident(user_name) || '.truncate_moments(campaign_id integer) RETURNS void AS $truncate_moments$
		BEGIN
			EXEXUTE ''TRUNCATE ' || quote_ident(user_name) || '.moments_'' || campaign_id;
			EXEXUTE ''UPDATE ' || quote_ident(user_name) || '.campaigns SET db_size = 0 WHERE id = '' || campaign_id;
		END;
		$truncate_moments$ LANGUAGE plpgsql SECURITY DEFINER';

	EXECUTE 'ALTER FUNCTION ' || quote_ident(user_name) || '.truncate_moments(campaign_id integer) OWNER TO rrr';
	EXECUTE 'REVOKE ALL ON FUNCTION ' || quote_ident(user_name) || '.truncate_moments(campaign_id integer) FROM PUBLIC';
	EXECUTE 'GRANT EXECUTE ON FUNCTION ' || quote_ident(user_name) || '.truncate_moments(campaign_id integer) TO ' || quote_ident(user_name);

	EXECUTE 'CREATE OR REPLACE FUNCTION ' || quote_ident(user_name) || '.truncate_batch_means_histograms(campaign_id integer) RETURNS void AS $truncate_batch_means_histograms$
		BEGIN
			EXEXUTE ''TRUNCATE ' || quote_ident(user_name) || '.batch_means_histograms_'' || campaign_id;
			EXEXUTE ''UPDATE ' || quote_ident(user_name) || '.campaigns SET db_size = 0 WHERE id = '' || campaign_id;
		END;
		$truncate_batch_means_histograms$ LANGUAGE plpgsql SECURITY DEFINER';

	EXECUTE 'ALTER FUNCTION ' || quote_ident(user_name) || '.truncate_batch_means_histograms(campaign_id integer) OWNER TO rrr';
	EXECUTE 'REVOKE ALL ON FUNCTION ' || quote_ident(user_name) || '.truncate_batch_means_histograms(campaign_id integer) FROM PUBLIC';
	EXECUTE 'GRANT EXECUTE ON FUNCTION ' || quote_ident(user_name) || '.truncate_batch_means_histograms(campaign_id integer) TO ' || quote_ident(user_name);

	EXECUTE 'CREATE OR REPLACE FUNCTION ' || quote_ident(user_name) || '.truncate_batch_means(campaign_id integer) RETURNS void AS $truncate_batch_means$
		BEGIN
			EXEXUTE ''TRUNCATE ' || quote_ident(user_name) || '.batch_means_histograms_'' || campaign_id || '', '
					     || quote_ident(user_name) || '.batch_means_'' || campaign_id;
			EXEXUTE ''UPDATE ' || quote_ident(user_name) || '.campaigns SET db_size = 0 WHERE id = '' || campaign_id;
		END;
		$truncate_batch_means$ LANGUAGE plpgsql SECURITY DEFINER';

	EXECUTE 'ALTER FUNCTION ' || quote_ident(user_name) || '.truncate_batch_means(campaign_id integer) OWNER TO rrr';
	EXECUTE 'REVOKE ALL ON FUNCTION ' || quote_ident(user_name) || '.truncate_batch_means(campaign_id integer) FROM PUBLIC';
	EXECUTE 'GRANT EXECUTE ON FUNCTION ' || quote_ident(user_name) || '.truncate_batch_means(campaign_id integer) TO ' || quote_ident(user_name);

	EXECUTE 'CREATE OR REPLACE FUNCTION ' || quote_ident(user_name) || '.truncate_lre_histograms(campaign_id integer) RETURNS void AS $truncate_lre_histograms$
		BEGIN
			EXEXUTE ''TRUNCATE ' || quote_ident(user_name) || '.lre_histograms_'' || campaign_id;
			EXEXUTE ''UPDATE ' || quote_ident(user_name) || '.campaigns SET db_size = 0 WHERE id = '' || campaign_id;
		END;
		$truncate_lre_histograms$ LANGUAGE plpgsql SECURITY DEFINER';

	EXECUTE 'ALTER FUNCTION ' || quote_ident(user_name) || '.truncate_lre_histograms(campaign_id integer) OWNER TO rrr';
	EXECUTE 'REVOKE ALL ON FUNCTION ' || quote_ident(user_name) || '.truncate_lre_histograms(campaign_id integer) FROM PUBLIC';
	EXECUTE 'GRANT EXECUTE ON FUNCTION ' || quote_ident(user_name) || '.truncate_lre_histograms(campaign_id integer) TO ' || quote_ident(user_name);

	EXECUTE 'CREATE OR REPLACE FUNCTION ' || quote_ident(user_name) || '.truncate_lres(campaign_id integer) RETURNS void AS $truncate_lres$
		BEGIN
			EXEXUTE ''TRUNCATE ' || quote_ident(user_name) || '.lre_histograms_'' || campaign_id || '', '
					     || quote_ident(user_name) || '.lres_'' || campaign_id;
			EXEXUTE ''UPDATE ' || quote_ident(user_name) || '.campaigns SET db_size = 0 WHERE id = '' || campaign_id;
		END;
		$truncate_lres$ LANGUAGE plpgsql SECURITY DEFINER';

	EXECUTE 'ALTER FUNCTION ' || quote_ident(user_name) || '.truncate_lres(campaign_id integer) OWNER TO rrr';
	EXECUTE 'REVOKE ALL ON FUNCTION ' || quote_ident(user_name) || '.truncate_lres(campaign_id integer) FROM PUBLIC';
	EXECUTE 'GRANT EXECUTE ON FUNCTION ' || quote_ident(user_name) || '.truncate_lres(campaign_id integer) TO ' || quote_ident(user_name);

	EXECUTE 'CREATE OR REPLACE FUNCTION ' || quote_ident(user_name) || '.truncate_dlre_histograms(campaign_id integer) RETURNS void AS $truncate_dlre_histograms$
		BEGIN
			EXEXUTE ''TRUNCATE ' || quote_ident(user_name) || '.dlre_histograms_'' || campaign_id;
			EXEXUTE ''UPDATE ' || quote_ident(user_name) || '.campaigns SET db_size = 0 WHERE id = '' || campaign_id;
		END;
		$truncate_dlre_histograms$ LANGUAGE plpgsql SECURITY DEFINER';

	EXECUTE 'ALTER FUNCTION ' || quote_ident(user_name) || '.truncate_dlre_histograms(campaign_id integer) OWNER TO rrr';
	EXECUTE 'REVOKE ALL ON FUNCTION ' || quote_ident(user_name) || '.truncate_dlre_histograms(campaign_id integer) FROM PUBLIC';
	EXECUTE 'GRANT EXECUTE ON FUNCTION ' || quote_ident(user_name) || '.truncate_dlre_histograms(campaign_id integer) TO ' || quote_ident(user_name);

	EXECUTE 'CREATE OR REPLACE FUNCTION ' || quote_ident(user_name) || '.truncate_dlres(campaign_id integer) RETURNS void AS $truncate_dlres$
		BEGIN
			EXEXUTE ''TRUNCATE ' || quote_ident(user_name) || '.dlre_histograms_'' || campaign_id || '', '
					     || quote_ident(user_name) || '.dlres_'' || campaign_id;
			EXEXUTE ''UPDATE ' || quote_ident(user_name) || '.campaigns SET db_size = 0 WHERE id = '' || campaign_id;
		END;
		$truncate_dlres$ LANGUAGE plpgsql SECURITY DEFINER';

	EXECUTE 'ALTER FUNCTION ' || quote_ident(user_name) || '.truncate_dlres(campaign_id integer) OWNER TO rrr';
	EXECUTE 'REVOKE ALL ON FUNCTION ' || quote_ident(user_name) || '.truncate_dlres(campaign_id integer) FROM PUBLIC';
	EXECUTE 'GRANT EXECUTE ON FUNCTION ' || quote_ident(user_name) || '.truncate_dlres(campaign_id integer) TO ' || quote_ident(user_name);

	EXECUTE 'CREATE OR REPLACE FUNCTION ' || quote_ident(user_name) || '.truncate_table_rows(campaign_id integer) RETURNS void AS $truncate_table_rows$
		BEGIN
			EXEXUTE ''TRUNCATE ' || quote_ident(user_name) || '.table_rows_'' || campaign_id;
			EXEXUTE ''UPDATE ' || quote_ident(user_name) || '.campaigns SET db_size = 0 WHERE id = '' || campaign_id;
		END;
		$truncate_table_rows$ LANGUAGE plpgsql SECURITY DEFINER';

	EXECUTE 'ALTER FUNCTION ' || quote_ident(user_name) || '.truncate_table_rows(campaign_id integer) OWNER TO rrr';
	EXECUTE 'REVOKE ALL ON FUNCTION ' || quote_ident(user_name) || '.truncate_table_rows(campaign_id integer) FROM PUBLIC';
	EXECUTE 'GRANT EXECUTE ON FUNCTION ' || quote_ident(user_name) || '.truncate_table_rows(campaign_id integer) TO ' || quote_ident(user_name);

	EXECUTE 'CREATE OR REPLACE FUNCTION ' || quote_ident(user_name) || '.truncate_tables(campaign_id integer) RETURNS void AS $truncate_tables$
		BEGIN
			EXEXUTE ''TRUNCATE ' || quote_ident(user_name) || '.table_rows_'' || campaign_id || '', '
					     || quote_ident(user_name) || '.tables_'' || campaign_id;
			EXEXUTE ''UPDATE ' || quote_ident(user_name) || '.campaigns SET db_size = 0 WHERE id = '' || campaign_id;
		END;
		$truncate_tables$ LANGUAGE plpgsql SECURITY DEFINER';

	EXECUTE 'ALTER FUNCTION ' || quote_ident(user_name) || '.truncate_tables(campaign_id integer) OWNER TO rrr';
	EXECUTE 'REVOKE ALL ON FUNCTION ' || quote_ident(user_name) || '.truncate_tables(campaign_id integer) FROM PUBLIC';
	EXECUTE 'GRANT EXECUTE ON FUNCTION ' || quote_ident(user_name) || '.truncate_tables(campaign_id integer) TO ' || quote_ident(user_name);

	EXECUTE 'CREATE OR REPLACE FUNCTION ' || quote_ident(user_name) || '.truncate_other_tables(campaign_id integer) RETURNS void AS $truncate_other_tables$
		BEGIN
			EXEXUTE ''TRUNCATE ' || quote_ident(user_name) || '.pdf_histograms_'' || campaign_id || '', '
					     || quote_ident(user_name) || '.pd_fs_'' || campaign_id || '', '
					     || quote_ident(user_name) || '.log_eval_entries_'' || campaign_id || '', '
					     || quote_ident(user_name) || '.log_evals_'' || campaign_id || '', '
					     || quote_ident(user_name) || '.moments_'' || campaign_id || '', '
					     || quote_ident(user_name) || '.batch_means_histograms_'' || campaign_id || '', '
					     || quote_ident(user_name) || '.batch_means_'' || campaign_id || '', '
					     || quote_ident(user_name) || '.lre_histograms_'' || campaign_id || '', '
					     || quote_ident(user_name) || '.lres_'' || campaign_id || '', '
					     || quote_ident(user_name) || '.dlre_histograms_'' || campaign_id || '', '
					     || quote_ident(user_name) || '.dlres_'' || campaign_id || '', '
					     || quote_ident(user_name) || '.table_rows_'' || campaign_id || '', '
					     || quote_ident(user_name) || '.tables_'' || campaign_id || '', '
					     || quote_ident(user_name) || '.scenarios_'' || campaign_id || '', '
					     || quote_ident(user_name) || '.jobs_'' || campaign_id || '', '
					     || quote_ident(user_name) || '.parameters_'' || campaign_id || '', '
					     || quote_ident(user_name) || '.files_'' || campaign_id;
			EXEXUTE ''UPDATE ' || quote_ident(user_name) || '.campaigns SET db_size = 0 WHERE id = '' || campaign_id;
		END;
		$truncate_other_tables$ LANGUAGE plpgsql SECURITY DEFINER';

	EXECUTE 'ALTER FUNCTION ' || quote_ident(user_name) || '.truncate_other_tables(campaign_id integer) OWNER TO rrr';
	EXECUTE 'REVOKE ALL ON FUNCTION ' || quote_ident(user_name) || '.truncate_other_tables(campaign_id integer) FROM PUBLIC';
	EXECUTE 'GRANT EXECUTE ON FUNCTION ' || quote_ident(user_name) || '.truncate_other_tables(campaign_id integer) TO ' || quote_ident(user_name);

END;
$$ LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION administration.users() RETURNS trigger AS $users_trigger$
DECLARE
	user_db text;
	db_use bigint;
BEGIN
	IF (TG_OP = 'INSERT') THEN
		IF NEW.group_account THEN
			EXECUTE 'SELECT * FROM pg_user WHERE usename = ' || quote_literal(NEW.user_name) INTO user_db;
			IF user_db IS NULL THEN
				EXECUTE 'CREATE ROLE ' || quote_ident(NEW.user_name);
			END IF;
			NEW.password := 'There is no password for this account type';
			NEW.db_quota := 0;
			RETURN NEW;
		ELSE
			PERFORM administration.create_user(NEW.id, NEW.user_name, NEW.full_name, NEW.password);
			NEW.password := 'Password is stored in DB server';
			RETURN NEW;
		END IF;
	ELSIF (TG_OP = 'UPDATE') THEN
		IF NOT OLD.group_account THEN
			EXECUTE 'SELECT sum(db_size) FROM ' || quote_ident(OLD.user_name) || '.campaigns' INTO db_use;
			IF db_use IS NULL THEN
				db_use := 0;
			END IF;
			NEW.db_use := db_use;

			IF (NEW.db_use > NEW.db_quota AND OLD.db_quota_exceeded = FALSE) THEN
				EXECUTE 'SELECT administration.revoke_campaign_access(' || OLD.id || ')';
				NEW.db_quota_exceeded = TRUE;
			ELSIF (NEW.db_use <= NEW.db_quota AND OLD.db_quota_exceeded = TRUE) THEN
				EXECUTE 'SELECT administration.grant_campaign_access(' || OLD.id || ')';
				NEW.db_quota_exceeded = FALSE;
			END IF;

			IF NEW.password != NULL THEN
				EXECUTE 'ALTER ROLE ' || OLD.user_name || ' PASSWORD ' || quote_literal(NEW.password);
			END IF;
		END IF;
		NEW.user_name = OLD.user_name;
		NEW.password = OLD.password;
		NEW.group_account = OLD.group_account;
		RETURN NEW;
	ELSIF (TG_OP = 'DELETE') THEN
		DELETE FROM administration.group_members WHERE group_members.user_id = OLD.id;
		DELETE FROM administration.group_members WHERE group_members.group_id = OLD.id;
		IF OLD.group_account THEN
--			EXECUTE 'DROP ROLE ' || quote_ident(OLD.user_name);
			RETURN OLD;
		ELSE
			EXECUTE 'DROP SCHEMA ' || quote_ident(OLD.user_name) || ' CASCADE';
			DELETE FROM administration.campaigns WHERE user_id = OLD.id;
			DELETE FROM administration.authorizations WHERE user_id = OLD.id;
			DELETE FROM administration.authorizations WHERE authorized_id = OLD.id;
			RETURN OLD;
		END IF;
	END IF;
END;
$users_trigger$ LANGUAGE plpgsql;

ALTER FUNCTION administration.users() OWNER TO rrr;

CREATE TRIGGER users_trigger
BEFORE INSERT OR UPDATE OR DELETE ON administration.users
FOR EACH ROW EXECUTE PROCEDURE administration.users();

