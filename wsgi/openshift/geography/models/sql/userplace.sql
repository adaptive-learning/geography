CREATE VIEW geography_elodifficulty_prepared AS
	SELECT
		geography_place.id AS place_id,
		COALESCE(geography_elodifficulty.value, 0) AS value
	FROM
		geography_place
		LEFT JOIN geography_elodifficulty
			ON geography_elodifficulty.place_id = geography_place.id;

CREATE VIEW geography_eloskill_prepared AS
	SELECT
		auth_user.id AS user_id,
		COALESCE(geography_eloskill.value, 0) AS value
	FROM
		auth_user
		LEFT JOIN geography_eloskill
			ON geography_eloskill.user_id = auth_user.id;

CREATE VIEW geography_elolocalskill_prepared AS
	SELECT
		geography_eloskill_prepared.user_id AS user_id,
		geography_elodifficulty_prepared.place_id AS place_id,
		geography_eloskill_prepared.value AS skill,
		geography_elodifficulty_prepared.value AS difficulty,
		COALESCE(
			geography_elolocalskill.value,
			geography_eloskill_prepared.value - geography_elodifficulty_prepared.value
		) AS value
	FROM
		geography_eloskill_prepared
		LEFT JOIN geography_elodifficulty_prepared ON true
		LEFT JOIN geography_elolocalskill USING(user_id, place_id);

CREATE VIEW geography_userplace AS
	SELECT
		geography_elolocalskill.user_id * 100000 + geography_elolocalskill.place_id AS dummy_id,
		geography_elolocalskill.user_id AS user_id,
		geography_elolocalskill.place_id AS place_id,
		geography_elolocalskill.value AS elo_skill
	FROM
		geography_elolocalskill
	GROUP BY
		geography_elolocalskill.user_id, geography_elolocalskill.place_id;
