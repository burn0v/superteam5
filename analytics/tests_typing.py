import unittest

from json_generation import MESSAGE_SCHEMA, normalize_message_payload, validate_message_payload


class TypingAndSchemaTests(unittest.TestCase):
    def test_normalize_message_payload_coerces_values_to_expected_types(self):
        payload = {
            "user": {
                "user_id": "7",
                "email": 123,
                "first_name": None,
                "last_name": "Иванов",
                "middle_name": "Иванович",
                "phone_number": "+79990000000",
                "educational_institution": "IGPT",
                "course": 2.0,
                "created_at": "10:15:20",
            },
            "ticket": {
                "ticket_id": "3",
                "subject": "Programming",
                "max_points": "50",
                "question_count": "5",
                "difficulty": "8",
            },
            "attempt": {
                "attemptId": "11",
                "userId": "7",
                "ticketId": "3",
                "attemptNumber": "4",
                "scoreEarned": "45",
                "maxScore": "50",
                "attemptDate": "12.07.2026;14:22:00",
                "sessionId": "22",
            },
        }

        normalized = normalize_message_payload(payload)

        self.assertIsInstance(normalized["user"]["user_id"], int)
        self.assertIsInstance(normalized["ticket"]["max_points"], int)
        self.assertIsInstance(normalized["attempt"]["attemptId"], int)
        self.assertIsNone(normalized["user"]["first_name"])

    def test_validate_message_payload_accepts_valid_schema(self):
        payload = {
            "user": {
                "user_id": 7,
                "email": "student@example.com",
                "first_name": "Иван",
                "last_name": "Иванов",
                "middle_name": "Иванович",
                "phone_number": "+79990000000",
                "educational_institution": "IGPT",
                "course": 2,
                "created_at": "10:15:20",
            },
            "ticket": {
                "ticket_id": 3,
                "subject": "Programming",
                "max_points": 50,
                "question_count": 5,
                "difficulty": 8,
            },
            "attempt": {
                "attemptId": 11,
                "userId": 7,
                "ticketId": 3,
                "attemptNumber": 4,
                "scoreEarned": 45,
                "maxScore": 50,
                "attemptDate": "12.07.2026;14:22:00",
                "sessionId": 22,
            },
        }

        validate_message_payload(payload)
        self.assertIn("properties", MESSAGE_SCHEMA)


if __name__ == "__main__":
    unittest.main()
