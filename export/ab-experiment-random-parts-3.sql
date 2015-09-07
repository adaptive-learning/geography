SET SCHEMA 'web_slepemapy_prod' ;

CREATE TABLE tmp_answer AS (SELECT proso_models_answer.*
    FROM proso_models_answer
    INNER JOIN proso_configab_answerexperimentsetup
        ON proso_models_answer.id = answer_id 
    WHERE experiment_setup_id IN (6, 7, 8, 9)
);
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
);

\copy tmp_rating TO '/tmp/ratings.csv' DELIMITER ',' CSV HEADER;
DROP TABLE tmp_rating;


CREATE TABLE tmp_ip_address AS (
    SELECT user_id, ip_address
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



