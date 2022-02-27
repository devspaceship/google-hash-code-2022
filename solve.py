from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from tqdm import tqdm

ROOT_DIR = Path(__file__).parent


@dataclass
class Contributor:
    name: str
    skills: dict[str, int]
    available: int = 0


@dataclass
class Project:
    name: str
    length: int
    points: int
    best_before: int
    roles: list[tuple[str, int]]

    @property
    def start_date(self):
        return self.best_before - self.length


@dataclass
class FilledProject:
    name: str
    contributors: list[Contributor]


def parse(name: str) -> tuple[list[Contributor], list[Project]]:
    input_file = ROOT_DIR / "input_data" / f"{name}.in.txt"
    contributors = []
    projects = []

    with input_file.open() as f:
        num_contributors, num_projects = [int(num) for num in f.readline().split(" ")]

        for _ in range(num_contributors):
            line = f.readline().split(" ")
            contributor_name = line[0]
            num_skills = int(line[1])

            skills = {}
            for _ in range(num_skills):
                line = f.readline().split(" ")
                skills[line[0]] = int(line[1])

            contributors.append(Contributor(contributor_name, skills))

        for _ in range(num_projects):
            line = f.readline().split(" ")
            project_name = line[0]
            length, points, best_before, num_roles = [int(num) for num in line[1:]]

            roles = []
            for _ in range(num_roles):
                line = f.readline().split(" ")
                roles.append((line[0], int(line[1])))

            projects.append(Project(project_name, length, points, best_before, roles))

    return contributors, projects


def get_available_contributor(
    contributors: list[Contributor],
    taken: list[Contributor],
    start_date: int,
    role: str,
    level: int,
) -> Optional[Contributor]:
    selected_contributor = None
    for contributor in contributors:
        if (
            contributor not in taken
            and contributor.available <= start_date
            and role in contributor.skills
            and level <= contributor.skills[role]
        ):
            if not selected_contributor or (
                selected_contributor
                and contributor.skills[role] < selected_contributor.skills[role]
            ):
                selected_contributor = contributor

            if selected_contributor.skills[role] == level:
                return selected_contributor

    return selected_contributor


def can_be_mentored(role: str, level: int, taken: list[Contributor]) -> bool:
    for contributor in taken:
        if role in contributor.skills and contributor.skills[role] >= level:
            return True
    return False


def solve(
    contributors: list[Contributor], projects: list[Project]
) -> list[FilledProject]:
    projects.sort(key=lambda p: p.start_date)

    solution = []
    for project in tqdm(projects):
        taken: list[Contributor] = []
        for role, level in project.roles:
            if can_be_mentored(role, level, taken):
                level -= 1
            contributor = get_available_contributor(
                contributors, taken, project.start_date, role, level
            )
            if not contributor:
                break
            taken.append(contributor)

        if len(taken) == len(project.roles):
            for contributor, (role, level) in zip(taken, project.roles):
                contributor.available = project.best_before
                if contributor.skills[role] <= level:
                    contributor.skills[role] += 1
            solution.append(
                FilledProject(project.name, [contributor.name for contributor in taken])
            )

    return solution


def format(name: str, solution: list[FilledProject]) -> None:
    output_dir = ROOT_DIR / "output_data"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / f"{name}.out.txt"
    with output_file.open("w") as f:
        f.write(f"{len(solution)}\n")
        for project in solution:
            f.write(f"{project.name}\n{' '.join(project.contributors)}\n")


if __name__ == "__main__":
    for name in ["a", "b", "c", "d", "e", "f"]:
        print(name)
        contributors, projects = parse(name)
        solution = solve(contributors, projects)
        format(name, solution)
