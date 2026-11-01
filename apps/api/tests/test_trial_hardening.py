import unittest

from fastapi import FastAPI, Response
from fastapi.responses import JSONResponse
from fastapi.testclient import TestClient
from pydantic import BaseModel

from app.auth import (
    clear_session_cookie,
    cookie_ok,
    is_protected_path,
    password_ok,
    request_authorized,
    session_token,
    set_session_cookie,
)
from app.config import settings
from app.engine.chat import (
    _job_facts,
    answer_from_job,
    match_resolve_intent,
    portfolio_digest,
    workspace_fallback,
)
from app.jobs_store import approve_reason, match_client_row, normalize_client_name


def _tiny_app() -> FastAPI:
    app = FastAPI()

    @app.middleware("http")
    async def require_pw(request, call_next):
        if settings.bridgit_password and is_protected_path(request.url.path):
            if not request_authorized(request):
                return JSONResponse({"detail": "unauthorized"}, status_code=401)
        return await call_next(request)

    @app.get("/health")
    def health():
        return {"ok": True}

    @app.get("/meta/app")
    def app_meta():
        return {"password_required": True, "env": "local", "show_demo": True}

    @app.get("/jobs")
    def jobs():
        return {"jobs": []}

    class Body(BaseModel):
        pw: str = ""

    @app.post("/meta/password-check")
    def check(body: Body, response: Response):
        if not password_ok(body.pw):
            return {"ok": False}
        set_session_cookie(response)
        return {"ok": True}

    @app.post("/meta/logout")
    def logout(response: Response):
        clear_session_cookie(response)
        return {"ok": True}

    return app


class ClientNameTests(unittest.TestCase):
    def test_collapse_whitespace(self):
        self.assertEqual(normalize_client_name("  Hit   Hunters Ltd  "), "Hit Hunters Ltd")

    def test_case_insensitive_reuse(self):
        rows = [{"id": "1", "name": "Hit Hunters Ltd"}]
        hit = match_client_row("hit hunters ltd", rows)
        self.assertIsNotNone(hit)
        self.assertEqual(hit["id"], "1")

    def test_does_not_title_case_existing(self):
        rows = [{"id": "1", "name": "Hit Hunters Ltd"}]
        hit = match_client_row("HIT HUNTERS LTD", rows)
        self.assertEqual(hit["name"], "Hit Hunters Ltd")

    def test_unknown_is_none(self):
        self.assertIsNone(match_client_row("Koliqi", [{"name": "Hit Hunters Ltd"}]))


class ApproveGateTests(unittest.TestCase):
    def test_ready_with_no_questions(self):
        self.assertIsNone(approve_reason("ready_for_review", 0))

    def test_already_approved(self):
        self.assertIsNone(approve_reason("approved", 0))

    def test_open_questions_block(self):
        self.assertEqual(approve_reason("ready_for_review", 3), "open questions remain")

    def test_needs_input_blocks(self):
        self.assertEqual(approve_reason("needs_input", 0), "job is not ready for review")


class PasswordAuthTests(unittest.TestCase):
    def setUp(self):
        self._old = settings.bridgit_password
        settings.bridgit_password = "test-secret-ok"
        self.client = TestClient(_tiny_app())

    def tearDown(self):
        settings.bridgit_password = self._old

    def test_wrong_password(self):
        self.assertFalse(password_ok("nope"))
        self.assertTrue(password_ok("test-secret-ok"))

    def test_jobs_unauthorized_without_cookie(self):
        res = self.client.get("/jobs")
        self.assertEqual(res.status_code, 401)

    def test_header_unlocks_jobs_route(self):
        res = self.client.get("/jobs", headers={"X-Bridgit-Password": "test-secret-ok"})
        self.assertEqual(res.status_code, 200)

    def test_login_sets_cookie(self):
        bad = self.client.post("/meta/password-check", json={"pw": "wrong"})
        self.assertEqual(bad.json().get("ok"), False)
        good = self.client.post("/meta/password-check", json={"pw": "test-secret-ok"})
        self.assertEqual(good.json().get("ok"), True)
        self.assertTrue(cookie_ok(session_token()))
        res = self.client.get("/jobs")
        self.assertEqual(res.status_code, 200)

    def test_logout_clears_cookie(self):
        self.client.post("/meta/password-check", json={"pw": "test-secret-ok"})
        self.assertEqual(self.client.get("/jobs").status_code, 200)
        out = self.client.post("/meta/logout")
        self.assertEqual(out.json().get("ok"), True)
        self.assertEqual(self.client.get("/jobs").status_code, 401)

    def test_health_stays_open(self):
        res = self.client.get("/health")
        self.assertEqual(res.status_code, 200)

    def test_app_meta_stays_open(self):
        res = self.client.get("/meta/app")
        self.assertEqual(res.status_code, 200)
        self.assertIn("show_demo", res.json())


