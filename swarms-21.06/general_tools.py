#%%
def extract_courses_data(filename: str) -> str:
    """
    Reads course data from the specified file and returns its content.
    
    Args:
        filename (str): The name of the file containing course data.

    Returns:
        str: The content of the file as a string.
    
    Example:
        >>> content = extract_courses_data("courses.txt")
        >>> print(content)
    """
    
    with open(filename, "r", encoding="utf-8") as file:
        return file.read()
