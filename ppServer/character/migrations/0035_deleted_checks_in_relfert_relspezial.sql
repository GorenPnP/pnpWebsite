BEGIN;
--
-- Remove field ep_rang from charakter
--
CREATE TABLE "new__character_charakter" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "in_erstellung" bool NOT NULL, "ep_system" bool NOT NULL, "name" varchar(200) NOT NULL UNIQUE, "manifest" decimal NOT NULL, "sonstiger_manifestverlust" decimal NOT NULL, "notizen_sonstiger_manifestverlust" varchar(200) NOT NULL, "gewicht" integer unsigned NOT NULL CHECK ("gewicht" >= 0), "größe" integer unsigned NOT NULL CHECK ("größe" >= 0), "alter" integer unsigned NOT NULL CHECK ("alter" >= 0), "geschlecht" varchar(100) NOT NULL, "sexualität" varchar(100) NOT NULL, "präf_arm" varchar(100) NOT NULL, "hautfarbe" varchar(100) NOT NULL, "haarfarbe" varchar(100) NOT NULL, "augenfarbe" varchar(100) NOT NULL, "nutzt_magie" smallint unsigned NOT NULL CHECK ("nutzt_magie" >= 0), "useEco" bool NOT NULL, "eco" integer unsigned NOT NULL CHECK ("eco" >= 0), "morph" integer unsigned NOT NULL CHECK ("morph" >= 0), "sp" integer unsigned NOT NULL CHECK ("sp" >= 0), "geld" integer NOT NULL, "HPplus" integer NOT NULL, "wesenschaden_waff_kampf" integer NOT NULL, "rang" integer unsigned NOT NULL CHECK ("rang" >= 0), "notizen" text NOT NULL, "persönlicheZiele" text NOT NULL, "sonstige_items" text NOT NULL, "beruf_id" integer NULL REFERENCES "character_beruf" ("id") DEFERRABLE INITIALLY DEFERRED, "eigentümer_id" integer NULL REFERENCES "character_spieler" ("id") DEFERRABLE INITIALLY DEFERRED, "religion_id" integer NULL REFERENCES "character_religion" ("id") DEFERRABLE INITIALLY DEFERRED, "wesenschaden_andere_gestalt" integer NULL, "ep" integer unsigned NOT NULL CHECK ("ep" >= 0), "HPplus_fix" integer NULL, "ip" integer NOT NULL, "tp" integer NOT NULL);
INSERT INTO "new__character_charakter" ("manifest", "haarfarbe", "HPplus_fix", "useEco", "hautfarbe", "gewicht", "ep", "sp", "id", "alter", "rang", "notizen", "geld", "persönlicheZiele", "wesenschaden_waff_kampf", "wesenschaden_andere_gestalt", "religion_id", "name", "augenfarbe", "eigentümer_id", "nutzt_magie", "sonstiger_manifestverlust", "notizen_sonstiger_manifestverlust", "sonstige_items", "in_erstellung", "eco", "HPplus", "größe", "ep_system", "morph", "beruf_id", "präf_arm", "geschlecht", "tp", "sexualität", "ip") SELECT "manifest", "haarfarbe", "HPplus_fix", "useEco", "hautfarbe", "gewicht", "ep", "sp", "id", "alter", "rang", "notizen", "geld", "persönlicheZiele", "wesenschaden_waff_kampf", "wesenschaden_andere_gestalt", "religion_id", "name", "augenfarbe", "eigentümer_id", "nutzt_magie", "sonstiger_manifestverlust", "notizen_sonstiger_manifestverlust", "sonstige_items", "in_erstellung", "eco", "HPplus", "größe", "ep_system", "morph", "beruf_id", "präf_arm", "geschlecht", "tp", "sexualität", "ip" FROM "character_charakter";
DROP TABLE "character_charakter";
ALTER TABLE "new__character_charakter" RENAME TO "character_charakter";
CREATE INDEX "character_charakter_beruf_id_90824ebd" ON "character_charakter" ("beruf_id");
CREATE INDEX "character_charakter_eigentümer_id_b22391ee" ON "character_charakter" ("eigentümer_id");
CREATE INDEX "character_charakter_religion_id_00ca8313" ON "character_charakter" ("religion_id");
--
-- Remove field aktuellerWert_fix from relattribut
--
CREATE TABLE "new__character_relattribut" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "aktuellerWert" integer unsigned NOT NULL CHECK ("aktuellerWert" >= 0), "maxWert" integer unsigned NOT NULL CHECK ("maxWert" >= 0), "fg" integer unsigned NOT NULL CHECK ("fg" >= 0), "notizen" varchar(200) NOT NULL, "attribut_id" integer NOT NULL REFERENCES "character_attribut" ("id") DEFERRABLE INITIALLY DEFERRED, "char_id" integer NOT NULL REFERENCES "character_charakter" ("id") DEFERRABLE INITIALLY DEFERRED, "maxWert_fix" integer unsigned NULL CHECK ("maxWert_fix" >= 0));
INSERT INTO "new__character_relattribut" ("fg", "notizen", "aktuellerWert", "maxWert_fix", "maxWert", "char_id", "attribut_id", "id") SELECT "fg", "notizen", "aktuellerWert", "maxWert_fix", "maxWert", "char_id", "attribut_id", "id" FROM "character_relattribut";
DROP TABLE "character_relattribut";
ALTER TABLE "new__character_relattribut" RENAME TO "character_relattribut";
CREATE UNIQUE INDEX "character_relattribut_char_id_attribut_id_fa6dd3bf_uniq" ON "character_relattribut" ("char_id", "attribut_id");
CREATE INDEX "character_relattribut_attribut_id_1db102f0" ON "character_relattribut" ("attribut_id");
CREATE INDEX "character_relattribut_char_id_02450446" ON "character_relattribut" ("char_id");
--
-- Remove field maxWert_fix from relattribut
--
CREATE TABLE "new__character_relattribut" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "aktuellerWert" integer unsigned NOT NULL CHECK ("aktuellerWert" >= 0), "maxWert" integer unsigned NOT NULL CHECK ("maxWert" >= 0), "fg" integer unsigned NOT NULL CHECK ("fg" >= 0), "notizen" varchar(200) NOT NULL, "attribut_id" integer NOT NULL REFERENCES "character_attribut" ("id") DEFERRABLE INITIALLY DEFERRED, "char_id" integer NOT NULL REFERENCES "character_charakter" ("id") DEFERRABLE INITIALLY DEFERRED);
INSERT INTO "new__character_relattribut" ("fg", "notizen", "aktuellerWert", "maxWert", "char_id", "attribut_id", "id") SELECT "fg", "notizen", "aktuellerWert", "maxWert", "char_id", "attribut_id", "id" FROM "character_relattribut";
DROP TABLE "character_relattribut";
ALTER TABLE "new__character_relattribut" RENAME TO "character_relattribut";
CREATE UNIQUE INDEX "character_relattribut_char_id_attribut_id_fa6dd3bf_uniq" ON "character_relattribut" ("char_id", "attribut_id");
CREATE INDEX "character_relattribut_attribut_id_1db102f0" ON "character_relattribut" ("attribut_id");
CREATE INDEX "character_relattribut_char_id_02450446" ON "character_relattribut" ("char_id");
--
-- Remove field notizen from relattribut
--
CREATE TABLE "new__character_relattribut" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "aktuellerWert" integer unsigned NOT NULL CHECK ("aktuellerWert" >= 0), "maxWert" integer unsigned NOT NULL CHECK ("maxWert" >= 0), "fg" integer unsigned NOT NULL CHECK ("fg" >= 0), "attribut_id" integer NOT NULL REFERENCES "character_attribut" ("id") DEFERRABLE INITIALLY DEFERRED, "char_id" integer NOT NULL REFERENCES "character_charakter" ("id") DEFERRABLE INITIALLY DEFERRED);
INSERT INTO "new__character_relattribut" ("fg", "aktuellerWert", "maxWert", "char_id", "attribut_id", "id") SELECT "fg", "aktuellerWert", "maxWert", "char_id", "attribut_id", "id" FROM "character_relattribut";
DROP TABLE "character_relattribut";
ALTER TABLE "new__character_relattribut" RENAME TO "character_relattribut";
CREATE UNIQUE INDEX "character_relattribut_char_id_attribut_id_fa6dd3bf_uniq" ON "character_relattribut" ("char_id", "attribut_id");
CREATE INDEX "character_relattribut_attribut_id_1db102f0" ON "character_relattribut" ("attribut_id");
CREATE INDEX "character_relattribut_char_id_02450446" ON "character_relattribut" ("char_id");
--
-- Remove field notizen from relfertigkeit
--
CREATE TABLE "new__character_relfertigkeit" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "fp" integer unsigned NOT NULL CHECK ("fp" >= 0), "pool" integer unsigned NOT NULL CHECK ("pool" >= 0), "char_id" integer NOT NULL REFERENCES "character_charakter" ("id") DEFERRABLE INITIALLY DEFERRED, "fertigkeit_id" integer NOT NULL REFERENCES "character_fertigkeit" ("id") DEFERRABLE INITIALLY DEFERRED);
INSERT INTO "new__character_relfertigkeit" ("fertigkeit_id", "id", "pool", "char_id", "fp") SELECT "fertigkeit_id", "id", "pool", "char_id", "fp" FROM "character_relfertigkeit";
DROP TABLE "character_relfertigkeit";
ALTER TABLE "new__character_relfertigkeit" RENAME TO "character_relfertigkeit";
CREATE UNIQUE INDEX "character_relfertigkeit_char_id_fertigkeit_id_0e5efdfe_uniq" ON "character_relfertigkeit" ("char_id", "fertigkeit_id");
CREATE INDEX "character_relfertigkeit_char_id_41cf96de" ON "character_relfertigkeit" ("char_id");
CREATE INDEX "character_relfertigkeit_fertigkeit_id_74b1eeb7" ON "character_relfertigkeit" ("fertigkeit_id");
--
-- Remove field pool from relfertigkeit
--
CREATE TABLE "new__character_relfertigkeit" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "fp" integer unsigned NOT NULL CHECK ("fp" >= 0), "char_id" integer NOT NULL REFERENCES "character_charakter" ("id") DEFERRABLE INITIALLY DEFERRED, "fertigkeit_id" integer NOT NULL REFERENCES "character_fertigkeit" ("id") DEFERRABLE INITIALLY DEFERRED);
INSERT INTO "new__character_relfertigkeit" ("fertigkeit_id", "char_id", "fp", "id") SELECT "fertigkeit_id", "char_id", "fp", "id" FROM "character_relfertigkeit";
DROP TABLE "character_relfertigkeit";
ALTER TABLE "new__character_relfertigkeit" RENAME TO "character_relfertigkeit";
CREATE UNIQUE INDEX "character_relfertigkeit_char_id_fertigkeit_id_0e5efdfe_uniq" ON "character_relfertigkeit" ("char_id", "fertigkeit_id");
CREATE INDEX "character_relfertigkeit_char_id_41cf96de" ON "character_relfertigkeit" ("char_id");
CREATE INDEX "character_relfertigkeit_fertigkeit_id_74b1eeb7" ON "character_relfertigkeit" ("fertigkeit_id");
--
-- Remove field notizen from relspezies
--
CREATE TABLE "new__character_relspezies" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "char_id" integer NOT NULL REFERENCES "character_charakter" ("id") DEFERRABLE INITIALLY DEFERRED, "spezies_id" integer NOT NULL REFERENCES "character_spezies" ("id") DEFERRABLE INITIALLY DEFERRED);
INSERT INTO "new__character_relspezies" ("char_id", "spezies_id", "id") SELECT "char_id", "spezies_id", "id" FROM "character_relspezies";
DROP TABLE "character_relspezies";
ALTER TABLE "new__character_relspezies" RENAME TO "character_relspezies";
CREATE UNIQUE INDEX "character_relspezies_char_id_spezies_id_5685d1d5_uniq" ON "character_relspezies" ("char_id", "spezies_id");
CREATE INDEX "character_relspezies_char_id_f8ea94b3" ON "character_relspezies" ("char_id");
CREATE INDEX "character_relspezies_spezies_id_227fa0eb" ON "character_relspezies" ("spezies_id");
--
-- Add field gfs to charakter
--
CREATE TABLE "new__character_charakter" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "gfs_id" integer NULL REFERENCES "character_gfs" ("id") DEFERRABLE INITIALLY DEFERRED, "in_erstellung" bool NOT NULL, "ep_system" bool NOT NULL, "name" varchar(200) NOT NULL UNIQUE, "manifest" decimal NOT NULL, "sonstiger_manifestverlust" decimal NOT NULL, "notizen_sonstiger_manifestverlust" varchar(200) NOT NULL, "gewicht" integer unsigned NOT NULL CHECK ("gewicht" >= 0), "größe" integer unsigned NOT NULL CHECK ("größe" >= 0), "alter" integer unsigned NOT NULL CHECK ("alter" >= 0), "geschlecht" varchar(100) NOT NULL, "sexualität" varchar(100) NOT NULL, "präf_arm" varchar(100) NOT NULL, "hautfarbe" varchar(100) NOT NULL, "haarfarbe" varchar(100) NOT NULL, "augenfarbe" varchar(100) NOT NULL, "nutzt_magie" smallint unsigned NOT NULL CHECK ("nutzt_magie" >= 0), "useEco" bool NOT NULL, "eco" integer unsigned NOT NULL CHECK ("eco" >= 0), "morph" integer unsigned NOT NULL CHECK ("morph" >= 0), "sp" integer unsigned NOT NULL CHECK ("sp" >= 0), "geld" integer NOT NULL, "HPplus" integer NOT NULL, "wesenschaden_waff_kampf" integer NOT NULL, "rang" integer unsigned NOT NULL CHECK ("rang" >= 0), "notizen" text NOT NULL, "persönlicheZiele" text NOT NULL, "sonstige_items" text NOT NULL, "beruf_id" integer NULL REFERENCES "character_beruf" ("id") DEFERRABLE INITIALLY DEFERRED, "eigentümer_id" integer NULL REFERENCES "character_spieler" ("id") DEFERRABLE INITIALLY DEFERRED, "religion_id" integer NULL REFERENCES "character_religion" ("id") DEFERRABLE INITIALLY DEFERRED, "wesenschaden_andere_gestalt" integer NULL, "ep" integer unsigned NOT NULL CHECK ("ep" >= 0), "HPplus_fix" integer NULL, "ip" integer NOT NULL, "tp" integer NOT NULL);
INSERT INTO "new__character_charakter" ("gfs_id", "manifest", "haarfarbe", "HPplus_fix", "useEco", "hautfarbe", "gewicht", "ep", "sp", "id", "alter", "rang", "notizen", "geld", "persönlicheZiele", "wesenschaden_waff_kampf", "wesenschaden_andere_gestalt", "religion_id", "name", "augenfarbe", "eigentümer_id", "nutzt_magie", "sonstiger_manifestverlust", "notizen_sonstiger_manifestverlust", "sonstige_items", "in_erstellung", "eco", "HPplus", "größe", "ep_system", "morph", "beruf_id", "präf_arm", "geschlecht", "tp", "sexualität", "ip") SELECT NULL, "manifest", "haarfarbe", "HPplus_fix", "useEco", "hautfarbe", "gewicht", "ep", "sp", "id", "alter", "rang", "notizen", "geld", "persönlicheZiele", "wesenschaden_waff_kampf", "wesenschaden_andere_gestalt", "religion_id", "name", "augenfarbe", "eigentümer_id", "nutzt_magie", "sonstiger_manifestverlust", "notizen_sonstiger_manifestverlust", "sonstige_items", "in_erstellung", "eco", "HPplus", "größe", "ep_system", "morph", "beruf_id", "präf_arm", "geschlecht", "tp", "sexualität", "ip" FROM "character_charakter";
DROP TABLE "character_charakter";
ALTER TABLE "new__character_charakter" RENAME TO "character_charakter";
CREATE INDEX "character_charakter_gfs_id_c75a5982" ON "character_charakter" ("gfs_id");
CREATE INDEX "character_charakter_beruf_id_90824ebd" ON "character_charakter" ("beruf_id");
CREATE INDEX "character_charakter_eigentümer_id_b22391ee" ON "character_charakter" ("eigentümer_id");
CREATE INDEX "character_charakter_religion_id_00ca8313" ON "character_charakter" ("religion_id");
--
-- Add field aktuell_bonus to relattribut
--
CREATE TABLE "new__character_relattribut" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "aktuellerWert" integer unsigned NOT NULL CHECK ("aktuellerWert" >= 0), "maxWert" integer unsigned NOT NULL CHECK ("maxWert" >= 0), "fg" integer unsigned NOT NULL CHECK ("fg" >= 0), "attribut_id" integer NOT NULL REFERENCES "character_attribut" ("id") DEFERRABLE INITIALLY DEFERRED, "char_id" integer NOT NULL REFERENCES "character_charakter" ("id") DEFERRABLE INITIALLY DEFERRED, "aktuell_bonus" integer unsigned NOT NULL CHECK ("aktuell_bonus" >= 0));
INSERT INTO "new__character_relattribut" ("fg", "aktuellerWert", "aktuell_bonus", "maxWert", "char_id", "attribut_id", "id") SELECT "fg", "aktuellerWert", 0, "maxWert", "char_id", "attribut_id", "id" FROM "character_relattribut";
DROP TABLE "character_relattribut";
ALTER TABLE "new__character_relattribut" RENAME TO "character_relattribut";
CREATE UNIQUE INDEX "character_relattribut_char_id_attribut_id_fa6dd3bf_uniq" ON "character_relattribut" ("char_id", "attribut_id");
CREATE INDEX "character_relattribut_attribut_id_1db102f0" ON "character_relattribut" ("attribut_id");
CREATE INDEX "character_relattribut_char_id_02450446" ON "character_relattribut" ("char_id");
--
-- Add field max_bonus to relattribut
--
CREATE TABLE "new__character_relattribut" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "aktuellerWert" integer unsigned NOT NULL CHECK ("aktuellerWert" >= 0), "maxWert" integer unsigned NOT NULL CHECK ("maxWert" >= 0), "fg" integer unsigned NOT NULL CHECK ("fg" >= 0), "attribut_id" integer NOT NULL REFERENCES "character_attribut" ("id") DEFERRABLE INITIALLY DEFERRED, "char_id" integer NOT NULL REFERENCES "character_charakter" ("id") DEFERRABLE INITIALLY DEFERRED, "aktuell_bonus" integer unsigned NOT NULL CHECK ("aktuell_bonus" >= 0), "max_bonus" integer unsigned NOT NULL CHECK ("max_bonus" >= 0));
INSERT INTO "new__character_relattribut" ("fg", "aktuellerWert", "max_bonus", "aktuell_bonus", "maxWert", "char_id", "attribut_id", "id") SELECT "fg", "aktuellerWert", 0, "aktuell_bonus", "maxWert", "char_id", "attribut_id", "id" FROM "character_relattribut";
DROP TABLE "character_relattribut";
ALTER TABLE "new__character_relattribut" RENAME TO "character_relattribut";
CREATE UNIQUE INDEX "character_relattribut_char_id_attribut_id_fa6dd3bf_uniq" ON "character_relattribut" ("char_id", "attribut_id");
CREATE INDEX "character_relattribut_attribut_id_1db102f0" ON "character_relattribut" ("attribut_id");
CREATE INDEX "character_relattribut_char_id_02450446" ON "character_relattribut" ("char_id");
--
-- Add field fp_bonus to relfertigkeit
--
CREATE TABLE "new__character_relfertigkeit" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "fp" integer unsigned NOT NULL CHECK ("fp" >= 0), "char_id" integer NOT NULL REFERENCES "character_charakter" ("id") DEFERRABLE INITIALLY DEFERRED, "fertigkeit_id" integer NOT NULL REFERENCES "character_fertigkeit" ("id") DEFERRABLE INITIALLY DEFERRED, "fp_bonus" integer NOT NULL);
INSERT INTO "new__character_relfertigkeit" ("fertigkeit_id", "char_id", "fp", "fp_bonus", "id") SELECT "fertigkeit_id", "char_id", "fp", 0, "id" FROM "character_relfertigkeit";
DROP TABLE "character_relfertigkeit";
ALTER TABLE "new__character_relfertigkeit" RENAME TO "character_relfertigkeit";
CREATE UNIQUE INDEX "character_relfertigkeit_char_id_fertigkeit_id_0e5efdfe_uniq" ON "character_relfertigkeit" ("char_id", "fertigkeit_id");
CREATE INDEX "character_relfertigkeit_char_id_41cf96de" ON "character_relfertigkeit" ("char_id");
CREATE INDEX "character_relfertigkeit_fertigkeit_id_74b1eeb7" ON "character_relfertigkeit" ("fertigkeit_id");
--
-- Add field pool to relspezialfertigkeit
--
CREATE TABLE "new__character_relspezialfertigkeit" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "gesamt" integer unsigned NOT NULL, "korrektur" integer unsigned NOT NULL, "stufe" integer unsigned NOT NULL, "w20" integer unsigned NOT NULL, "würfelÜbrig" integer unsigned NOT NULL, "char_id" integer NOT NULL REFERENCES "character_charakter" ("id") DEFERRABLE INITIALLY DEFERRED, "spezialfertigkeit_id" integer NOT NULL REFERENCES "character_spezialfertigkeit" ("id") DEFERRABLE INITIALLY DEFERRED, "pool" integer unsigned NOT NULL);
INSERT INTO "new__character_relspezialfertigkeit" ("korrektur", "würfelÜbrig", "spezialfertigkeit_id", "char_id", "pool", "gesamt", "w20", "stufe", "id") SELECT "korrektur", "würfelÜbrig", "spezialfertigkeit_id", "char_id", 0, "gesamt", "w20", "stufe", "id" FROM "character_relspezialfertigkeit";
DROP TABLE "character_relspezialfertigkeit";
ALTER TABLE "new__character_relspezialfertigkeit" RENAME TO "character_relspezialfertigkeit";
CREATE UNIQUE INDEX "character_relspezialfertigkeit_char_id_spezialfertigkeit_id_e3d9c2e1_uniq" ON "character_relspezialfertigkeit" ("char_id", "spezialfertigkeit_id");
CREATE INDEX "character_relspezialfertigkeit_char_id_c56d69cf" ON "character_relspezialfertigkeit" ("char_id");
CREATE INDEX "character_relspezialfertigkeit_spezialfertigkeit_id_3f29c067" ON "character_relspezialfertigkeit" ("spezialfertigkeit_id");
--
-- Alter field ip on charakter
--
CREATE TABLE "new__character_charakter" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "in_erstellung" bool NOT NULL, "ep_system" bool NOT NULL, "name" varchar(200) NOT NULL UNIQUE, "manifest" decimal NOT NULL, "sonstiger_manifestverlust" decimal NOT NULL, "notizen_sonstiger_manifestverlust" varchar(200) NOT NULL, "gewicht" integer unsigned NOT NULL CHECK ("gewicht" >= 0), "größe" integer unsigned NOT NULL CHECK ("größe" >= 0), "alter" integer unsigned NOT NULL CHECK ("alter" >= 0), "geschlecht" varchar(100) NOT NULL, "sexualität" varchar(100) NOT NULL, "präf_arm" varchar(100) NOT NULL, "hautfarbe" varchar(100) NOT NULL, "haarfarbe" varchar(100) NOT NULL, "augenfarbe" varchar(100) NOT NULL, "nutzt_magie" smallint unsigned NOT NULL CHECK ("nutzt_magie" >= 0), "useEco" bool NOT NULL, "eco" integer unsigned NOT NULL CHECK ("eco" >= 0), "morph" integer unsigned NOT NULL CHECK ("morph" >= 0), "sp" integer unsigned NOT NULL CHECK ("sp" >= 0), "geld" integer NOT NULL, "HPplus" integer NOT NULL, "wesenschaden_waff_kampf" integer NOT NULL, "rang" integer unsigned NOT NULL CHECK ("rang" >= 0), "notizen" text NOT NULL, "persönlicheZiele" text NOT NULL, "sonstige_items" text NOT NULL, "beruf_id" integer NULL REFERENCES "character_beruf" ("id") DEFERRABLE INITIALLY DEFERRED, "eigentümer_id" integer NULL REFERENCES "character_spieler" ("id") DEFERRABLE INITIALLY DEFERRED, "religion_id" integer NULL REFERENCES "character_religion" ("id") DEFERRABLE INITIALLY DEFERRED, "wesenschaden_andere_gestalt" integer NULL, "ep" integer unsigned NOT NULL CHECK ("ep" >= 0), "HPplus_fix" integer NULL, "tp" integer NOT NULL, "gfs_id" integer NULL REFERENCES "character_gfs" ("id") DEFERRABLE INITIALLY DEFERRED, "ip" integer NOT NULL);
INSERT INTO "new__character_charakter" ("gfs_id", "manifest", "haarfarbe", "HPplus_fix", "useEco", "hautfarbe", "gewicht", "ep", "sp", "id", "alter", "rang", "notizen", "geld", "persönlicheZiele", "wesenschaden_waff_kampf", "wesenschaden_andere_gestalt", "religion_id", "name", "augenfarbe", "eigentümer_id", "nutzt_magie", "sonstiger_manifestverlust", "notizen_sonstiger_manifestverlust", "sonstige_items", "in_erstellung", "eco", "HPplus", "größe", "ep_system", "morph", "beruf_id", "präf_arm", "geschlecht", "tp", "sexualität", "ip") SELECT "gfs_id", "manifest", "haarfarbe", "HPplus_fix", "useEco", "hautfarbe", "gewicht", "ep", "sp", "id", "alter", "rang", "notizen", "geld", "persönlicheZiele", "wesenschaden_waff_kampf", "wesenschaden_andere_gestalt", "religion_id", "name", "augenfarbe", "eigentümer_id", "nutzt_magie", "sonstiger_manifestverlust", "notizen_sonstiger_manifestverlust", "sonstige_items", "in_erstellung", "eco", "HPplus", "größe", "ep_system", "morph", "beruf_id", "präf_arm", "geschlecht", "tp", "sexualität", "ip" FROM "character_charakter";
DROP TABLE "character_charakter";
ALTER TABLE "new__character_charakter" RENAME TO "character_charakter";
CREATE INDEX "character_charakter_beruf_id_90824ebd" ON "character_charakter" ("beruf_id");
CREATE INDEX "character_charakter_eigentümer_id_b22391ee" ON "character_charakter" ("eigentümer_id");
CREATE INDEX "character_charakter_religion_id_00ca8313" ON "character_charakter" ("religion_id");
CREATE INDEX "character_charakter_gfs_id_c75a5982" ON "character_charakter" ("gfs_id");
--
-- Alter field tp on charakter
--
CREATE TABLE "new__character_charakter" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "in_erstellung" bool NOT NULL, "ep_system" bool NOT NULL, "name" varchar(200) NOT NULL UNIQUE, "manifest" decimal NOT NULL, "sonstiger_manifestverlust" decimal NOT NULL, "notizen_sonstiger_manifestverlust" varchar(200) NOT NULL, "gewicht" integer unsigned NOT NULL CHECK ("gewicht" >= 0), "größe" integer unsigned NOT NULL CHECK ("größe" >= 0), "alter" integer unsigned NOT NULL CHECK ("alter" >= 0), "geschlecht" varchar(100) NOT NULL, "sexualität" varchar(100) NOT NULL, "präf_arm" varchar(100) NOT NULL, "hautfarbe" varchar(100) NOT NULL, "haarfarbe" varchar(100) NOT NULL, "augenfarbe" varchar(100) NOT NULL, "nutzt_magie" smallint unsigned NOT NULL CHECK ("nutzt_magie" >= 0), "useEco" bool NOT NULL, "eco" integer unsigned NOT NULL CHECK ("eco" >= 0), "morph" integer unsigned NOT NULL CHECK ("morph" >= 0), "sp" integer unsigned NOT NULL CHECK ("sp" >= 0), "geld" integer NOT NULL, "HPplus" integer NOT NULL, "wesenschaden_waff_kampf" integer NOT NULL, "rang" integer unsigned NOT NULL CHECK ("rang" >= 0), "notizen" text NOT NULL, "persönlicheZiele" text NOT NULL, "sonstige_items" text NOT NULL, "beruf_id" integer NULL REFERENCES "character_beruf" ("id") DEFERRABLE INITIALLY DEFERRED, "eigentümer_id" integer NULL REFERENCES "character_spieler" ("id") DEFERRABLE INITIALLY DEFERRED, "religion_id" integer NULL REFERENCES "character_religion" ("id") DEFERRABLE INITIALLY DEFERRED, "wesenschaden_andere_gestalt" integer NULL, "ep" integer unsigned NOT NULL CHECK ("ep" >= 0), "HPplus_fix" integer NULL, "ip" integer NOT NULL, "gfs_id" integer NULL REFERENCES "character_gfs" ("id") DEFERRABLE INITIALLY DEFERRED, "tp" integer NOT NULL);
INSERT INTO "new__character_charakter" ("gfs_id", "manifest", "haarfarbe", "HPplus_fix", "useEco", "hautfarbe", "gewicht", "ep", "sp", "id", "alter", "rang", "notizen", "geld", "persönlicheZiele", "wesenschaden_waff_kampf", "wesenschaden_andere_gestalt", "religion_id", "name", "augenfarbe", "eigentümer_id", "nutzt_magie", "sonstiger_manifestverlust", "notizen_sonstiger_manifestverlust", "sonstige_items", "in_erstellung", "eco", "HPplus", "größe", "ep_system", "morph", "beruf_id", "präf_arm", "geschlecht", "tp", "sexualität", "ip") SELECT "gfs_id", "manifest", "haarfarbe", "HPplus_fix", "useEco", "hautfarbe", "gewicht", "ep", "sp", "id", "alter", "rang", "notizen", "geld", "persönlicheZiele", "wesenschaden_waff_kampf", "wesenschaden_andere_gestalt", "religion_id", "name", "augenfarbe", "eigentümer_id", "nutzt_magie", "sonstiger_manifestverlust", "notizen_sonstiger_manifestverlust", "sonstige_items", "in_erstellung", "eco", "HPplus", "größe", "ep_system", "morph", "beruf_id", "präf_arm", "geschlecht", "tp", "sexualität", "ip" FROM "character_charakter";
DROP TABLE "character_charakter";
ALTER TABLE "new__character_charakter" RENAME TO "character_charakter";
CREATE INDEX "character_charakter_beruf_id_90824ebd" ON "character_charakter" ("beruf_id");
CREATE INDEX "character_charakter_eigentümer_id_b22391ee" ON "character_charakter" ("eigentümer_id");
CREATE INDEX "character_charakter_religion_id_00ca8313" ON "character_charakter" ("religion_id");
CREATE INDEX "character_charakter_gfs_id_c75a5982" ON "character_charakter" ("gfs_id");
--
-- Alter field fp on relfertigkeit
--
CREATE TABLE "new__character_relfertigkeit" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "char_id" integer NOT NULL REFERENCES "character_charakter" ("id") DEFERRABLE INITIALLY DEFERRED, "fertigkeit_id" integer NOT NULL REFERENCES "character_fertigkeit" ("id") DEFERRABLE INITIALLY DEFERRED, "fp_bonus" integer NOT NULL, "fp" integer NOT NULL);
INSERT INTO "new__character_relfertigkeit" ("fertigkeit_id", "char_id", "fp", "fp_bonus", "id") SELECT "fertigkeit_id", "char_id", "fp", "fp_bonus", "id" FROM "character_relfertigkeit";
DROP TABLE "character_relfertigkeit";
ALTER TABLE "new__character_relfertigkeit" RENAME TO "character_relfertigkeit";
CREATE UNIQUE INDEX "character_relfertigkeit_char_id_fertigkeit_id_0e5efdfe_uniq" ON "character_relfertigkeit" ("char_id", "fertigkeit_id");
CREATE INDEX "character_relfertigkeit_char_id_41cf96de" ON "character_relfertigkeit" ("char_id");
CREATE INDEX "character_relfertigkeit_fertigkeit_id_74b1eeb7" ON "character_relfertigkeit" ("fertigkeit_id");
--
-- Add Migration to django_migrations
--
insert into django_migrations ('app', 'name', 'applied') values ('character', '0035_manually_via_sql', '2020-08-11 09:54:40.590041');
COMMIT;
