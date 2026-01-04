import unittest
from unittest.mock import patch

from fucker import ExamCtx


class ExamCtxGetQuestionAnswerTests(unittest.TestCase):
    def _make_ctx(self) -> ExamCtx:
        ctx = ExamCtx.__new__(ExamCtx)
        ctx.allAnswerCache = {}
        ctx.answerCache = {}
        ctx.referenceMaterials = []
        ctx.unsupportedQuestionTypes = set()
        return ctx

    @patch("fucker.time.sleep", return_value=None)
    def test_no_choices_returns_tuple(self, _sleep):
        ctx = self._make_ctx()
        q = {"id": 1, "questionType": 1, "content": "Q", "optionVos": []}
        answer, note = ctx.getQuestionAnswer(q)
        self.assertIsNone(answer)
        self.assertEqual(note, "no choices")

    @patch("fucker.time.sleep", return_value=None)
    def test_single_choice_returns_tuple(self, _sleep):
        ctx = self._make_ctx()
        q = {
            "id": 2,
            "questionType": 1,
            "content": "Q",
            "optionVos": [{"id": 11, "content": "A"}],
        }
        answer, note = ctx.getQuestionAnswer(q)
        self.assertEqual(answer, [11])
        self.assertEqual(note, "only option")

    @patch("fucker.time.sleep", return_value=None)
    def test_cached_returns_tuple(self, _sleep):
        ctx = self._make_ctx()
        ctx.allAnswerCache = {"3": {"answer": "1#@#2"}}
        q = {
            "id": 3,
            "questionType": 1,
            "version": 1,
            "content": "Q",
            "optionVos": [{"id": 1, "content": "A"}, {"id": 2, "content": "B"}],
        }
        answer, note = ctx.getQuestionAnswer(q)
        self.assertEqual(answer, ["1", "2"])
        self.assertEqual(note, "cached")

    def test_unsupported_type_returns_tuple(self):
        ctx = self._make_ctx()
        q = {"id": 4, "questionType": 4, "content": "Q", "optionVos": []}
        answer, note = ctx.getQuestionAnswer(q)
        self.assertIsNone(answer)
        self.assertIn("unsupported type", note)
        self.assertIn(4, ctx.unsupportedQuestionTypes)


class ExamCtxStartFuckTests(unittest.TestCase):
    def test_startFuck_sets_examStopped_on_error(self):
        ctx = ExamCtx.__new__(ExamCtx)
        ctx.examTestId = 1
        ctx.courseId = 1
        ctx.examPaperId = 1
        ctx.knowledgeId = 1
        ctx.progress_view = False
        ctx.examStopped = False
        ctx.readAnswerCache = lambda examTestId: ({}, {})
        ctx.openExam = lambda: True
        ctx.getSheetContent = lambda: (_ for _ in ()).throw(ValueError("boom"))

        with self.assertRaises(ValueError):
            ctx.startFuck(referenceMaterials=[])

        self.assertTrue(ctx.examStopped)


if __name__ == "__main__":
    unittest.main()

