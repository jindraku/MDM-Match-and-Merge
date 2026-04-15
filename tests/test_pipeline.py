"""Unit tests for the Week 1 MDM pipeline."""

import unittest

from src.config import THRESHOLDS
from src.embedding import generate_candidate_pairs
from src.matcher import classify, evaluate_candidate
from src.profiling import build_profile
from src.preprocessing import RawRecord, normalize_text, preprocess_record


class PipelineTests(unittest.TestCase):
    def test_normalize_text_expands_abbreviations(self) -> None:
        self.assertEqual(normalize_text("ABC Co. Ltd"), "abc company limited")

    def test_preprocess_record_handles_multilingual_tokens(self) -> None:
        record = RawRecord(
            record_id="3",
            company_name="Sociedad Internacional",
            address="45 Calle Mayor",
            city="Madrid",
            country="Spain",
        )
        processed = preprocess_record(record)
        self.assertEqual(processed.normalized_company_name, "company international")
        self.assertEqual(processed.normalized_address, "45 street mayor")
        self.assertEqual(processed.company_language, "possible_non_english")
        self.assertEqual(processed.address_language, "possible_non_english")

    def test_profile_report_captures_duplicate_rate(self) -> None:
        records = [
            RawRecord("1", "ABC Co.", "12 King St.", "London", "UK", "ABC Company"),
            RawRecord("2", "ABC Company", "12 King Street", "London", "UK", ""),
            RawRecord("3", "Unique Corp", "9 Market Rd", "Leeds", "UK", ""),
        ]
        report = build_profile(records)
        self.assertEqual(report.record_count, 3)
        self.assertEqual(report.exact_duplicate_pairs, 1)
        self.assertGreater(report.duplicate_rate, 0)

    def test_candidate_generation_finds_obvious_duplicate(self) -> None:
        records = [
            preprocess_record(
                RawRecord("1", "ABC Co.", "12 King St.", "London", "UK", "ABC Company")
            ),
            preprocess_record(
                RawRecord("2", "ABC Company", "12 King Street", "London", "UK", "")
            ),
        ]
        candidates = generate_candidate_pairs(records, THRESHOLDS.candidate_similarity)
        self.assertEqual(len(candidates), 1)
        self.assertEqual(candidates[0].left_record_id, "1")
        self.assertEqual(candidates[0].right_record_id, "2")

    def test_evaluate_candidate_scores_exact_match_high(self) -> None:
        records = [
            preprocess_record(
                RawRecord("1", "ABC Co.", "12 King St.", "London", "UK", "ABC Company")
            ),
            preprocess_record(
                RawRecord("2", "ABC Company", "12 King Street", "London", "UK", "")
            ),
        ]
        records_by_id = {record.record_id: record for record in records}
        candidate = generate_candidate_pairs(records, THRESHOLDS.candidate_similarity)[0]
        result = evaluate_candidate(candidate, records_by_id)
        self.assertTrue(result.exact_match)
        self.assertEqual(result.classification, "High Confidence Match")
        self.assertGreaterEqual(result.final_score, 85)

    def test_classify_uses_expected_thresholds(self) -> None:
        self.assertEqual(classify(90), "High Confidence Match")
        self.assertEqual(classify(60), "Potential Match")
        self.assertEqual(classify(59), "Non-Match")


if __name__ == "__main__":
    unittest.main()
