import types
import unittest

import pandas as pd

from cjml import ActualJourney
from icons import IconSelect
from parser import extractJourneyInfo, extract_journey_end_user_type


class EndUserNodeNameTests(unittest.TestCase):
    def test_extracts_legacy_journey_title_from_read_excel_header(self):
        dataframe = pd.DataFrame(
            [
                ["End-user name", None, None, "Customer 1"],
                ["Start of journey", None, None, "2024-02-01"],
                ["Journey status", None, None, "Completed"],
                ["Journey short summary", None, None, "Short summary"],
                ["Journey long summary", None, None, "Long summary"],
                [None, None, None, None],
            ],
            columns=["Online shopping", "Unnamed: 1", "Unnamed: 2", "Unnamed: 3"],
        )

        journey = extractJourneyInfo(dataframe, 1)

        self.assertEqual(journey.journeyTitle, "Online shopping")
        self.assertEqual(journey.journeyStartDate, "2024-02-01")

    def test_extracts_journey_title_from_read_excel_header(self):
        dataframe = pd.DataFrame(
            [
                ["End-user name", None, None, "Customer"],
                ["Start of journey", None, None, "2024-12-05"],
                ["Journey status", None, None, "Completed"],
                ["Journey short summary", None, None, "Short summary"],
                ["Journey long summary", None, None, "Long summary"],
                ["Journey creator", None, None, "Creator"],
            ],
            columns=["Journey title", "Unnamed: 1", "Unnamed: 2", "Unnamed: 3"],
        )

        journey = extractJourneyInfo(dataframe, 1)

        self.assertEqual(journey.journeyTitle, "Journey title")

    def test_extracts_journey_title_from_template_metadata(self):
        dataframe = pd.DataFrame(
            [
                ["Journey title", None, None, "Patient journey"],
                ["End-user name", None, None, "Customer"],
                ["Start of journey", None, None, "2024-12-05"],
                ["Journey status", None, None, "Completed"],
                ["Journey short summary", None, None, "Short summary"],
                ["Journey long summary", None, None, "Long summary"],
            ],
            columns=list("ABCD"),
        )

        journey = extractJourneyInfo(dataframe, 1)

        self.assertEqual(journey.journeyTitle, "Patient journey")
        self.assertEqual(journey.journeyStartDate, "2024-12-05")

    def test_serializes_journey_start_date(self):
        journey = ActualJourney()
        journey.journeyID = 1
        journey.journeyStartDate = "2024-12-05"

        self.assertIn(
            "<journeyStartDate>2024-12-05</journeyStartDate>",
            journey.toXML([]),
        )

    def test_extracts_end_user_type_from_labeled_cell(self):
        dataframe = pd.DataFrame(
            [[None, None, None, None], [None, None, None, None], ["End-user type", None, None, "Customer"]],
            columns=list("ABCD"),
        )

        self.assertEqual(extract_journey_end_user_type(dataframe), "Customer")

    def test_extracts_end_user_type_from_symbolic_label(self):
        dataframe = pd.DataFrame(
            [[None, None, None, None], [None, None, None, None], ["#sym:journeyEndUserType", None, None, "Patient"]],
            columns=list("ABCD"),
        )

        self.assertEqual(extract_journey_end_user_type(dataframe), "Patient")

    def test_extracts_end_user_type_from_label_row_in_actual_template_layout(self):
        dataframe = pd.DataFrame(
            [
                ["End-user name", None, None, "Customer"],
                ["End-user type", None, None, "Customer"],
                ["Start of journey", None, None, "2024-12-05"],
            ],
            columns=list("ABCD"),
        )

        self.assertEqual(extract_journey_end_user_type(dataframe), "Customer")

    def test_end_user_node_defaults_to_end_user(self):
        journey = ActualJourney()
        journey.journeyEndUserType = ""

        self.assertEqual(journey.get_end_user_node_name(), "endUser")

    def test_end_user_node_uses_supported_type_mapping(self):
        journey = ActualJourney()

        for raw_value, expected in [
            ("Customer", "customer"),
            ("user", "user"),
            ("employee", "employee"),
            ("patient", "patient"),
            ("citizen", "citizen"),
        ]:
            journey.journeyEndUserType = raw_value
            self.assertEqual(journey.get_end_user_node_name(), expected)

    def test_get_icons_falls_back_to_generated_placeholders_when_assets_are_missing(self):
        selector = IconSelect({"patient": "Patient"})

        images = selector.get_icons()

        self.assertEqual(len(images), len(selector.options))
        self.assertTrue(all(img is not None for img in images))

    def test_match_icons_keeps_selected_icon_names_in_actor_mapping(self):
        selector = object.__new__(IconSelect)
        actors = {"patient": ["Patient", "Patient Group"], "doctor": ["Doctor", "Doctor Group"]}
        actor_values = [["Patient", "Option 1"], ["Doctor", "Option 2"]]
        root = types.SimpleNamespace(destroy=lambda: None)

        selector.match_icons(actors, actor_values, root)

        self.assertEqual(actors["patient"], ["Patient", "Option 1"])
        self.assertEqual(actors["doctor"], ["Doctor", "Option 2"])


if __name__ == "__main__":
    unittest.main()