class ChatIntentTests(unittest.TestCase):
    def test_plain_account_codes_first_open_question(self):
        ex = [
            {
                "id": "e1",
                "kind": "unknown",
                "description": "Bright Forge Ltd",
                "question": "New payee Bright Forge Ltd",
                "proposed_account": "",
            }
        ]
        intent = match_resolve_intent("Motor", ex, ["Motor", "Phone"])
        self.assertEqual(intent["intent"], "resolve")
        self.assertEqual(intent["exception_id"], "e1")
        self.assertEqual(intent["account_name"], "Motor")

    def test_question_does_not_resolve(self):
        ex = [{"id": "e1", "kind": "unknown", "description": "O2", "question": "O2?"}]
        self.assertIsNone(match_resolve_intent("why is O2 in Phone?", ex, ["Phone"]))

    def test_named_payee_and_account(self):
        ex = [
            {"id": "e1", "kind": "unknown", "description": "Bright Forge Ltd", "question": "New payee"},
            {"id": "e2", "kind": "unknown", "description": "Lime Cycle Hire", "question": "New payee"},
        ]
        intent = match_resolve_intent("code bright forge to Salaries", ex, ["Salaries", "Motor"])
        self.assertEqual(intent["exception_id"], "e1")
        self.assertEqual(intent["account_name"], "Salaries")

    def test_keep_both_on_duplicate(self):
        ex = [{"id": "d1", "kind": "duplicate", "description": "Tesco Stores", "question": "Keep both or repeat?"}]
        intent = match_resolve_intent("keep both", ex, [])
        self.assertEqual(intent["action"], "accept")

    def test_bank_rec_from_job_facts(self):
        job = {
            "engine": {"bank_rec": {"ok": True, "difference": 0.0}},
            "exceptions": [],
        }
        reply = answer_from_job("does the bank rec tie?", job, [], [])
        self.assertIn("ties", reply.lower())

    def test_learned_mappings_from_job_facts(self):
        job = {"engine": {}, "exceptions": []}
        maps = [{"description_pattern": "O2", "account_name": "Phone", "account_code": "Phone"}]
        reply = answer_from_job("what have you learned for this client?", job, maps, [])
        self.assertIn("1 saved payee", reply)

    def test_job_facts_include_knowledge(self):
        facts = _job_facts(
            {
                "client_name": "Northbridge Demo Ltd",
                "chat": [{"role": "user", "text": "code tesco to motor"}],
                "documents": [{"kind": "bank", "file_name": "bank.csv"}],
                "engine": {"last_error": "Processing failed. Check the bank file and retry."},
            },
            [],
            ["Motor"],
            [{"description_pattern": "O2", "account_name": "Phone", "vat_code": "SR"}],
        )
        self.assertEqual(facts["mapping_count"], 1)
        self.assertEqual(len(facts["recent_chat"]), 1)
        self.assertEqual(facts["uploaded"][0]["file"], "bank.csv")
        self.assertTrue(facts["last_error"])

    def test_working_file_question_when_process_failed(self):
        job = {
            "status": "queued",
            "engine": {"last_error": "Processing failed. Check the bank file and retry."},
            "exceptions": [],
            "transactions": [],
        }
        reply = answer_from_job("is our working file ready?", job, [], [])
        self.assertIn("did not finish", reply.lower())

    def test_what_files_lists_uploads(self):
        job = {
            "status": "needs_input",
            "engine": {},
            "exceptions": [],
            "documents": [
                {"kind": "bank", "file_name": "northbridge-bank.csv"},
                {"kind": "supporting", "file_name": "p60.pdf"},
                {"kind": "working_file", "file_name": "bridgit.xlsx"},
            ],
        }
        reply = answer_from_job("what files are on this job?", job, [], [])
        self.assertIn("northbridge-bank.csv", reply)
        self.assertIn("p60.pdf", reply)
        self.assertNotIn("bridgit.xlsx", reply)

    def test_working_file_question_when_processed(self):
        job = {
            "status": "needs_input",
            "transaction_count": 16,
            "engine": {"coded": 11, "processed_at": "2026-10-25T00:00:00Z"},
            "exceptions": [{}],
            "transactions": [{}] * 16,
        }
        reply = answer_from_job("is our working file ready?", job, [], [])
        self.assertIn("16", reply)


class WorkspaceChatTests(unittest.TestCase):
    def test_desk_chat_does_not_need_a_job(self):
        self.assertTrue(is_protected_path("/meta/chat"))
        reply = workspace_fallback("how are we doing?", [])
        self.assertIn("no jobs", reply.lower())

    def test_digest_names_a_client(self):
        jobs = [{
            "id": "1",
            "title": "Meridian live",
            "client_name": "Meridian Studio Ltd",
            "status": "needs_input",
            "job_type_label": "Year-end",
            "engine": {"coded": 10, "exceptions": 2, "bank_rec": {"ok": True, "difference": 0}},
            "documents": [{"kind": "bank", "file_name": "bank.csv"}, {"kind": "working_file", "file_name": "out.xlsx"}],
        }]
        digest = portfolio_digest(jobs)
        self.assertEqual(digest[0]["files"], ["bank.csv"])
        reply = workspace_fallback("what about meridian studio ltd", jobs)
        self.assertIn("Meridian", reply)


if __name__ == "__main__":
    unittest.main()
