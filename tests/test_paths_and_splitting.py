import unittest
from pathlib import Path

from ocr_translation.main import _output_paths
from ocr_translation.translation.translator import _sentence_split


class PathAndSplittingTests(unittest.TestCase):
    def test_output_paths_keep_input_folder_and_add_suffixes(self) -> None:
        english, romanian = _output_paths(Path("/tmp/My Book.pdf"))

        self.assertEqual(english, Path("/tmp/My Book_extracted_en.docx"))
        self.assertEqual(romanian, Path("/tmp/My Book_translated_ro.docx"))

    def test_sentence_split_keeps_simple_sentences(self) -> None:
        self.assertEqual(
            _sentence_split("First sentence. Second sentence! Third?"),
            ["First sentence.", "Second sentence!", "Third?"],
        )


if __name__ == "__main__":
    unittest.main()
