from typing import Optional

import pytest

from ..autocheck import autocheck, AutocheckResponse, ResponseType, ContentDescriptor


@pytest.mark.stop_on_failure
@autocheck(test_title="File Submission")
def test_file_submitted(submitted_file: Optional[bytes]) -> AutocheckResponse:
    """
    Tests that the hanich submitted a file. This fails the entire autocheck
    Use if you need a hanich submission for all tests
    And put it first (sorry...)
    """
    if submitted_file is not None:
        return AutocheckResponse([], ResponseType.AutoCheck)

    return AutocheckResponse([ContentDescriptor("No File Submitted!", "Comment")], ResponseType.Redo, segel_only=False)
