"""Unit tests for preprocessing and MDM golden-record helpers."""

from pathlib import Path
import unittest

from src.config import THRESHOLDS
from src.embedding import generate_candidate_pairs
from src.golden_record import assemble_golden_records
from src.match_pipeline import run_end_to_end_match_pipeline
from src.mdm_loader import load_party_groups
from src.matcher import classify, evaluate_candidate
from src.profiling import build_profile
from src.preprocessing import RawRecord, normalize_text, preprocess_record
from src.runtime import DEFAULT_RUNTIME_SETTINGS


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
        report = build_profile(Path("MDM- Match and Merge data"))
        self.assertEqual(report.party_count, 100)
        self.assertGreater(report.table_row_counts["individual"], 0)
        self.assertGreater(report.duplicate_rate, 0)

    def test_load_party_groups_reads_real_schema(self) -> None:
        groups = load_party_groups(Path("MDM- Match and Merge data"))
        self.assertEqual(len(groups), 100)
        self.assertTrue(all(group.party.party_id for group in groups))
        self.assertTrue(any(len(group.individuals) > 1 for group in groups))

    def test_golden_record_assembly_returns_best_ids(self) -> None:
        groups = load_party_groups(Path("MDM- Match and Merge data"))
        golden_records = assemble_golden_records(groups[:2])
        self.assertEqual(len(golden_records), 2)
        self.assertTrue(golden_records[0].best_individual_id)
        self.assertTrue(golden_records[0].best_phone_id)
        self.assertTrue(golden_records[0].best_address_id)

    def test_end_to_end_match_pipeline_returns_scored_results(self) -> None:
        groups = load_party_groups(Path("MDM- Match and Merge data"))
        output = run_end_to_end_match_pipeline(groups, settings=DEFAULT_RUNTIME_SETTINGS)
        self.assertEqual(len(output.golden_records), len(groups))
        self.assertGreater(len(output.match_results), 0)
        self.assertIn(
            output.match_results[0].classification,
            {"High Confidence Match", "Potential Match", "Non-Match"},
        )
        self.assertTrue(output.match_results[0].reasoning)

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
