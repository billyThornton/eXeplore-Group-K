INSERT INTO location(location_name, location_image_url, clue) 
VALUES('Harrison 101','Harrison.jpg', 'This is the room you started in!');

INSERT INTO location(location_name, location_image_url, clue) 
VALUES('Harrison Desk', 'Harrison.jpg',  'Where might you hand in your physical coursework submissions?');

INSERT INTO location(location_name, location_image_url, clue) 
VALUES('Innovation Babbage','Innovation.jpg', 'The dedicated computer science Linux labs.');

INSERT INTO location(location_name, location_image_url, clue) 
VALUES('Sports Park','SportsPark.jpg', 'The front desk before entering the university gym');

INSERT INTO location(location_name, location_image_url, clue) 
VALUES('Student Health Centre','HealthCenter.jpg', 'Found opposite the Reed Mews Wellbeing Centre, this is where you can come for booked appointments or prescriptions');

INSERT INTO location(location_name, location_image_url, clue) 
VALUES('Peter Chalk and Newman','PeterChalk.jpg', 'A lot of your lectures will be in here; The lecture theaters are named after colours');

INSERT INTO location(location_name, location_image_url, clue) 
VALUES('Forum','Forum.jpg', 'The main building on campus containing places such as the library, seminar rooms and Market Place');

INSERT INTO location(location_name, location_image_url, clue) 
VALUES('Library','Library.jpg', 'A quiet space to work or borrow books from');

INSERT INTO location(location_name, location_image_url, clue) 
VALUES('Innovation Offices','InnovationOffices.jpg', 'These offices belong to your lecturers and personal tutor and can be found opposite Lovelace and Babbage labs');

INSERT INTO office(location_id, office_name) 
VALUES((SELECT location_id FROM location WHERE location_name = 'Innovation Offices'), 'Room 3');

INSERT INTO route(route_name)
VALUES('Standard');

INSERT INTO question(location_id, question_content, multiple_choice_a, multiple_choice_b, multiple_choice_c, multiple_choice_d, answer)
VALUES((SELECT location_id FROM location WHERE location_name='Harrison 101'), 'How many stairs are there to get to this room from the entrance?', '32', '24', '73', '51', 'C');

INSERT INTO question(location_id, question_content, multiple_choice_a, multiple_choice_b, multiple_choice_c, multiple_choice_d, answer)
VALUES((SELECT location_id FROM location WHERE location_name = 'Harrison Desk'), 'Where, from the front desk in the Harrison Building, is the lecture theatre called “Harrison 004”?', 'Opposite the desk, going upstairs', 'Opposite the desk, going downstairs', 'Past the desk, straight on', 'Behind the Desk', 'B');

INSERT INTO question(location_id, question_content, multiple_choice_a, multiple_choice_b, multiple_choice_c, multiple_choice_d, answer)
VALUES((SELECT location_id FROM location WHERE location_name = 'Innovation Babbage'), 'How many monitors are there in the room “Babbage”?', '38', '36', '35', '37', 'D');

INSERT INTO question(location_id, question_content, multiple_choice_a, multiple_choice_b, multiple_choice_c, multiple_choice_d, answer)
VALUES((SELECT location_id FROM location WHERE location_name = 'Sports Park'), 'How many courts are in the covered court building?', '4', '6', '8', '10', 'B');

INSERT INTO question(location_id, question_content, multiple_choice_a, multiple_choice_b, multiple_choice_c, multiple_choice_d, answer)
VALUES((SELECT location_id FROM location WHERE location_name = 'Student Health Centre'), 'From the entrance to the mini car park, where is the NHS centre?', 'Straight on', 'To the left', 'To the right', 'Behind you', 'C');

INSERT INTO question(location_id, question_content, multiple_choice_a, multiple_choice_b, multiple_choice_c, multiple_choice_d, answer)
VALUES((SELECT location_id FROM location WHERE location_name = 'Peter Chalk and Newman'), 'Which lecture theatre is the largest here?', 'Newman Blue', 'Newman Red', 'Newman Green', 'Newman Purple', 'A');

INSERT INTO question(location_id, question_content, multiple_choice_a, multiple_choice_b, multiple_choice_c, multiple_choice_d, answer)
VALUES((SELECT location_id FROM location WHERE location_name = 'Forum'), 'Where are the Exploration Labs in the Forum, from facing away from the info desk?', 'Downstairs, to the left', 'Downstairs, to the right', 'Upstairs, to the left', 'Upstairs, to the right', 'D');

INSERT INTO question(location_id, question_content, multiple_choice_a, multiple_choice_b, multiple_choice_c, multiple_choice_d, answer)
VALUES((SELECT location_id FROM location WHERE location_name = 'Library'), 'For whom are the computers specified to be used by?', 'Professors', 'Students', 'Staff', 'Public', 'B');

INSERT INTO question(location_id, question_content, multiple_choice_a, multiple_choice_b, multiple_choice_c, multiple_choice_d, answer)
VALUES((SELECT location_id FROM location WHERE location_name = 'Innovation Offices'), 'What does the sign behind the Cafe say?', 'Flavour by nature', 'Fun times with friends', 'A latte fun', 'Coffee time', 'A');

INSERT INTO route_location_bridge(route_id, location_id, sequence_order, question_id)
VALUES((SELECT route_id FROM route WHERE route_name = 'Standard'), (SELECT location_id FROM location WHERE location_name = 'Harrison 101'), 0, NULL);

INSERT INTO route_location_bridge(route_id, location_id, sequence_order, question_id)
VALUES((SELECT route_id FROM route WHERE route_name = 'Standard'), (SELECT location_id FROM location WHERE location_name = 'Harrison Desk'), 1, 1);

INSERT INTO route_location_bridge(route_id, location_id, sequence_order, question_id)
VALUES((SELECT route_id FROM route WHERE route_name = 'Standard'), (SELECT location_id FROM location WHERE location_name = 'Innovation Babbage'), 2, 2);

INSERT INTO route_location_bridge(route_id, location_id, sequence_order, question_id)
VALUES((SELECT route_id FROM route WHERE route_name = 'Standard'), (SELECT location_id FROM location WHERE location_name = 'Sports Park'), 3, 3);

INSERT INTO route_location_bridge(route_id, location_id, sequence_order, question_id)
VALUES((SELECT route_id FROM route WHERE route_name = 'Standard'), (SELECT location_id FROM location WHERE location_name = 'Peter Chalk and Newman'), 4, 4);

INSERT INTO route_location_bridge(route_id, location_id, sequence_order, question_id)
VALUES((SELECT route_id FROM route WHERE route_name = 'Standard'), (SELECT location_id FROM location WHERE location_name = 'Forum'), 5, 5);

INSERT INTO route_location_bridge(route_id, location_id, sequence_order, question_id)
VALUES((SELECT route_id FROM route WHERE route_name = 'Standard'), (SELECT location_id FROM location WHERE location_name = 'Library'), 6, 6);

INSERT INTO route_location_bridge(route_id, location_id, sequence_order, question_id)
VALUES((SELECT route_id FROM route WHERE route_name = 'Standard'), (SELECT location_id FROM location WHERE location_name = 'Innovation Offices'), 7, 7);
