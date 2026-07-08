CREATE TABLE IF NOT EXISTS exam_tracker.`user` (
    user_id Int32,
    email String,
    first_name String,
    last_name String,
    middle_name String,
    phone_number String,
    educational_institution String,
    faculty String,
    group String,
    course String,
    created_at DateTime
) ENGINE = MergeTree()
ORDER BY user_id;