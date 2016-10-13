SET SCHEMA 'web_slepemapy_prod' ;

CREATE TABLE tmp_answer AS (
    SELECT
        proso_models_answer.*,
        proso_models_answer.type AS direction,
        proso_configab_answerexperimentsetup.experiment_setup_id
    FROM proso_models_answer
    INNER JOIN proso_configab_answerexperimentsetup
        ON proso_models_answer.id = answer_id
    INNER JOIN proso_flashcards_flashcardanswer
        ON proso_models_answer.id = answer_ptr_id
    WHERE experiment_setup_id IN (6, 7, 8, 9)
    ORDER BY proso_models_answer.id
);
ALTER TABLE tmp_answer DROP column type;
\copy tmp_answer TO '/tmp/answers.csv' DELIMITER ',' CSV HEADER;
DROP TABLE tmp_answer;


CREATE TABLE tmp_rating AS (
    SELECT *
    FROM proso_feedback_rating
    WHERE user_id IN (
        SELECT DISTINCT(user_id)
        FROM proso_models_answer
        INNER JOIN proso_configab_answerexperimentsetup
            ON proso_models_answer.id = answer_id
        WHERE experiment_setup_id IN (6, 7, 8, 9)
    )
    ORDER BY id
);
\copy tmp_rating TO '/tmp/ratings.csv' DELIMITER ',' CSV HEADER;
DROP TABLE tmp_rating;


CREATE TABLE tmp_ip_address AS (
    SELECT proso_user_session.id as session_id, user_id, ip_address
    FROM proso_user_session
    INNER JOIN proso_user_location
        ON location_id = proso_user_location.id
    WHERE user_id IN (
        SELECT DISTINCT(user_id)
        FROM proso_models_answer
        INNER JOIN proso_configab_answerexperimentsetup
            ON proso_models_answer.id = answer_id
        WHERE experiment_setup_id IN (6, 7, 8, 9)
    )
);
\copy tmp_ip_address TO '/tmp/ip_address.csv' DELIMITER ',' CSV HEADER;
DROP TABLE tmp_ip_address;


CREATE TABLE tmp_context AS (
    SELECT
        fc.item_id AS item_id,
        cat.identifier AS term_type,
        t.name AS term_name,
        con.name AS context_name
    FROM proso_flashcards_flashcard as fc
    INNER JOIN proso_models_itemrelation as rel_t ON rel_t.child_id = fc.item_id
    INNER JOIN proso_flashcards_term as t ON rel_t.parent_id = t.item_id AND t.lang = 'en'
    INNER JOIN proso_models_itemrelation AS rel_cat ON rel_cat.child_id = t.item_id
    INNER JOIN proso_flashcards_category AS cat ON rel_cat.parent_id = cat.item_id AND cat.type = 'flashcard_type' AND cat.lang = 'en'
    INNER JOIN proso_models_itemrelation AS rel_con ON rel_con.child_id = fc.item_id
    INNER JOIN proso_flashcards_context AS con ON rel_con.parent_id = con.item_id AND con.lang = 'en'
    WHERE fc.lang = 'en'
);
\copy tmp_context TO '/tmp/flashcards.csv' DELIMITER ',' CSV HEADER;
DROP TABLE tmp_context;


CREATE TABLE tmp_items AS (
    SELECT
        proso_flashcards_flashcard.id AS fc_id,
        proso_flashcards_flashcard.item_id AS item_id
    FROM proso_flashcards_flashcard
);
\copy tmp_items TO '/tmp/items.csv' DELIMITER ',' CSV HEADER;
DROP TABLE tmp_items;


CREATE TABLE tmp_difficulty AS (
    SELECT
        item_primary_id AS item_id,
        value AS difficulty
    FROM proso_models_variable
    WHERE key = 'difficulty' AND info_id = (
        SELECT MAX(id)
        FROM proso_models_environmentinfo
        WHERE status = 3
    )
);
\copy tmp_difficulty TO '/tmp/difficulty.csv' DELIMITER ',' CSV HEADER;
DROP TABLE tmp_difficulty;


CREATE TABLE tmp_option AS (
    SELECT proso_flashcards_flashcardanswer_options.*
    FROM proso_models_answer
    INNER JOIN proso_configab_answerexperimentsetup
        ON proso_models_answer.id = answer_id
    INNER JOIN proso_flashcards_flashcardanswer
        ON proso_models_answer.id = answer_ptr_id
    INNER JOIN proso_flashcards_flashcardanswer_options
        ON proso_models_answer.id = flashcardanswer_id
    WHERE experiment_setup_id IN (6, 7, 8, 9)
    ORDER BY proso_models_answer.id
);
\copy tmp_option TO '/tmp/options.csv' DELIMITER ',' CSV HEADER;
DROP TABLE tmp_option;
