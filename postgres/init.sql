ALTER ROLE postgres SET client_encoding TO 'utf8';
ALTER ROLE postgres SET default_transaction_isolation TO 'read committed';
ALTER ROLE postgres SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE noncensuradb TO postgres;

CREATE EXTENSION IF NOT EXISTS unaccent;

CREATE OR REPLACE FUNCTION remove_accents(input_text text)
RETURNS text AS $$
BEGIN
  RETURN unaccent('unaccent', input_text);
END;
$$ LANGUAGE plpgsql IMMUTABLE;

