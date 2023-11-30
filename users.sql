BEGIN TRANSACTION;
CREATE TABLE IF NOT EXISTS "users" (
	"id"	INTEGER,
	"rfid_tag"	TEXT NOT NULL,
	"name"	TEXT NOT NULL,
	"temp_threshold"	INTEGER,
	"humidity_threshold"	INTEGER,
	"light_threshold"	INTEGER,
	PRIMARY KEY("id")
);
INSERT INTO "users" VALUES (1,'8D DF F6 30','Roberto',22.8,'',29);
INSERT INTO "users" VALUES (2,'7D DD FF 31','George',0,'',30);
INSERT INTO "users" VALUES (3,'ED 7C 06 31','Imran',22.7,'',29);
COMMIT;
