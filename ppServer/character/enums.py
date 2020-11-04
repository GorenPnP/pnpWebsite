magie_enum = [('r', "reinmagisch"),
              ("t", "teilmagisch"),
              ("m", "mundan")]


enum_wesenkr = [('a', 'alle'),
                ('m', 'magisch'),
                ('w', "wesenspezifisch"),
                ('f', 'manifest < ..')
                ]


""" enum for <code>Fertigkeit</code>"""
limit_enum = [('-', 'keins'),
              ('g', 'geistig'),
              ('k', 'körperlich'),
              ('m', 'magisch')]


status_enum = [
    ('zahm', 'zahm'),
    ('rebellisch', 'rebellisch')
]


EcoMorph_enum = [('e', 'echo'),
                 ('m', 'morph')]


nutzt_magie_enum = [(20, "selten"),
                    (30, "regelmäßig"),
                    (50, "häufig")]


würfelart_enum = [(4, "W4"), (6, 'W6'), (8, "W8"), (10, "W10"), (12, "W12"), (20, "W20"), (100, "W100")]


""" enum for SkilltreeEntry"""
skilltreeentry_enum = [('w', 'Wesen'),
              ]


skilltreeBase_enum = [('s', 'Schusswaffen'),
                      ('n', 'N.-Waffen'),
                      ('z', 'Zauber'),
                      ('t', "Technik"),
                      ("r", "Rüstung"),
                      ("k", "Wesenkraft"),

                      ("w", "Wesen"),
                      ("g", "Gfs"),
                      ("p", "Professionen")
                      ]


""" enum for kategorie SkilltreeEntryKategorie"""
skilltree_kategorie_enum = [("sk", "Krit. Schaden"),
                            ("st", "Tödl. Schaden"),
                            ("ak", "Krit. Abwehr"),
                            ("at", "Totale Abwehr"),

                            ('ss', 'Schaden'),
                            ("sm", "Munition"),
                            ("sp", "Präzision"),
                            ("sd", "Durchschlagskraft"),
                            ("sr", "Reichweite"),
                            ("sb", "BS"),

                            ("zs", "Wirkung"),
                            ("sa", "Astralschaden"),
                            ("zw", "Wirkdauer"),
                            ("ze", "Aufrechterhalten"),
                            ("zc", "Schwellwert"),

                            #("ns", "Schaden"),
                            #("nb", "BS"),

                            ("tp", "Prozession"),
                            ("tw", "Wifi"),
                            ("tj", "Projektion"),
                            ("ts", "Sicherheit"),
                            ("te", "Speicher"),

                            ("ru", "Schutz"),
                            ("rt", "Stärke"),

                            #("ka", "Astralschaden"),
                            ("kw", "Wirkdauer"),
                            ("ke", "Effekt")
                            ]

teil_erstellung_enum = [("i", "immer"),
                        ("e", "in Erstellung"),
                        ("n", "nicht Erstelllung")
                        ]

talent_enum = [('k', 'Kampfkunst'),
               ('g', 'Geistig'),
               ('m', 'Magisch'),
               ('a', 'Kampfmagisch'),
               ('u', 'Support'),
               ('o', 'Sozial'),
               ('w', 'Schwächend'),
               ('p', 'Gameplay'),
               ('v', 'Verteidigung'),
            ]
