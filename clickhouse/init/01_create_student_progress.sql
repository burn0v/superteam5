CREATE TABLE IF NOT EXISTS student_progress (
    student_id UInt32,
    score Float32
) ENGINE = MergeTree()
ORDER BY student_id;
