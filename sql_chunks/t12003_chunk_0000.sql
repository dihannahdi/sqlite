-- Table: t12003
-- Chunk: 1
-- Rows: 8

CREATE TABLE "t12003" (id INTEGER PRIMARY KEY, content TEXT, page TEXT, parent TEXT, is_deleted TEXT);

-- Insert data for t12003
INSERT INTO [t12003] VALUES (1,'المجلد الأول','1','0','0');
INSERT INTO [t12003] VALUES (2,'المجلد الأول','1','1','0');
INSERT INTO [t12003] VALUES (3,'المجلد الثاني','223','0','0');
INSERT INTO [t12003] VALUES (4,'المجلد الثاني','223','3','0');
INSERT INTO [t12003] VALUES (5,'المجلد الثالث','498','0','0');
INSERT INTO [t12003] VALUES (6,'المجلد الثالث','498','5','0');
INSERT INTO [t12003] VALUES (7,'المجلد الرابع','776','0','0');
INSERT INTO [t12003] VALUES (8,'المجلد الرابع','776','7','0');
