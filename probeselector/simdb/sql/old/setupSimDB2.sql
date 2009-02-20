CREATE LANGUAGE plpgsql;

CREATE USER administrator;
CREATE SCHEMA administration AUTHORIZATION administrator;
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

ALTER TABLE administration.users OWNER TO administrator;
GRANT SELECT ON TABLE administration.users TO PUBLIC;
INSERT INTO administration.users (user_name, full_name, password, group_account) VALUES ('PUBLIC', 'public user', '', TRUE);

CREATE TABLE administration.group_members (
	id SERIAL PRIMARY KEY,
	user_id integer,
	group_id integer,
	UNIQUE (user_id, group_id)
);

ALTER TABLE administration.group_members OWNER TO administrator;
REVOKE UPDATE ON TABLE administration.group_members FROM administrator;
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

ALTER TABLE administration.campaigns OWNER TO administrator;
GRANT SELECT ON TABLE administration.campaigns TO PUBLIC;

CREATE SEQUENCE administration.campaigns_id_seq;
ALTER TABLE administration.campaigns_id_seq OWNER TO administrator;
GRANT SELECT ON TABLE administration.campaigns_id_seq TO PUBLIC;

CREATE TABLE administration.authorizations (
	id integer PRIMARY KEY,
	user_id integer REFERENCES administration.users,
	campaign_id integer,
	authorized_id integer
);

ALTER TABLE administration.authorizations OWNER TO administrator;
GRANT SELECT ON TABLE administration.authorizations TO PUBLIC;

CREATE SEQUENCE administration.authorizations_id_seq;
ALTER TABLE administration.authorizations_id_seq OWNER TO administrator;

CREATE OR REPLACE FUNCTION public.set_user_schema() RETURNS VOID AS $set_user_schema_function$
BEGIN
	SET constraint_exclusion = on;
	EXECUTE 'SET search_path TO ' || quote_ident(user);
END;
$set_user_schema_function$ LANGUAGE plpgsql;

ALTER FUNCTION public.set_user_schema() OWNER TO administrator;
GRANT EXECUTE ON FUNCTION public.set_user_schema() TO PUBLIC;

CREATE FUNCTION public.administrate_db() RETURNS VOID AS $administrate_db_function$
BEGIN
	SET constraint_exclusion = on;
	SET search_path TO administration;
END;
$administrate_db_function$ LANGUAGE plpgsql;

ALTER FUNCTION public.administrate_db() OWNER TO administrator;
GRANT EXECUTE ON FUNCTION public.administrate_db() TO PUBLIC;

CREATE FUNCTION administration.change_password(password text) RETURNS VOID AS $change_password_function$
BEGIN
	EXECUTE 'ALTER ROLE ' || user || ' PASSWORD ' || quote_literal(password);
END;
$change_password_function$ LANGUAGE plpgsql;

ALTER FUNCTION administration.change_password(password text) OWNER TO administrator;

CREATE OR REPLACE FUNCTION administration.calculate_campaign_size(campaign_id integer) RETURNS bigint AS $$
DECLARE
	campaign_size bigint;
	campaign_size_help bigint;
	user_name text;
