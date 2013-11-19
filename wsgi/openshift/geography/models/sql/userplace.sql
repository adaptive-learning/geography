CREATE VIEW geography_difficulty_prepared AS
	SELECT
		geography_place.id AS place_id,
		COALESCE(geography_difficulty.value, 0) AS value
	FROM
		geography_place
		LEFT JOIN geography_difficulty
			ON geography_difficulty.place_id = geography_place.id;

CREATE VIEW geography_skill_prepared AS
	SELECT
		auth_user.id AS user_id,
		COALESCE(geography_skill.value, 0) AS value
	FROM
		auth_user
		LEFT JOIN geography_skill
			ON geography_skill.user_id = auth_user.id;

CREATE VIEW geography_localskill_prepared AS
	SELECT
		geography_skill_prepared.user_id AS user_id,
		geography_difficulty_prepared.place_id AS place_id,
		geography_skill_prepared.value AS skill,
		geography_difficulty_prepared.value AS difficulty,
		COALESCE(
			geography_localskill.value,
			geography_skill_prepared.value - geography_difficulty_prepared.value
		) AS value
	FROM
		geography_skill_prepared
		LEFT JOIN geography_difficulty_prepared ON true
		LEFT JOIN geography_localskill USING(user_id, place_id);

CREATE VIEW geography_userplace AS
	SELECT
		geography_localskill.user_id * 100000 + geography_localskill.place_id AS dummy_id,
		geography_localskill.user_id AS user_id,
		geography_localskill.place_id AS place_id,
		geography_localskill.value AS skill
	FROM
		geography_localskill
	GROUP BY
		geography_localskill.user_id, geography_localskill.place_id;
