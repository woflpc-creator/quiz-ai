from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
from ai_client import AIQuestionGenerator
from test_grader import TestGrader
from grader import QuizGrader
from dotenv import load_dotenv

load_dotenv("api_key.env")

app = Flask(__name__, static_folder="testu_AI")
CORS(app)

ai_generator = None
test_grader = TestGrader()
quiz_grader = QuizGrader()

try:
    ai_generator = AIQuestionGenerator()
except ValueError:
    print(
        "Warning: AI generator not initialized. Set GROQ_API_KEY environment variable."
    )


@app.route("/")
def index():
    return send_from_directory("testu_AI", "index.html")


@app.route("/<path:path>")
def serve_static(path):
    return send_from_directory("testu_AI", path)


@app.route("/api/generate-questions", methods=["POST"])
def generate_questions():
    try:
        data = request.json
        topic = data.get("topic", "")
        difficulty = data.get("difficulty", "medium")
        num_questions = data.get("num_questions", 5)

        if not topic:
            return jsonify({"error": "Topic is required"}), 400

        if ai_generator is None:
            return (
                jsonify(
                    {
                        "error": "AI generator not configured. Set GROQ_API_KEY environment variable."
                    }
                ),
                500,
            )

        questions = ai_generator.generate_questions(topic, difficulty, num_questions)
        return jsonify({"success": True, "questions": questions})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/check-answer", methods=["POST"])
def check_answer():
    try:
        data = request.json
        question = data.get("question")
        user_answer = data.get("user_answer")

        if not question or user_answer is None:
            return jsonify({"error": "Question and answer required"}), 400

        is_correct = test_grader.check_answer(question, user_answer)
        feedback = test_grader.get_feedback(question, user_answer, is_correct)

        return jsonify(
            {"success": True, "is_correct": is_correct, "feedback": feedback}
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/submit-quiz", methods=["POST"])
def submit_quiz():
    try:
        data = request.json
        topic = data.get("topic")
        difficulty = data.get("difficulty", "medium")
        results = data.get("results", [])

        if not topic or not results:
            return jsonify({"error": "Topic and results required"}), 400

        score_data = quiz_grader.calculate_score(results)
        quiz_grader.save_result(topic, difficulty, score_data)
        grade = quiz_grader.get_grade(score_data["percentage"])

        return jsonify({"success": True, "score": score_data, "grade": grade})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/history", methods=["GET"])
def get_history():
    try:
        limit = request.args.get("limit", 10, type=int)
        history = quiz_grader.get_history(limit)
        return jsonify({"success": True, "history": history})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/statistics", methods=["GET"])
def get_statistics():
    try:
        stats = quiz_grader.get_statistics()
        return jsonify({"success": True, "statistics": stats})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/health", methods=["GET"])
def health_check():
    return jsonify({"status": "healthy", "ai_available": ai_generator is not None})


if __name__ == "__main__":
    os.makedirs("testu_AI", exist_ok=True)
    app.run(debug=True, host="0.0.0.0", port=5000)
