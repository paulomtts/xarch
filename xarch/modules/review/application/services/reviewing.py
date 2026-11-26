from __future__ import annotations

from dataclasses import replace

from xarch.modules.review.application.logic.accepting import accepted, digest, stale
from xarch.modules.review.application.logic.answers import accepted_file, cache_folder, record_file, versions
from xarch.modules.review.application.logic.doubt import (
    asked_again,
    averaged,
    by_part,
    pieces_read,
    ranked,
    ranks,
    reading,
)
from xarch.modules.review.application.logic.evaluation import orders
from xarch.modules.review.application.logic.judging import asked_of, below_app, in_order, standing, unasked_of, went
from xarch.modules.review.application.logic.litmus_reading import with_litmus
from xarch.modules.review.application.logic.masking import masked
from xarch.modules.review.application.logic.placing import groups, held_as, marked, undoubted
from xarch.modules.review.application.logic.placing import standing as placed
from xarch.modules.review.application.logic.questions import (
    FIRST,
    carried,
    characters,
    entry_questions,
    named_orders,
    of_piece,
    piece_requests,
    placement,
    reordered,
    request,
    role_only,
    tokens,
)
from xarch.modules.review.application.logic.selection import chosen, judged, left_out, ways, within_cap
from xarch.modules.review.application.logic.sending import needs_key, unusable_key, why_unasked
from xarch.modules.review.application.logic.withholding import held_back, kept_examples, kept_files, unmatched
from xarch.modules.review.application.ports.acceptances import Acceptances
from xarch.modules.review.application.ports.calibrations import Calibrations
from xarch.modules.review.application.ports.code import Code
from xarch.modules.review.application.ports.decision_model import DecisionModel
from xarch.modules.review.application.ports.profile import Profile
from xarch.modules.review.application.services.answering import AnsweringService
from xarch.modules.review.contract import Review, ReviewPlanned, ReviewReading
from xarch.modules.review.domain.errors import NoKey, Refused
from xarch.modules.review.domain.published import CALIBRATED, Choice, EvalRead, PiecesRead, Reading, Request, Unasked
from xarch.modules.review.domain.values import Answer, CodeFile, EvalText, PartText, Run, Words

Asking = tuple[EvalText, EvalRead, tuple[Request, ...]]
Wanted = tuple[tuple[tuple[str, Choice], ...], tuple[tuple[str, Choice], ...]]
"""The questions asked of a file, each under its name: those of its first request, and the other orders of
placement's question when they are known to be asked (its first answer kept and near its line)."""
"""An eval of the profile's own that runs: the eval, how it stands, and one question about each thing it reads."""


