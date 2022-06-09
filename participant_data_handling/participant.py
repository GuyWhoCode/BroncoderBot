import json


class Participant:
    # custom classes must be converted to dictionary or list to be serializable

    def __init__(
        self,
        points=0,
        total_points=0,
        problems_solved=0,
        easy=0,
        medium=0,
        hard=0,
        won=0,
        first=0,
    ) -> None:
        self.points = points
        self.total_points = total_points
        self.problems_solved = problems_solved  # also days committed
        self.easy = easy
        self.medium = medium
        self.hard = hard
        self.won = won
        self.first = first

    def toJSON(self):
        return json.dumps(self, default=lambda x: x.__dict__, sort_keys=True, indent=2)

    def to_string(self):
        result = "\ntotal_points: " + str(self.total_points)
        result += "\nproblems solved: " + str(self.problems_solved)
        result += "\nEasy problems solved: " + str(self.easy)
        result += "\nMedium problems solved: " + str(self.medium)
        result += "\nhard problems solved: " + str(self.hard)
        result += "\nCompetitions won: " + str(self.won)
        result += "\nfirst submissions: " + str(self.first)
        return result

    def get_points(self):
        return self.points

    def clear_points(self):
        self.points = 0

    def update_win(self):
        self.won += 1

    def update_stats(self, difficulty: str, points_recieved: int, was_first: bool):
        if difficulty == "hard":
            self.hard += 1
        elif difficulty == "med":
            self.medium += 1
        elif difficulty == "easy":
            self.easy += 1

        self.points += points_recieved
        self.problems_solved += 1
        self.total_points += points_recieved
        self.first += 1 if was_first else 0
