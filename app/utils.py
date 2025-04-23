def extract_data(xpath, page):
    """Extract data from a specific xpath or return empty string if not found"""
    if page.locator(xpath).count() > 0:
        return page.locator(xpath).inner_text()
    return ""