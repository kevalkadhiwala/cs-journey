# ============================================================
# AI ASSISTANT (optional)
# ============================================================
# Answers plain-English questions such as
#   "Who is below 40 in Databases this term?"
# The model never sees or writes SQL. It can only ask for one of four
# safe tools below; this code checks the tool name and arguments, runs
# the tool, and gives the result back. The final answer is then checked:
# every number in it must come from a tool result, so the model cannot
# invent marks or averages.

import json
import re
from typing import Literal

from pydantic import BaseModel, Field, ValidationError, field_validator

from llm import LLMError

MAX_STEPS = 4

TERM_PATTERN = re.compile(r"\d{4}-S[12]")
NUMBER_PATTERN = re.compile(r"\d+(?:\.\d+)?")


# ---------------- tool arguments ----------------

class SubjectArgs(BaseModel):
    subject: str = Field(min_length=1, max_length=50)
    term: str | None = None

    @field_validator("subject")
    @classmethod
    def tidy_subject(cls, value):
        return " ".join(value.split()).title()

    @field_validator("term")
    @classmethod
    def check_term(cls, value):
        if value is None:
            return None
        value = value.strip().upper()
        if not TERM_PATTERN.fullmatch(value):
            raise ValueError("term must look like 2026-S1")
        return value


class BelowArgs(SubjectArgs):
    mark: float = Field(ge=0, le=100)


class StudentArgs(BaseModel):
    name: str = Field(min_length=1, max_length=60)


class NoArgs(BaseModel):
    pass


class ToolCall(BaseModel):
    tool: Literal["list_subjects", "class_average", "students_below",
                  "student_results"]
    arguments: dict = {}


class FinalAnswer(BaseModel):
    answer: str = Field(min_length=1, max_length=800)


# ---------------- the tools ----------------

class StudentTools:
    """The only things the model is allowed to do. All read-only, and they
    return names and marks only (no ages or other personal details)."""

    def __init__(self, database, student_names):
        self.database = database
        self.student_names = student_names

    def list_subjects(self, args):
        return {"subjects": self.database.list_subjects()}

    def class_average(self, args):
        average, count = self.database.subject_average(args.subject, args.term)
        return {"subject": args.subject, "term": args.term,
                "average": average, "number_of_marks": count}

    def students_below(self, args):
        rows = self.database.students_below(args.subject, args.mark, args.term)
        return {"subject": args.subject, "term": args.term, "below": args.mark,
                "students": [{"name": r["student_name"], "term": r["term"],
                              "mark": r["mark"]} for r in rows]}

    def student_results(self, args):
        if args.name not in self.student_names:
            return {"error": f"no student called {args.name!r}"}
        return {"name": args.name,
                "results": self.database.get_subject_marks(args.name)}

    ARGUMENTS = {
        "list_subjects": NoArgs,
        "class_average": SubjectArgs,
        "students_below": BelowArgs,
        "student_results": StudentArgs,
    }

    def run(self, call):
        args = self.ARGUMENTS[call.tool].model_validate(call.arguments)
        return getattr(self, call.tool)(args)


SYSTEM_PROMPT = """You answer questions about student marks. You cannot see the
database. To get data, reply with JSON naming one tool:
  {"tool": "list_subjects", "arguments": {}}
  {"tool": "class_average", "arguments": {"subject": "Maths", "term": "2026-S1"}}
  {"tool": "students_below", "arguments": {"subject": "Maths", "mark": 40, "term": "2026-S1"}}
  {"tool": "student_results", "arguments": {"name": "Aisha Doyle"}}
"term" is optional (omit it for all terms). Terms look like 2026-S1.
When you have the data, reply with {"answer": "..."} in one or two plain
sentences. Only use numbers that appear in tool results.
Reply with exactly one JSON object and nothing else."""


def numbers_in(text):
    # 57.0 and 57 count as the same number
    return {float(n) for n in NUMBER_PATTERN.findall(text)}


def check_numbers(answer, question, tool_results):
    allowed = numbers_in(question) | numbers_in(json.dumps(tool_results))
    invented = numbers_in(answer) - allowed

    if invented:
        shown = ", ".join(f"{n:g}" for n in sorted(invented))
        raise ValueError(f"the answer uses numbers that no tool returned: {shown}")


def check_names(answer, steps):
    # llama3.2 once listed 1 of the 3 students under a mark. If the answer
    # names any student from a students_below result, it must name them all.
    for step in steps:
        if step["tool"] != "students_below":
            continue

        names = [row["name"] for row in step["result"]["students"]]
        missing = [name for name in names if name not in answer]

        if missing and len(missing) < len(names):
            raise ValueError("the answer leaves out students from the "
                             f"result: {', '.join(missing)}")


def build_prompt(question, steps, problem):
    prompt = f"Question: {question}\n"

    for step in steps:
        prompt += (f"\nYou called {step['tool']} with {json.dumps(step['arguments'])}"
                   f"\nResult: {json.dumps(step['result'])}\n")

    if steps:
        # Small models tend to keep calling tools, so say plainly what's next
        prompt += ('\nIf these results answer the question, reply now with '
                   '{"answer": "..."}. Only call another tool if you need '
                   'different data.\n')

    if problem:
        prompt += f"\nYour last reply was rejected: {problem}\nTry again.\n"
    return prompt


def ask(question, llm, tools):
    """Run the tool-calling loop. Returns a dict for the API response."""
    steps = []
    problem = None
    rejected_answers = 0

    # A couple of spare rounds for replies that get rejected
    for _ in range(MAX_STEPS + 2):
        try:
            reply = json.loads(llm.complete(SYSTEM_PROMPT,
                                            build_prompt(question, steps, problem)))
        except json.JSONDecodeError:
            problem = "reply was not valid JSON"
            continue
        except LLMError as error:
            return {"answer": None, "steps": steps, "error": str(error)}

        problem = None

        if isinstance(reply, dict) and "answer" in reply:
            try:
                answer = FinalAnswer.model_validate(reply).answer
                check_numbers(answer, question, [s["result"] for s in steps])
                check_names(answer, steps)
                return {"answer": answer, "steps": steps, "error": None}
            except (ValidationError, ValueError) as error:
                rejected_answers += 1
                if rejected_answers == 2:
                    break
                problem = str(error)
                continue

        if len(steps) == MAX_STEPS:
            problem = "no more tool calls allowed; give your answer"
            continue

        try:
            call = ToolCall.model_validate(reply)
        except ValidationError as error:
            problem = "; ".join(item["msg"] for item in error.errors())
            continue

        # llama3.2 also copied "2026-S1" from the examples into questions
        # about all terms, so a term the user never mentioned is dropped
        if "term" in call.arguments and not TERM_PATTERN.search(question.upper()):
            call.arguments.pop("term")

        # Found with llama3.2: it would ask for the same data again and
        # again instead of answering. Don't run it twice, point at the result.
        if any(step["tool"] == call.tool and step["arguments"] == call.arguments
               for step in steps):
            problem = (f"you already called {call.tool} with those arguments "
                       "and the result is above; use it to answer")
            continue

        try:
            result = tools.run(call)
        except ValidationError as error:
            problem = "; ".join(item["msg"] for item in error.errors())
            continue

        steps.append({"tool": call.tool, "arguments": call.arguments, "result": result})

    return {"answer": None, "steps": steps,
            "error": "could not produce a checked answer; see the tool results"}
