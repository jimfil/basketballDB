CREATE TABLE `Stadium` (
  `id` int AUTO_INCREMENT PRIMARY KEY,
  `location` varchar(255),
  `name` varchar(255),
  `capacity` int,
  UNIQUE (`location`, `name`)
);
CREATE TABLE `Team` (
  `id` int AUTO_INCREMENT PRIMARY KEY,
  `name` varchar(255),
  UNIQUE (`name`)
);


CREATE TABLE `Match` (
  `id` int AUTO_INCREMENT PRIMARY KEY,
  `match_date` date,
  `status` ENUM ('Scheduled', 'Ongoing', 'Completed', 'Stopped'),
  `matchday_id` int,
  `stadium_id` int,  
  `home_team_id` int,
  `away_team_id` int,
  FOREIGN KEY (`stadium_id`) REFERENCES `Stadium` (`id`),
  FOREIGN KEY (`home_team_id`) REFERENCES `Team` (`id`),
  FOREIGN KEY (`away_team_id`) REFERENCES `Team` (`id`)
);


CREATE TABLE `Event` (
  `id` int AUTO_INCREMENT PRIMARY KEY,
  `name` ENUM (
    'Turnover', 
    'Steal', 
    'Block',
    'Offensive Rebound', 
    'Defensive Rebound',
    'Personal Foul', 
    'Technical Foul', 
    'Flagrant Foul', 
    'Offensive Foul',
    'Substitution',
    'Free Throw Made', 
    'Free Throw Attempt',
    '2-Point Field Goal Made', 
    '2-Point Field Goal Attempt',
    '3-Point Field Goal Made', 
    '3-Point Field Goal Attempt',
    'Assist', 
    'Time running out')
);

CREATE TABLE `Person` (
  `id` int AUTO_INCREMENT PRIMARY KEY,
  `first_name` varchar(30),
  `last_name` varchar(30),
  `speciality` ENUM ('Player', 'Coach')
);

CREATE TABLE `Season` (
  `year` int AUTO_INCREMENT PRIMARY KEY
);

CREATE TABLE `Phase` (
  `id` int AUTO_INCREMENT PRIMARY KEY,
  `phase_id` int,
  `year` int,
  FOREIGN KEY (`year`) REFERENCES `Season` (`year`)
);

CREATE TABLE `Round` (
  `id` int AUTO_INCREMENT PRIMARY KEY,
  `round_id` int,
  `phase_id` int,
  FOREIGN KEY (`phase_id`) REFERENCES `Phase` (`id`)
);

CREATE TABLE `Referee` (
  `id` int AUTO_INCREMENT PRIMARY KEY,
  `first_name` varchar(30),
  `last_name` varchar(30)
);

CREATE TABLE `Person_Team` (
  `person_id` int,
  `team_id` int,
  `beginning` timestamp,
  `ending` timestamp,
  `shirt_num` int,
  PRIMARY KEY (`person_id`, `team_id`),
  FOREIGN KEY (`person_id`) REFERENCES `Person` (`id`),
  FOREIGN KEY (`team_id`) REFERENCES `Team` (`id`)
);

CREATE TABLE `Match_Referee` (
  `match_id` int,
  `referee_id` int,
  PRIMARY KEY (`match_id`, `referee_id`),
  FOREIGN KEY (`match_id`) REFERENCES `Match` (`id`),
  FOREIGN KEY (`referee_id`) REFERENCES `Referee` (`id`)
);

CREATE TABLE `Event_Creation` (
  `id` int AUTO_INCREMENT PRIMARY KEY, 
  `match_id` int,
  `person_id` int,
  `event_id` int,
  `real_time` timestamp DEFAULT CURRENT_TIMESTAMP,
  `game_time` timestamp,
  FOREIGN KEY (`match_id`) REFERENCES `Match` (`id`),
  FOREIGN KEY (`person_id`) REFERENCES `Person` (`id`),
  FOREIGN KEY (`event_id`) REFERENCES `Event` (`id`)
);

CREATE TABLE `Team_stadium` (
  `team_id` int,
  `stadium_id` int, 
  `round_id` int,
  PRIMARY KEY (`team_id`, `stadium_id`, `round_id`),
  FOREIGN KEY (`team_id`) REFERENCES `Team` (`id`),
  FOREIGN KEY (`stadium_id`) REFERENCES `Stadium` (`id`),
  FOREIGN KEY (`round_id`) REFERENCES `Round` (`id`)
);



