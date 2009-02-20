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

