import json
import os
from datetime import datetime

class QuizGrader:
    def __init__(self, history_file="quiz_history.json"):
        self.history_file = history_file
        self.history = self._load_history()
    
    def _load_history(self):
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return []
        return []
    
    def _save_history(self):
        try:
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(self.history, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Klaida išsaugant istoriją: {e}")
    
    def calculate_score(self, results):
        total = len(results)
        correct = sum(1 for _, _, is_correct in results if is_correct)
        percentage = (correct / total * 100) if total > 0 else 0
        
        return {
            "total": total,
            "correct": correct,
            "incorrect": total - correct,
            "percentage": round(percentage, 1)
        }
    
    def save_result(self, topic, difficulty, score_data):
        result = {
            "topic": topic,
            "difficulty": difficulty,
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "score": score_data["correct"],
            "total": score_data["total"],
            "percentage": score_data["percentage"]
        }
        self.history.insert(0, result)
        self.history = self.history[:50]
        self._save_history()
    
    def get_history(self, limit=10):
        return self.history[:limit]
    
    def get_statistics(self):
        if not self.history:
            return None
        
        total_quizzes = len(self.history)
        avg_score = sum(h["percentage"] for h in self.history) / total_quizzes
        best_score = max(self.history, key=lambda x: x["percentage"])
        
        topics = {}
        for h in self.history:
            topic = h["topic"]
            if topic not in topics:
                topics[topic] = {"count": 0, "avg": 0}
            topics[topic]["count"] += 1
            topics[topic]["avg"] += h["percentage"]
        
        for topic in topics:
            topics[topic]["avg"] /= topics[topic]["count"]
            topics[topic]["avg"] = round(topics[topic]["avg"], 1)
        
        return {
            "total_quizzes": total_quizzes,
            "average_score": round(avg_score, 1),
            "best_score": best_score,
            "topics": topics
        }
    
    def get_grade(self, percentage):
        if percentage >= 90:
            return "Puikiai! 🏆"
        elif percentage >= 80:
            return "Labai gerai! 🌟"
        elif percentage >= 70:
            return "Gerai! 👍"
        elif percentage >= 60:
            return "Patenkinamai 📚"
        elif percentage >= 50:
            return "Silpnai 📖"
        else:
            return "Reikia geriau pasimokyti 💪"
