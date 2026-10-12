"""Ask about many items in one call; check each answer alone (F3 §4.3 rule 4, rel01 D30).

A headless call costs about the same whether it asks about one item or twenty,
so questions are batched. Batching must not weaken the check-immediately rule:
each item's answer is validated on its own, and an item that fails is re-asked
**alone, once**, with the failed check named. One item failing never discards
another item's accepted answer.
"""
from __future__ import annotations

import copy
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass, field
from typing import Any

from ..llm import Answer, AnswerRejected, Backend, Question
from .guards import GuardFailure, check_schema

BuildQuestion = Callable[[Sequence[Any], "str | None"], Question]
#: Stands in for the answer that never arrived, so a rejected call has nothing to record (I-79).
_EMPTY = Answer(data={}, backend="none", model="none")
Accept = Callable[[Any, dict[str, Any]], None]
LockInput = Callable[[Any], Mapping[str, Any]]


@dataclass
class BatchResult:
    failures: dict[str, str] = field(default_factory=dict)
    judgments: dict[str, str] = field(default_factory=dict)     # item id -> judgment id (with a lock)


def ask_each(
    items: Sequence[Any],
    item_id: Callable[[Any], str],
    backend: Backend,
    build_question: BuildQuestion,
    list_key: str,
    id_key: str,
    accept: Accept,
    note: str | None = None,
    lock: Any | None = None,
    lock_input: LockInput | None = None,
) -> BatchResult:
    """Run the batch; `accept` raises GuardFailure to reject one item.

    `note` is put in the first question too — used when the whole question is
    itself a retry, as in the T3 split re-ask (F3 AC-3.12); such a question is
    never answered from the lock.

    With a `lock` (F3 §4.7), each item is first looked up by its own input and a
    hit is replayed through `accept`; only the misses are asked, and each
    accepted answer is recorded.
    """
    result = BatchResult()
    shape = build_question([], None)
    hashes: dict[str, str] = {}
    todo: list[Any] = []
    for item in items:
        identifier = item_id(item)
        if lock is not None and lock_input is not None:
            hashes[identifier] = lock.key(shape.kind, shape.schema_version, shape.prompt, lock_input(item))
            hit = None if note else lock.lookup(shape.kind, hashes[identifier])
            if hit is not None:
                payload = copy.deepcopy(hit["answer"])
                payload[id_key] = identifier
                try:
                    accept(item, payload)
                    result.judgments[identifier] = hit["id"]
                    lock.replayed += 1
                    continue
                except GuardFailure:
                    pass
        todo.append(item)
    if not todo:
        return result

    heads: dict[int, str] = {}

    def keep(item: Any, payload: dict[str, Any], answer: Answer, attempts: int) -> None:
        identifier = item_id(item)
        if lock is None or identifier not in hashes:
            return
        entry = {k: v for k, v in payload.items() if k != id_key}
        result.judgments[identifier] = lock.record(
            shape.kind, shape.schema_version, hashes[identifier], entry, answer, attempts,
            batch_of=heads.get(id(answer)))
        heads.setdefault(id(answer), result.judgments[identifier])

    answers, batch_error, answer = _ask(backend, build_question, todo, item_id, list_key, id_key, note)
    for item in todo:
        identifier = item_id(item)
        payload = answers.get(identifier)
        problem = batch_error or (None if payload else "the answer contained no entry for this item")
        if problem is None:
            try:
                accept(item, payload)
                keep(item, payload, answer, attempts=1)
                continue
            except GuardFailure as failure:
                problem = str(failure)

        retry_note = f"{note} {problem}" if note else problem
        retry, retry_error, retry_answer = _ask(
            backend, build_question, [item], item_id, list_key, id_key, retry_note)
        payload = retry.get(identifier)
        if retry_error or payload is None:
            result.failures[identifier] = retry_error or problem
            continue
        try:
            accept(item, payload)
            keep(item, payload, retry_answer, attempts=2)
        except GuardFailure as failure:
            result.failures[identifier] = str(failure)
    return result


def _ask(
    backend: Backend,
    build_question: BuildQuestion,
    items: list[Any],
    item_id: Callable[[Any], str],
    list_key: str,
    id_key: str,
    note: str | None,
) -> tuple[dict[str, dict[str, Any]], str | None, Answer]:
    """Ask, then apply G5 to the whole answer. Returns entries keyed by item id."""
    question = build_question(items, note)
    try:
        answer = backend.ask(question)
        check_schema(answer.data, question.schema)
    except AnswerRejected as rejected:      # I-79: one unusable answer, not a dead backend
        return {}, str(rejected), _EMPTY
    except GuardFailure as failure:
        return {}, str(failure), answer

    wanted = {item_id(item) for item in items}
    return {
        entry[id_key]: entry for entry in answer.data[list_key] if entry[id_key] in wanted
    }, None, answer
