import difflib
import re


class TestGrader:
    """Class for checking and grading quiz answers"""

    @staticmethod
    def check_answer(question, user_answer):
        """
        Check if user's answer is correct

        Args:
            question: Question dictionary with type and correct answer
            user_answer: User's submitted answer

        Returns:
            Boolean indicating if answer is correct
        """
        if not user_answer or not user_answer.strip():
            return False

        if question["type"] == "multiple_choice":
            return TestGrader._check_multiple_choice(question, user_answer)
        elif question["type"] == "short":
            return TestGrader._check_short_answer(question, user_answer)
        else:
            return False

    @staticmethod
    def _check_multiple_choice(question, user_answer):
        """Check multiple choice answer (exact match)"""
        correct = question["correct"].strip().upper()
        user = user_answer.strip().upper()

        # Allow both "A" and "A)" formats
        if len(user) > 1 and user[1] == ")":
            user = user[0]

        return user == correct

    @staticmethod
    def _normalize_answer(text):
        """Normalize answer by removing common prefixes and formatting"""
        text = text.strip().lower()

        # Remove common variable assignments like "x = ", "y = ", etc.
        text = re.sub(r"^[a-z]\s*=\s*", "", text)

        # Remove common words/phrases
        remove_phrases = [
            "atsakymas:",
            "answer:",
            "tai yra",
            "yra",
            "is",
            "equals",
            "the answer is",
            "atsakymas yra",
        ]
        for phrase in remove_phrases:
            text = text.replace(phrase.lower(), "")

        # Clean up extra spaces
        text = " ".join(text.split())

        return text.strip()

    @staticmethod
    def _check_short_answer(question, user_answer):
        """Check short answer using fuzzy matching with improved normalization"""
        correct = question["correct"].strip().lower()
        user = user_answer.strip().lower()

        # First try exact match
        if correct == user:
            return True

        # Normalize both answers (remove "x = " type prefixes)
        correct_normalized = TestGrader._normalize_answer(correct)
        user_normalized = TestGrader._normalize_answer(user)

        # Try exact match on normalized
        if correct_normalized == user_normalized:
            return True

        # For numeric answers, extract numbers and compare
        correct_numbers = re.findall(r"-?\d+(?:\.\d+)?", correct_normalized)
        user_numbers = re.findall(r"-?\d+(?:\.\d+)?", user_normalized)
        if correct_numbers and user_numbers:
            # Compare as floats
            correct_numbers = [float(n) for n in correct_numbers]
            user_numbers = [float(n) for n in user_numbers]
            if correct_numbers == user_numbers:
                return True

        # Calculate similarity ratio on normalized text
        similarity = difflib.SequenceMatcher(
            None, correct_normalized, user_normalized
        ).ratio()

        # Consider correct if similarity > 60%
        return similarity > 0.6

    @staticmethod
    def calculate_similarity(str1, str2):
        """
        Calculate similarity between two strings

        Returns:
            Float between 0 and 1 (1 = identical)
        """
        return difflib.SequenceMatcher(None, str1.lower(), str2.lower()).ratio()

    @staticmethod
    def get_feedback(question, user_answer, is_correct):
        """
        Generate feedback for an answer

        Returns:
            Dictionary with feedback information
        """
        feedback = {
            "is_correct": is_correct,
            "user_answer": user_answer,
            "correct_answer": question["correct"],
        }

        if "explanation" in question:
            feedback["explanation"] = question["explanation"]

        if not is_correct and question["type"] == "short":
            similarity = TestGrader.calculate_similarity(
                question["correct"], user_answer
            )
            feedback["similarity"] = f"{similarity * 100:.1f}%"

        return feedback


# Test function
if __name__ == "__main__":
    # Test multiple choice
    q1 = {
        "question": "Kokia yra sostinė?",
        "type": "multiple_choice",
        "options": ["A) Vilnius", "B) Kaunas", "C) Klaipėda", "D) Šiauliai"],
        "correct": "A",
    }

    print("Multiple Choice Test:")
    print(f"Answer 'A': {TestGrader.check_answer(q1, 'A')}")  # True
    print(f"Answer 'a': {TestGrader.check_answer(q1, 'a')}")  # True
    print(f"Answer 'B': {TestGrader.check_answer(q1, 'B')}")  # False

    # Test short answer
    q2 = {
        "question": "Kas yra mitochondrija?",
        "type": "short",
        "correct": "Energijos gamykla ląstelėje",
        "explanation": "Mitochondrija gamina ATP",
    }

    print("\nShort Answer Test:")
    print(
        f"Exact: {TestGrader.check_answer(q2, 'Energijos gamykla ląstelėje')}"
    )  # True
    print(f"Similar: {TestGrader.check_answer(q2, 'energijos gamykla')}")  # True
    print(f"Wrong: {TestGrader.check_answer(q2, 'branduolys')}")  # False

    # Test math answers
    q3 = {
        "question": "Koks yra lygties 2x + 5 = 11 sprendinys?",
        "type": "short",
        "correct": "x = 3",
        "explanation": "Sprendimas yra 3",
    }

    print("\nMath Answer Test:")
    print(f"Answer 'x = 3': {TestGrader.check_answer(q3, 'x = 3')}")  # True
    print(f"Answer '3': {TestGrader.check_answer(q3, '3')}")  # True (NOW WORKS!)
    print(f"Answer 'x=3': {TestGrader.check_answer(q3, 'x=3')}")  # True
    print(f"Answer '5': {TestGrader.check_answer(q3, '5')}")  # False

    # Test feedback
    feedback = TestGrader.get_feedback(q2, "energijos gamykla", True)
    print(f"\nFeedback: {feedback}")
