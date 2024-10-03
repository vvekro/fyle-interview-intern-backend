-- Write query to find the number of grade A's given by the teacher who has graded the most assignments
WITH teacher_grades AS (
    SELECT teacher_id, COUNT(id) AS total_graded
    FROM assignments
    WHERE state = 'GRADED'
    GROUP BY teacher_id
)
SELECT COUNT(a.id) AS grade_a_count
FROM assignments a
JOIN teacher_grades tg ON a.teacher_id = tg.teacher_id
WHERE a.grade = 'A' AND a.teacher_id = (
    SELECT teacher_id
    FROM teacher_grades
    ORDER BY total_graded DESC
    LIMIT 1
);
