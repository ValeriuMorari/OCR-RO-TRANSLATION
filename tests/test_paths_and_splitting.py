import unittest
from pathlib import Path

from ocr_translation.gui import BUTTON_TEXT, DONE_TEXT
from ocr_translation.processor import output_paths
from ocr_translation.translation.translator import _sentence_split


class PathAndSplittingTests(unittest.TestCase):
    def test_output_paths_keep_input_folder_and_add_suffixes(self) -> None:
        english, romanian = output_paths(Path("/tmp/My Book.pdf"))

        self.assertEqual(english, Path("/tmp/My Book_extracted_en.docx"))
        self.assertEqual(romanian, Path("/tmp/My Book_translated_ro.docx"))

    def test_sentence_split_keeps_simple_sentences(self) -> None:
        self.assertEqual(
            _sentence_split("First sentence. Second sentence! Third?"),
            ["First sentence.", "Second sentence!", "Third?"],
        )

    def test_gui_text_is_expected_romanian_copy(self) -> None:
        self.assertEqual(BUTTON_TEXT, "CLICK AICI PENTRU A INCARCA PDF")
        self.assertEqual(DONE_TEXT, "AM TERMINAT, BRAVO!, CU DRAG, VALERIU")


if __name__ == "__main__":
    unittest.main()
