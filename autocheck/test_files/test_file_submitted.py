from autocheck.autocheck import (
    AutocheckResponse,
    ContentDescriptor,
    ResponseType,
    autocheck,
)


@autocheck(test_title="File Submission")
def test_file_submitted(submitted_file: bytes | None) -> AutocheckResponse:
    """Tests that the hanich submitted a file.

    Use if you need a hanich submission for all tests.
    """
    if submitted_file is not None:
        return AutocheckResponse([], ResponseType.AutoCheck)

    return AutocheckResponse(
        [ContentDescriptor("No File Submitted!", "Comment")],
        ResponseType.Redo,
        segel_only=False,
    )
