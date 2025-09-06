-- Table: t1
-- Chunk: 1
-- Rows: 9

CREATE TABLE "t1" (id INTEGER PRIMARY KEY, content TEXT, page TEXT, parent TEXT, is_deleted TEXT);

-- Insert data for t1
INSERT INTO [t1] VALUES (1,'تقريظ الشيخ العلامة الجليل صالح بن إبراهيم البليهي','2','0','0');
INSERT INTO [t1] VALUES (2,'مقدمة المحقق','6','0','0');
INSERT INTO [t1] VALUES (3,'النسخ المعتمد عليه في التحقيق','8','2','0');
INSERT INTO [t1] VALUES (4,'ترجمة المؤلف','10','0','0');
INSERT INTO [t1] VALUES (5,'سبب تأليف هذه الرسالة وصفتها','17','0','0');
INSERT INTO [t1] VALUES (6,'المسألة الأولى','21','0','0');
INSERT INTO [t1] VALUES (7,'المسألة الثانية','52','0','0');
INSERT INTO [t1] VALUES (8,'المسألة الثالثة','83','0','0');
INSERT INTO [t1] VALUES (9,'أهم المراجع حسب ورودها في الكتاب','90','0','0');
