from cockpit.shared.utils import normalize_column_name


def test_spaces_become_underscores():
    assert normalize_column_name("Square Feet") == "square_feet"


def test_hash_becomes_number():
    assert normalize_column_name("Bldg #") == "bldg_number"


def test_camel_case_split():
    assert normalize_column_name("camelCase") == "camel_case"


def test_hyphen_preserved():
    assert normalize_column_name("Final Bill - kbtu") == "final_bill_-_kbtu"


def test_double_spaces_deduplicated():
    assert normalize_column_name("Adjusted  Usage") == "adjusted_usage"


def test_all_caps_lowered():
    assert normalize_column_name("ADJUSTED METERS") == "adjusted_meters"


def test_mixed_hash_and_spaces():
    assert normalize_column_name("Building # Name") == "building_number_name"
