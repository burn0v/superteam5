from analytics.kafka_consumer import build_clickhouse_rows
payload = {
    'user': {
        'user_id': 7,
        'email': 'x@example.com',
        'first_name': 'Иван',
        'last_name': 'Иванов',
        'middle_name': 'Иванович',
        'phone_number': '+79990000000',
        'educational_institution': 'IGPT',
        'course': 2,
        'created_at': '10:15:20',
    },
    'ticket': {
        'ticket_id': 3,
        'subject': 'Programming',
        'max_points': 50,
        'question_count': 5,
        'difficulty': 8,
    },
    'attempt': {
        'attemptId': 11,
        'userId': 7,
        'ticketId': 3,
        'attemptNumber': 4,
        'scoreEarned': 45,
        'maxScore': 50,
        'attemptDate': '12.07.2026;14:22:00',
        'sessionId': 22,
    },
}
rows = build_clickhouse_rows(payload)
print(rows['users'][0]['user_id'])
print(rows['tickets'][0]['subject'])
print(rows['attempts'][0]['attempt_id'])
print(rows['attempts'][0]['attempt_date'])
