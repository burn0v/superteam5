CREATE TABLE IF NOT EXISTS exam_tracker.attempt (
    attempt_id Int32,
    user_id Int32,
    ticket_id Int32,
    attempt_number Int32,
    score_earned Int32,
    score_max Int32,
    passing_rate Float32,
    attempt_date DateTime,
    session_id Int32
) ENGINE = MergeTree()
ORDER BY attempt_id;