CREATE OR REPLACE VIEW geography_difficulty_prepared AS
	SELECT
		geography_place.id AS place_id,
		COALESCE(geography_difficulty.value, 0) AS value
	FROM
		geography_place
		LEFT JOIN geography_difficulty
			ON geography_difficulty.place_id = geography_place.id;

CREATE OR REPLACE VIEW geography_priorskill_prepared AS
	SELECT
		auth_user.id AS user_id,
		COALESCE(geography_priorskill.value, 0) AS value
	FROM
		auth_user
		LEFT JOIN geography_priorskill
			ON geography_priorskill.user_id = auth_user.id;

CREATE OR REPLACE VIEW geography_currentskill_prepared AS
	SELECT
		geography_priorskill_prepared.user_id AS user_id,
		geography_difficulty_prepared.place_id AS place_id,
		geography_priorskill_prepared.value AS skill,
		geography_difficulty_prepared.value AS difficulty,
		COALESCE(
			geography_currentskill.value,
			geography_priorskill_prepared.value - geography_difficulty_prepared.value
		) AS value
	FROM
		geography_priorskill_prepared
		LEFT JOIN geography_difficulty_prepared ON true
		LEFT JOIN geography_currentskill USING(user_id, place_id);

CREATE OR REPLACE VIEW geography_userplace AS
	SELECT
		geography_currentskill.user_id * 100000 + geography_currentskill.place_id AS dummy_id,
		geography_currentskill.user_id AS user_id,
		geography_currentskill.place_id AS place_id,
		geography_currentskill.value AS skill
	FROM
		geography_currentskill
	GROUP BY
		geography_currentskill.user_id, geography_currentskill.place_id;

CREATE OR REPLACE VIEW geography_averageplace AS
  SELECT
    geography_difficulty.place_id AS dummy_id,
    geography_difficulty.place_id AS place_id,
    geography_difficulty.value AS skill
  FROM
    geography_difficulty
  GROUP BY
    geography_difficulty.place_id;
