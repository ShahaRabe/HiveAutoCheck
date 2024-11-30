# TL;DR
Here before you is a simple auto-checking infrasturcture for Hive.<br>
For examples on how to use it please jump forward to [the examples](#some-examples)<br>
## Important Notes
1. If some responses are marked as segel-only and some aren't than 2 responses would be posted - one for all the student facing responses and one for segel facing
1. In the same category (segel only or student facing) there is a difference between the result (AutoCheck, Done or Redo) the most decisive is the one chosen (Redo, then Done and finaly AutoCheck).
1. Same goes on hide checker name - if even one test chose to hide it it will be hidden
1. Both segel-only and hide-checker-name default to True
# The Longer Version
Hello, happy to have you here.<br>
This project was written after a little pain I experienced after being part of a course with insufficient auto checking and with the acknowledgement that Hive may provide a solid foundation to write auto checks but it has a long way to go to be intuitive, and that every course has a different view on creating an auto checking infrastructure.<br>
# Technologies Chosen
To integrate into hive's autochecks the obvious part was packing the whole system into a docker container.<br>
And to make your lives easier in integrating this system into your course i chose to write it using python 3.12 and pytest (that looks at any python file not just the ones starting with test) with a bunch of prewritten fixtures.
So the minimum work you should do is write a single test with the `@autocheck` decorator and a Dockerfile that inherits from this project's image, sets a few environemnt variables and includes your amazing test files somewhere under `/test` inside the docker (preferably a subdirectory to avoid overwriting any of the files).
# Wait... A bunch of fixtures?
Yes, and a decorator! Here they are:<br>
### Decorator
Each test needs to be marked with the `@autocheck` decorator - that handles all the logic for posing comments.<br>
signature: `@autocheck(test_title = None)`<br>
`test_title` is used as a title in the comment posted from this test on the exercise (whether it's segel only or not). if it's equal to None then the test function name is used.
### Fixtures
|Fixture|Type|Purpose|Scope|
|-------|----|-------|-----|
|`input_json`|`Dict[str, Any]`|Get the contents of the json given by Hive|Session|
|`exercise`|`Exercise`|Use Hive's API to get info about the exercise|Session|
|`original_file_path`|`Optional[Path]`|The path where the file, as submitted by the student, is saved - None if no file was submitted|Session|
|`submitted_file`|`Optional[bytes]`|The contents of the file submitted by the student - None is no file was submitted|Session|
|`extracted_path`|`Optional[Path]`|The path to which the contents of the file submitted by the student is extracted to - None if no file was submitted or the file submitted is not a archive|Session|
# Tell me more about the tests themselves
So as mentioned you have to use the `@autotest` decorator.<br>
In addition you need to return an `AutocheckResponse` item that is defined in [autocheck.py](autocheck/autocheck.py).<br>
The test title (either a given title or the test name by default) MUST be unique as it's used as a dictionary key.<br>
Anything beyond that is up to your imagination - go wild!<br>
If any test throws you'd be noticed by a segel_only response by the infrastructure.
# Some Examples
Examplary `autocheck.Dockerfile`:
```Dockerfile
FROM autocheck:latest

ENV API_USER=admin
ENV API_PASS=admin
ENV HIVE_HOST=https://<hive-ip>

COPY *.py /test/test_files
```
Some tests:
```python
import os
from pathlib import Path
from typing import Optional

from exercise import Exercise
from autocheck import AutocheckResponse, ResponseType, ContentDescriptor, autocheck


# This is a test that does stuff with the info from the submitted exercise
@autocheck
def test_exercise(exercise: Exercise):
    exercise_string_id = f"{exercise.subject_letter}_{exercise.subject_name}/{exercise.module_name}/{exercise.name}"
    return AutocheckResponse([ ContentDescriptor(exercise_string_id, "Comment") ], ResponseType.AutoCheck, False)


# This is a test that does stuff with th file the student submitted and the files that could be extracted from it, also the title of it's response would be "File Check"
@autocheck(test_title="File Check")
def test_files(submitted_file: Optional[bytes], original_file_path: Optional[Path], extracted_path: Optional[Path]):
    if original_file_path:
        with original_file_path.open('rb') as orig:
            content = orig.read()
        
        string = ['good job, the files match' if submitted_file == content else 'What just happened?']

        if extracted_path:
            for root, _, files in os.walk(extracted_path):
                string += [str(Path(root) / file) for file in files]
    else:
        string = ['No file submitted']
        
    return AutocheckResponse([ ContentDescriptor('\n'.join(string), "Comment") ], ResponseType.AutoCheck if string[0] != 'What just happened?' else ResponseType.Redo)

```