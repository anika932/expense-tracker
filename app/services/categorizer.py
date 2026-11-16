def categorize(description, categories):
    """Return the Category whose keyword appears in the description."""
    text = description.lower()
    other = None

    for category in categories:
        if category.name == "Other":
            other = category      # fallback if nothing matches
            continue
        for keyword in (category.keywords or "").split(","):
            keyword = keyword.strip().lower()
            if keyword and keyword in text:
                return category

    return other