BEGIN
	campaign_size := 0;

	EXECUTE 'SELECT user_name FROM administration.users JOIN administration.campaigns ON users.id = campaigns.user_id WHERE campaigns.id = ' || campaign_id INTO user_name;

	EXECUTE 'SELECT pg_total_relation_size(\'' || user_name || '.scenarios_' || campaign_id || '\')' INTO campaign_size_help;
	campaign_size := campaign_size_help;

	EXECUTE 'SELECT pg_total_relation_size(\'' || user_name || '.files_' || campaign_id || '\')' INTO campaign_size_help;
	campaign_size := campaign_size + campaign_size_help;

	EXECUTE 'SELECT pg_total_relation_size(\'' || user_name || '.parameters_' || campaign_id || '\')' INTO campaign_size_help;
	campaign_size := campaign_size + campaign_size_help;

	EXECUTE 'SELECT pg_total_relation_size(\'' || user_name || '.jobs_' || campaign_id || '\')' INTO campaign_size_help;
	campaign_size := campaign_size + campaign_size_help;

	EXECUTE 'SELECT pg_total_relation_size(\'' || user_name || '.pd_fs_' || campaign_id || '\')' INTO campaign_size_help;
	campaign_size := campaign_size + campaign_size_help;

	EXECUTE 'SELECT pg_total_relation_size(\'' || user_name || '.pdf_histograms_' || campaign_id || '\')' INTO campaign_size_help;
	campaign_size := campaign_size + campaign_size_help;

	EXECUTE 'SELECT pg_total_relation_size(\'' || user_name || '.log_evals_' || campaign_id || '\')' INTO campaign_size_help;
	campaign_size := campaign_size + campaign_size_help;

	EXECUTE 'SELECT pg_total_relation_size(\'' || user_name || '.log_eval_entries_' || campaign_id || '\')' INTO campaign_size_help;
	campaign_size := campaign_size + campaign_size_help;

	EXECUTE 'SELECT pg_total_relation_size(\'' || user_name || '.moments_' || campaign_id || '\')' INTO campaign_size_help;
	campaign_size := campaign_size + campaign_size_help;

	EXECUTE 'SELECT pg_total_relation_size(\'' || user_name || '.batch_means_' || campaign_id || '\')' INTO campaign_size_help;
	campaign_size := campaign_size + campaign_size_help;

	EXECUTE 'SELECT pg_total_relation_size(\'' || user_name || '.batch_means_histograms_' || campaign_id || '\')' INTO campaign_size_help;
	campaign_size := campaign_size + campaign_size_help;

	EXECUTE 'SELECT pg_total_relation_size(\'' || user_name || '.lres_' || campaign_id || '\')' INTO campaign_size_help;
	campaign_size := campaign_size + campaign_size_help;

	EXECUTE 'SELECT pg_total_relation_size(\'' || user_name || '.lre_histograms_' || campaign_id || '\')' INTO campaign_size_help;
	campaign_size := campaign_size + campaign_size_help;

	EXECUTE 'SELECT pg_total_relation_size(\'' || user_name || '.dlres_' || campaign_id || '\')' INTO campaign_size_help;
	campaign_size := campaign_size + campaign_size_help;

	EXECUTE 'SELECT pg_total_relation_size(\'' || user_name || '.dlre_histograms_' || campaign_id || '\')' INTO campaign_size_help;
	campaign_size := campaign_size + campaign_size_help;

	EXECUTE 'SELECT pg_total_relation_size(\'' || user_name || '.tables_' || campaign_id || '\')' INTO campaign_size_help;
	campaign_size := campaign_size + campaign_size_help;

	EXECUTE 'SELECT pg_total_relation_size(\'' || user_name || '.table_rows_' || campaign_id || '\')' INTO campaign_size_help;
	campaign_size := campaign_size + campaign_size_help;

	RETURN campaign_size;
END
$$ LANGUAGE plpgsql;

ALTER FUNCTION administration.calculate_campaign_size(campaign_id integer) OWNER TO administrator;


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

ALTER FUNCTION administration.revoke_campaign_access(user_id integer) OWNER TO administrator;


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

ALTER FUNCTION administration.grant_campaign_access(user_id integer) OWNER TO administrator;


CREATE OR REPLACE FUNCTION administration.calculate_db_use() RETURNS void AS $$
BEGIN
	UPDATE administration.campaigns SET db_size = 0;
END
$$ LANGUAGE plpgsql SECURITY DEFINER;

ALTER FUNCTION administration.calculate_db_use() OWNER TO administrator;
GRANT EXECUTE ON FUNCTION administration.calculate_db_use() TO PUBLIC;
