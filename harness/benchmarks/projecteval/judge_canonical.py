"""Trial 1, the one number: run ProjectEval's own judge on ProjectEval's own canonical answer.

No model is called: requirements, start commands, start files and parameter values are all supplied,
so the judge never asks its LLM class for anything (the class below fails loudly if it does).

Run from the ProjectEval checkout, inside its virtualenv:
    cd download/ProjectEval && . .venv/bin/activate && python ../../judge_canonical.py [project ids…]
"""
import json
import sys

sys.path.insert(0, ".")
from controller import JudgeController  # noqa: E402  (ProjectEval's module; cwd is its checkout)


class NoModel:
    """Stands in for ProjectEval's LLMTest. Any call means the judge needed a model: stop."""

    def __init__(self, llm=None, device=None, *args, **kwargs):
        self.llm = llm or "no-model"

    def __getattr__(self, name):
        raise RuntimeError(f"the judge asked the model for {name!r}; this trial must not call a model")


ids = sys.argv[1:] or [str(n) for n in range(1, 21)]
console = {"16", "17", "18", "19"}
initiate_command = {pid: ([] if pid in console else [[]]) for pid in ids}
requirements = {pid: (["openpyxl", "pandas"] if pid in console
                      else ["django", "matplotlib", "pyperclip", "qrcode", "markdown"]) for pid in ids}
start_files = {pid: f"{pid}-stdanswer.py" for pid in console}

judge = JudgeController(question_path="data/project_eval_project.json",
                        answer_path="data/project_eval_answer.json",
                        parameter_file_path="data/project_eval_parameter.json",
                        model_class=NoModel, llm="canonical")
score, table = judge.evaluate(initiate_command, requirements, project_id_list=ids,
                              start_file_list=start_files)
print("RESULT", json.dumps({"score": score, "per_project": table}))
