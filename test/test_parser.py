from agent.io.parser import FileParser

def test_extract_files_with_code_blocks():
    response = (
        "Create a file modules/test.py\n"
        "[code]\n"
        "class Test:\n"
        "    def hello(self):\n"
        "        return 'Hello'\n"
        "[/code]"
    )
    result = FileParser.extract_files(response)
    assert "modules/test.py" in result
    assert "class Test:" in result["modules/test.py"]

def test_extract_files_with_hashes():
    response = (
        "# Create a file modules/test.py\n"
        "# [code]\n"
        "class Test:\n"
        "    pass\n"
        "# [/code]"
    )
    result = FileParser.extract_files(response)
    assert "modules/test.py" in result
    assert "class Test:" in result["modules/test.py"]