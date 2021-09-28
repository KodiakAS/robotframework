*** Orthogonal Factors ***
ANIMAL       ["cat", "dog"]
COLOR        ["red", "green", "blue"]
SIZE        ["big", "small"]

*** Variables ***
${AGE}        5
${NAME}       dog

*** Test Cases ***

if case
    IF    "$${ANIMAL}" == "dog"
        Log    $${SIZE}$${COLOR}$${ANIMAL}
    ELSE IF   "$${ANIMAL}" == "cat"
        Log    mew
    ELSE
        Log    unknown
    END

if case2
    IF    "$${ANIMAL}" == "dog"
        Log    wang
    ELSE IF   "$${ANIMAL}" == "cat"
        Log    mew
    ELSE
        Log    unknown
    END

*** Keywords ***
Test
    Log   Test begin
    