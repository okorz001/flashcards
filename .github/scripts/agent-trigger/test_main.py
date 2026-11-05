import unittest

import main

REPO = "okorz001/flashcards"


class DecideLabel(unittest.TestCase):
    def test_collaborator_labels_collaborator_issue_starts_implement(self):
        for role in ("admin", "maintain", "write"):
            for association in ("OWNER", "COLLABORATOR"):
                with self.subTest(role=role, association=association):
                    decision = main.decide_label(role, association, 7, False)
                    self.assertEqual(decision, main.Decision("run", "implement", 7))

    def test_sender_without_write_is_skipped(self):
        for role in ("read", "triage", "none"):
            with self.subTest(role=role):
                decision = main.decide_label(role, "OWNER", 7, False)
                self.assertEqual(decision, main.Decision("skip"))

    def test_issue_opened_by_non_collaborator_removes_label(self):
        for association in ("NONE", "CONTRIBUTOR", "MEMBER", "FIRST_TIMER"):
            with self.subTest(association=association):
                decision = main.decide_label("admin", association, 7, False)
                self.assertEqual(decision, main.Decision("remove_label", issue=7))

    def test_open_pr_moves_issue_to_with_agent(self):
        decision = main.decide_label("admin", "OWNER", 7, True)
        self.assertEqual(decision, main.Decision("move_to_with_agent", issue=7))

    def test_non_collaborator_issue_wins_over_open_pr(self):
        decision = main.decide_label("admin", "NONE", 7, True)
        self.assertEqual(decision, main.Decision("remove_label", issue=7))


class DecideReview(unittest.TestCase):
    def test_non_approving_review_on_agent_issue_starts_review(self):
        for state in ("commented", "changes_requested"):
            for label in ("with-agent", "agent-failed"):
                with self.subTest(state=state, label=label):
                    decision = main.decide_review(state, "OWNER", 7, [label, "enhancement"])
                    self.assertEqual(decision, main.Decision("run", "review", 7))

    def test_approval_is_skipped(self):
        self.assertEqual(main.decide_review("approved", "OWNER", 7, ["with-agent"]), main.Decision("skip"))

    def test_state_comparison_ignores_case(self):
        self.assertEqual(main.decide_review("APPROVED", "OWNER", 7, ["with-agent"]), main.Decision("skip"))

    def test_non_collaborator_reviewer_is_skipped(self):
        decision = main.decide_review("commented", "NONE", 7, ["with-agent"])
        self.assertEqual(decision, main.Decision("skip"))

    def test_unmapped_branch_is_skipped(self):
        decision = main.decide_review("commented", "OWNER", None, [])
        self.assertEqual(decision, main.Decision("skip"))

    def test_issue_in_other_states_is_skipped(self):
        for label in ("needs-triage", "ready-for-agent", "with-collaborator", "agent-blocked"):
            with self.subTest(label=label):
                decision = main.decide_review("commented", "OWNER", 7, [label])
                self.assertEqual(decision, main.Decision("skip"))


class IssueForBranch(unittest.TestCase):
    def test_issue_branch_maps_to_number(self):
        self.assertEqual(main.issue_for_branch("issue-21/foo", REPO, REPO), 21)
        self.assertEqual(main.issue_for_branch("issue-21/foo/bar", REPO, REPO), 21)

    def test_fork_does_not_map(self):
        self.assertIsNone(main.issue_for_branch("issue-21/foo", "other/flashcards", REPO))

    def test_deleted_fork_does_not_map(self):
        self.assertIsNone(main.issue_for_branch("issue-21/foo", None, REPO))

    def test_other_branches_do_not_map(self):
        for ref in ("main", "issue-x/foo", "issue-21", "issue-21foo", "my-issue-21/foo"):
            with self.subTest(ref=ref):
                self.assertIsNone(main.issue_for_branch(ref, REPO, REPO))


class HasOpenIssuePr(unittest.TestCase):
    def test_matching_branch(self):
        prs = [{"headRefName": "issue-7/foo", "isCrossRepository": False}]
        self.assertTrue(main.has_open_issue_pr(prs, 7))

    def test_other_issue_branch(self):
        prs = [{"headRefName": "issue-70/foo", "isCrossRepository": False}]
        self.assertFalse(main.has_open_issue_pr(prs, 7))

    def test_cross_repo_pr_with_matching_name(self):
        prs = [{"headRefName": "issue-7/foo", "isCrossRepository": True}]
        self.assertFalse(main.has_open_issue_pr(prs, 7))

    def test_no_prs(self):
        self.assertFalse(main.has_open_issue_pr([], 7))


if __name__ == "__main__":
    unittest.main()