class ReviewService:
    """Reads the files chosen, says what placement and each eval of the profile's own that may run would ask of each,
    and asks it of the decision model, an answer kept being read instead of asked again."""

    def __init__(self, code: Code, profile: Profile, model: DecisionModel, answering: AnsweringService,
                 calibrations: Calibrations, acceptances: Acceptances):
        self._code, self._profile, self._model, self._answering = code, profile, model, answering
        self._calibrations, self._acceptances = calibrations, acceptances

    def review(self, cmd: Review) -> ReviewPlanned | ReviewReading:
        """What placement and the evals that may run would send for each file judged (and each piece of it, with
        pieces), with a dry run; else the reading of each, from the answers kept and those asked, a file whose first
        answer is near its part's line asked again in other orders of the options and read on their mean, each read
        once the parts whose `holds` it would break are ruled out of its answers, the pieces of each ranked inside it,
        and the readings of each eval of the profile's own at or above its line (placement and each eval standing as
        held to the examples review.never does not match), a doubtful file a person accepted read as accepted while its
        code is as it was then, and the files of the record of accepted files that are stale; raises
        NoSelection, AllWithOthers, InPieces, OverCap, Refused (the files, the profile, its examples or a record
        cannot be read), and NoKey for a question to send with no key set, before anything is sent."""
        paths = chosen(cmd.paths, cmd.listed, cmd.every, cmd.app, cmd.pieces)
        found = self._code.files(paths, cmd.cwd, cmd.app, cmd.profile, cmd.tests)
        words = self._profile.words(cmd.profile)
        examples = tuple(kept_files(side, words.never) for side in self._profile.examples(cmd.profile))
        question, parts = placement(words.parts), {part.name: part for part in words.parts}
        files = held_back(found, words.never)
        judging = within_cap(judged(files), cmd.max_files, cmd.pieces)
        sends = self._model.sends()
        calibration = placed(self._calibrations.placement(record_file(cmd.app)),
                             held_as(question, words.parts, examples, (cmd.app.name, words.examples_root), words.mask),
                             sends.model)
        record = self._acceptances.get(accepted_file(cmd.app))
        going, answering = Run(cache_folder(cmd.app, cmd.cache), cmd.offline), self._answering
        requests = tuple(request(file, cmd.app.name, words.mask) for file in judging)
        others, breaks = reordered(question), self._breaks(cmd, judging) if not cmd.dry_run else {}
        wanted = tuple(self._wanted(going, item, question, others, parts[item.part], breaks.get(item.file, ()))
                       for item in requests)
        kept = tuple(answering.kept(going, item.text, asked) for item, groups_of in zip(requests, wanted, strict=True)
                     for named in groups_of for _, asked in named)
        pieced = tuple((file, *piece_requests(file, cmd.app.name, words.mask, cmd.context)) for file in judging
                       if cmd.pieces)
        piece = of_piece(question)
        asking = tuple(item for _, items, _ in pieced if ranks(items) for item in items)
        held = tuple(answering.kept(going, item.text, piece) for item in asking)
        evals, idle = self._evals(cmd, words, judging, sends.model)
        each = tuple((item, order) for asked, _, items in evals for item in items for order in orders(asked.question))
        later = tuple(answering.kept(going, item.text, order) for item, order in each)
        total, by = len(found.read) + len(found.unread), ways(cmd.paths, cmd.listed, cmd.every)
        if cmd.dry_run:
            shown = (self._carrying(going, requests, wanted)
                     + self._shown(asking, held, (piece,) * len(asking))
                     + self._shown(tuple(item for item, _ in each), later, tuple(order for _, order in each)))
            sent = (sum(carried(item, tuple(asked for _, asked in named)) for item in self._carrying(going, requests, wanted)
                        for named in (self._named(item, wanted, requests),))
                    + characters(asking, piece) + sum(characters((item,), order) for item, order in each))
            return ReviewPlanned(by, total, shown, left_out(files), question, role_only(words.parts), sent,
                                 tokens(sent), words.mask, sends, len(reordered(question)),
                                 piece.ask if cmd.pieces else "", cmd.context,
                                 in_order(idle + tuple(s for _, s, _ in evals), words.evals), words.never,
                                 unmatched(found, words.never), groups(words.parts), len(record),
                                 tuple((name, part.name, entry) for part in words.parts if entry_questions(part)
                                       for (name, _), entry in zip(entry_questions(part), part.entries, strict=True)),
                                 words.yes_line)
        if needs_key(kept + held + later, cmd.offline, sends.keyed):
            raise NoKey(sends.key)
        if unusable := unusable_key(kept + held + later, cmd.offline, sends):
            raise Refused(unusable)
        readings: list[Reading] = []
        unasked: list[Unasked] = []
        for item, (named, _) in zip(requests, wanted, strict=True):
            got, going = answering.batch(going, item.text, named)
            first, entered = got[0], got[1:]
            answers = [first]
            if first is not None and asked_again(first, parts[item.part], breaks[item.file]):
                again, going = answering.batch(going, item.text, named_orders(others))
                answers += again
            if any(answer is None for answer in (*answers, *entered)):
                said = answering.refusal(going, item.text, (*(asked for _, asked in named), *others))
                unasked.append(Unasked(item.file, why_unasked(bool(going.failure), said), said=said))
            else:
                read = reading(item, averaged(tuple(a for a in answers if a is not None)), parts[item.part],
                               len(answers), breaks[item.file])
                readings.append(with_litmus(read, parts[item.part].entries if entered else (),
                                            tuple(a for a in entered if a is not None), words.yes_line))
        ranked_pieces: list[PiecesRead] = []
        for file, items, too_small in pieced:
            pieces: list[Answer | None] = []
            for item in items if ranks(items) else ():
                answer, going = answering.answer(going, item.text, piece)
                pieces.append(answer)
                if answer is None:
                    said = answering.refusal(going, item.text, (piece,))
                    unasked.append(Unasked(item.file, why_unasked(bool(going.failure), said), item.piece, said=said))
            ranked_pieces.append(pieces_read(file, items, tuple(pieces), too_small, cmd.context,
                                             parts[file.part].alike))
        ran: list[EvalRead] = []
        for asked, stood, items in evals:
            answered: list[tuple[Answer, ...] | None] = []
            for item in items:
                found_answers, going = answering.all(going, item.text, orders(asked.question))
                answered.append(found_answers)
            unasked += unasked_of(asked, items, tuple(answered), bool(going.failure),
                                  tuple(answering.refusal(going, item.text, orders(asked.question)) for item in items))
            ran.append(went(asked, stood, items, tuple(answered)))
        judged_files = accepted(undoubted(tuple(readings), calibration),
                                {item.file: digest(item.text) for item in requests}, record)
        return ReviewReading(by, total, ranked(judged_files), left_out(files), tuple(unasked), sends,
                             len(going.asked), len(going.reused), sum(a.input_tokens for a in going.asked),
                             sum(a.output_tokens for a in going.asked), going.failure, role_only(words.parts),
                             marked(by_part(judged_files, words.parts), calibration), tuple(ranked_pieces),
                             in_order(idle + tuple(ran), words.evals), calibration, versions(*going.asked, *going.reused),
                             len(record), stale(record, judging, left_out(files), judged_files, cmd.every),
                             going.requests)

    def _wanted(self, going: Run, item: Request, question: Choice, others: tuple[Choice, ...], part: PartText,
                breaks: tuple[str, ...]) -> Wanted:
        """The questions asked of a file, each under its name, in two requests: the first, placement's question in its
        first order with the yes-or-no question of each entry of its part's litmus list (when it has two or more);
        the second, the other orders of placement's question, asked only of a file whose first answer is near its
        line, so known here only when that answer is kept (none else: they are asked once the first answer comes). A
        dry run, which asks nothing of where else a file could lie, reads how near its line a kept answer is with no
        part ruled out."""
        first = self._answering.kept(going, item.text, question)
        near = first is not None and asked_again(first, part, breaks)
        return ((FIRST, question), *entry_questions(part)), named_orders(others) if near else ()

    def _carrying(self, going: Run, requests: tuple[Request, ...], wanted: tuple[Wanted, ...]) -> tuple[Request, ...]:
        """The requests about the files as a dry run shows them: for each file, each of its two requests that would
        send a question, with the names of those it would send (those whose answers are not kept) and the body it
        would send; one request whose answers are all kept, marked so, when it would send none."""
        shown: list[Request] = []
        for item, (first, again) in zip(requests, wanted, strict=True):
            sending = [named for named in (self._missing(going, item, first), self._missing(going, item, again)) if named]
            for named in sending or [first]:
                shown.append(replace(item, questions=tuple(name for name, _ in named), cached=not sending,
                                     body=self._model.body_all(item.text, named)))
        return tuple(shown)

    def _named(self, shown: Request, wanted: tuple[Wanted, ...],
               requests: tuple[Request, ...]) -> tuple[tuple[str, Choice], ...]:
        """The questions a request a dry run shows carries, by the names it says."""
        (first, again), = (pair for item, pair in zip(requests, wanted, strict=True) if item.file == shown.file)
        return tuple(named for named in (*first, *again) if named[0] in shown.questions)

    def _missing(self, going: Run, item: Request,
                 named: tuple[tuple[str, Choice], ...]) -> tuple[tuple[str, Choice], ...]:
        """The questions of a request whose answers are not kept: those it would send."""
        return tuple((name, asked) for name, asked in named if self._answering.kept(going, item.text, asked) is None)

    def _breaks(self, cmd: Review, judging: tuple[CodeFile, ...]) -> dict[str, tuple[str, ...]]:
        """The parts whose `holds` each file judged would break were it to lie there, by the file, read with the
        other files of the app."""
        if not judging:
            return {}
        files = tuple((below_app(file.file), file.text) for file in judging)
        return dict(zip((file.file for file in judging), self._code.breaks(cmd.profile, cmd.app.name, files, cmd.app),
                        strict=True))

    def _evals(self, cmd: Review, words: Words, judging: tuple[CodeFile, ...],
               model: str) -> tuple[tuple[Asking, ...], tuple[EvalRead, ...]]:
        """Each eval of the profile's own that may run, with how it stands and what it would ask of the files judged;
        and how each other one stands, which does not run."""
        record = self._calibrations.get(record_file(cmd.app))
        running: list[Asking] = []
        idle: list[EvalRead] = []
        for asked in words.evals:
            stood = standing(kept_examples(asked, words.never), record, model, (cmd.app.name,), words.mask)
            if stood.state != CALIBRATED:
                idle.append(stood)
                continue
            shown = {below_app(file.file): file for file in judging}
            files = tuple((path, file.text) for path, file in shown.items())
            reads = self._code.reads(cmd.profile, cmd.app.name, asked.asked, files) if files else ()
            running.append((asked, stood, tuple(
                item for found in reads for file in (shown[found.file.file],)
                for item in asked_of(asked, file.file, file.part, masked(file.text, file.imports, cmd.app.name,
                                                                          words.mask, comments=file.comments), found))))
        return tuple(running), tuple(idle)

    def _shown(self, requests: tuple[Request, ...], kept: tuple[Answer | None, ...],
               questions: tuple[Choice, ...]) -> tuple[Request, ...]:
        """The requests as a dry run shows them: each with whether its answer is kept, and the body it would send."""
        return tuple(replace(item, cached=answer is not None, body=self._model.body(item.text, asked))
                     for item, answer, asked in zip(requests, kept, questions, strict=True))
