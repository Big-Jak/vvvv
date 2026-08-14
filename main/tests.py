from django.test import TestCase

from main.pipeline import get_feedback


class FeedbackPipelineTests(TestCase):
    def test_fallback_feedback_uses_essay_text(self):
        essay = (
            "This essay argues that public transportation makes cities more livable. "
            "For example, less traffic reduces commute times and lowers pollution. "
            "In addition, improved bus and rail access helps workers reach jobs and students reach schools. "
            "The argument is clear because the writer connects transportation to everyday quality of life."
        )

        feedback = get_feedback(essay)

        combined = " ".join(
            " ".join(category["strengths"] + category["weaknesses"] + category["suggestions"])
            for category in feedback["categories"].values()
        )

        self.assertIn("public transportation", combined.lower())
        self.assertIn("thesis", combined.lower())
        self.assertNotIn("reasonable sense of organization", combined.lower())
