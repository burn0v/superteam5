CREATE TABLE IF NOT EXISTS exam_tracker.ticket (
    ticket_id Int32,
    subject String,
    max_points Int32,
    question_count Int32,
    difficulty Int32
) ENGINE = MergeTree()
ORDER BY ticket_id;