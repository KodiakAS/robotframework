*** Orthogonal Factors ***
ANIMAL       ["cat", "dog"]
COLOR        ["red", "green", "blue"]

*** Variables ***
${AGE}        5
${NAME}       dog

*** Test Cases ***
show_animal_color
    Test
    Log    my $${COLOR} $${ANIMAL} is ${AGE} years old

a_normal_case
    Test
    Log    ${AGE}

show_animal
    Test
    Log    $${ANIMAL}

another_normal_case
    Test
    Log    ${AGE}

loop case
    FOR    ${i}    IN RANGE    10
           Log    $${ANIMAL}
    END

if case
    IF    "$${ANIMAL}" == "dog"
        Log    $${ANIMAL}
    ELSE IF   "$${ANIMAL}" == "cat"
        Log    mew
    ELSE
        Log    unknown
    END

if and loop
    FOR    ${i}    IN RANGE    10
        IF    "$${ANIMAL}" == "dog"
            Log    $${ANIMAL}
        ELSE
            Log    unknown
        END
    END

complex_loop
    FOR    ${i}    IN RANGE    5
        FOR    ${i}    IN RANGE    2
            Log    $${COLOR}$${ANIMAL}
        END
    END

complex_if
    IF    "$${ANIMAL}" == "dog"
        Log    $${ANIMAL}
    ELSE
        IF    "$${ANIMAL}" == "cat"
            Log    $${ANIMAL}
        ELSE
            Log    unknown
        END
    END

*** Keywords ***
Test
    Log   Test begin
    