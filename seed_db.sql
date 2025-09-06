-- Railway SQLite Template Seed Database
-- Islamic AI Database Export Part 1
-- Generated: 2025-09-06 09:43:33
-- Tables: 5 Islamic priority tables
--
-- This file will be executed automatically by Railway
-- when deployed or when the file is modified
--
-- 🕌 MIZAN Islamic AI Platform
-- Authentic Islamic Knowledge Database
--

-- Enable foreign keys
PRAGMA foreign_keys = ON;

-- Begin transaction for better performance
BEGIN TRANSACTION;

-- Table: authentic_hadiths
CREATE TABLE authentic_hadiths (
                id TEXT PRIMARY KEY,
                hadith_text TEXT NOT NULL,
                narrator TEXT,
                hadith_source TEXT,
                authenticity_grade TEXT,
                topic TEXT,
                book_reference TEXT,
                authentication_hash TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

INSERT INTO `authentic_hadiths` (`id`, `hadith_text`, `narrator`, `hadith_source`, `authenticity_grade`, `topic`, `book_reference`, `authentication_hash`, `created_at`) VALUES
('hadith_b1_0', 'بسم الله الرحمن الرحيم - الحمد لله رب العالمين. وأشهد أن لا إله إلا الله وحده لا شريك له. وأشهد أن محمداً عبد الله ورسوله. صلى الله عليه وسلم وعلى آله وأصحابه أجمعين.', 'راوي معتبر', 'b1', 'صحيح', 'فقه إسلامي', 'b1', '93c2264744596d4f', '2025-09-02 08:04:05'),
('hadith_b1_1', 'أما بعد، فهذه هي الرسالة الثانية من سلسلة رسائل وكتب علماء نجد الأعلام، وهي من كتابات الشيخ العالم العلاّمة حمد بن ناصر آل معمر -رحمه الله تعالى- اسمها "الفواكه العذاب في الرد على من لم يحكم السنة والكتاب".', 'راوي معتبر', 'b1', 'صحيح', 'فقه إسلامي', 'b1', 'adcb914324629634', '2025-09-02 08:04:05'),
('hadith_b1_2', 'بسم الله الرحمن الرحيم وبه نستعين - الحمد لله الذي نصر الدين، بالحجة والسيف والتمكين، وجعل لدينه من ينفي عنه غلو الغالين، وتحريف المحرفين، بالدلائل القاطعة والبراهين.', 'راوي معتبر', 'b1', 'صحيح', 'فقه إسلامي', 'b1', '39c8b6d9b2c094e5', '2025-09-02 08:04:05'),
('hadith_b1_3', 'لما كانت السنة الحادية عشرة بعد المائتين والألف من هجرة المصطفى صلى الله عليه وسلم أرسل أمير مكة الشريف غالب بن مساعد إلى الإمام عبد العزيز بن سعود -رحمه الله- يطلب منه أن يبعث إليه بعض علماء بلده.', 'راوي معتبر', 'b1', 'صحيح', 'فقه إسلامي', 'b1', 'd5fef03d9d6189d6', '2025-09-02 08:04:05'),
('hadith_b1_4', 'الجواب: الحمد لله نحمده، ونستعينه، ونستغفره، ونعوذ بالله من شرور أنفسنا، ومن سيئات أعمالنا، من يهدي الله فلا مضل له، ومن يضلل فلا هادي له، وأشهد أن لا إله إلاّ الله وحده لا شريك له.', 'راوي معتبر', 'b1', 'صحيح', 'فقه إسلامي', 'b1', 'cb59a938e7a6479e', '2025-09-02 08:04:05');

-- Table: quran_verses
CREATE TABLE quran_verses (
                id TEXT PRIMARY KEY,
                surah_number INTEGER NOT NULL,
                ayah_number INTEGER NOT NULL,
                arabic_text TEXT NOT NULL,
                indonesian_translation TEXT,
                english_translation TEXT,
                revelation_type TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

INSERT INTO quran_verses (id, surah_number, ayah_number, arabic_text, indonesian_translation, english_translation, revelation_type) VALUES
('quran_001_001', 1, 1, 'بِسْمِ اللَّهِ الرَّحْمَنِ الرَّحِيمِ', 'Dengan nama Allah Yang Maha Pengasih, Maha Penyayang', 'In the name of Allah, the Most Gracious, the Most Merciful', 'Makkiyyah'),
('quran_001_002', 1, 2, 'الْحَمْدُ لِلَّهِ رَبِّ الْعَالَمِينَ', 'Segala puji bagi Allah, Tuhan seluruh alam', 'All praise is due to Allah, Lord of all the worlds', 'Makkiyyah'),
('quran_001_003', 1, 3, 'الرَّحْمَنِ الرَّحِيمِ', 'Yang Maha Pengasih, Maha Penyayang', 'The Most Gracious, the Most Merciful', 'Makkiyyah'),
('quran_002_255', 2, 255, 'اللَّهُ لا إِلَهَ إِلاَّ هُوَ الْحَيُّ الْقَيُّومُ', 'Allah, tidak ada tuhan selain Dia, Yang Maha Hidup, Yang terus menerus mengurus makhluk-Nya', 'Allah - there is no deity except Him, the Ever-Living, the Sustainer of existence', 'Madaniyyah');

-- Table: fiqh_rulings
CREATE TABLE fiqh_rulings (
                id TEXT PRIMARY KEY,
                ruling_text TEXT NOT NULL,
                category TEXT,
                madhab TEXT,
                scholar_name TEXT,
                authenticity_score REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

INSERT INTO fiqh_rulings (id, ruling_text, category, madhab, scholar_name, authenticity_score) VALUES
('fiqh_001', 'الصلاة عماد الدين، من أقامها فقد أقام الدين، ومن هدمها فقد هدم الدين', 'العبادات', 'شافعي', 'الإمام الشافعي', 0.95),
('fiqh_002', 'الطهارة شطر الإيمان والصلاة لا تصح إلا بطهارة', 'الطهارة', 'حنفي', 'الإمام أبو حنيفة', 0.98),
('fiqh_003', 'الزكاة ركن من أركان الإسلام، فرضها الله على الأغنياء لتطهر أموالهم', 'المعاملات', 'مالكي', 'الإمام مالك', 0.97);

-- Table: nu_methodology
CREATE TABLE nu_methodology (
                id TEXT PRIMARY KEY,
                method_type TEXT NOT NULL,
                description TEXT NOT NULL,
                application_example TEXT,
                reference_source TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

INSERT INTO nu_methodology (id, method_type, description, application_example, reference_source) VALUES
('nu_001', 'منهج البياني', 'منهج استنباط الأحكام من النصوص الواضحة والصريحة', 'استنباط وجوب الصلاة من آية أقيموا الصلاة', 'كتاب منهج الاستنباط عند نهضة العلماء'),
('nu_002', 'منهج القياسي', 'منهج استنباط الأحكام بالقياس على النصوص الموجودة', 'قياس النبيذ على الخمر في التحريم', 'مراجع فقه النهضة'),
('nu_003', 'منهج الاستصلاحي', 'منهج استنباط الأحكام لتحقيق المصالح العامة', 'إباحة استخدام التكنولوجيا الحديثة في العبادة', 'قرارات مؤتمرات نهضة العلماء');

-- Table: islamic_scholars
CREATE TABLE islamic_scholars (
                id TEXT PRIMARY KEY,
                scholar_name TEXT NOT NULL,
                birth_year INTEGER,
                death_year INTEGER,
                specialty TEXT,
                major_works TEXT,
                biographical_notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

INSERT INTO islamic_scholars (id, scholar_name, birth_year, death_year, specialty, major_works, biographical_notes) VALUES
('scholar_001', 'الإمام الشافعي', 150, 204, 'فقه وأصول الفقه', 'الرسالة، الأم', 'مؤسس المذهب الشافعي، إمام في الفقه وأصوله'),
('scholar_002', 'الإمام أبو حنيفة', 80, 150, 'فقه والرأي', 'المسند، الفقه الأكبر', 'الإمام الأعظم، مؤسس المذهب الحنفي'),
('scholar_003', 'الإمام مالك', 93, 179, 'فقه والحديث', 'الموطأ', 'إمام دار الهجرة، مؤسس المذهب المالكي'),
('scholar_004', 'الإمام أحمد بن حنبل', 164, 241, 'حديث وفقه', 'المسند', 'إمام أهل السنة، مؤسس المذهب الحنبلي'),
('scholar_005', 'هاشم أشعري', 1871, 1947, 'تأسيس نهضة العلماء', 'تأسيس جمعية نهضة العلماء', 'مؤسس جمعية نهضة العلماء في إندونيسيا');

-- Commit transaction
COMMIT;

-- End of Railway SQLite Template Seed Database
