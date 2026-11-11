import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from agentic_ads.cli import reproduce


CONFIG_TEMPLATE = """
[study]
id = "test-run"
seed = 1
persona_replicates = 1
ad_id = "test-ad"
[design]
preferences = ["price_first", "performance_first"]
histories = ["budget_pressure", "product_failure"]
price_contexts = ["near_benchmark", "favorable_contrast"]
quality_contexts = ["near_benchmark", "favorable_contrast"]
prompt_variants = ["a"]
models = ["mock"]
[runner]
engine = "mock"
temperature = 0.0
[outputs]
root = "{output_root}"
"""


def prepare_repo(root: Path, output_root: str = "tmp/generated") -> None:
    (root / "config.toml").write_text(
        CONFIG_TEMPLATE.format(output_root=output_root).strip() + "\n",
        encoding="utf-8",
    )
    required = {
        "data/raw/manifest.json": "{}\n",
        "prompts/persona_compiler_v1.txt": "compiler\n",
        "prompts/a.txt": "response\n",
        "schemas/persona.schema.json": "{}\n",
        "schemas/response.schema.json": "{}\n",
    }
    for relative, content in required.items():
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")


class PipelineTests(unittest.TestCase):
    def test_end_to_end_smoke_and_provenance(self):
        with tempfile.TemporaryDirectory() as directory:
            temp_root = Path(directory)
            prepare_repo(temp_root)
            with patch("agentic_ads.cli.repo_root", return_value=temp_root):
                run_dir = reproduce("config.toml")
            summary = json.loads((run_dir / "summary.json").read_text(encoding="utf-8"))
            manifest = json.loads((run_dir / "manifest.json").read_text(encoding="utf-8"))
            response = json.loads(
                (run_dir / "responses.jsonl").read_text(encoding="utf-8").splitlines()[0]
            )
            self.assertEqual(summary["cell_count"], 16)
            self.assertEqual(summary["response_count"], 16)
            self.assertEqual(manifest["counts"]["personas"], 4)
            self.assertGreaterEqual(manifest["runtime_seconds"], 0)
            self.assertIn("prompts/a.txt", manifest["input_sha256"])
            self.assertIn("perceived_claim", response)
            self.assertIn("perceived_intent", response)
            self.assertIn("intended_audience", response)

    def test_repeated_runs_have_distinct_directories(self):
        with tempfile.TemporaryDirectory() as directory:
            temp_root = Path(directory)
            prepare_repo(temp_root)
            with patch("agentic_ads.cli.repo_root", return_value=temp_root):
                first = reproduce("config.toml")
                second = reproduce("config.toml")
            self.assertNotEqual(first, second)
            self.assertTrue(first.is_dir())
            self.assertTrue(second.is_dir())

    def test_rejects_absolute_and_traversing_paths_before_output(self):
        with tempfile.TemporaryDirectory() as directory:
            temp_root = Path(directory)
            prepare_repo(temp_root, output_root="../escape")
            with patch("agentic_ads.cli.repo_root", return_value=temp_root):
                with self.assertRaisesRegex(ValueError, "outputs.root escapes"):
                    reproduce("config.toml")
                with self.assertRaisesRegex(ValueError, "config path must be relative"):
                    reproduce(str(temp_root / "config.toml"))
            self.assertFalse((temp_root.parent / "escape").exists())

    def test_rejects_protected_repository_output_path(self):
        with tempfile.TemporaryDirectory() as directory:
            temp_root = Path(directory)
            prepare_repo(temp_root, output_root="src/generated")
            with patch("agentic_ads.cli.repo_root", return_value=temp_root):
                with self.assertRaisesRegex(ValueError, "outputs.root must be under"):
                    reproduce("config.toml")
            self.assertFalse((temp_root / "src/generated").exists())


if __name__ == "__main__":
    unittest.main()
