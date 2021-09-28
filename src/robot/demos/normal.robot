*** Variables ***
${AGE}        5

*** Test Cases ***
show_animal_color
    Test
    Log    I am ${AGE} years old

show_animal
    Test
    Log    das

*** Keywords ***
Test
    Log   Test begin
    