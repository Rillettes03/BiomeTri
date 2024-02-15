create table biometrics(
	id int NOT NULL PRIMARY KEY,
	nom VARCHAR(255),
	prenom VARCHAR(255),
	email VARCHAR(255),
	FacialData VARCHAR(255),
	lastAccess date
);