--------------------------------------------------------------------------------
-- TYPES
--------------------------------------------------------------------------------

DROP TYPE IF EXISTS "activity" CASCADE;
CREATE TYPE "activity" AS ENUM( 'enabled', 'disabled' );

DROP TYPE IF EXISTS "place_type" CASCADE;
CREATE TYPE "place_type" AS ENUM( 'state', 'city', 'world', 'continent' );

--------------------------------------------------------------------------------
-- TRIGGERS
--------------------------------------------------------------------------------

CREATE OR REPLACE FUNCTION update_modified_column()
	RETURNS TRIGGER AS '
	BEGIN
		 NEW.modified = now();
		 RETURN NEW;
	END;
' LANGUAGE 'plpgsql' IMMUTABLE CALLED ON NULL INPUT SECURITY INVOKER;

--------------------------------------------------------------------------------
-- TABLES
--------------------------------------------------------------------------------

DROP TABLE IF EXISTS "abstract_item" CASCADE;
CREATE TABLE IF NOT EXISTS "abstract_item" (
	"active" ACTIVITY NOT NULL DEFAULT 'enabled',
	"version" VARCHAR(255) NOT NULL,
	"modified" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
	"inserted" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

DROP TABLE IF EXISTS "user" CASCADE;
CREATE TABLE IF NOT EXISTS "user" (
	"id_user" SERIAL PRIMARY KEY
) INHERITS ( "abstract_item" );
CREATE TRIGGER "update_user_modtime" BEFORE UPDATE
	ON "user" FOR EACH ROW EXECUTE PROCEDURE update_modified_column();

DROP TABLE IF EXISTS "place" CASCADE;
CREATE TABLE IF NOT EXISTS "place" (
	"id_place" SERIAL PRIMARY KEY NOT NULL,
	"type" PLACE_TYPE NOT NULL,
	"code" VARCHAR(10) NOT NULL,
	"name" VARCHAR(255) NOT NULL,
	unique( "code" )
) INHERITS ( "abstract_item" );
CREATE TRIGGER "update_place_modtime" BEFORE UPDATE
	ON "place" FOR EACH ROW EXECUTE PROCEDURE update_modified_column();

DROP TABLE IF EXISTS "answer" CASCADE;
CREATE TABLE IF NOT EXISTS "answer" (
	"id_answer" SERIAL PRIMARY KEY NOT NULL,
	"id_user" SERIAL REFERENCES "user" ( "id_user" ) NOT NULL,
	"id_place_asked" SERIAL REFERENCES "place" ( "id_place" ) NOT NULL,
	"id_place_answered" SERIAL REFERENCES "place" ( "id_place" ) NOT NULL,
	"response_time" INT NOT NULL
) INHERITS ( "abstract_item" );
CREATE TRIGGER "update_answer_modtime" BEFORE UPDATE
	ON "answer" FOR EACH ROW EXECUTE PROCEDURE update_modified_column();


--------------------------------------------------------------------------------
-- VIEWS
--------------------------------------------------------------------------------

DROP VIEW IF EXISTS "view_user_place" CASCADE;
CREATE VIEW "view_user_place" AS
	SELECT
		"user"."id_user" AS "id_user",
		"place"."id_place" AS "id_place",
		"place"."code" AS "place_code",
		"place"."name" AS "place_name",
		"place"."type" AS "place_type",
		COUNT(*) AS "asked_count",
		(
			SELECT
				COUNT(*)
			FROM
				"answer"
			WHERE
				"answer"."id_user" = "id_user"
				AND
				"answer"."id_place_asked" = "id_place"
				AND
				"answer"."id_place_asked" != "answer"."id_place_answered"
			GROUP BY
				"answer"."id_user", "answer"."id_place_asked"
		) AS "correctly_answered_count",
		MAX("answer"."inserted") AS "last_asked",
		MIN("answer"."inserted") AS "first_asked"
	FROM
		"user"
		INNER JOIN "answer" USING("id_user")
		INNER JOIN "place" ON "answer"."id_place_asked" = "place"."id_place"
	GROUP BY
		"id_user", "id_place"
