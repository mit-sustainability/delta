import re


def normalize_column_name(col_name):
    """Normalize column name to lowercase and replace special characters"""
    col_name = col_name.replace("#", "Number")
    col_name = re.sub(r"([a-z])([A-Z])", r"\1_\2", col_name)
    col_name = col_name.replace(" ", "_")
    col_name = col_name.lower()
    # Remove duplicate underscores
    col_name = re.sub(r"_+", "_", col_name)
    return col_name
